bl_info = {
    "name": "CyclesWireframing",
    "author": "Gustaf Blomqvist",
    "version": (1, 0, 0),
    "blender": (2, 73, 0),
    "location": "Sweden",
    "description": "Setting up wireframe renders has never been easier!",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

if 'bpy' in locals():
    import imp

    if 'wtools' in locals():
        imp.reload(wtools)

    if 'btools' in locals():
        imp.reload(btools)

    if 'woperators' in locals():
        imp.reload(woperators)

    if 'wvariables' in locals():
        imp.reload(wvariables)

    if 'bscene_w' in locals():
        imp.reload(bscene_w)


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
    del bpy.types.scene.Materials

if __name__ == '__main__':
    register()


def scene_materials(scene, context):

    mat_list = []
    counter = 0

    for mat in bpy.data.materials:
        mat_list.append((mat.name, mat.name, ''))
        counter += 1

    return mat_list


class MaterialSettings(bpy.types.PropertyGroup):

    mat_clay = bpy.props.EnumProperty(items=scene_materials,
                                      name='Clay material')

    mat_wire = bpy.props.EnumProperty(items=scene_materials,
                                      name='Clay material')


class WireMaterials(bpy.types.PropertyGroup):

    mat_wire = bpy.props.EnumProperty(items=scene_materials,
                                      name='Wire material')


def update_color_wire(self, context):
    """Updates the real wireframe material's color."""
    try:
        if bpy.context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
            wvariables.wire_freestyle.color = bpy.context.scene.ColorWire[0:3]
            wvariables.wire_freestyle.alpha = bpy.context.scene.ColorWire[-1]

        elif bpy.context.scene.WireframeType == 'WIREFRAME_MODIFIER':
            for node in wvariables.wire_modifier_mat.node_tree.nodes:
                if node.type == 'BSDF_DIFFUSE':
                    node.inputs[0].default_value = bpy.context.scene.ColorWire
            wvariables.wire_modifier_mat.diffuse_color = bpy.context.scene.ColorWire[0:3]

        elif bpy.context.scene.WireframeType == 'WIREFRAME_BI':
            wvariables.wire_bi_mat.diffuse_color = bpy.context.scene.ColorWire[0:3]
            wvariables.wire_bi_mat.alpha = bpy.context.scene.ColorWire[-1]

    except AttributeError:
        pass


def update_color_clay(self, context):
    """Updates the real clay material's color."""
    try:
        for node in wvariables.clay_mat.node_tree.nodes:
            if node.type == 'BSDF_DIFFUSE':
                node.inputs[0].default_value = bpy.context.scene.ColorClay
        wvariables.clay_mat.diffuse_color = bpy.context.scene.ColorClay[0:3]

    except AttributeError:
        pass


def update_wire_thickness(self, context):
    """Updates the real wireframe's thickness."""
    try:
        if bpy.context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
            wvariables.wire_freestyle.thickness = bpy.context.scene.SliderWireThicknessFreestyle

        elif bpy.context.scene.WireframeType == 'WIREFRAME_MODIFIER':
            for obj in bpy.context.scene.objects:
                if (obj in wvariables.only_selected
                        or BlenderSceneW.object_on_layer(bpy.context.scene, obj,
                                                         wvariables.affected_layers_numbers)):
                    for modifier in obj.modifiers:
                        if modifier.type == 'WIREFRAME':
                            modifier.thickness = bpy.context.scene.SliderWireThicknessModifier

    except AttributeError:
        pass


def update_checkboxes(self, context):

    if bpy.context.scene.WireframeType == 'WIREFRAME_BI':
        bpy.context.scene.CheckboxComp = True
        bpy.context.scene.CheckboxNewScene = True

    if bpy.context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
        bpy.context.scene.CheckboxComp = False

    if bpy.context.scene.WireframeType == 'WIREFRAME_MODIFIER':
        bpy.context.scene.CheckboxComp = False

# creates the drop-down list with different wireframe types
bpy.types.Scene.WireframeType = bpy.props.EnumProperty(
    items=[('WIREFRAME_MODIFIER', 'Modifier', 'Create wireframe using cycles and the wireframe modifier'),
           ('WIREFRAME_FREESTYLE', 'Freestyle', 'Create wireframe using cycles freestyle renderer'),
           ('WIREFRAME_BI', 'Blender Internal', 'Create wireframe using blender\'s internal renderer')],
    name='Wireframe methods',
    default='WIREFRAME_FREESTYLE',
    update=update_checkboxes)

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
bpy.types.Scene.CheckboxNewScene = bpy.props.BoolProperty(default=True, description="Create a new scene")
bpy.types.Scene.CheckboxOnlySelected = bpy.props.BoolProperty(default=False,
                                                              description="Only affect the selected meshes")
bpy.types.Scene.CheckboxUseAO = bpy.props.BoolProperty(default=False,
                                                       description="Use ambient occlusion lighting setup")
bpy.types.Scene.CheckboxClearRLayers = bpy.props.BoolProperty(default=True,
                                                              description="Remove all previous render layers")
bpy.types.Scene.CheckboxUseClay = bpy.props.BoolProperty(default=True, description="Activate the use of clay")
bpy.types.Scene.CheckboxOnlyClay = bpy.props.BoolProperty(default=False, description="Only use clay, no wires")
bpy.types.Scene.CheckboxUseMatWire = bpy.props.BoolProperty(default=False, description="Use material from scene "
                                                                                        "as wire material")
bpy.types.Scene.CheckboxUseMatClay = bpy.props.BoolProperty(default=False, description="Use material from scene "
                                                                                       "as clay material")

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


class WireframePanel(bpy.types.Panel):
    """The panel in the GUI."""

    bl_label = "Set up Wireframe"
    bl_idname = 'create_wireframe'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'Wireframing'

    # draws the GUI
    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.label(text='Wireframing method:')

        row = layout.row()
        row.prop(context.scene, property='WireframeType', text='')

        row = layout.row()
        row.prop(context.scene, property='CheckboxComp', text='Composited wires')

        if (bpy.context.scene.WireframeType == 'WIREFRAME_FREESTYLE'
                and any(list(bpy.context.scene.LayersAffected))
                and any(list(bpy.context.scene.LayersOther))):
            row.active = True

        layout.separator()

        # background box START
        box = layout.box()

        row = box.row()
        row.prop(context.scene, property='CheckboxNewScene', text='New scene/s')

        if bpy.context.scene.WireframeType == 'WIREFRAME_BI':
            row.active = False

        row = box.row()
        row.prop(context.scene, property='CheckboxClearRLayers', text='Clear render layers')

        row = box.row()

        if (wvariables.error_1 and bpy.context.scene.CheckboxOnlySelected
                and not btools.check_any_selected(bpy.context.scene, ['MESH'])):
            row.alert = True

        else:
            wvariables.error_1 = False

        row.prop(context.scene, property='CheckboxOnlySelected', text='Only selected')

        row = box.row()
        row.prop(context.scene, property='CheckboxUseAO', text='AO as light')

        row = box.row()
        row.prop(context.scene, property='CheckboxUseClay', text='Use clay')

        row = box.row()
        row.prop(context.scene, property='CheckboxOnlyClay', text='Only clay')

        if bpy.context.scene.CheckboxUseClay is not True:
            row.active = False
        # background box END

        layout.separator()

        row = layout.row()
        row.label(text='Wires:')
        row = layout.row()
        row.prop(context.scene, property='ColorWire', text='')
        row_matwirecheck = layout.row()

        if bpy.context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
            row_matwirecheck.active = False

        row_matwirecheck.prop(context.scene, property='CheckboxUseMatWire', text='Material from scene:')
        row_matwire = layout.row()
        row_matwire.prop(context.scene.Materials, property='mat_wire', text='')

        if not bpy.context.scene.CheckboxUseMatWire or not row_matwirecheck.active:
            row_matwire.active = False

        layout.box()

        row = layout.row()
        row.label(text='Clay:')
        row = layout.row()
        row.prop(context.scene, property='ColorClay', text='')
        row_matclaycheck = layout.row()
        row_matclaycheck.prop(context.scene, property='CheckboxUseMatClay', text='Material from scene:')
        row_matclay = layout.row()
        row_matclay.prop(context.scene.Materials, property='mat_clay', text='')

        if not bpy.context.scene.CheckboxUseMatClay or not row_matclaycheck.active:
            row_matclay.active = False

        layout.box()
        layout.separator()

        row = layout.row()

        if bpy.context.scene.WireframeType == 'WIREFRAME_FREESTYLE':
            row.prop(context.scene, property='SliderWireThicknessFreestyle', text='Wire thickness')

        elif bpy.context.scene.WireframeType == 'WIREFRAME_MODIFIER':
            row.prop(context.scene, property='SliderWireThicknessModifier', text='Wire thickness')

        layout.separator()

        split = layout.split()
        col = split.column()

        col.label(text='Affected layers:')

        row = col.row(align=True)
        row.operator(operator='wireframe_op.select_layers_affected', text='All')
        row.operator(operator='wireframe_op.deselect_layers_affected', text='None')

        col.prop(context.scene, property='LayersAffected', text='')

        if bpy.context.scene.CheckboxOnlySelected:
            col.active = False
            row.active = False

        split = layout.split()
        col = split.column()

        col.label(text='Other included layers:')

        row = col.row(align=True)
        row.operator(operator='wireframe_op.select_layers_other', text='All')
        row.operator(operator='wireframe_op.deselect_layers_other', text='None')

        col.prop(context.scene, property='LayersOther', text='')

        layout.separator()

        row = layout.row()

        row.scale_y = 1.3
        row.operator(operator='wireframe_op.create_wireframe', text='Work', icon='WIRE')

        row = layout.row()
        row.operator(operator='wireframe_op.clear_wireframes', text='Quick remove', icon='CANCEL')