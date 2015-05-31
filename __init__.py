bl_info = {
    "name": "CyclesWireframing",
    "author": "Gustaf Blomqvist",
    "version": (1, 0, 0),
    "blender": (2, 73, 0),
    "location": "3D View --> Toolshelf --> Wireframing",
    "description": "Setting up wireframe renders has never been easier!",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

if 'bpy' in locals():
    import importlib

    if 'wtools' in locals():
        importlib.reload(wtools)

    if 'btools' in locals():
        importlib.reload(btools)

    if 'woperators' in locals():
        importlib.reload(woperators)

    if 'wvariables' in locals():
        importlib.reload(wvariables)

    if 'bscene_w' in locals():
        importlib.reload(bscene_w)


# noinspection PyUnresolvedReferences
import bpy
from . import wtools
from . import btools
from . import woperators
from . import wvariables
from .bscene_w import BlenderSceneW


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.Materials = bpy.props.PointerProperty(type=MaterialSettings)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.Materials

if __name__ == '__main__':
    register()


def scene_materials(scene, context):

    mat_list = []

    for mat in bpy.data.materials:
        mat_list.append((mat.name, mat.name, ''))

    return mat_list


class MaterialSettings(bpy.types.PropertyGroup):

    mat_clay = bpy.props.EnumProperty(items=scene_materials,
                                      name='Clay material')

    mat_wire = bpy.props.EnumProperty(items=scene_materials,
                                      name='Wire material')


def update_color_wire(self, context):
    """Updates the real wireframe material's color."""
    try:
        if context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
            wvariables.wire_freestyle.color = context.scene.ColorWire[0:3]
            wvariables.wire_freestyle.alpha = context.scene.ColorWire[-1]

        elif context.scene.WireframeType == 'WIREFRAME_MODIFIER':
            for node in wvariables.wire_modifier_mat.node_tree.nodes:
                if node.type == 'BSDF_DIFFUSE':
                    node.inputs[0].default_value = context.scene.ColorWire
            wvariables.wire_modifier_mat.diffuse_color = context.scene.ColorWire[0:3]

        elif context.scene.WireframeType == 'WIREFRAME_BI':
            wvariables.wire_bi_mat.diffuse_color = context.scene.ColorWire[0:3]
            wvariables.wire_bi_mat.alpha = context.scene.ColorWire[-1]

    except AttributeError:
        pass


def update_color_clay(self, context):
    """Updates the real clay material's color."""
    try:
        for node in wvariables.clay_mat.node_tree.nodes:
            if node.type == 'BSDF_DIFFUSE':
                node.inputs[0].default_value = context.scene.ColorClay
        wvariables.clay_mat.diffuse_color = context.scene.ColorClay[0:3]

    except AttributeError:
        pass


def update_wire_thickness(self, context):
    """Updates the real wireframe's thickness."""
    if context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
        wvariables.wire_freestyle.thickness = context.scene.SliderWireThicknessFreestyle

    elif context.scene.WireframeType == 'WIREFRAME_MODIFIER':
        for obj in context.scene.objects:
            if ((context.scene.CheckboxOnlySelected and obj in wvariables.only_selected)
                    or (not context.scene.CheckboxOnlySelected and 
                    btools.object_on_layer(context.scene, obj,
                                           wvariables.affected_layers_numbers))):
                for modifier in obj.modifiers:
                    if modifier.type == 'WIREFRAME':
                        modifier.thickness = context.scene.SliderWireThicknessModifier

# creates the drop-down list with different wireframe types
bpy.types.Scene.WireframeType = bpy.props.EnumProperty(
    items=[('WIREFRAME_MODIFIER', 'Modifier', 'Create wireframe using cycles and the wireframe modifier'),
           ('WIREFRAME_FREESTYLE', 'Freestyle', 'Create wireframe using cycles freestyle renderer'),
           ('WIREFRAME_BI', 'Blender Internal', 'Create wireframe using blender\'s internal renderer')],
    name='Wireframe methods',
    default='WIREFRAME_FREESTYLE')

# creates the two color pickers
bpy.types.Scene.ColorWire = bpy.props.FloatVectorProperty(subtype='COLOR',
                                                          min=0,
                                                          max=1,
                                                          size=4,
                                                          default=(0, 1, 0.977, 0.8),
                                                          update=update_color_wire,
                                                          description="Wire color (changes real-time)")

bpy.types.Scene.ColorClay = bpy.props.FloatVectorProperty(subtype='COLOR',
                                                          min=0, max=1,
                                                          size=4,
                                                          default=(0, 0.154, 0.255, 1),
                                                          update=update_color_clay,
                                                          description="Clay color (changes real-time)")

# creates the two layer tables
bpy.types.Scene.LayersAffected = bpy.props.BoolVectorProperty(subtype='LAYER',
                                                              size=20,
                                                              default=(True,) + (False,) * 19,
                                                              description="Layers whose meshes will be affected")
bpy.types.Scene.LayersOther = bpy.props.BoolVectorProperty(subtype='LAYER',
                                                           size=20,
                                                           default=(False,) * 20,
                                                           description="Layers whose objects will be "
                                                                       "included as is, e.g. lights")
# creates all the checkboxes
bpy.types.Scene.CheckboxComp = bpy.props.BoolProperty(default=False,
                                                      description="Add the wires through composition")
bpy.types.Scene.CheckboxBackup = bpy.props.BoolProperty(default=True,
                                                        description="Create a backup scene")
bpy.types.Scene.CheckboxOnlySelected = bpy.props.BoolProperty(default=False,
                                                              description="Only affect the selected meshes")
bpy.types.Scene.CheckboxUseAO = bpy.props.BoolProperty(default=False,
                                                       description="Use ambient occlusion lighting setup")
bpy.types.Scene.CheckboxClearRLayers = bpy.props.BoolProperty(default=True,
                                                              description="Remove all previous render layers")
bpy.types.Scene.CheckboxUseClay = bpy.props.BoolProperty(default=True,
                                                         description="Activate the use of clay")
bpy.types.Scene.CheckboxOnlyClay = bpy.props.BoolProperty(default=False,
                                                          description="Only use clay, no wires")
bpy.types.Scene.CheckboxUseMatWire = bpy.props.BoolProperty(default=False,
                                                            description="Use material from scene as wire material")
bpy.types.Scene.CheckboxUseMatClay = bpy.props.BoolProperty(default=False,
                                                            description="Use material from scene as clay material")

# creates the sliders for the wireframe thickness
bpy.types.Scene.SliderWireThicknessFreestyle = bpy.props.FloatProperty(name='Wire Thickness',
                                                                       subtype='FACTOR',
                                                                       precision=1,
                                                                       soft_min=0.1,
                                                                       soft_max=10,
                                                                       default=1.5,
                                                                       update=update_wire_thickness,
                                                                       description="Wire thickness "
                                                                                   "(changes real-time)")

bpy.types.Scene.SliderWireThicknessModifier = bpy.props.FloatProperty(name='Wire Thickness',
                                                                      subtype='FACTOR',
                                                                      precision=3,
                                                                      soft_min=0.001,
                                                                      soft_max=0.1,
                                                                      default=0.004,
                                                                      update=update_wire_thickness,
                                                                      description="Wire thickness "
                                                                                  "(changes real-time)")
# creates the custom naming text field
bpy.types.Scene.CustomSceneName = bpy.props.StringProperty(description='Use a custom made scene name',
                                                           default='over_9000_tris',
                                                           maxlen=47)
bpy.types.Scene.CustomSceneName2 = bpy.props.StringProperty(description='Use a custom made scene name',
                                                            default='over_9000_power',
                                                            maxlen=47)


class WireframePanel(bpy.types.Panel):
    """The panel in the GUI."""

    bl_label = 'Set Up Wireframe'
    bl_idname = 'wireframe_panel'
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
        row.prop(context.scene, property='WireframeType', text='')

        layout.separator()

        box = layout.box()
        split = box.split()
        col = split.column()

        row = col.row()
        row.prop(context.scene, property='CheckboxBackup', text='Backup scene')

        if context.scene.WireframeType == 'WIREFRAME_BI':
            row.enabled = False

        row = col.row()
        row.prop(context.scene, property='CheckboxClearRLayers', text='Clear render layers')

        row = col.row()

        if (wvariables.error_101 and context.scene.CheckboxOnlySelected
                and not btools.check_any_selected(context.scene, ['MESH'])):
            row.alert = True

        else:
            wvariables.error_1 = False

        row.prop(context.scene, property='CheckboxOnlySelected', text='Only selected')

        if context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
            row_checkcomp = col.row()
            row_checkcomp.prop(context.scene, property='CheckboxComp', text='Composited wires')

            if not (any(list(context.scene.LayersAffected)) and any(list(context.scene.LayersOther))):
                row_checkcomp.active = False

        col = split.column()

        row = col.row()
        row.prop(context.scene, property='CheckboxUseAO', text='AO as light')

        row = col.row()
        row.prop(context.scene, property='CheckboxUseClay', text='Use clay')

        row = col.row()
        row.separator()
        row.prop(context.scene, property='CheckboxOnlyClay', text='Only clay')

        if context.scene.CheckboxUseClay is not True:
            row.active = False

        layout.separator()
        row = layout.row()
        row.prop(context.scene, property='ColorWire', text='Wire color')

        split = layout.split()
        col = split.column()

        row_matwirecheck = col.row()
        if context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
            row_matwirecheck.active = False

        if wvariables.error_201 and context.scene.CheckboxUseMatWire and len(bpy.data.materials) == 0:
            row_matwirecheck.alert = True
        else:
            wvariables.error_201 = False
        row_matwirecheck.prop(context.scene, property='CheckboxUseMatWire', text='Material from scene:')

        col = split.column()

        row_matwire = col.row()
        row_matwire.prop(context.scene.Materials, property='mat_wire', text='')

        if context.scene.WireframeType == 'WIREFRAME_FREESTYLE' or not context.scene.CheckboxUseMatWire:
            row_matwire.active = False

        if context.scene.CheckboxUseClay:
            layout.separator()

            row = layout.row()
            row.prop(context.scene, property='ColorClay', text='Clay color')

            split = layout.split()
            col = split.column()

            row_matclaycheck = col.row()
            if wvariables.error_202 and context.scene.CheckboxUseMatClay and len(bpy.data.materials) == 0:
                row_matclaycheck.alert = True
            else:
                wvariables.error_202 = False
            row_matclaycheck.prop(context.scene, property='CheckboxUseMatClay', text='Material from scene:')

            col = split.column()

            row_matclay = col.row()
            row_matclay.prop(context.scene.Materials, property='mat_clay', text='')

            if not context.scene.CheckboxUseMatClay:
                row_matclay.active = False

        if context.scene.WireframeType in 'WIREFRAME_FREESTYLE WIREFRAME_MODIFIER':
            layout.separator()
            row = layout.row()
            row.label('Wire thickness:')

            if context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
                row.prop(context.scene, property='SliderWireThicknessFreestyle', text='Thickness')

            elif context.scene.WireframeType == 'WIREFRAME_MODIFIER':
                row.prop(context.scene, property='SliderWireThicknessModifier', text='Thickness')

        layout.separator()
        split = layout.split()
        col = split.column()

        col.label(text='Affected layers:')
        row = col.row(align=True)
        row.operator(operator='wireframe_op.select_layers_affected', text='All')
        row.operator(operator='wireframe_op.deselect_layers_affected', text='None')

        col.prop(context.scene, property='LayersAffected', text='')

        if context.scene.CheckboxOnlySelected:
            col.active = False
            row.active = False

        col = split.column()

        col.label(text='Other included layers:')

        row = col.row(align=True)
        row.operator(operator='wireframe_op.select_layers_other', text='All')
        row.operator(operator='wireframe_op.deselect_layers_other', text='None')

        col.prop(context.scene, property='LayersOther', text='')

        layout.separator()

        row = layout.row()
        row.prop(context.scene, property='CustomSceneName', text='Wire scene name')

        if context.scene.WireframeType == 'WIREFRAME_BI':
            row = layout.row()
            row.prop(context.scene, property='CustomSceneName2', text='Clay scene name')

        layout.separator()

        row = layout.row()

        row.scale_y = 1.3
        row.operator(operator='wireframe_op.create_wireframe', text='Set up', icon='WIRE')