# TODO check this info
bl_info = {
    "name": "CyclesWireframing",
    "author": "Gustaf Blomqvist",
    "version": (1, 0, 0),
    "blender": (2, 73, 0),
    "location": "Scene settings --> Wireframing",
    "description": "Setting up wireframe/clay renders has never been easier!",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

if 'bpy' in locals():
    import importlib

    if 'wtools' in locals():
        importlib.reload(w_tools)

    if 'btools' in locals():
        importlib.reload(b_tools)

    if 'woperators' in locals():
        importlib.reload(w_operators)

    if 'wvariables' in locals():
        importlib.reload(w_var)

    if 'bscene_w' in locals():
        importlib.reload(w_b_scene)


# noinspection PyUnresolvedReferences
import bpy
from . import w_tools
from . import b_tools
from . import w_operators
from . import w_var
from .w_b_scene import BlenderSceneW


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.materials = bpy.props.PointerProperty(type=MaterialLists)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.materials

if __name__ == '__main__':
    register()


def scene_materials(scene, context):
    mat_list = []
    mat_id = 0

    for mat in bpy.data.materials:

        # sequence of enum items formatted: [(identifier, name, description, icon, number), ...]
        mat_list.append((mat.name, mat.name, 'aa', 'MATERIAL', mat_id))
        mat_id += 1  # TODO: Why do I need id? What can id do for me? ask blenderartists.org

    return mat_list


class MaterialLists(bpy.types.PropertyGroup):
    clay = bpy.props.EnumProperty(items=scene_materials,
                                  name='Clay material')
    wire = bpy.props.EnumProperty(items=scene_materials,
                                  name='Wire material')


def update_color_wire(self, context):
    """Updates the real wireframe material's color."""
    try:
        if context.scene.wireframe_type == 'WIREFRAME_FREESTYLE':
            w_var.wire_freestyle_linestyle.color = context.scene.color_wire[0:3]
            w_var.wire_freestyle_linestyle.alpha = context.scene.color_wire[-1]

        elif context.scene.wireframe_type == 'WIREFRAME_MODIFIER':
            for node in w_var.wire_modifier_mat.node_tree.nodes:
                # TODO: Set name instead here.
                if node.type == 'BSDF_DIFFUSE':
                    node.inputs[0].default_value = context.scene.color_wire

            # updating viewport color
            w_var.wire_modifier_mat.diffuse_color = context.scene.color_wire[0:3]

        elif context.scene.wireframe_type == 'WIREFRAME_BI':
            w_var.wire_bi_mat.diffuse_color = context.scene.color_wire[0:3]
            w_var.wire_bi_mat.alpha = context.scene.color_wire[-1]

    except AttributeError:
        pass


def update_color_clay(self, context):
    """Updates the real clay material's color."""
    try:
        for node in w_var.clay_mat.node_tree.nodes:
            # TODO: Set name instead here.
            if node.type == 'BSDF_DIFFUSE':
                node.inputs[0].default_value = context.scene.color_clay

        # updating viewport color
        w_var.clay_mat.diffuse_color = context.scene.color_clay[0:3]

    except AttributeError:
        pass


def update_wire_thickness(self, context):
    """Updates the real wireframe's thickness."""
    if context.scene.wireframe_type == 'WIREFRAME_FREESTYLE':
        w_var.wire_freestyle_linestyle.thickness = context.scene.slider_wt_freestyle
    # TODO: Can I improve this maybe?
    elif context.scene.wireframe_type == 'WIREFRAME_MODIFIER':
        for obj in context.scene.objects:
            if ((context.scene.cb_only_selected and obj in w_var.only_selected)
                    or (not context.scene.cb_only_selected and
                        b_tools.object_on_layer(context.scene, obj, w_var.layer_numbers_affected))):
                for modifier in obj.modifiers:
                    if modifier.type == 'WIREFRAME':
                        modifier.thickness = context.scene.slider_wt_modifier


def update_cb_comp(self, context):
    if context.scene.wireframe_type != 'WIREFRAME_FREESTYLE':
        context.scene.cb_comp = False

# creates drop-down list with different wireframe types
bpy.types.Scene.wireframe_type = bpy.props.EnumProperty(
    items=[('WIREFRAME_MODIFIER', 'Modifier', 'Create wireframe using cycles and the wireframe modifier'),
           ('WIREFRAME_FREESTYLE', 'Freestyle', 'Create wireframe using cycles freestyle renderer'),
           ('WIREFRAME_BI', 'Blender Internal', 'Create wireframe using blender\'s internal renderer')],
    name='Wireframe methods',
    default='WIREFRAME_FREESTYLE',
    update=update_cb_comp)

# creates two color pickers
bpy.types.Scene.color_wire = bpy.props.FloatVectorProperty(subtype='COLOR',
                                                           min=0,
                                                           max=1,
                                                           size=4,
                                                           default=(0, 1, 0.977, 0.8),
                                                           update=update_color_wire,
                                                           description="Wire color (changes real-time)")
bpy.types.Scene.color_clay = bpy.props.FloatVectorProperty(subtype='COLOR',
                                                           min=0, max=1,
                                                           size=4,
                                                           default=(0, 0.154, 0.255, 1),
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

# creates all checkboxes
bpy.types.Scene.cb_backup = bpy.props.BoolProperty(default=True, description="Create a backup scene")
bpy.types.Scene.cb_clear_rlayers = bpy.props.BoolProperty(default=True, description="Remove all previous render layers")
bpy.types.Scene.cb_clear_mats = bpy.props.BoolProperty(default=True,
                                                       description="Remove all previous materials from objects")
bpy.types.Scene.cb_comp = bpy.props.BoolProperty(default=False, description="Add the wireframe through composition")
bpy.types.Scene.cb_only_selected = bpy.props.BoolProperty(default=False, description="Only affect the selected meshes")
bpy.types.Scene.cb_ao = bpy.props.BoolProperty(default=False, description="Use ambient occlusion lighting setup")
bpy.types.Scene.cb_clay = bpy.props.BoolProperty(default=True, description="Activate the use of clay")
bpy.types.Scene.cb_clay_only = bpy.props.BoolProperty(default=False, description="Only use clay, no wireframe")
bpy.types.Scene.cb_mat_wire = bpy.props.BoolProperty(default=False,
                                                     description="Use material from scene as wire material")
bpy.types.Scene.cb_mat_clay = bpy.props.BoolProperty(default=False,
                                                     description="Use material from scene as clay material")

# creates sliders for the wireframe thickness
bpy.types.Scene.slider_wt_freestyle = bpy.props.FloatProperty(name='Wire Thickness',
                                                              subtype='FACTOR',
                                                              precision=3,
                                                              soft_min=0.1,
                                                              soft_max=10,
                                                              default=1.5,
                                                              update=update_wire_thickness,
                                                              description="Wire thickness "
                                                              "(changes real-time)")
bpy.types.Scene.slider_wt_modifier = bpy.props.FloatProperty(name='Wire Thickness',
                                                             subtype='FACTOR',
                                                             precision=4,
                                                             soft_min=0.001,
                                                             soft_max=0.1,
                                                             default=0.004,
                                                             update=update_wire_thickness,
                                                             description="Wire thickness "
                                                             "(changes real-time)")

# creates scene naming text fields
bpy.types.Scene.scene_name_1 = bpy.props.StringProperty(description="The wireframe scene's name",
                                                        default='wireframe',
                                                        maxlen=47)
bpy.types.Scene.scene_name_2 = bpy.props.StringProperty(description="The clay/other scene's name "
                                                                    "(depending on if you use clay or not)",
                                                        default='clay',
                                                        maxlen=47)


class WireframePanel(bpy.types.Panel):
    """The panel in the GUI."""

    bl_label = 'Set Up Wireframe'
    bl_idname = 'wireframe_panel'  # TODO: Should say something else.
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='', icon='WIRE')

    # draws the GUI
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, property='wireframe_type', text='')

        layout.separator()
        box = layout.box()
        split = box.split()
        col = split.column()
        row = col.row()
        row.prop(context.scene, property='cb_backup', text='Backup scene')

        row = col.row()
        row.prop(context.scene, property='cb_clear_rlayers', text='Clear render layers')

        row = col.row()
        row.prop(context.scene, property='cb_clear_mats', text='Clear materials')

        row_cb_comp = col.row()
        row_cb_comp.prop(context.scene, property='cb_comp', text='Composited wires')

        if context.scene.wireframe_type != 'WIREFRAME_FREESTYLE':
            row_cb_comp.enabled = False

        layers_affected = list(context.scene.layers_affected)
        layers_other = list(context.scene.layers_other)

        if not context.scene.cb_only_selected:
            if not (any(layers_affected)
                    and any(b_tools.manipulate_layerlists('subtract', layers_other, layers_affected))):
                row_cb_comp.active = False
                w_var.cb_comp_active = False
            else:
                w_var.cb_comp_active = True

        col = split.column()
        row = col.row()

        if (w_var.error_101 and context.scene.cb_only_selected
                and not b_tools.check_any_selected(context.scene, ('MESH',))):
            row.alert = True
        else:
            w_var.error_101 = False

        row.prop(context.scene, property='cb_only_selected', text='Only selected')

        row = col.row()
        row.prop(context.scene, property='cb_ao', text='AO as light')

        row = col.row()
        row.prop(context.scene, property='cb_clay', text='Use clay')

        row = col.row()
        row.separator()
        row.prop(context.scene, property='cb_clay_only', text='Only clay')

        if context.scene.cb_clay is not True:
            row.active = False
            w_var.cb_clay_only_active = False
        else:
            w_var.cb_clay_only_active = True

        layout.separator()
        row = layout.row()
        row.prop(context.scene, property='color_wire', text='Wire color')

        split = layout.split()
        col = split.column()
        row_cb_mat_wire = col.row()

        if context.scene.wireframe_type == 'WIREFRAME_FREESTYLE':
            row_cb_mat_wire.active = False
            w_var.cb_mat_wire_active = False
        else:
            w_var.cb_mat_wire_active = True

        if w_var.error_201 and context.scene.cb_mat_wire:
            row_cb_mat_wire.alert = True
        else:
            w_var.error_201 = False

        row_cb_mat_wire.prop(context.scene, property='cb_mat_wire', text='Material from scene:')

        col = split.column()
        row_matwire = col.row()
        row_matwire.prop(context.scene.materials, property='wire', text='')

        if context.scene.wireframe_type == 'WIREFRAME_FREESTYLE' or not context.scene.cb_mat_wire:
            row_matwire.active = False

        if context.scene.cb_clay:
            layout.separator()
            row = layout.row()
            row.prop(context.scene, property='color_clay', text='Clay color')
            split = layout.split()
            col = split.column()

            row_cb_mat_clay = col.row()

            if not context.scene.cb_clay:
                row_cb_mat_clay.active = False
                w_var.cb_mat_clay_active = False
            else:
                w_var.cb_mat_clay_active = True

            if w_var.error_202 and context.scene.cb_mat_clay:
                row_cb_mat_clay.alert = True
            else:
                w_var.error_202 = False

            row_cb_mat_clay.prop(context.scene, property='cb_mat_clay', text='Material from scene:')

            col = split.column()
            row_matclay = col.row()
            row_matclay.prop(context.scene.materials, property='clay', text='')

            if not context.scene.cb_mat_clay:
                row_matclay.active = False

        if context.scene.wireframe_type in 'WIREFRAME_FREESTYLE WIREFRAME_MODIFIER':
            layout.separator()
            row = layout.row()
            row.label('Wire thickness:')

            if context.scene.wireframe_type == 'WIREFRAME_FREESTYLE':
                row.prop(context.scene, property='slider_wt_freestyle', text='Thickness')

            elif context.scene.wireframe_type == 'WIREFRAME_MODIFIER':
                row.prop(context.scene, property='slider_wt_modifier', text='Thickness')

        layout.separator()
        split = layout.split()
        col = split.column()
        col.label(text='Affected layers:')
        row = col.row(align=True)
        row.operator(operator='wireframe_op.select_layers_affected', text='All')
        row.operator(operator='wireframe_op.deselect_layers_affected', text='None')
        col.prop(context.scene, property='layers_affected', text='')

        if context.scene.cb_only_selected:
            col.active = False
            row.active = False

        col = split.column()
        col.label(text='Other included layers:')
        row = col.row(align=True)
        row.operator(operator='wireframe_op.select_layers_other', text='All')
        row.operator(operator='wireframe_op.deselect_layers_other', text='None')
        col.prop(context.scene, property='layers_other', text='')

        layout.separator()
        row = layout.row()

        if w_var.error_301 and len(context.scene.field_scene_name) == 0:
            row.alert = True
        else:
            w_var.error_301 = False

        row.prop(context.scene, property='scene_name_1', text='Wire scene name')

        if context.scene.wireframe_type == 'WIREFRAME_BI':
            row = layout.row()

            if w_var.error_302 and len(context.scene.field_scene_name2) == 0:
                row.alert = True
            else:
                w_var.error_302 = False

            if context.scene.cb_clay:
                row.prop(context.scene, property='scene_name_2', text='Clay scene name')
            else:
                row.prop(context.scene, property='scene_name_2', text='Other scene name')

        layout.separator()
        row = layout.row()
        row.scale_y = 1.5
        row.operator(operator='wireframe_op.set_up', text='Set up', icon='WIRE')

        row = layout.row()
        row.scale_y = 1.2
        row.operator(operator='wireframe_op.add_to_current', text='Add to current', icon='PLUS')

        row = layout.row()
        row.scale_y = 1.2
        row.operator(operator='wireframe_op.quick_remove', text='Quick remove', icon='X')
