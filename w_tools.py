# noinspection PyUnresolvedReferences
import bpy
from . import b_tools
from . import w_var
from .w_b_scene import BlenderSceneW


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
    """"""  # TODO

    # original scene
    w_var.original_scene = context.scene

    # from interface:
    # wireframe type
    w_var.wireframe_type = context.scene.wireframe_type

    # checkboxes
    w_var.cb_backup = context.scene.cb_backup
    w_var.cb_clear_rlayers = context.scene.cb_clear_rlayers
    w_var.cb_clear_mats = context.scene.cb_clear_mats
    w_var.cb_only_selected = context.scene.cb_only_selected
    w_var.cb_ao = context.scene.cb_ao
    w_var.cb_clay = context.scene.cb_clay
    w_var.cb_clay_only = w_var.cb_clay_only_active and context.scene.cb_clay_only
    w_var.cb_comp = w_var.cb_comp_active and context.scene.cb_comp
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
    """"""  # TODO
    success = True
    error_msg = ""

    if w_var.cb_only_selected and not b_tools.check_any_selected(context.scene, 'MESH'):
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
        error_msg += '- No wire scene name!\n'
        success = False

        # used for row alert in __init__.py
        w_var.error_301 = True

    if w_var.wireframe_type == 'WIREFRAME_BI' and len(w_var.scene_name_2) == 0:
        error_msg += '- No clay scene name!\n'
        success = False
        # used for row alert in __init__.py
        w_var.error_302 = True

    return success, error_msg


def update_material_lists():
    """"""  # TODO
    if len(w_var.mat_wire_name) > 0:
        if not (w_var.wireframe_type == 'WIREFRAME_BI' and w_var.cb_clay_only):
            bpy.data.scenes[w_var.scene_name_1].materials.wire = w_var.mat_wire_name

            if w_var.wireframe_type == 'WIREFRAME_BI':
                bpy.data.scenes[w_var.scene_name_2].materials.wire = w_var.mat_wire_name

            if w_var.cb_backup:
                w_var.original_scene.materials.wire = w_var.mat_wire_name

        else:
            bpy.data.scenes[w_var.scene_name_2].materials.wire = w_var.mat_wire_name

    if len(w_var.mat_clay_name) > 0:
        if not (w_var.wireframe_type == 'WIREFRAME_BI' and w_var.cb_clay_only):
            bpy.data.scenes[w_var.scene_name_1].materials.clay = w_var.mat_clay_name

            if w_var.wireframe_type == 'WIREFRAME_BI':
                bpy.data.scenes[w_var.scene_name_2].materials.clay = w_var.mat_clay_name

            if w_var.cb_backup:
                w_var.original_scene.materials.clay = w_var.mat_clay_name

        else:
            bpy.data.scenes[w_var.scene_name_2].materials.clay = w_var.mat_clay_name


def create_wireframe_bi():
    """Creates the complete wireframe using the blender internal setup."""

    # sets up a wireframe scene
    if not w_var.cb_clay_only:

        # creates wireframe scene
        wire_scene = BlenderSceneW(w_var.original_scene, True, w_var.scene_name_1, 'BLENDER_RENDER')

        if w_var.cb_only_selected:

            # sets all selected meshes to a list
            # (need to set only_selected after I copy the scene to get the selected meshes from the copied scene)
            wire_scene.selected_objects_to_list(['MESH'])

        # changes 3D view pivot point to bounding box center for scaling to work as expected later on
        # (also saves original pivot point to be able to change back in the end)
        original_pivotpoint = wire_scene.view3d_pivotpoint('get')
        wire_scene.view3d_pivotpoint('set', 'BOUNDING_BOX_CENTER')

        # deletes unnecessary objects and removes all materials from the meshes left
        wire_scene.clean_objects()
        wire_scene.clear_all_materials()

        # sets up renderlayer
        wire_scene.set_up_rlayer('wireframe', [0, 1], [0], [1])

        # selects and moves all affected objects to layer 0
        wire_scene.select('SELECT', layers=w_var.layer_numbers_affected, layers_excluded={'ELSE'})
        wire_scene.move_selected_to_layer(0)

        # selects and moves all 'other' objects to layer 1
        wire_scene.select('SELECT', layers=w_var.layer_numbers_other, layers_excluded={'ELSE'})
        wire_scene.move_selected_to_layer(1)

        # selects all meshes on layer 0 and copies them to layer 1, then sets up wireframe material
        # (copy first to skip materials on copies)
        wire_scene.select('SELECT', {'MESH'}, {'ELSE'}, {0}, {'ELSE'})
        wire_scene.copy_selected_to_layer(1)
        w_var.wire_bi_mat = wire_scene.add_wireframe_bi()

        # sets render alpha mode to transparent, to be able to composite this wireframe on top of the clay later
        bpy.data.scenes[wire_scene.name].render.alpha_mode = 'TRANSPARENT'

        # changes back to original 3D view pivot point and deselects all objects as a last thing to clean up
        wire_scene.view3d_pivotpoint('set', original_pivotpoint)
        wire_scene.select('DESELECT', {'ALL'}, layers={'ALL'})

        # creates clay/other scene, I only call it clay_scene but clay material might not be used
        clay_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_2, 'CYCLES')

        # sets up renderlayer and composition for wireframe (and ambient occlusion lighting if used)
        clay_scene.set_up_rlayer('clay')
        clay_scene.comp_add_wireframe_bi(wire_scene)

    # only sets up a clay scene
    else:
        # creates clay scene
        clay_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_2, 'CYCLES')
        clay_scene.set_up_rlayer('clay')

    if w_var.cb_only_selected:

            # sets all selected meshes to a list
            # (need to set only_selected after I copy the scene to get the selected meshes from the copied scene)
            clay_scene.selected_objects_to_list(['MESH'])

    if w_var.cb_clear_mats:

        # removes all materials from the meshes
        clay_scene.clear_all_materials()

    if w_var.cb_clay:

        # adds clay material to affected meshes
        clay_scene.select('SELECT', {'MESH'}, {'ELSE'}, layers_excluded={'ELSE'})
        w_var.clay_mat = clay_scene.add_clay_to_selected()

    if w_var.cb_ao:

        # sets up ambient occlusion lighting
        clay_scene.set_up_world_ao()

    # deselects all objects as a last thing to clean up
    clay_scene.select('DESELECT', {'ALL'}, layers={'ALL'})


def create_wireframe_freestyle():
    """Creates the complete wireframe using the freestyle setup."""

    # creates wireframe scene
    wire_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_1, 'CYCLES')

    if w_var.cb_only_selected:

            # sets all selected meshes to a list
            # (need to set only_selected after I copy the scene to get the selected meshes from the copied scene)
            wire_scene.selected_objects_to_list(['MESH'])

    if not w_var.cb_clay_only:

        # sets up renderlayer(s) (depending on 'Composited wireframing' checkbox) and freestyle wireframing
        wire_scene.set_up_rlayer('wireframe', rlname_other='other')
        w_var.wire_freestyle_linestyle = wire_scene.add_wireframe_freestyle()

    else:
        # sets up renderlayer named 'clay' instead of 'wireframe'
        wire_scene.set_up_rlayer('clay')

    if w_var.cb_clear_mats:

        # removes all materials from the meshes
        wire_scene.clear_all_materials()

    if w_var.cb_clay:

        # adds clay material to affected meshes
        wire_scene.select('SELECT', {'MESH'}, {'ELSE'}, layers_excluded={'ELSE'})
        w_var.clay_mat = wire_scene.add_clay_to_selected()

    if w_var.cb_ao and not w_var.cb_comp:

        # sets up ambient occlusion lighting
        wire_scene.comp_add_ao()
        wire_scene.set_up_world_ao()

    elif w_var.cb_comp:

        # sets up composition for wireframe and sets up ambient occlusion lighting if used
        wire_scene.comp_add_wireframe_freestyle()
        bpy.data.scenes[wire_scene.name].cycles.film_transparent = True

        if w_var.cb_ao:
            wire_scene.set_up_world_ao()

    # deselects all objects as a last thing to clean up
    wire_scene.select('DESELECT', {'ALL'}, layers={'ALL'})


def create_wireframe_modifier():
    """Creates the complete wireframe using the modifier setup.

    If the mesh(es) you apply this to have several materials each and you don't use clay, the material of the
    wireframe will not be the expected one as it depends on the material offset set in the wireframe modifier.
    """

    # creates wireframe scene
    wire_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_1, 'CYCLES')

    if w_var.cb_only_selected:

            # sets all selected meshes to a list
            # (need to set only_selected after I copy the scene to get the selected meshes from the copied scene)
            wire_scene.selected_objects_to_list(['MESH'])

    if w_var.cb_clear_mats:

        # removes all materials from the meshes
        wire_scene.clear_all_materials()

    if w_var.cb_clay:

        # adds clay material to affected meshes
        # (need to add clay before wireframe for material offset in wireframe modifier to be correct)
        wire_scene.select('SELECT', {'MESH'}, {'ELSE'}, layers_excluded={'ELSE'})
        w_var.clay_mat = wire_scene.add_clay_to_selected()

    if not w_var.cb_clay_only:

        # sets up renderlayer and adds wireframe modifier to affected meshes
        wire_scene.set_up_rlayer('wireframe')
        w_var.wire_modifier_mat = wire_scene.add_wireframe_modifier()

    else:

        # sets up renderlayer named 'clay' instead of 'wireframe'
        wire_scene.set_up_rlayer('clay')

    if w_var.cb_ao:

        # sets up ambient occlusion lighting
        wire_scene.set_up_world_ao()
        wire_scene.comp_add_ao()

    # deselects all objects as a last thing to clean up
    wire_scene.select('DESELECT', {'ALL'}, layers={'ALL'})


def add_to_wireframe_bi():
    """"""  # TODO
    # sets up a wireframe scene
    if not w_var.cb_clay_only:

        # TODO
        wire_scene = BlenderSceneW(bpy.data.scenes[w_var.scene_name_1], False)

        if w_var.cb_only_selected:

            # sets all selected meshes to a list
            # (need to set only_selected after I copy the scene to get the selected meshes from the copied scene)
            wire_scene.selected_objects_to_list(['MESH'])

        # changes 3D view pivot point to bounding box center for scaling to work as expected later on
        # (also saves original pivot point to be able to change back in the end)
        original_pivotpoint = wire_scene.view3d_pivotpoint('get')
        wire_scene.view3d_pivotpoint('set', 'BOUNDING_BOX_CENTER')

        # deletes unnecessary objects and removes all materials from the meshes left
        wire_scene.clean_objects()
        wire_scene.clear_all_materials()

        # sets up renderlayer
        wire_scene.set_up_rlayer('wireframe', [0, 1], [0], [1])

        # selects and moves all affected objects to layer 0
        wire_scene.select('SELECT', layers=w_var.layer_numbers_affected, layers_excluded={'ELSE'})
        wire_scene.move_selected_to_layer(0)

        # selects and moves all 'other' objects to layer 1
        wire_scene.select('SELECT', layers=w_var.layer_numbers_other, layers_excluded={'ELSE'})
        wire_scene.move_selected_to_layer(1)

        # selects all meshes on layer 0 and copies them to layer 1, then sets up wireframe material
        # (copy first to skip materials on copies)
        wire_scene.select('SELECT', {'MESH'}, {'ELSE'}, {0}, {'ELSE'})
        wire_scene.copy_selected_to_layer(1)
        w_var.wire_bi_mat = wire_scene.add_wireframe_bi()

        # sets render alpha mode to transparent, to be able to composite this wireframe on top of the clay later
        bpy.data.scenes[wire_scene.name].render.alpha_mode = 'TRANSPARENT'

        # changes back to original 3D view pivot point and deselects all objects as a last thing to clean up
        wire_scene.view3d_pivotpoint('set', original_pivotpoint)
        wire_scene.select('DESELECT', {'ALL'}, layers={'ALL'})

        # creates clay/other scene, I only call it clay_scene but clay material might not be used
        clay_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_2, 'CYCLES')

        # sets up renderlayer and composition for wireframe (and ambient occlusion lighting if used)
        clay_scene.set_up_rlayer('clay')
        clay_scene.comp_add_wireframe_bi(wire_scene)

    # only sets up a clay scene
    else:
        # creates clay scene
        clay_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, 'clay', 'CYCLES')
        clay_scene.set_up_rlayer('clay')

    if w_var.cb_only_selected:

            # sets all selected meshes to a list
            # (need to set only_selected after I copy the scene to get the selected meshes from the copied scene)
            clay_scene.selected_objects_to_list(['MESH'])

    if w_var.cb_clear_mats:

        # removes all materials from the meshes
        clay_scene.clear_all_materials()

    if w_var.cb_clay:

        # adds clay material to affected meshes
        clay_scene.select('SELECT', {'MESH'}, {'ELSE'}, layers_excluded={'ELSE'})
        w_var.clay_mat = clay_scene.add_clay_to_selected()

    if w_var.cb_ao:

        # sets up ambient occlusion lighting
        clay_scene.set_up_world_ao()

    # deselects all objects as a last thing to clean up
    clay_scene.select('DESELECT', {'ALL'}, layers={'ALL'})


def add_to_wireframe_freestyle():
    """"""  # TODO


def add_to_wireframe_modifier():
    """"""  # TODO
