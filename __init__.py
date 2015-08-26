# <pep8-80 compliant>

bl_info = {
    "name": "Cycles Wireframe and Clay",
    "author": "Gustaf Blomqvist",
    "version": (1, 0, 0),
    "blender": (2, 75, 0),
    "location": "Render settings --> Set up Wireframe and Clay",
    "description": "Setting up wireframe and clay renders has never been easier!",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render"
}

if 'bpy' in locals():
    import importlib

    if 'w_b_scene' in locals():
        importlib.reload(w_b_scene)

    if 'w_tools' in locals():
        importlib.reload(w_tools)

    if 'b_tools' in locals():
        importlib.reload(b_tools)

    if 'w_operators' in locals():
        importlib.reload(w_operators)

    if 'w_var' in locals():
        importlib.reload(w_var)

    if 'constants' in locals():
        importlib.reload(constants)


# noinspection PyUnresolvedReferences
import bpy
from .w_b_scene import BlenderSceneW
from . import w_tools
from . import b_tools
from . import w_operators
from . import w_var
from . import constants


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.materials = bpy.props.PointerProperty(type=MaterialLists)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.materials


if __name__ == '__main__':
    register()


def scene_materials(scene, context):
    """Fetching scene materials."""
    mat_list = []
    mat_id = 0

    for mat in bpy.data.materials:
        # sequence of enum items formatted: [(identifier, name, description, icon, number), ...]
        mat_list.append((mat.name, mat.name, '', 'MATERIAL', mat_id))
        mat_id += 1

    return mat_list


class MaterialLists(bpy.types.PropertyGroup):
    """Setting up material lists."""
    clay = bpy.props.EnumProperty(items=scene_materials,
                                  name='Material',
                                  description='Use as clay material')
    wire = bpy.props.EnumProperty(items=scene_materials,
                                  name='Material',
                                  description='Use as wireframe material')


def update_color_wire(self, context):
    """Updates the wireframe material's color."""

    if context.scene.wireframe_method == 'WIREFRAME_FREESTYLE':
        if hasattr(w_var.wire_freestyle_linestyle, 'color'):
            w_var.wire_freestyle_linestyle.color = context.scene.color_wire[0:3]
            w_var.wire_freestyle_linestyle.alpha = context.scene.color_wire[-1]

    elif context.scene.wireframe_method == 'WIREFRAME_MODIFIER':
        if hasattr(w_var.wire_modifier_mat, 'node_tree'):
            node = w_var.wire_modifier_mat.node_tree.nodes[w_var.node_wireframe_diffuse]
            node.inputs[0].default_value = context.scene.color_wire

            # updating viewport color
            w_var.wire_modifier_mat.diffuse_color = context.scene.color_wire[0:3]

    elif context.scene.wireframe_method == 'WIREFRAME_BI':
        if hasattr(w_var.wire_bi_mat, 'diffuse_color'):
            w_var.wire_bi_mat.diffuse_color = context.scene.color_wire[0:3]
            w_var.wire_bi_mat.alpha = context.scene.color_wire[-1]


def update_color_clay(self, context):
    """Updates the clay material's color."""
    if hasattr(w_var.clay_mat, 'node_tree'):
        node = w_var.clay_mat.node_tree.nodes[w_var.node_clay_diffuse]
        node.inputs[0].default_value = context.scene.color_clay

        # updating viewport color
        w_var.clay_mat.diffuse_color = context.scene.color_clay[0:3]


def update_wire_thickness(self, context):
    """Updates the wireframe's thickness."""
    if context.scene.wireframe_method == 'WIREFRAME_FREESTYLE':
        w_var.wire_freestyle_linestyle.thickness = context.scene.slider_wt_freestyle

    elif context.scene.wireframe_method == 'WIREFRAME_MODIFIER':
        for obj in context.scene.objects:
            if obj in w_var.objects_affected and obj.type == 'MESH':
                if w_var.modifier_wireframe in obj.modifiers:
                    obj.modifiers[w_var.modifier_wireframe].thickness = context.scene.slider_wt_modifier

# creates drop-down list with different wireframe methods
bpy.types.Scene.wireframe_method = bpy.props.EnumProperty(
    items=[('WIREFRAME_MODIFIER', 'Modifier', 'Create wireframe using cycles and the wireframe modifier'),
           ('WIREFRAME_FREESTYLE', 'Freestyle', 'Create wireframe using cycles freestyle renderer'),
           ('WIREFRAME_BI', 'Blender Internal', 'Create wireframe using blender\'s internal renderer')],
    name='Method',
    description='Wireframe method',
    default='WIREFRAME_FREESTYLE')

# creates all checkboxes
bpy.types.Scene.cb_backup = bpy.props.BoolProperty(default=True, description="Create a backup scene")
bpy.types.Scene.cb_clear_rlayers = bpy.props.BoolProperty(default=True, description="Remove all previous render layers")
bpy.types.Scene.cb_clear_materials = bpy.props.BoolProperty(default=True,
                                                            description="Remove all previous materials from objects")
bpy.types.Scene.cb_composited = bpy.props.BoolProperty(default=False,
                                                       description="Add the wireframe through composition "
                                                                   "(only available when there is a posibility "
                                                                   "that it is needed)")
bpy.types.Scene.cb_only_selected = bpy.props.BoolProperty(default=False, description="Only affect the selected meshes")
bpy.types.Scene.cb_ao = bpy.props.BoolProperty(default=False, description="Use ambient occlusion lighting setup")
bpy.types.Scene.cb_clay = bpy.props.BoolProperty(default=True, description="Activate the use of clay")
bpy.types.Scene.cb_clay_only = bpy.props.BoolProperty(default=False, description="Only use clay, "
                                                                                 "don't set up wireframe")
bpy.types.Scene.cb_mat_wire = bpy.props.BoolProperty(default=False,
                                                     description="Use material from scene as wireframe material")
bpy.types.Scene.cb_mat_clay = bpy.props.BoolProperty(default=False,
                                                     description="Use material from scene as clay material")

# creates two color pickers
bpy.types.Scene.color_wire = bpy.props.FloatVectorProperty(subtype='COLOR',
                                                           min=0,
                                                           max=1,
                                                           size=4,
                                                           default=(0.051, 0.743, 0.000, 0.500),
                                                           update=update_color_wire,
                                                           description="Wireframe color (changes real-time)")
bpy.types.Scene.color_clay = bpy.props.FloatVectorProperty(subtype='COLOR',
                                                           min=0, max=1,
                                                           size=4,
                                                           default=(0.030, 0.143, 0.000, 1.000),
                                                           update=update_color_clay,
                                                           description="Clay color (changes real-time)")

# creates two layer tables
bpy.types.Scene.layers_affected = bpy.props.BoolVectorProperty(subtype='LAYER',
                                                               size=20,
                                                               default=(True,) + (False,) * 19,
                                                               description="Layers whose meshes will be affected")
bpy.types.Scene.layers_other = bpy.props.BoolVectorProperty(subtype='LAYER',
                                                            size=20,
                                                            default=(False,) * 20,
                                                            description="Layers whose objects will be "
                                                                        "included as is, e.g. lights")

# creates sliders for the wireframe thickness
bpy.types.Scene.slider_wt_freestyle = bpy.props.FloatProperty(name='Wire Thickness',
                                                              subtype='FACTOR',
                                                              precision=3,
                                                              soft_min=0.1,
                                                              soft_max=10,
                                                              default=1.5,
                                                              update=update_wire_thickness,
                                                              description="Wireframe thickness "
                                                                          "(changes real-time)")
bpy.types.Scene.slider_wt_modifier = bpy.props.FloatProperty(name='Wire Thickness',
                                                             subtype='FACTOR',
                                                             precision=4,
                                                             soft_min=0.001,
                                                             soft_max=0.1,
                                                             default=0.004,
                                                             update=update_wire_thickness,
                                                             description="Wireframe thickness "
                                                                         "(changes real-time)")

# creates scene naming text fields
bpy.types.Scene.scene_name_1 = bpy.props.StringProperty(description="The wireframe/clay scene's name",
                                                        default='wireframe',
                                                        maxlen=47)
bpy.types.Scene.scene_name_2 = bpy.props.StringProperty(description="The clay/other scene's name "
                                                                    "(depending on if you use clay or not)",
                                                        default='clay',
                                                        maxlen=47)


class WireframePanel(bpy.types.Panel):
    """The panel in the GUI."""

    bl_label = 'Set Up Wireframe and Clay'
    bl_idname = 'RENDER_PT_wireframe'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='', icon='WIRE')

    # draws the GUI
    def draw(self, context):
        scene = BlenderSceneW(context.scene, False)
        layout = self.layout

        # config file
        row = layout.row(align=True)
        row.label("Config file:")
        row.operator(operator='scene.wireframe_and_clay_config_save', text='Save', icon='SAVE_PREFS')
        row.operator(operator='scene.wireframe_and_clay_config_load', text='Load', icon='FILESEL')

        # box line
        layout.box()

        # method
        layout.separator()
        layout.prop(context.scene, property='wireframe_method')

        # box start
        layout.separator()
        box = layout.box()

        # backup scene
        split = box.split()
        col = split.column()
        row = col.row()
        row.prop(context.scene, property='cb_backup', text='Backup scene')

        # clear render layers
        row = col.row()
        row.prop(context.scene, property='cb_clear_rlayers', text='Clear render layers')

        # clear materials
        row = col.row()
        row.prop(context.scene, property='cb_clear_materials', text='Clear materials')

        # composited wires
        row = col.row()

        if scene.get_original_scene().wireframe_method == 'WIREFRAME_FREESTYLE':
            layers_affected = list(scene.get_original_scene().layers_affected)
            layers_other = list(scene.get_original_scene().layers_other)

            if not scene.get_original_scene().cb_only_selected:
                if not (any(layers_affected)
                        and any(b_tools.manipulate_layerlists('subtract', layers_other, layers_affected))):
                    row.active = False
                    w_var.cb_composited_active = False

                else:
                    w_var.cb_composited_active = True

            row.prop(context.scene, property='cb_composited', text='Composited wires')

        # only selected
        col = split.column()
        row = col.row()

        if w_var.error_101 and scene.get_original_scene().cb_only_selected and not scene.check_any_selected():
            row.alert = True

        else:
            w_var.error_101 = False

        row.prop(context.scene, property='cb_only_selected', text='Only selected')

        # ao as light
        row = col.row()
        row.prop(context.scene, property='cb_ao', text='AO as light')

        # use clay
        row = col.row()
        row.prop(context.scene, property='cb_clay', text='Use clay')

        # only clay
        row = col.row()
        row.separator()

        if scene.get_original_scene().cb_clay is not True:
            row.active = False
            w_var.cb_clay_only_active = False

        else:
            w_var.cb_clay_only_active = True

        row.prop(context.scene, property='cb_clay_only', text='Only clay')
        # box end

        # wire color
        layout.separator()
        row = layout.row()

        if ((scene.get_original_scene().cb_mat_wire
                and scene.get_original_scene().wireframe_method != 'WIREFRAME_FREESTYLE')
                or (scene.get_original_scene().cb_clay_only and w_var.cb_clay_only_active)):
            row.active = False

        row.prop(context.scene, property='color_wire', text='Wire color')

        if scene.get_original_scene().wireframe_method != 'WIREFRAME_FREESTYLE':

            # use material (wire)
            split = layout.split()
            col = split.column()
            row = col.row()

            if (scene.get_original_scene().wireframe_method == 'WIREFRAME_FREESTYLE' or
                    (scene.get_original_scene().cb_clay_only and w_var.cb_clay_only_active)):
                row.active = False
                w_var.cb_mat_wire_active = False

            else:
                w_var.cb_mat_wire_active = True

            if w_var.error_201 and scene.get_original_scene().cb_mat_wire:
                row.alert = True

            else:
                w_var.error_201 = False

            row.prop(context.scene, property='cb_mat_wire', text='Use material:')

            # wire material
            col = split.column()
            row = col.row()

            if (not scene.get_original_scene().cb_mat_wire or
                    (scene.get_original_scene().cb_clay_only and scene.get_original_scene().cb_clay)):
                row.active = False

            row.prop(scene.get_original_scene().materials, property='wire', text='')

        # clay color
        layout.separator()
        row = layout.row()

        if scene.get_original_scene().cb_mat_clay or not scene.get_original_scene().cb_clay:
            row.active = False

        row.prop(context.scene, property='color_clay', text='Clay color')

        # use material (clay)
        split = layout.split()
        col = split.column()
        row = col.row()

        if not scene.get_original_scene().cb_clay:
            row.active = False
            w_var.cb_mat_clay_active = False

        else:
            w_var.cb_mat_clay_active = True

        if w_var.error_202 and scene.get_original_scene().cb_mat_clay:
            row.alert = True

        else:
            w_var.error_202 = False

        row.prop(context.scene, property='cb_mat_clay', text='Use material:')

        # clay material
        col = split.column()
        row = col.row()

        if not (scene.get_original_scene().cb_mat_clay and w_var.cb_mat_clay_active):
            row.active = False

        row.prop(scene.get_original_scene().materials, property='clay', text='')

        # wire thickness
        if scene.get_original_scene().wireframe_method != 'WIREFRAME_BI':
            layout.separator()
            row = layout.row()
            row.label('Wire thickness:')

            if scene.get_original_scene().wireframe_method == 'WIREFRAME_BI':
                row.active = False

            if scene.get_original_scene().wireframe_method in 'WIREFRAME_FREESTYLE':
                row.prop(context.scene, property='slider_wt_freestyle', text='Thickness')

            elif scene.get_original_scene().wireframe_method == 'WIREFRAME_MODIFIER':
                row.prop(context.scene, property='slider_wt_modifier', text='Thickness')

        # 'affected layers' buttons
        layout.separator()
        split = layout.split()
        col = split.column()
        col.label(text='Affected layers:')
        row = col.row(align=True)

        if scene.get_original_scene().cb_only_selected:
            col.active = False
            row.active = False

        row.operator(operator='scene.wireframe_and_clay_select_layers_affected', text='All')
        row.operator(operator='scene.wireframe_and_clay_deselect_layers_affected', text='None')
        col.prop(context.scene, property='layers_affected', text='')

        # 'other layers' buttons
        col = split.column()
        col.label(text='Other included layers:')
        row = col.row(align=True)
        row.operator(operator='scene.wireframe_and_clay_select_layers_other', text='All')
        row.operator(operator='scene.wireframe_and_clay_deselect_layers_other', text='None')
        col.prop(context.scene, property='layers_other', text='')

        # scene name 1
        layout.separator()
        row = layout.row()

        if w_var.error_301 and len(scene.get_original_scene().scene_name_1) == 0:
            row.alert = True

        else:
            w_var.error_301 = False

        if (scene.get_original_scene().cb_clay_only and w_var.cb_clay_only_active
                and scene.get_original_scene().wireframe_method != 'WIREFRAME_BI'):
            row.prop(context.scene, property='scene_name_1', text='Clay scene name')

        else:
            row.prop(context.scene, property='scene_name_1', text='Wire scene name')

            if scene.get_original_scene().cb_clay_only and w_var.cb_clay_only_active:
                row.active = False

        # scene name 2
        if scene.get_original_scene().wireframe_method == 'WIREFRAME_BI':
            row = layout.row()

            if w_var.error_302 and len(scene.get_original_scene().scene_name_2) == 0:
                row.alert = True

            else:
                w_var.error_302 = False

            if scene.get_original_scene().cb_clay:
                row.prop(context.scene, property='scene_name_2', text='Clay scene name')
            else:
                row.prop(context.scene, property='scene_name_2', text='Other scene name')

        # 'set up new' and 'quick remove' buttons
        layout.separator()
        col = layout.column(align=True)
        col.scale_y = 1.2
        col.operator(operator='scene.wireframe_and_clay_set_up_new', text='Set up new', icon='WIRE')
        col.operator(operator='scene.wireframe_and_clay_quick_remove', text='Quick remove', icon='X')
