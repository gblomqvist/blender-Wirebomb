# <pep8-80 compliant>

import bpy
from . import w_b_scene
from . import w_tools
from . import b_tools
from . import w_operators
from . import w_var
from . import constants

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

bl_info = {
    "name": "Cycles Wireframe and Clay (CWaC)",
    "author": "Gustaf Blomqvist",
    "version": (1, 0, 0),
    "blender": (2, 76, 0),
    "location": "Render settings --> Set up Wireframe and Clay",
    "description": "Setting up wireframe and clay renders has never been easier!",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render"
}


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.cwac = bpy.props.PointerProperty(type=CWaC)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.cwac


if __name__ == '__main__':
    register()


def update_color_wire(self, context):
    """Updates the wireframe material's color."""
    if context.scene.cwac.data_freestyle_linestyle in bpy.data.linestyles:
        linestyle = bpy.data.linestyles[context.scene.cwac.data_freestyle_linestyle]
        linestyle.color = context.scene.cwac.color_wire[0:3]
        linestyle.alpha = context.scene.cwac.color_wire[-1]

    elif context.scene.cwac.wireframe_method == 'WIREFRAME_MODIFIER':
        if context.scene.cwac.data_material_wire in bpy.data.materials:
            material = bpy.data.materials[context.scene.cwac.data_material_wire]
            node = material.node_tree.nodes['addon_wireframe']
            node.inputs[0].default_value = context.scene.cwac.color_wire

            # updating viewport color
            material.diffuse_color = context.scene.cwac.color_wire[0:3]


def update_color_clay(self, context):
    """Updates the clay material's color."""
    if context.scene.cwac.data_material_clay in bpy.data.materials:
        material = bpy.data.materials[context.scene.cwac.data_material_clay]
        node = material.node_tree.nodes['addon_clay']
        node.inputs[0].default_value = context.scene.cwac.color_clay[0:3] + (1.0, )

        # updating viewport color
        material.diffuse_color = context.scene.cwac.color_clay[0:3]


def update_wire_thickness(self, context):
    """Updates the wireframe's thickness."""
    if context.scene.cwac.data_freestyle_linestyle in bpy.data.linestyles:
        linestyle = bpy.data.linestyles[context.scene.cwac.data_freestyle_linestyle]
        linestyle.thickness = context.scene.cwac.slider_wt_freestyle

    elif context.scene.cwac.wireframe_method == 'WIREFRAME_MODIFIER':
        for col_obj in context.scene.cwac.data_objects_affected:
            if col_obj.name in bpy.data.objects:
                obj = bpy.data.objects[col_obj.name]
                if obj.type == 'MESH':
                    if 'addon_wireframe' in obj.modifiers:
                        obj.modifiers['addon_wireframe'].thickness = context.scene.cwac.slider_wt_modifier


def update_cb_composited(self, context):
    if context.scene.cwac.wireframe_method != 'WIREFRAME_FREESTYLE':
        context.scene.cwac.cb_composited = False


class CWaC(bpy.types.PropertyGroup):
    """Stores data for the add-on."""

    # names of the materials used
    data_material_wire = bpy.props.StringProperty()
    data_material_clay = bpy.props.StringProperty()

    # freestyle linstyle used in freestyle wireframe method
    data_freestyle_linestyle = bpy.props.StringProperty()

    # objects affected, other and all are saved in these collections
    data_objects_affected = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    data_objects_other = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    data_objects_all = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    # drop-down list with different wireframe methods
    wireframe_method = bpy.props.EnumProperty(
        items=[('WIREFRAME_MODIFIER', 'Modifier', 'Create wireframe using cycles and the wireframe modifier'),
               ('WIREFRAME_FREESTYLE', 'Freestyle', 'Create wireframe using cycles freestyle renderer')],
        name='Method',
        description='Wireframe method',
        default='WIREFRAME_FREESTYLE',
        update=update_cb_composited)

    # checkboxes
    cb_backup = bpy.props.BoolProperty(default=True, description="Create a backup scene")
    cb_clear_rlayers = bpy.props.BoolProperty(default=True, description="Remove all previous render layers")
    cb_clear_materials = bpy.props.BoolProperty(default=True, description="Remove all previous materials from objects")
    cb_composited = bpy.props.BoolProperty(default=False, description="Add the wireframe through composition "
                                                                      "(only available when there is a posibility "
                                                                      "that it is needed)")
    cb_only_selected = bpy.props.BoolProperty(default=False, description="Only affect the selected meshes")
    cb_ao = bpy.props.BoolProperty(default=False, description="Use ambient occlusion lighting setup")
    cb_clay = bpy.props.BoolProperty(default=True, description="Activate the use of clay")
    cb_clay_only = bpy.props.BoolProperty(default=False, description="Only use clay, don't set up wireframe")
    cb_mat_wire = bpy.props.BoolProperty(default=False, description="Use material from scene as wireframe material")
    cb_mat_clay = bpy.props.BoolProperty(default=False, description="Use material from scene as clay material")

    # color pickers
    color_wire = bpy.props.FloatVectorProperty(subtype='COLOR',
                                               min=0,
                                               max=1,
                                               size=4,
                                               default=(1.0, 1.0, 1.0, 0.6),
                                               update=update_color_wire,
                                               description="Wireframe color (changes real-time)")
    color_clay = bpy.props.FloatVectorProperty(subtype='COLOR',
                                               min=0, max=1,
                                               size=4,
                                               default=(0.087876, 0.138719, 0.189033, 1.0),
                                               update=update_color_clay,
                                               description="Clay color (changes real-time)")

    # materials from prop searches
    material_wire = bpy.props.StringProperty()
    material_clay = bpy.props.StringProperty()

    # layer tables
    layers_affected = bpy.props.BoolVectorProperty(subtype='LAYER',
                                                   size=20,
                                                   default=(True,) + (False,) * 19,
                                                   description="Layers whose meshes will be affected")
    layers_other = bpy.props.BoolVectorProperty(subtype='LAYER',
                                                size=20,
                                                default=(False,) * 20,
                                                description="Layers whose objects will be "
                                                            "included as is, e.g. lights")

    # sliders for the wireframe thickness
    slider_wt_freestyle = bpy.props.FloatProperty(name='Wireframe Thickness',
                                                  subtype='FACTOR',
                                                  precision=3,
                                                  soft_min=0.1,
                                                  soft_max=10,
                                                  default=1.5,
                                                  update=update_wire_thickness,
                                                  description="Wireframe thickness "
                                                              "(changes real-time)")
    slider_wt_modifier = bpy.props.FloatProperty(name='Wireframe Thickness',
                                                 subtype='FACTOR',
                                                 precision=4,
                                                 soft_min=0.001,
                                                 soft_max=0.1,
                                                 default=0.004,
                                                 update=update_wire_thickness,
                                                 description="Wireframe thickness "
                                                             "(changes real-time)")

    # scene naming text fields
    scene_name_1 = bpy.props.StringProperty(default='wireframe',
                                            maxlen=47,
                                            description="The wireframe/clay scene's name")


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
        scene = w_b_scene.BlenderSceneW(context.scene, False)
        layout = self.layout

        # config file
        row = layout.row(align=True)
        row.label("Config file:")
        row.operator(operator='scene.cwac_config_save', text='Save', icon='SAVE_PREFS')
        row.operator(operator='scene.cwac_config_load', text='Load', icon='FILESEL')

        # box line
        layout.box()

        # method
        layout.separator()
        layout.prop(context.scene.cwac, property='wireframe_method')

        # box start
        layout.separator()
        box = layout.box()

        # backup scene
        split = box.split()
        col = split.column()
        row = col.row()
        row.prop(context.scene.cwac, property='cb_backup', text='Backup scene')

        # clear render layers
        row = col.row()
        row.prop(context.scene.cwac, property='cb_clear_rlayers', text='Clear render layers')

        # clear materials
        row = col.row()
        row.prop(context.scene.cwac, property='cb_clear_materials', text='Clear materials')

        # composited wires
        row = col.row()

        if scene.get_scene().cwac.wireframe_method == 'WIREFRAME_FREESTYLE':
            row.prop(context.scene.cwac, property='cb_composited', text='Composited wires')

        # only selected
        col = split.column()
        row = col.row()

        if w_var.error_101 and scene.get_scene().cwac.cb_only_selected and not scene.check_any_selected():
            row.alert = True

        else:
            w_var.error_101 = False

        row.prop(context.scene.cwac, property='cb_only_selected', text='Only selected')

        # ao as light
        row = col.row()
        row.prop(context.scene.cwac, property='cb_ao', text='AO as light')

        # use clay
        row = col.row()
        row.prop(context.scene.cwac, property='cb_clay', text='Use clay')

        # only clay
        row = col.row()
        row.separator()

        if scene.get_scene().cwac.cb_clay is not True:
            row.active = False
            w_var.cb_clay_only_active = False

        else:
            w_var.cb_clay_only_active = True

        row.prop(context.scene.cwac, property='cb_clay_only', text='Only clay')
        # box end

        # wire color
        layout.separator()
        row = layout.row()

        if ((scene.get_scene().cwac.cb_mat_wire and
             scene.get_scene().cwac.wireframe_method != 'WIREFRAME_FREESTYLE') or
                (scene.get_scene().cwac.cb_clay_only and w_var.cb_clay_only_active)):
            row.active = False

        row.prop(context.scene.cwac, property='color_wire', text='Wireframe color')

        if scene.get_scene().cwac.wireframe_method != 'WIREFRAME_FREESTYLE':

            # use material (wire)
            split = layout.split()
            col = split.column()
            row = col.row()

            if (scene.get_scene().cwac.wireframe_method == 'WIREFRAME_FREESTYLE' or
                    (scene.get_scene().cwac.cb_clay_only and w_var.cb_clay_only_active)):
                row.active = False
                w_var.cb_mat_wire_active = False

            else:
                w_var.cb_mat_wire_active = True

            if scene.get_scene().cwac.cb_mat_wire and scene.get_scene().cwac.material_wire == '':
                row.alert = True

            row.prop(context.scene.cwac, property='cb_mat_wire', text='Use material:')

            # wire material
            col = split.column()
            row = col.row()

            if (not scene.get_scene().cwac.cb_mat_wire or
                    (scene.get_scene().cwac.cb_clay_only and scene.get_scene().cwac.cb_clay)):
                row.active = False

            row.prop_search(context.scene.cwac, 'material_wire', bpy.data, 'materials', text='')

        # clay color
        layout.separator()
        row = layout.row()

        if scene.get_scene().cwac.cb_mat_clay or not scene.get_scene().cwac.cb_clay:
            row.active = False

        row.prop(context.scene.cwac, property='color_clay', text='Clay color')

        # use material (clay)
        split = layout.split()
        col = split.column()
        row = col.row()

        if not scene.get_scene().cwac.cb_clay:
            row.active = False
            w_var.cb_mat_clay_active = False

        else:
            w_var.cb_mat_clay_active = True

        if scene.get_scene().cwac.cb_mat_clay and scene.get_scene().cwac.material_clay == '':
            row.alert = True

        row.prop(context.scene.cwac, property='cb_mat_clay', text='Use material:')

        # clay material
        col = split.column()
        row = col.row()

        if not (scene.get_scene().cwac.cb_mat_clay and w_var.cb_mat_clay_active):
            row.active = False

        row.prop_search(context.scene.cwac, 'material_clay', bpy.data, 'materials', text='')

        # wire thickness
        layout.separator()
        row = layout.row()
        row.label('Wireframe thickness:')

        if scene.get_scene().cwac.wireframe_method == 'WIREFRAME_FREESTYLE':
            row.prop(context.scene.cwac, property='slider_wt_freestyle', text='Thickness')

        elif scene.get_scene().cwac.wireframe_method == 'WIREFRAME_MODIFIER':
            row.prop(context.scene.cwac, property='slider_wt_modifier', text='Thickness')

        # 'affected layers' buttons
        layout.separator()
        split = layout.split()
        col = split.column()
        col.label(text='Affected layers:')
        row = col.row(align=True)

        if scene.get_scene().cwac.cb_only_selected:
            col.active = False
            row.active = False

        row.operator(operator='scene.cwac_select_layers_affected', text='All')
        row.operator(operator='scene.cwac_deselect_layers_affected', text='None')
        col.prop(context.scene.cwac, property='layers_affected', text='')

        # 'other layers' buttons
        col = split.column()
        col.label(text='Other included layers:')
        row = col.row(align=True)
        row.operator(operator='scene.cwac_select_layers_other', text='All')
        row.operator(operator='scene.cwac_deselect_layers_other', text='None')
        col.prop(context.scene.cwac, property='layers_other', text='')

        # scene name 1
        layout.separator()
        row = layout.row()

        if w_var.error_301 and len(scene.get_scene().cwac.scene_name_1) == 0:
            row.alert = True

        else:
            w_var.error_301 = False

        row.prop(context.scene.cwac, property='scene_name_1', text='Scene name')

        # 'set up new' and 'quick remove' buttons
        layout.separator()
        row = layout.row()
        row.scale_y = 1.3
        row.operator(operator='scene.cwac_set_up_new', text='Set up new', icon='WIRE')
