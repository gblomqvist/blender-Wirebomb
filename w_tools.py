# <pep8-80 compliant>

import bpy
import configparser
from .w_b_scene import BlenderSceneW
from . import b_tools
from . import w_var


def set_layers_affected():
    """Sets all layers who will be affected by wireframing and/or clay material to a list.

    Returns:
        A list with booleans representing all the layers that will be affected affected by
            wireframing and/or clay material.
    """
    if w_var.cb_only_selected:
        layers_affected = [False, ]*20

        for obj in bpy.context.scene.objects:
            if obj.select:
                layers_affected = b_tools.manipulate_layerlists('add', layers_affected, obj.layers)

    else:
        layers_affected = list(w_var.original_scene.layers_affected)

    return layers_affected


def set_layers_other(layers_affected):
    """Sets all layers who will be included in the render layer just as they are in a list.

    Returns:
        A list with booleans representing all the layers that will be included in the render layer just as they are.
    """
    layers_other = list(w_var.original_scene.layers_other)

    for index in range(0, 20):
        if layers_other[index] and layers_affected[index]:
            layers_other[index] = False

    return layers_other


def set_variables(context):
    """Sets variables in w_var with data from the UI, also resets some variables.

    Args:
        context: Scene context object.
    """

    # resetting unique IDs for use in real-time color change and wireframe modifier thickness change
    w_var.node_wireframe_diffuse = ''
    w_var.node_clay_diffuse = ''
    w_var.modifier_wireframe = ''

    # resetting render layer names
    w_var.rlname = ''
    w_var.rlname_2 = ''
    w_var.rlname_other = ''

    # resetting objects selected
    w_var.objects_affected = set()
    w_var.objects_other = set()
    w_var.objects_all_used = set()

    # resetting materials
    w_var.wire_freestyle_linestyle = None
    w_var.wire_modifier_mat = None
    w_var.wire_bi_mat = None
    w_var.clay_mat = None

    # original scene
    w_var.original_scene = context.scene

    # from interface:
    # wireframe type
    w_var.wireframe_method = context.scene.wireframe_method

    # checkboxes
    w_var.cb_backup = context.scene.cb_backup
    w_var.cb_clear_rlayers = context.scene.cb_clear_rlayers
    w_var.cb_clear_materials = context.scene.cb_clear_materials
    w_var.cb_composited = w_var.cb_composited_active and context.scene.cb_composited
    w_var.cb_only_selected = context.scene.cb_only_selected
    w_var.cb_ao = context.scene.cb_ao
    w_var.cb_clay = context.scene.cb_clay
    w_var.cb_clay_only = w_var.cb_clay_only_active and context.scene.cb_clay_only
    w_var.cb_mat_wire = w_var.cb_mat_wire_active and context.scene.cb_mat_wire
    w_var.cb_mat_clay = w_var.cb_mat_clay_active and context.scene.cb_mat_clay

    # colors set
    w_var.color_wire = context.scene.color_wire
    w_var.color_clay = context.scene.color_clay

    # materials set (names)
    w_var.mat_wire_name = context.scene.materials.wire
    w_var.mat_clay_name = context.scene.materials.clay

    # sliders
    w_var.slider_wt_freestyle = context.scene.slider_wt_freestyle
    w_var.slider_wt_modifier = context.scene.slider_wt_modifier

    # layers selected
    layers_affected = set_layers_affected()
    layers_other = set_layers_other(layers_affected)
    w_var.layer_numbers_affected = b_tools.layerlist_to_numberset(layers_affected)
    w_var.layer_numbers_other = b_tools.layerlist_to_numberset(layers_other)

    # affected and other layers together, | is logical OR operator
    w_var.layer_numbers_all_used = w_var.layer_numbers_affected | w_var.layer_numbers_other

    # scene names set
    w_var.scene_name_1 = context.scene.scene_name_1
    w_var.scene_name_2 = context.scene.scene_name_2


def error_check(context):
    """Checks for any possible errors.

    Args:
        context: Scene context object.
    """
    success = True
    error_msg = ""

    scene = BlenderSceneW(context.scene, False)

    if w_var.cb_only_selected and not scene.check_any_selected('MESH'):
        error_msg += "- Checkbox 'Only selected' is activated but no mesh is selected!\n"
        success = False

        # used for row alert in __init__.py
        w_var.error_101 = True

    if (not w_var.cb_only_selected and
            not len(w_var.layer_numbers_affected) > 0 and not len(w_var.layer_numbers_other) > 0):
        error_msg += "- No layers selected! Maybe you forgot to use 'Only selected'?\n"
        success = False

    if w_var.cb_mat_wire and w_var.mat_wire_name == '':
        error_msg += '- No wire material selected!\n'
        success = False

        # used for row alert in __init__.py
        w_var.error_201 = True

    if w_var.cb_mat_clay and w_var.mat_clay_name == '':
        error_msg += '- No clay material selected! Maybe there\'s no materials in this .blend file?\n'
        success = False

        # used for row alert in __init__.py
        w_var.error_202 = True

    if len(w_var.scene_name_1) == 0:
        error_msg += '- No wire/clay scene name!\n'
        success = False

        # used for row alert in __init__.py
        w_var.error_301 = True

    if w_var.wireframe_method == 'WIREFRAME_BI' and len(w_var.scene_name_2) == 0:
        error_msg += '- No clay/other scene name!\n'
        success = False

        # used for row alert in __init__.py
        w_var.error_302 = True

    return success, error_msg


def config_load(context, filepath):
    """Loads an INI config file from filepath."""

    config = configparser.ConfigParser()
    config.read(filepath)

    context.scene.wireframe_method = config['WIREFRAME TYPE']['wireframe_method']

    context.scene.cb_backup = eval(config['CHECKBOXES']['cb_backup'])
    context.scene.cb_clear_rlayers = eval(config['CHECKBOXES']['cb_clear_rlayers'])
    context.scene.cb_clear_materials = eval(config['CHECKBOXES']['cb_clear_materials'])
    context.scene.cb_composited = eval(config['CHECKBOXES']['cb_composited'])
    context.scene.cb_only_selected = eval(config['CHECKBOXES']['cb_only_selected'])
    context.scene.cb_ao = eval(config['CHECKBOXES']['cb_ao'])
    context.scene.cb_clay = eval(config['CHECKBOXES']['cb_clay'])
    context.scene.cb_clay_only = eval(config['CHECKBOXES']['cb_clay_only'])
    context.scene.cb_mat_wire = eval(config['CHECKBOXES']['cb_mat_wire'])
    context.scene.cb_mat_clay = eval(config['CHECKBOXES']['cb_mat_clay'])

    context.scene.color_wire = eval(config['COLORS SET']['color_wire'])
    context.scene.color_clay = eval(config['COLORS SET']['color_clay'])

    context.scene.materials.wire = config['MATERIALS SET (NAMES)']['wire']
    context.scene.materials.clay = config['MATERIALS SET (NAMES)']['clay']

    context.scene.slider_wt_freestyle = eval(config['SLIDERS']['slider_wt_freestyle'])
    context.scene.slider_wt_modifier = eval(config['SLIDERS']['slider_wt_modifier'])

    context.scene.layers_affected = eval(config['LAYERS SELECTED']['layers_affected'])
    context.scene.layers_other = eval(config['LAYERS SELECTED']['layers_other'])

    context.scene.scene_name_1 = config['SCENE NAMES SET']['scene_name_1']
    context.scene.scene_name_2 = config['SCENE NAMES SET']['scene_name_2']


def config_save(context, filepath):
    """Saves an INI config file to filepath."""

    config = configparser.ConfigParser()

    config['WIREFRAME TYPE'] = {'wireframe_method': context.scene.wireframe_method}

    config['CHECKBOXES'] = {'cb_backup': context.scene.cb_backup,
                            'cb_clear_rlayers': context.scene.cb_clear_rlayers,
                            'cb_clear_materials': context.scene.cb_clear_materials,
                            'cb_composited': context.scene.cb_composited,
                            'cb_only_selected': context.scene.cb_only_selected,
                            'cb_ao': context.scene.cb_ao,
                            'cb_clay': context.scene.cb_clay,
                            'cb_clay_only': context.scene.cb_clay_only,
                            'cb_mat_wire': context.scene.cb_mat_wire,
                            'cb_mat_clay': context.scene.cb_mat_clay}

    config['COLORS SET'] = {'color_wire': list(context.scene.color_wire),
                            'color_clay': list(context.scene.color_clay)}

    config['MATERIALS SET (NAMES)'] = {'wire': context.scene.materials.wire,
                                       'clay': context.scene.materials.clay}

    config['SLIDERS'] = {'slider_wt_freestyle': context.scene.slider_wt_freestyle,
                         'slider_wt_modifier': context.scene.slider_wt_modifier}

    config['LAYERS SELECTED'] = {'layers_affected': list(context.scene.layers_affected),
                                 'layers_other': list(context.scene.layers_other)}

    config['SCENE NAMES SET'] = {'scene_name_1': context.scene.scene_name_1,
                                 'scene_name_2': context.scene.scene_name_2}

    with open(filepath, 'w') as configfile:
        config.write(configfile)


def update_material_lists():
    """Updates material lists items to be what they were before in backup scene and wireframe scene(s), as long as the
    items were not empty strings."""
    if len(w_var.mat_wire_name) > 0:
        if not (w_var.wireframe_method == 'WIREFRAME_BI' and w_var.cb_clay_only):
            bpy.data.scenes[w_var.scene_name_1].materials.wire = w_var.mat_wire_name

            if w_var.wireframe_method == 'WIREFRAME_BI':
                bpy.data.scenes[w_var.scene_name_2].materials.wire = w_var.mat_wire_name

            if w_var.cb_backup:
                w_var.original_scene.materials.wire = w_var.mat_wire_name

        else:
            bpy.data.scenes[w_var.scene_name_2].materials.wire = w_var.mat_wire_name

    if len(w_var.mat_clay_name) > 0:
        if not (w_var.wireframe_method == 'WIREFRAME_BI' and w_var.cb_clay_only):
            bpy.data.scenes[w_var.scene_name_1].materials.clay = w_var.mat_clay_name

            if w_var.wireframe_method == 'WIREFRAME_BI':
                bpy.data.scenes[w_var.scene_name_2].materials.clay = w_var.mat_clay_name

            if w_var.cb_backup:
                w_var.original_scene.materials.clay = w_var.mat_clay_name

        else:
            bpy.data.scenes[w_var.scene_name_2].materials.clay = w_var.mat_clay_name


def set_up_wireframe_bi():
    """Sets up the complete wireframe using the blender internal setup."""

    # sets up a wireframe scene
    if not w_var.cb_clay_only:

        # creates wireframe scene
        wire_scene = BlenderSceneW(w_var.original_scene, True, w_var.scene_name_1, 'BLENDER_RENDER')

        # sets all used objects to three sets: affected objects, other object and all used objects
        # (need to do after I copy the scene to get the objects from the copied scene)
        wire_scene.add_objects_used()

        # changes 3D view pivot point to bounding box center for scaling to work as expected later on
        original_pivotpoint = wire_scene.view3d_pivotpoint('get')
        wire_scene.view3d_pivotpoint('set', 'BOUNDING_BOX_CENTER')

        # updates progress bar to 14 %
        bpy.context.window_manager.progress_update(14)

        # deletes unnecessary objects and removes all materials from the affected meshes
        wire_scene.clean_objects()
        wire_scene.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        wire_scene.clear_materials_on_selected()

        # updates progress bar to 26 %
        bpy.context.window_manager.progress_update(26)

        # sets up renderlayer
        wire_scene.set_up_rlayer('wireframe', [0, 1], [0], mask_layers=[1])

        # selects and moves all affected objects to layer 0, then copies them to layer 1
        wire_scene.select('SELECT', objects_excluded={'ELSE'})
        wire_scene.move_selected_to_layer([0])
        wire_scene.copy_selected_to_layer([1])

        # updates progress bar to 33 %
        bpy.context.window_manager.progress_update(33)

        # selects and moves all 'other' objects to layer 1
        wire_scene.select('SELECT', objects=w_var.objects_other, objects_excluded={'ELSE'})
        wire_scene.move_selected_to_layer([1])

        # updates progress bar to 37 %
        bpy.context.window_manager.progress_update(38)

        # sets up wireframe material on affected meshes
        w_var.wire_bi_mat = wire_scene.add_wireframe_bi()

        # sets render alpha mode to transparent, to be able to composite this wireframe on top of the clay later
        bpy.data.scenes[wire_scene.name].render.alpha_mode = 'TRANSPARENT'

        # changes back to original 3D view pivot point and deselects all objects as a last thing to clean up
        wire_scene.view3d_pivotpoint('set', original_pivotpoint)
        wire_scene.select('DESELECT', objects={'ALL'})

        # updates progress bar to 55 %
        bpy.context.window_manager.progress_update(55)

        # creates clay/other scene
        clay_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_2, 'CYCLES')

        # sets up renderlayer and composition for wireframe (and ambient occlusion lighting if used)
        # (need to set up render layer before composition)
        clay_scene.set_up_rlayer('clay')
        clay_scene.comp_add_wireframe_bi(wire_scene)

    # only sets up a clay scene
    else:
        # creates clay scene
        clay_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_2, 'CYCLES')

        # updates progress bar to 30 % and sets up render layer
        bpy.context.window_manager.progress_update(30)
        clay_scene.set_up_rlayer('clay')

    # updates progress bar to 60 %
    bpy.context.window_manager.progress_update(60)

    # sets all used objects to three sets: affected objects, other object and all used objects
    # (need to do after I copy the scene to get the objects from the copied scene)
    clay_scene.add_objects_used()

    # updates progress bar to 72 %
    bpy.context.window_manager.progress_update(72)

    if w_var.cb_clear_materials:

        # removes all materials from affected meshes
        clay_scene.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        clay_scene.clear_materials_on_selected()

    # updates progress bar to 85 %
    bpy.context.window_manager.progress_update(85)

    if w_var.cb_clay:

        # adds clay material to affected meshes
        clay_scene.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        w_var.clay_mat = clay_scene.add_clay_to_selected()

    # updates progress bar to 99 %
    bpy.context.window_manager.progress_update(99)

    if w_var.cb_ao:

        # sets up ambient occlusion lighting
        clay_scene.set_up_world_ao()

    # deselects all objects as a last thing to clean up
    clay_scene.select('DESELECT', objects={'ALL'})


def set_up_wireframe_freestyle():
    """Sets up the complete wireframe using the freestyle setup."""

    # creates wireframe scene
    wire_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_1, 'CYCLES')

    # sets all used objects to three sets: affected objects, other object and all used objects
    # (need to do after I copy the scene to get the objects from the copied scene)
    wire_scene.add_objects_used()

    # updates progress bar to 25 %
    bpy.context.window_manager.progress_update(25)

    if not w_var.cb_clay_only:

        # sets up renderlayer(s) (depending on 'Composited wireframing' checkbox) and freestyle wireframing
        wire_scene.set_up_rlayer('wireframe', rlname_other='other')
        w_var.wire_freestyle_linestyle = wire_scene.add_wireframe_freestyle()

    else:
        # sets up renderlayer named 'clay' instead of 'wireframe'
        wire_scene.set_up_rlayer('clay')

    # updates progress bar to 50 %
    bpy.context.window_manager.progress_update(50)

    if w_var.cb_clear_materials:

        # removes all materials from affected meshes
        wire_scene.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        wire_scene.clear_materials_on_selected()

    # updates progress bar to 75 %
    bpy.context.window_manager.progress_update(75)

    if w_var.cb_clay:

        # adds clay material to affected meshes
        wire_scene.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        w_var.clay_mat = wire_scene.add_clay_to_selected()

    # updates progress bar to 99 %
    bpy.context.window_manager.progress_update(99)

    if w_var.cb_ao and not w_var.cb_composited:

        # sets up ambient occlusion lighting
        wire_scene.comp_add_ao()
        wire_scene.set_up_world_ao()

    elif w_var.cb_composited:

        # sets up composition for wireframe and sets up ambient occlusion lighting if used
        wire_scene.comp_add_wireframe_freestyle()
        bpy.data.scenes[wire_scene.name].cycles.film_transparent = True

        if w_var.cb_ao:
            wire_scene.set_up_world_ao()

    # deselects all objects as a last thing to clean up
    wire_scene.select('DESELECT', objects={'ALL'})


def set_up_wireframe_modifier():
    """Sets up the complete wireframe using the modifier setup.

    If the mesh(es) you apply this to have several materials each and you don't use clay, the material of the
    wireframe will not be the expected one as it depends on the material offset set in the wireframe modifier.
    """

    # creates wireframe scene
    wire_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_1, 'CYCLES')

    # sets all used objects to three sets: affected objects, other object and all used objects
    # (need to do after I copy the scene to get the objects from the copied scene)
    wire_scene.add_objects_used()

    # updates progress bar to 25 %
    bpy.context.window_manager.progress_update(25)

    if w_var.cb_clear_materials:

        # removes all materials from affected meshes
        wire_scene.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        wire_scene.clear_materials_on_selected()

    # updates progress bar to 50 %
    bpy.context.window_manager.progress_update(50)

    if w_var.cb_clay:

        # adds clay material to affected meshes
        # (need to add clay material before wireframe material for material offset in wireframe modifier to be correct)
        wire_scene.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        w_var.clay_mat = wire_scene.add_clay_to_selected()

    # updates progress bar to 75 %
    bpy.context.window_manager.progress_update(75)

    if not w_var.cb_clay_only:

        # sets up renderlayer and adds wireframe modifier to affected meshes
        wire_scene.set_up_rlayer('wireframe')
        w_var.wire_modifier_mat = wire_scene.add_wireframe_modifier()

    else:

        # sets up renderlayer named 'clay' instead of 'wireframe'
        wire_scene.set_up_rlayer('clay')

    # updates progress bar to 99 %
    bpy.context.window_manager.progress_update(99)

    if w_var.cb_ao:

        # sets up ambient occlusion lighting
        wire_scene.set_up_world_ao()
        wire_scene.comp_add_ao()

    # deselects all objects as a last thing to clean up
    wire_scene.select('DESELECT', objects={'ALL'})
