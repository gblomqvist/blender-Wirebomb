# noinspection PyUnresolvedReferences
import bpy
from . import w_tools
from . import w_var


class WireframeOperator(bpy.types.Operator):
    """Set up wireframe/clay render"""
    bl_label = "Wireframe"
    bl_idname = 'wireframe_op.set_up'

    def execute(self, context):
        if self.success:

            # runs wireframing
            if w_var.wireframe_type == 'WIREFRAME_BI':
                w_tools.create_wireframe_bi()

            elif w_var.wireframe_type == 'WIREFRAME_FREESTYLE':
                w_tools.create_wireframe_freestyle()

            elif w_var.wireframe_type == 'WIREFRAME_MODIFIER':
                w_tools.create_wireframe_modifier()

            # setting material lists items to be what they were before in backup scene and wireframe scene(s),
            # as long as the items were not empty strings
            w_tools.update_material_lists()

            self.report({'INFO'}, 'There you go!')

        elif not self.success:
            self.report({'ERROR'}, self.error_msg)

        return {'FINISHED'}

    def invoke(self, context, event):

        # saves information from user's interface
        w_tools.set_variables(context)

        # checks for any errors
        self.success, self.error_msg = w_tools.error_check(context)

        return self.execute(context)


class AddToCurrentOperator(bpy.types.Operator):
    """Adds the object(s) to the current wireframe/clay render setup"""
    bl_label = "Add to current"
    bl_idname = 'wireframe_op.add_to_current'

    def execute(self, context):
        if self.success:

            # adds to current wireframe
            if w_var.wireframe_type == 'WIREFRAME_BI':
                w_tools.add_to_wireframe_bi()

            elif w_var.wireframe_type == 'WIREFRAME_FREESTYLE':
                w_tools.add_to_wireframe_freestyle()

            elif w_var.wireframe_type == 'WIREFRAME_MODIFIER':
                w_tools.add_to_wireframe_modifier()

            self.report({'INFO'}, 'There you go!')

        elif not self.success:
            self.report({'ERROR'}, self.error_msg)

        return {'FINISHED'}

    def invoke(self, context, event):

        # saves information from user's interface
        w_tools.set_variables(context)

        # checks for any errors
        self.success, self.error_msg = w_tools.error_check(context)

        return self.execute(context)


class QuickRemoveOperator(bpy.types.Operator):
    """Removes all scenes created via this add-on during this blender session"""
    bl_label = "Quick remove"
    bl_idname = 'wireframe_op.quick_remove'

    def invoke(self, context, event):  # TODO: Do this in execute instead?

        for scene in w_var.created_scenes:
            if scene.name in bpy.data.scenes:
                bpy.data.scenes.remove(scene)

        return {'FINISHED'}


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
