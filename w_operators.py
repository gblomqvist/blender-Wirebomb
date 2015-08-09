# noinspection PyUnresolvedReferences
import bpy
from . import w_tools
from . import b_tools
from . import w_var
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
        # checks for any errors
        if context.scene.cb_only_selected and not b_tools.check_any_selected(context.scene, 'MESH'):
            self.error_msg += "- Checkbox 'Only Selected' is activated but no mesh is selected!\n"
            self.success = False
            w_var.error_101 = True  # used for row alert in __init__.py

        if (not context.scene.cb_only_selected and
                not any(list(context.scene.layers_affected)) and not any(list(context.scene.layers_other))):
            self.error_msg += "- No affected layers selected!\n"
            self.success = False

        if (context.scene.wireframe_type != 'WIREFRAME_FREESTYLE' and context.scene.cb_mat_wire
                and context.scene.materials.wire == ''):
            self.error_msg += '- No wire material selected!\n'
            self.success = False
            w_var.error_201 = True  # used for row alert in __init__.py

        if context.scene.cb_clay and context.scene.cb_mat_clay and context.scene.materials.clay == '':
            self.error_msg += '- No clay material selected!\n'
            self.success = False
            w_var.error_202 = True  # used for row alert in __init__.py

        if len(context.scene.field_scene_name) == 0:
            self.error_msg += '- No wire scene name!\n'
            self.success = False
            w_var.error_301 = True  # used for row alert in __init__.py

        if context.scene.wireframe_type == 'WIREFRAME_BI' and len(context.scene.field_scene_name2) == 0:
            self.error_msg += '- No clay scene name!\n'
            self.success = False
            w_var.error_302 = True  # used for row alert in __init__.py

        # if no error:
        if self.success:
            # original scene
            w_var.original_scene = context.scene

            # from interface:
            # wireframe type
            w_var.wireframe_type = context.scene.wireframe_type

            # checkboxes
            w_var.cb_backup = context.scene.cb_backup
            w_var.cb_clear_rlayers = context.scene.cb_clear_rlayers
            w_var.cb_only_selected = context.scene.cb_only_selected
            w_var.cb_ao = context.scene.cb_ao
            w_var.cb_clay = context.scene.cb_clay
            w_var.cb_clay_only = w_var.cb_clay_only_active and context.scene.cb_clay_only
            w_var.cb_comp = w_var.cb_comp_active and context.scene.cb_comp
            w_var.cb_mat_wire = w_var.cb_mat_wire_active and context.scene.cb_mat_wire
            w_var.cb_mat_clay = w_var.cb_mat_clay_active and context.scene.cb_mat_clay

            # materials set
            w_var.mat_wire_set = bpy.data.materials[context.scene.materials.wire]
            w_var.mat_clay_set = bpy.data.materials[context.scene.materials.clay]

            # layers selected
            w_var.layer_numbers_affected = b_tools.layerlist_to_numberlist(w_tools.set_layers_affected())
            w_var.layer_numbers_other = b_tools.layerlist_to_numberlist(w_tools.set_layers_other())
            w_var.layer_numbers_all_used = w_var.layer_numbers_affected + w_var.layer_numbers_other

            # scene names set
            w_var.scene_name_1 = context.scene.field_scene_name
            w_var.scene_name_2 = context.scene.field_scene_name2

            if w_var.cb_only_selected:
                w_var.only_selected = BlenderSceneW.selected_objects_to_list(context.scene, 'MESH')

            # runs wireframing
            if w_var.original_scene.wireframe_type == 'WIREFRAME_BI':
                self.create_wireframe_scene_bi()

            elif w_var.original_scene.wireframe_type == 'WIREFRAME_FREESTYLE':
                self.create_wireframe_scene_freestyle()

            elif w_var.original_scene.wireframe_type == 'WIREFRAME_MODIFIER':
                self.create_wireframe_scene_modifier()
            # TODO: Better comment?
            # setting material lists items to be what they were before, in backup scene and wireframe scene(s) as long
            # as the items were not empty strings
            if len(w_var.mat_wire_set.name) > 0:
                bpy.data.scenes[w_var.scene_name_1].materials.wire = w_var.mat_wire_set.name

                if w_var.wireframe_type == 'WIREFRAME_BI':
                    bpy.data.scenes[w_var.scene_name_2].materials.wire = w_var.mat_wire_set.name

                if w_var.cb_backup:
                    w_var.original_scene.materials.wire = w_var.mat_wire_set.name

            if len(w_var.mat_clay_set.name) > 0:
                bpy.data.scenes[w_var.scene_name_1].materials.clay = w_var.mat_clay_set.name

                if w_var.wireframe_type == 'WIREFRAME_BI':
                    bpy.data.scenes[w_var.scene_name_2].materials.clay = w_var.mat_clay_set.name

                if w_var.cb_backup:
                    w_var.original_scene.materials.clay = w_var.mat_clay_set.name

        return self.execute(context)

    @staticmethod
    def create_wireframe_scene_bi():
        """Creates the complete wireframe using the blender internal setup."""
        if not w_var.cb_clay_only:
            # creates wireframe scene
            wire_scene = BlenderSceneW(w_var.original_scene, True, w_var.scene_name_1, 'BLENDER_RENDER')
            # changes 3D view pivotpoint
            original_pivotpoint = wire_scene.view3d_pivotpoint('get')
            wire_scene.view3d_pivotpoint('set', 'BOUNDING_BOX_CENTER')
            # deletes unnecessary objects and removes all materials from the objects left
            wire_scene.clean_objects()
            wire_scene.clear_all_materials()
            # sets up renderlayer
            wire_scene.set_up_rlayer('wireframe', [0, 1], [0], [1])
            # TODO: Continue commenting.
            wire_scene.select('SELECT', layers=w_var.layer_numbers_affected, layers_excluded={'ELSE'})
            wire_scene.move_selected_to_layer(0)

            wire_scene.select('SELECT', layers=w_var.layer_numbers_other, layers_excluded={'ELSE'})
            wire_scene.move_selected_to_layer(1)
            # copy first to skip materials on copies
            wire_scene.select('SELECT', {'MESH'}, {'ELSE'}, {0}, {'ELSE'})
            wire_scene.copy_selected_to_layer(1)

            wire_scene.select('SELECT', {'MESH'}, {'ELSE'}, {0}, {'ELSE'})
            w_var.wire_bi_mat = wire_scene.add_wireframe_bi_to_selected()

            wire_scene.select('DESELECT', {'ALL'}, layers={'ALL'})
            wire_scene.view3d_pivotpoint('set', original_pivotpoint)
            bpy.data.scenes[wire_scene.name].render.alpha_mode = 'TRANSPARENT'

            # creates clay scene
            clay_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_2, 'CYCLES')
            clay_scene.set_up_rlayer('clay')
            clay_scene.comp_add_wireframe_bi(wire_scene)

        else:
            clay_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, 'clay', 'CYCLES')
            clay_scene.set_up_rlayer('clay')

        if w_var.cb_clay:
            clay_scene.select('SELECT', {'MESH'}, {'ELSE'})
            w_var.clay_mat = clay_scene.add_clay_mat_to_selected()

        if w_var.cb_ao:
            clay_scene.set_up_world_ao()

        clay_scene.select('DESELECT', {'ALL'}, layers={'ALL'})

    @staticmethod
    def create_wireframe_scene_freestyle():
        """Creates the complete wireframe using the freestyle setup."""
        wire_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_1, 'CYCLES')
        # TODO: Need to deselect all objects before starting, either here and all other methods, or in invoke method?
        if not w_var.cb_clay_only:
            wire_scene.set_up_rlayer('wireframe', rlname_other='other')
            w_var.wire_freestyle_linestyle = wire_scene.add_wireframe_freestyle()

        else:
            wire_scene.set_up_rlayer('clay')

        if w_var.cb_clay:
            wire_scene.select('SELECT', {'MESH'}, {'ELSE'})
            w_var.clay_mat = wire_scene.add_clay_mat_to_selected()

        # TODO: Is this part correct?
        if w_var.cb_ao and not w_var.cb_comp:
            wire_scene.comp_add_ao()
            wire_scene.set_up_world_ao()
        # TODO: Deactivate AO checkbox when comp checkbox is True
        elif w_var.cb_comp:
            wire_scene.comp_add_wireframe_freestyle()
            bpy.data.scenes[wire_scene.name].cycles.film_transparent = True

        wire_scene.select('DESELECT', {'ALL'}, layers={'ALL'})

    @staticmethod
    def create_wireframe_scene_modifier():
        """Creates the complete wireframe using the modifier setup."""
        # TODO(15-08-07): I suspect a bug.
        wire_scene = BlenderSceneW(w_var.original_scene, w_var.cb_backup, w_var.scene_name_1, 'CYCLES')

        if not w_var.cb_clay_only:
            wire_scene.set_up_rlayer('wireframe')
            wire_scene.select('SELECT', {'MESH'}, {'ELSE'})
            w_var.wire_modifier_mat = wire_scene.add_wireframe_modifier()

        else:
            wire_scene.set_up_rlayer('clay')

        if w_var.cb_clay:
            wire_scene.select('SELECT', {'MESH'}, {'ELSE'})
            w_var.clay_mat = wire_scene.add_clay_mat_to_selected()

        if w_var.cb_ao:
            wire_scene.set_up_world_ao()
            wire_scene.comp_add_ao()

        wire_scene.select('DESELECT', {'ALL'}, layers={'ALL'})


class SelectLayersAffectedOperator(bpy.types.Operator):
    """Select all layers"""
    bl_label = "Select all layers affected"
    bl_idname = 'wireframe_op.select_layers_affected'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.layers_affected[i] = True

        return {'FINISHED'}


class SelectLayersOtherOperator(bpy.types.Operator):
    """Select all layers"""
    bl_label = "Select all other layers"
    bl_idname = 'wireframe_op.select_layers_other'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.layers_other[i] = True

        return {'FINISHED'}


class DeselectLayersAffectedOperator(bpy.types.Operator):
    """Deselect all layers"""
    bl_label = "Deselect all layers affected"
    bl_idname = 'wireframe_op.deselect_layers_affected'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.layers_affected[i] = False

        return {'FINISHED'}


class DeselectLayersOtherOperator(bpy.types.Operator):
    """Deselect all layers"""
    bl_label = "Deselect all other layers"
    bl_idname = 'wireframe_op.deselect_layers_other'

    def invoke(self, context, event):
        for i in range(0, 20):
            bpy.context.scene.layers_other[i] = False

        return {'FINISHED'}
