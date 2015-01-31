# noinspection PyUnresolvedReferences
import bpy
from .bscene_w import BlenderSceneW
from . import wtools
from . import btools
from . import wvariables


class WireframeOperator(bpy.types.Operator):
    """---"""
    bl_label = "Wireframe"
    bl_idname = 'wireframe_op.create_wireframe'

    def __init__(self):

        self.success = None
        self.error_msg = ""

    def execute(self, context):

        if self.success:
            self.report({'INFO'}, 'There you go!')

        elif not self.success:
            self.report({'ERROR'}, self.error_msg)

        return {'FINISHED'}

    def invoke(self, context, event):
        wvariables.affected_layers_numbers = btools.layerlist_to_numberlist(wtools.set_layers_affected())
        if (bpy.context.scene.CheckboxOnlySelected
                and not BlenderSceneW.check_any_selected(bpy.context.scene, ['MESH'])):
            self.error_msg = "Checkbox 'Only Selected' is activated but no mesh is selected!"
            self.success = False

        elif not any(list(bpy.context.scene.LayersAffected)) and not any(list(bpy.context.scene.LayersOther)):
            self.error_msg = "No layers are selected!"
            self.success = False

        else:
            wvariables.rlname = None
            wvariables.rlname_2 = None
            wvariables.original_scene = bpy.context.scene
            wvariables.other_layers_numbers = btools.layerlist_to_numberlist(wtools.set_layers_other())
            wvariables.affected_layers_numbers = btools.layerlist_to_numberlist(wtools.set_layers_affected())
            wvariables.all_layers_used_numbers = btools.layerlist_to_numberlist(wtools.set_layers_used())
            wvariables.only_selected = []

            if wvariables.original_scene.WireframeType == 'WIREFRAME_BI':
                self.create_wireframe_scene_bi()

            elif wvariables.original_scene.WireframeType == 'WIREFRAME_FREESTYLE':
                self.create_wireframe_scene_freestyle()

            elif wvariables.original_scene.WireframeType == 'WIREFRAME_MODIFIER':
                self.create_wireframe_scene_modifier()

            self.success = True

        return self.execute(context)

    @staticmethod
    def create_wireframe_scene_bi():
        """Creates the complete wireframe by using the blender internal setup."""
        if not (wvariables.original_scene.CheckboxOnlyClay and wvariables.original_scene.CheckboxUseClay):
            # creates wires scene
            wire_scene = BlenderSceneW(wvariables.original_scene, bpy.context.scene.CheckboxNewScene,
                                       'wireframe_wires', 'BLENDER_RENDER')
            wire_scene.set_as_active()

            bpy.context.space_data.pivot_point = 'BOUNDING_BOX_CENTER'

            if wvariables.original_scene.CheckboxOnlySelected:
                wvariables.only_selected = wire_scene.selected_objects_to_list(['MESH'])

            wire_scene.select(wire_scene, 'DESELECT', ['ALL'])
            wtools.clean_objects_bi(wire_scene)

            wire_scene.select(wire_scene, 'SELECT', ['ALL'])
            wire_scene.clear_all_materials()

            wire_scene.set_up_rlayer(wire_scene, 'wireframe', [0, 1], [0], [1])

            wire_scene.select(wire_scene, 'SELECT', ['MESH', 'CAMERA'], ['ELSE'],
                              wvariables.affected_layers_numbers, ['ELSE'])
            wire_scene.move_selected_to_layer(0)

            wire_scene.select(wire_scene, 'SELECT', ['MESH'], ['ELSE'],
                              wvariables.other_layers_numbers, ['ELSE'])
            wire_scene.move_selected_to_layer(1)

            wire_scene.select(wire_scene, 'SELECT', ['MESH'], ['ELSE'], [0], ['ELSE'])
            wire_scene.copy_selected_to_layer(1)
            wire_scene.select(wire_scene, 'DESELECT', ['ALL'])

            wire_scene.select(wire_scene, 'SELECT', ['MESH'], ['ELSE'], [0])
            wvariables.wire_bi_mat = wtools.add_wireframe_bi_to_selected(wire_scene)

            wire_scene.select(wire_scene, 'DESELECT', ['ALL'])

            bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

            # creates clay scene
            clay_scene = BlenderSceneW(wvariables.original_scene, bpy.context.scene.CheckboxNewScene,
                                       'wireframe_clay', 'CYCLES')

        else:
            clay_scene = BlenderSceneW(wvariables.original_scene, bpy.context.scene.CheckboxNewScene,
                                       'clay', 'CYCLES')

        clay_scene.set_as_active()

        if wvariables.original_scene.CheckboxOnlySelected:
            wvariables.only_selected = clay_scene.selected_objects_to_list(['MESH'])

        clay_scene.select(clay_scene, 'DESELECT', ['ALL'])
        clay_scene.set_up_rlayer(clay_scene, 'clay')

        if not (wvariables.original_scene.CheckboxOnlyClay and wvariables.original_scene.CheckboxUseClay):
            wtools.comp_add_wireframe_bi(clay_scene, wire_scene)
            clay_scene.comp_show_backdrop()

        if wvariables.original_scene.CheckboxUseClay:
            clay_scene.select(clay_scene, 'SELECT', ['MESH'], ['ELSE'])
            wvariables.clay_mat = wtools.add_clay_mat_to_selected(clay_scene)

        if wvariables.original_scene.CheckboxUseAO:
            wtools.set_up_world_ao(clay_scene)

        clay_scene.select(clay_scene, 'DESELECT', ['ALL'])

    @staticmethod
    def create_wireframe_scene_freestyle():
        """Creates the complete wireframe by using the freestyle setup."""
        if not (wvariables.original_scene.CheckboxOnlyClay and wvariables.original_scene.CheckboxUseClay):
            wire_scene = BlenderSceneW(wvariables.original_scene, bpy.context.scene.CheckboxNewScene,
                                       'wireframe', 'CYCLES')

        else:
            wire_scene = BlenderSceneW(wvariables.original_scene, bpy.context.scene.CheckboxNewScene,
                                       'clay', 'CYCLES')

        wire_scene.set_as_active()

        if wvariables.original_scene.CheckboxOnlySelected:
            wvariables.only_selected = wire_scene.selected_objects_to_list(['MESH'])

        wire_scene.select(wire_scene, 'DESELECT', ['ALL'])

        if not (wvariables.original_scene.CheckboxOnlyClay and wvariables.original_scene.CheckboxUseClay):
            wire_scene.set_up_rlayer(wire_scene, 'wireframe', rlname_other='clay')

        else:
            wire_scene.set_up_rlayer(wire_scene, 'clay')

        if wvariables.original_scene.CheckboxUseClay:
            wire_scene.select(wire_scene, 'SELECT', ['MESH'], ['ELSE'])
            wvariables.clay_mat = wtools.add_clay_mat_to_selected(wire_scene)

        if not (wvariables.original_scene.CheckboxOnlyClay and wvariables.original_scene.CheckboxUseClay):
            wvariables.wire_freestyle = wtools.add_wireframe_freestyle(wire_scene)

        if wvariables.original_scene.CheckboxUseAO and not wvariables.original_scene.CheckboxComp:
            wtools.comp_add_ao(wire_scene)
            wtools.set_up_world_ao(wire_scene)

        elif wvariables.original_scene.CheckboxComp:
            wtools.comp_add_wireframe_freestyle(wire_scene)
            bpy.context.scene.cycles.film_transparent = True

        wire_scene.select(wire_scene, 'DESELECT', ['ALL'])

    @staticmethod
    def create_wireframe_scene_modifier():
        """Creates the complete wireframe by using the modifier setup."""
        if not (wvariables.original_scene.CheckboxOnlyClay and wvariables.original_scene.CheckboxUseClay):
            wire_scene = BlenderSceneW(wvariables.original_scene, bpy.context.scene.CheckboxNewScene,
                                       'wireframe', 'CYCLES')

        else:
            wire_scene = BlenderSceneW(wvariables.original_scene, bpy.context.scene.CheckboxNewScene,
                                       'clay', 'CYCLES')

        wire_scene.set_as_active()

        if wvariables.original_scene.CheckboxOnlySelected:
            wvariables.only_selected = wire_scene.selected_objects_to_list(['MESH'])

        wire_scene.select(wire_scene, 'DESELECT', ['ALL'])

        if not (wvariables.original_scene.CheckboxOnlyClay and wvariables.original_scene.CheckboxUseClay):
            wire_scene.set_up_rlayer(wire_scene, 'wireframe')

        else:
            wire_scene.set_up_rlayer(wire_scene, 'clay')

        if wvariables.original_scene.CheckboxUseClay:
            wire_scene.select(wire_scene, 'SELECT', ['MESH'], ['ELSE'])
            wvariables.clay_mat = wtools.add_clay_mat_to_selected(wire_scene)

        if wvariables.original_scene.CheckboxUseAO:
            wtools.set_up_world_ao(wire_scene)
            wtools.comp_add_ao(wire_scene)

        if not (wvariables.original_scene.CheckboxOnlyClay and wvariables.original_scene.CheckboxUseClay):
            wire_scene.select(wire_scene, 'SELECT', ['MESH'], ['ELSE'])
            wvariables.wire_modifier_mat = wtools.add_wireframe_modifier(wire_scene)

        wire_scene.select(wire_scene, 'DESELECT', ['ALL'])


class ClearWireframesOperator(bpy.types.Operator):
    """An operator that delete scenes that this add-on has created."""
    bl_label = "Clear wireframes"
    bl_idname = 'wireframe_op.clear_wireframes'

    def invoke(self, context, event):

        for scene in bpy.data.scenes:
            if '_wireframe' in scene.name or '_clay' in scene.name:
                bpy.data.scenes.remove(scene)

        return {'FINISHED'}


class SelectLayersAffectedOperator(bpy.types.Operator):
    """An operator that selects all 'Affected layers'."""
    bl_label = "Select all layers affected"
    bl_idname = 'wireframe_op.select_layers_affected'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.LayersAffected[i] = True

        return {'FINISHED'}


class SelectLayersOtherOperator(bpy.types.Operator):
    """An operator that selects all 'Other layers'."""
    bl_label = "Select all other layers"
    bl_idname = 'wireframe_op.select_layers_other'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.LayersOther[i] = True

        return {'FINISHED'}


class DeselectLayersAffectedOperator(bpy.types.Operator):
    """An operator that deselects all 'Affected layers'."""
    bl_label = "Deselect all layers affected"
    bl_idname = 'wireframe_op.deselect_layers_affected'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.LayersAffected[i] = False

        return {'FINISHED'}


class DeselectLayersOtherOperator(bpy.types.Operator):
    """An operator that deselects all 'Other layers'."""
    bl_label = "Deselect all other layers"
    bl_idname = 'wireframe_op.deselect_layers_other'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.LayersOther[i] = False

        return {'FINISHED'}