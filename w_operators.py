# noinspection PyUnresolvedReferences
import bpy
from . import w_tools
from . import b_tools
from . import w_variables
from .w_b_scene import BlenderSceneW


class WireframeOperator(bpy.types.Operator):
    """Set up wireframe/clay render"""
    bl_label = "Wireframe"
    bl_idname = 'wireframe_op.create_wireframe'

    def __init__(self):
        self.success = True
        self.error_msg = ""

    def execute(self, context):
        if self.success:
            self.report({'INFO'}, 'There you go!')

        elif not self.success:
            self.report({'ERROR'}, self.error_msg)

        return {'FINISHED'}

    def invoke(self, context, event):
        if (context.scene.CheckboxOnlySelected
                and not b_tools.check_any_selected(context.scene, ['MESH'])):
            self.error_msg += "- Checkbox 'Only Selected' is activated but no mesh is selected!\n"
            self.success = False
            w_variables.error_101 = True  # used for row alert in __init__.py

        if (not context.scene.CheckboxOnlySelected and
                not any(list(context.scene.LayersAffected)) and not any(list(context.scene.LayersOther))):
            self.error_msg += "- No affected layers selected!\n"
            self.success = False

        if ((context.scene.WireframeType != 'WIREFRAME_FREESTYLE' and context.scene.CheckboxUseMatWire)
                or context.scene.CheckboxUseMatClay) and len(bpy.data.materials) == 0:
            self.error_msg += '- No materials in scene!\n'
            self.success = False
            if context.scene.CheckboxUseMatWire:
                w_variables.error_201 = True  # used for row alert in __init__.py
            if context.scene.CheckboxUseMatClay:
                w_variables.error_202 = True  # used for row alert in __init__.py

        if len(context.scene.CustomSceneName) == 0:
            self.error_msg += '- No wire scene name!\n'
            self.success = False
            w_variables.error_301 = True  # used for row alert in __init__.py

        if context.scene.WireframeType == 'WIREFRAME_BI' and len(context.scene.CustomSceneName2) == 0:
            self.error_msg += '- No clay scene name!\n'
            self.success = False
            w_variables.error_302 = True  # used for row alert in __init__.py

        if self.success:
            w_variables.scene_name_1 = context.scene.CustomSceneName
            w_variables.scene_name_2 = context.scene.CustomSceneName2
            w_variables.original_scene = context.scene
            w_variables.other_layers_numbers = b_tools.layerlist_to_numberlist(w_tools.set_layers_other())
            w_variables.affected_layers_numbers = b_tools.layerlist_to_numberlist(w_tools.set_layers_affected())
            w_variables.all_layers_used_numbers = b_tools.layerlist_to_numberlist(w_tools.set_layers_used())

            if context.scene.WireframeType != 'WIREFRAME_FREESTYLE' and context.scene.CheckboxUseMatWire:
                w_variables.wire_mat_set = bpy.data.materials[context.scene.Materials.mat_wire]

            if context.scene.CheckboxUseMatClay:
                w_variables.clay_mat_set = bpy.data.materials[context.scene.Materials.mat_clay]

            if w_variables.original_scene.WireframeType == 'WIREFRAME_BI':
                self.create_wireframe_scene_bi()

            elif w_variables.original_scene.WireframeType == 'WIREFRAME_FREESTYLE':
                self.create_wireframe_scene_freestyle()

            elif w_variables.original_scene.WireframeType == 'WIREFRAME_MODIFIER':
                self.create_wireframe_scene_modifier()

            # TODO below not needed anymore?
            # setting material lists items to be what they were before, in backup scene and original scene
            # if context.scene.CheckboxBackup:
            #     try:
            #         context.scene.Materials.mat_wire = wvariables.wire_mat_set.name
            #         context.scene.Materials.mat_clay = wvariables.clay_mat_set.name
            #         wvariables.original_scene.Materials.mat_wire = wvariables.wire_mat_set.name
            #         wvariables.original_scene.Materials.mat_clay = wvariables.clay_mat_set.name
            #     except AttributeError:
            #         pass

            self.success = True

        return self.execute(context)

    @staticmethod
    def create_wireframe_scene_bi():
        """Creates the complete wireframe using the blender internal setup."""
        if not (w_variables.original_scene.CheckboxOnlyClay and w_variables.original_scene.CheckboxUseClay):
            # creates wires scene
            wire_scene = BlenderSceneW(w_variables.original_scene, w_variables.original_scene.CheckboxBackup,
                                       w_variables.scene_name_1, 'BLENDER_RENDER')
            wire_scene.set_as_active()
            original_pivotpoint = wire_scene.view3d_pivotpoint('get')
            wire_scene.view3d_pivotpoint('set', 'BOUNDING_BOX_CENTER')

            if w_variables.original_scene.CheckboxOnlySelected:
                w_variables.only_selected = wire_scene.selected_objects_to_list(['MESH'])
            # TODO make sure it runs...
            # TODO clean 'select' function calls?
            # TODO remove 'set_as_active' calls?
            wire_scene.clean_objects()
            wire_scene.clear_all_materials()
            wire_scene.set_up_rlayer('wireframe', [0, 1], [0], [1])

            wire_scene.select('SELECT', ['MESH', 'CAMERA'], ['ELSE'], w_variables.affected_layers_numbers, ['ELSE'])
            wire_scene.move_selected_to_layer(0)

            wire_scene.select('SELECT', ['MESH'], ['ELSE'], w_variables.other_layers_numbers, ['ELSE'])
            wire_scene.move_selected_to_layer(1)

            wire_scene.select('SELECT', ['MESH'], ['ELSE'], [0], ['ELSE'])
            wire_scene.copy_selected_to_layer(1)
            """
            wire_scene.select('DESELECT', ['ALL'])

            wire_scene.select('SELECT', ['MESH'], ['ELSE'], [0])
            w_variables.wire_bi_mat = wire_scene.add_wireframe_bi_to_selected()

            wire_scene.select('DESELECT', ['ALL'])
            wire_scene.view3d_pivotpoint('set', original_pivotpoint)
            #TODO
            bpy.data.scenes[wire_scene.name].render.alpha_mode = 'TRANSPARENT'

            # creates clay scene
            clay_scene = BlenderSceneW(w_variables.original_scene, w_variables.original_scene.CheckboxBackup,
                                       w_variables.scene_name_2, 'CYCLES')
            clay_scene.set_up_rlayer('clay')
            clay_scene.comp_add_wireframe_bi(wire_scene)

        else:
            clay_scene = BlenderSceneW(w_variables.original_scene, w_variables.original_scene.CheckboxBackup,
                                       'clay', 'CYCLES')
            clay_scene.set_up_rlayer('clay')
        
        if w_variables.original_scene.CheckboxOnlySelected:
            w_variables.only_selected = clay_scene.selected_objects_to_list(['MESH'])

        if w_variables.original_scene.CheckboxUseClay:
            clay_scene.select('SELECT', ['MESH'], ['ELSE'])
            w_variables.clay_mat = clay_scene.add_clay_mat_to_selected()

        if w_variables.original_scene.CheckboxUseAO:
            clay_scene.set_up_world_ao()

        clay_scene.select('DESELECT', ['ALL'])
        """
    @staticmethod
    def create_wireframe_scene_freestyle():
        """Creates the complete wireframe using the freestyle setup."""
        if not (w_variables.original_scene.CheckboxOnlyClay and w_variables.original_scene.CheckboxUseClay):
            wire_scene = BlenderSceneW(w_variables.original_scene, w_variables.original_scene.CheckboxBackup,
                                       w_variables.scene_name_1, 'CYCLES')

        else:
            wire_scene = BlenderSceneW(w_variables.original_scene, w_variables.original_scene.CheckboxBackup,
                                       w_variables.scene_name_1, 'CYCLES')
        # TODO fix composite checkbox not active thing
        wire_scene.set_as_active()

        if w_variables.original_scene.CheckboxOnlySelected:
            w_variables.only_selected = wire_scene.selected_objects_to_list(['MESH'])

        if not (w_variables.original_scene.CheckboxOnlyClay and w_variables.original_scene.CheckboxUseClay):
            wire_scene.set_up_rlayer('wireframe', rlname_other='clay')

        else:
            wire_scene.set_up_rlayer('clay')

        if w_variables.original_scene.CheckboxUseClay:
            wire_scene.select('SELECT', ['MESH'], ['ELSE'])
            w_variables.clay_mat = wire_scene.add_clay_mat_to_selected()

        if not (w_variables.original_scene.CheckboxOnlyClay and w_variables.original_scene.CheckboxUseClay):
            w_variables.wire_freestyle = wire_scene.add_wireframe_freestyle()

        if w_variables.original_scene.CheckboxUseAO and not w_variables.original_scene.CheckboxComp:
            wire_scene.comp_add_ao()
            wire_scene.set_up_world_ao()

        elif w_variables.original_scene.CheckboxComp:
            wire_scene.comp_add_wireframe_freestyle()
            bpy.data.scenes[wire_scene.name].cycles.film_transparent = True

        wire_scene.select('DESELECT', ['ALL'])

    @staticmethod
    def create_wireframe_scene_modifier():
        """Creates the complete wireframe using the modifier setup."""
        if not (w_variables.original_scene.CheckboxOnlyClay and w_variables.original_scene.CheckboxUseClay):
            wire_scene = BlenderSceneW(w_variables.original_scene, w_variables.original_scene.CheckboxBackup,
                                       w_variables.scene_name_1, 'CYCLES')

        else:
            wire_scene = BlenderSceneW(w_variables.original_scene, w_variables.original_scene.CheckboxBackup,
                                       w_variables.scene_name_1, 'CYCLES')

        wire_scene.set_as_active()

        if w_variables.original_scene.CheckboxOnlySelected:
            w_variables.only_selected = wire_scene.selected_objects_to_list(['MESH'])

        if not (w_variables.original_scene.CheckboxOnlyClay and w_variables.original_scene.CheckboxUseClay):
            wire_scene.set_up_rlayer('wireframe')

        else:
            wire_scene.set_up_rlayer('clay')

        if w_variables.original_scene.CheckboxUseClay:
            wire_scene.select('SELECT', ['MESH'], ['ELSE'])
            w_variables.clay_mat = wire_scene.add_clay_mat_to_selected()

        if w_variables.original_scene.CheckboxUseAO:
            wire_scene.set_up_world_ao()
            wire_scene.comp_add_ao()

        if not (w_variables.original_scene.CheckboxOnlyClay and w_variables.original_scene.CheckboxUseClay):
            wire_scene.select('SELECT', ['MESH'], ['ELSE'])
            w_variables.wire_modifier_mat = wire_scene.add_wireframe_modifier()

        wire_scene.select('DESELECT', ['ALL'])


class SelectLayersAffectedOperator(bpy.types.Operator):
    """Select all layers"""
    bl_label = "Select all layers affected"
    bl_idname = 'wireframe_op.select_layers_affected'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.LayersAffected[i] = True

        return {'FINISHED'}


class SelectLayersOtherOperator(bpy.types.Operator):
    """Select all layers"""
    bl_label = "Select all other layers"
    bl_idname = 'wireframe_op.select_layers_other'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.LayersOther[i] = True

        return {'FINISHED'}


class DeselectLayersAffectedOperator(bpy.types.Operator):
    """Deselect all layers"""
    bl_label = "Deselect all layers affected"
    bl_idname = 'wireframe_op.deselect_layers_affected'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.LayersAffected[i] = False

        return {'FINISHED'}


class DeselectLayersOtherOperator(bpy.types.Operator):
    """Deselect all layers"""
    bl_label = "Deselect all other layers"
    bl_idname = 'wireframe_op.deselect_layers_other'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.LayersOther[i] = False

        return {'FINISHED'}
