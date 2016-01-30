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
        layers_affected = list(w_var.original_scene.wirebomb.layers_affected)

    return layers_affected


def set_layers_other(layers_affected):
    """Sets all layers who will be included in the render layer just as they are in a list.

    Returns:
        A list with booleans representing all the layers that will be included in the render layer just as they are.
    """
    layers_other = list(w_var.original_scene.wirebomb.layers_other)

    for index in range(0, 20):
        if layers_other[index] and layers_affected[index]:
            layers_other[index] = False

    return layers_other


def set_variables(context):
    """Sets variables in w_var with data from the UI, also resets some variables.

    Args:
        context: Scene context object.
    """

    # resetting render layer names
    w_var.rlname = ''
    w_var.rlname_other = ''

    # resetting objects selected
    w_var.objects_affected = set()
    w_var.objects_other = set()
    w_var.objects_all_used = set()

    # original scene
    w_var.original_scene = context.scene

    # from interface:
    # wireframe type
    w_var.wireframe_method = context.scene.wirebomb.wireframe_method

    # checkboxes
    w_var.cb_backup = context.scene.wirebomb.cb_backup
    w_var.cb_clear_rlayers = context.scene.wirebomb.cb_clear_rlayers
    w_var.cb_clear_materials = context.scene.wirebomb.cb_clear_materials
    w_var.cb_composited = context.scene.wirebomb.cb_composited
    w_var.cb_only_selected = context.scene.wirebomb.cb_only_selected
    w_var.cb_ao = context.scene.wirebomb.cb_ao
    w_var.cb_clay = context.scene.wirebomb.cb_clay
    w_var.cb_clay_only = w_var.cb_clay_only_active and context.scene.wirebomb.cb_clay_only
    w_var.cb_mat_wire = w_var.cb_mat_wire_active and context.scene.wirebomb.cb_mat_wire
    w_var.cb_mat_clay = w_var.cb_mat_clay_active and context.scene.wirebomb.cb_mat_clay

    # colors set
    w_var.color_wire = context.scene.wirebomb.color_wire
    w_var.color_clay = context.scene.wirebomb.color_clay

    # materials set (names)
    w_var.mat_wire_name = context.scene.wirebomb.material_wire
    w_var.mat_clay_name = context.scene.wirebomb.material_clay

    # sliders
    w_var.slider_wt_freestyle = context.scene.wirebomb.slider_wt_freestyle
    w_var.slider_wt_modifier = context.scene.wirebomb.slider_wt_modifier

    # layers selected
    layers_affected = set_layers_affected()
    layers_other = set_layers_other(layers_affected)
    w_var.layer_numbers_affected = b_tools.layerlist_to_numberset(layers_affected)
    w_var.layer_numbers_other = b_tools.layerlist_to_numberset(layers_other)

    # affected and other layers together, | is logical OR operator
    w_var.layer_numbers_all_used = w_var.layer_numbers_affected | w_var.layer_numbers_other

    # scene name set
    w_var.scene_name_1 = context.scene.wirebomb.scene_name_1


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
        error_msg += '- No wireframe material selected!\n'
        success = False

    if w_var.cb_mat_clay and w_var.mat_clay_name == '':
        error_msg += '- No clay material selected!\n'
        success = False

    if len(w_var.scene_name_1) == 0 and w_var.cb_backup:
        error_msg += '- No wireframe/clay scene name!\n'
        success = False

        # used for row alert in __init__.py
        w_var.error_301 = True

    return success, error_msg


def config_load(context, filepath):
    """Loads an INI config file from filepath."""

    config = configparser.ConfigParser()
    config.read(filepath)

    if 'WIREFRAME TYPE' in config and 'wireframe_method' in config['WIREFRAME TYPE']:
        context.scene.wirebomb.wireframe_method = config['WIREFRAME TYPE']['wireframe_method']

    if 'CHECKBOXES' in config:
        if 'cb_backup' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_backup = eval(config['CHECKBOXES']['cb_backup'])

        if 'cb_clear_rlayers' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_clear_rlayers = eval(config['CHECKBOXES']['cb_clear_rlayers'])

        if 'cb_clear_materials' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_clear_materials = eval(config['CHECKBOXES']['cb_clear_materials'])

        if 'cb_composited' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_composited = eval(config['CHECKBOXES']['cb_composited'])

        if 'cb_only_selected' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_only_selected = eval(config['CHECKBOXES']['cb_only_selected'])

        if 'cb_ao' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_ao = eval(config['CHECKBOXES']['cb_ao'])

        if 'cb_clay' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_clay = eval(config['CHECKBOXES']['cb_clay'])

        if 'cb_clay_only' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_clay_only = eval(config['CHECKBOXES']['cb_clay_only'])

        if 'cb_mat_wire' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_mat_wire = eval(config['CHECKBOXES']['cb_mat_wire'])

        if 'cb_mat_clay' in config['CHECKBOXES']:
            context.scene.wirebomb.cb_mat_clay = eval(config['CHECKBOXES']['cb_mat_clay'])

    if 'COLORS SET' in config:
        if 'color_wireframe' in config['COLORS SET']:
            context.scene.wirebomb.color_wire = eval(config['COLORS SET']['color_wireframe'])

        if 'color_clay' in config['COLORS SET']:
            context.scene.wirebomb.color_clay = eval(config['COLORS SET']['color_clay'])

    if 'MATERIALS SET' in config:
        if 'wireframe' in config['MATERIALS SET']:
            if config['MATERIALS SET']['wireframe'] in bpy.data.materials:
                context.scene.wirebomb.material_wire = config['MATERIALS SET']['wireframe']

        if 'clay' in config['MATERIALS SET']:
            if config['MATERIALS SET']['clay'] in bpy.data.materials:
                context.scene.wirebomb.material_clay = config['MATERIALS SET']['clay']

    if 'SLIDERS' in config:
        if 'slider_wt_freestyle' in config['SLIDERS']:
            context.scene.wirebomb.slider_wt_freestyle = eval(config['SLIDERS']['slider_wt_freestyle'])

        if 'slider_wt_modifier' in config['SLIDERS']:
            context.scene.wirebomb.slider_wt_modifier = eval(config['SLIDERS']['slider_wt_modifier'])

    if 'LAYERS SELECTED' in config:
        if 'layers_affected' in config['LAYERS SELECTED']:
            context.scene.wirebomb.layers_affected = eval(config['LAYERS SELECTED']['layers_affected'])

        if 'layers_other' in config['LAYERS SELECTED']:
            context.scene.wirebomb.layers_other = eval(config['LAYERS SELECTED']['layers_other'])

    if 'SCENE NAME SET' in config:
        if 'scene_name_1' in config['SCENE NAME SET']:
            context.scene.wirebomb.scene_name_1 = config['SCENE NAME SET']['scene_name_1']


def config_save(context, filepath):
    """Saves an INI config file to filepath."""

    config = configparser.ConfigParser()

    config['WIREFRAME TYPE'] = {'wireframe_method': context.scene.wirebomb.wireframe_method}

    config['CHECKBOXES'] = {'cb_backup': context.scene.wirebomb.cb_backup,
                            'cb_clear_rlayers': context.scene.wirebomb.cb_clear_rlayers,
                            'cb_clear_materials': context.scene.wirebomb.cb_clear_materials,
                            'cb_composited': context.scene.wirebomb.cb_composited,
                            'cb_only_selected': context.scene.wirebomb.cb_only_selected,
                            'cb_ao': context.scene.wirebomb.cb_ao,
                            'cb_clay': context.scene.wirebomb.cb_clay,
                            'cb_clay_only': context.scene.wirebomb.cb_clay_only,
                            'cb_mat_wire': context.scene.wirebomb.cb_mat_wire,
                            'cb_mat_clay': context.scene.wirebomb.cb_mat_clay}

    config['COLORS SET'] = {'color_wireframe': list(context.scene.wirebomb.color_wire),
                            'color_clay': list(context.scene.wirebomb.color_clay)}

    config['MATERIALS SET'] = {'wireframe': context.scene.wirebomb.material_wire,
                               'clay': context.scene.wirebomb.material_clay}

    config['SLIDERS'] = {'slider_wt_freestyle': context.scene.wirebomb.slider_wt_freestyle,
                         'slider_wt_modifier': context.scene.wirebomb.slider_wt_modifier}

    config['LAYERS SELECTED'] = {'layers_affected': list(context.scene.wirebomb.layers_affected),
                                 'layers_other': list(context.scene.wirebomb.layers_other)}

    config['SCENE NAME SET'] = {'scene_name_1': context.scene.wirebomb.scene_name_1}

    with open(filepath, 'w') as configfile:
        config.write(configfile)


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
        # also saves freestyle linestyle name
        wire_scene.set_up_rlayer('wireframe', rlname_other='other')
        wire_scene.get_scene().wirebomb.data_freestyle_linestyle = wire_scene.add_wireframe_freestyle().name

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

        # adds clay material to affected meshes and saves material name
        wire_scene.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        wire_scene.get_scene().wirebomb.data_material_clay = wire_scene.add_clay_to_selected().name

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

        # adds clay material to affected meshes and saves material name
        # (need to add clay material before wireframe material for material offset in wireframe modifier to be correct)
        wire_scene.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        wire_scene.get_scene().wirebomb.data_material_clay = wire_scene.add_clay_to_selected().name

    # updates progress bar to 75 %
    bpy.context.window_manager.progress_update(75)

    if not w_var.cb_clay_only:

        # sets up renderlayer and adds wireframe modifier/material to affected meshes and saves wireframe material
        wire_scene.set_up_rlayer('wireframe')
        wire_scene.get_scene().wirebomb.data_material_wire = wire_scene.add_wireframe_modifier().name

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
