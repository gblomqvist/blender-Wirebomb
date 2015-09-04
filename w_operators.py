# <pep8-80 compliant>

import bpy
import time
from . import w_tools
from . import w_var


class WireframeOperator(bpy.types.Operator):
    """Set up wireframe/clay render"""
    bl_label = "Wireframe"
    bl_idname = 'scene.wireframe_and_clay_set_up_new'

    def __init__(self):
        self.start = time.time()
        self.success = False
        self.error_msg = ""

    def execute(self, context):
        if self.success:

            # initiates progress bar and updates it to 1 %
            context.window_manager.progress_begin(0, 100)
            context.window_manager.progress_update(1)

            # runs wireframing
            if w_var.wireframe_method == 'WIREFRAME_BI':
                w_tools.set_up_wireframe_bi()

            elif w_var.wireframe_method == 'WIREFRAME_FREESTYLE':
                w_tools.set_up_wireframe_freestyle()

            elif w_var.wireframe_method == 'WIREFRAME_MODIFIER':
                w_tools.set_up_wireframe_modifier()

            w_tools.update_material_lists()

            # terminates the progress bar
            context.window_manager.progress_end()

            self.report({'INFO'}, "Setup done in {} seconds!".format(round(time.time() - self.start, 2)))

        elif not self.success:
            self.report({'ERROR'}, self.error_msg)

        return {'FINISHED'}

    def invoke(self, context, event):

        # saves information from UI and resets variables
        w_tools.set_variables(context)

        # checks for any errors
        self.success, self.error_msg = w_tools.error_check(context)

        return self.execute(context)


class QuickRemoveOperator(bpy.types.Operator):
    """Removes all scenes created via this add-on during this blender session"""
    bl_label = "Quick remove"
    bl_idname = 'scene.wireframe_and_clay_quick_remove'

    def __init__(self):
        self.start = time.time()

    def execute(self, context):

        # iterates over copy because original is being changed
        for scene in list(w_var.created_scenes):
            if scene.name in bpy.data.scenes:
                bpy.data.scenes.remove(scene)
                w_var.created_scenes.remove(scene)

        self.report({'INFO'}, "Remove done in {} seconds!".format(round(time.time() - self.start, 2)))
        return {'FINISHED'}


class ConfigSaveOperator(bpy.types.Operator):
    """Saves a config INI file"""
    bl_label = "Save INI file"
    bl_idname = 'scene.wireframe_and_clay_config_save'

    filepath = bpy.props.StringProperty()
    filename = bpy.props.StringProperty()

    def execute(self, context):
        if self.filename.lower().endswith('.ini'):
            w_tools.config_save(context, self.filepath)
            self.report({'INFO'}, "{} saved successfully!".format(self.filename))

        else:
            self.report({'ERROR'}, "File extension must be INI !")

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ConfigLoadOperator(bpy.types.Operator):
    """Loads a config INI file"""
    bl_label = "Load INI file"
    bl_idname = 'scene.wireframe_and_clay_config_load'

    filepath = bpy.props.StringProperty()
    filename = bpy.props.StringProperty()

    def execute(self, context):
        if self.filename.lower().endswith('.ini'):
            try:
                w_tools.config_load(context, self.filepath)
                self.report({'INFO'}, "{} loaded successfully!".format(self.filename))

            except KeyError as e:
                self.report({'ERROR'}, "Key missing in file: {}.".format(e))

        else:
            self.report({'ERROR'}, "File extension must be INI !")

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SelectLayersAffectedOperator(bpy.types.Operator):
    """Selects all layers"""
    bl_label = "Select all layers affected"
    bl_idname = 'scene.wireframe_and_clay_select_layers_affected'

    def execute(self, context):
        for i in range(0, 20):
            bpy.context.scene.layers_affected[i] = True

        return {'FINISHED'}


class SelectLayersOtherOperator(bpy.types.Operator):
    """Selects all layers"""
    bl_label = "Select all other layers"
    bl_idname = 'scene.wireframe_and_clay_select_layers_other'

    def execute(self, context):
        for i in range(0, 20):
            bpy.context.scene.layers_other[i] = True

        return {'FINISHED'}


class DeselectLayersAffectedOperator(bpy.types.Operator):
    """Deselects all layers"""
    bl_label = "Deselect all layers affected"
    bl_idname = 'scene.wireframe_and_clay_deselect_layers_affected'

    def execute(self, context):
        for i in range(0, 20):
            bpy.context.scene.layers_affected[i] = False

        return {'FINISHED'}


class DeselectLayersOtherOperator(bpy.types.Operator):
    """Deselects all layers"""
    bl_label = "Deselect all other layers"
    bl_idname = 'scene.wireframe_and_clay_deselect_layers_other'

    def execute(self, context):
        for i in range(0, 20):
            bpy.context.scene.layers_other[i] = False

        return {'FINISHED'}
