# noinspection PyUnresolvedReferences
import bpy
from . import btools
from . import wvariables
from .bscene_w import BlenderSceneW


def comp_add_wireframe_bi(clay_scene_instance, wire_scene_intance):
    """Sets up the compositor nodes for the wireframe type 'Blender Internal'.

    Args:
        scene_instance: An instance of the class BlenderSceneW.
    """
    scene = clay_scene_instance.set_as_active()

    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()

    # creating the nodes
    alphaover = tree.nodes.new('CompositorNodeAlphaOver')
    alphaover.location = -100, -80

    rlwire = tree.nodes.new('CompositorNodeRLayers')
    rlwire.location = -400, -75
    rlwire.scene = bpy.data.scenes[wire_scene_intance.name]
    rlwire.layer = wvariables.rlname

    rlclay = tree.nodes.new('CompositorNodeRLayers')
    rlclay.location = -400, 250
    rlclay.layer = wvariables.rlname_2

    comp = tree.nodes.new('CompositorNodeComposite')
    comp.location = 400, 65

    viewer = tree.nodes.new('CompositorNodeViewer')
    viewer.location = 400, -125

    # connecting the nodes
    links = tree.links
    links.new(rlclay.outputs[0], alphaover.inputs[1])
    links.new(rlwire.outputs[0], alphaover.inputs[2])

    if wvariables.original_scene.CheckboxUseAO:
        colormix = tree.nodes.new('CompositorNodeMixRGB')
        colormix.location = 100, 140
        colormix.blend_type = 'MULTIPLY'
        colormix.inputs[0].default_value = 0.73

        links.new(alphaover.outputs[0], colormix.inputs[1])
        links.new(rlclay.outputs[10], colormix.inputs[2])
        links.new(colormix.outputs[0], comp.inputs[0])
        links.new(colormix.outputs[0], viewer.inputs[0])

    else:
        links.new(alphaover.outputs[0], comp.inputs[0])
        links.new(alphaover.outputs[0], viewer.inputs[0])

    for node in tree.nodes:
        node.select = False


def comp_add_wireframe_freestyle(scene_instance):
    """Sets up the compositor nodes for the wireframe type 'Freestyle'.

    Args:
        scene_instance: An instance of the class BlenderSceneW.
    """
    scene = scene_instance.set_as_active()

    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()

    # creating the nodes
    alphaover = tree.nodes.new('CompositorNodeAlphaOver')
    alphaover.location = -25, 50

    rlwire = tree.nodes.new('CompositorNodeRLayers')
    rlwire.location = -400, 250
    rlwire.layer = wvariables.rlname

    rlclay = tree.nodes.new('CompositorNodeRLayers')
    rlclay.location = -400, -75
    rlclay.layer = wvariables.rlname_other

    comp = tree.nodes.new('CompositorNodeComposite')
    comp.location = 400, 65

    viewer = tree.nodes.new('CompositorNodeViewer')
    viewer.location = 400, -125

    # connecting the nodes
    links = tree.links
    links.new(rlwire.outputs[0], alphaover.inputs[1])
    links.new(rlclay.outputs[0], alphaover.inputs[2])

    if wvariables.original_scene.CheckboxUseAO:
        colormix_wire = tree.nodes.new('CompositorNodeMixRGB')
        colormix_wire.location = -125, 150
        colormix_wire.blend_type = 'MULTIPLY'
        colormix_wire.inputs[0].default_value = 0.73

        colormix_clay = tree.nodes.new('CompositorNodeMixRGB')
        colormix_clay.location = -125, -100
        colormix_clay.blend_type = 'MULTIPLY'
        colormix_clay.inputs[0].default_value = 0.73

        alphaover.location = 125, 75

        links.new(rlwire.outputs[0], colormix_wire.inputs[1])
        links.new(rlwire.outputs[10], colormix_wire.inputs[2])

        links.new(rlclay.outputs[0], colormix_clay.inputs[1])
        links.new(rlclay.outputs[10], colormix_clay.inputs[2])

        links.new(colormix_wire.outputs[0], alphaover.inputs[1])
        links.new(colormix_clay.outputs[0], alphaover.inputs[2])

        links.new(alphaover.outputs[0], comp.inputs[0])
        links.new(alphaover.outputs[0], viewer.inputs[0])

    else:
        links.new(alphaover.outputs[0], comp.inputs[0])
        links.new(alphaover.outputs[0], viewer.inputs[0])

    for node in tree.nodes:
        node.select = False


def comp_add_ao(scene_instance):
    """Sets up the compositor nodes for the ambient occlusion (AO) effect.

    Args:
        scene_instance: An instance of the class BlenderSceneW.
    """
    scene = scene_instance.set_as_active()

    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()

    # creating the nodes
    colormix = tree.nodes.new('CompositorNodeMixRGB')
    colormix.location = 0, 60
    colormix.blend_type = 'MULTIPLY'
    colormix.inputs[0].default_value = 0.73

    rlayer = tree.nodes.new('CompositorNodeRLayers')
    rlayer.location = -300, 100
    rlayer.layer = wvariables.rlname

    comp = tree.nodes.new('CompositorNodeComposite')
    comp.location = 300, 130

    viewer = tree.nodes.new('CompositorNodeViewer')
    viewer.location = 300, -100

    # connecting the nodes
    links = tree.links
    links.new(rlayer.outputs[0], colormix.inputs[1])
    links.new(rlayer.outputs[10], colormix.inputs[2])
    links.new(colormix.outputs[0], comp.inputs[0])
    links.new(colormix.outputs[0], viewer.inputs[0])

    for node in tree.nodes:
        node.select = False


def add_clay_mat_to_selected(scene_instance):
    """Creates and sets the clay material to all selected objects in cycles.

    Args:
        scene_instance: An instance of the class BlenderSceneW.

    Returns:
        The clay material data object.
    """
    scene = scene_instance.set_as_active()

    if bpy.context.scene.CheckboxUseMatClay:
        clay_mat = wvariables.clay_mat_set

    else:
        clay_color = wvariables.original_scene.ColorClay
        # separating rgb from alpha
        clay_color_rgb = clay_color[0:3]

        clay_mat = bpy.data.materials.new('clay')

        clay_mat.use_nodes = True
        tree = clay_mat.node_tree
        tree.nodes.clear()

        # creating the nodes
        diffuse_node = tree.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse_node.location = -150, 50
        diffuse_node.inputs['Color'].default_value = clay_color
        diffuse_node.inputs['Roughness'].default_value = 0.05
        diffuse_node.color = clay_color_rgb

        output_node = tree.nodes.new('ShaderNodeOutputMaterial')
        output_node.location = 150, 50

        # sets the viewport color
        clay_mat.diffuse_color = clay_color_rgb

        # connecting the nodes.
        tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

        for node in tree.nodes:
            node.select = False

    # 1 if all meshes is selected, 0 if not.
    mesh_select = 1

    for obj in scene.objects:
        if obj.type == 'MESH':
            if not obj.select:
                mesh_select = 0
                break

    if mesh_select == 1 and wvariables.original_scene.WireframeType != 'WIREFRAME_MODIFIER':
        scene.render.layers.active.material_override = clay_mat

    else:
        previous_layers = list(scene.layers)
        scene.layers = (True,)*20
        for obj in scene.objects:
            if obj.select:
                scene.objects.active = obj

                obj.data.materials.append(clay_mat)
                clay_index = btools.find_material_index(obj, clay_mat)
                obj.active_material_index = clay_index

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                bpy.ops.object.material_slot_assign()

                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

        scene.layers = previous_layers

    return clay_mat


def add_wireframe_bi_to_selected(scene_instance):
    """Creates and sets the wireframe material to all selected objects in blender internal.

    Args:
        scene_instance: An instance of the class BlenderSceneW.

    Returns:
        The wireframe material data object.
    """
    scene_instance.set_as_active()

    if bpy.context.scene.CheckboxUseMatWire:
        wireframe_mat = wvariables.wire_mat_set

    else:
        wire_color = wvariables.original_scene.ColorWire
        # separating rgb and alpha
        wire_color_rgb = wire_color[0:3]
        wire_color_alpha = wire_color[-1]

        wireframe_mat = bpy.data.materials.new('wireframe')

        wireframe_mat.type = 'WIRE'
        wireframe_mat.diffuse_color = wire_color_rgb
        wireframe_mat.use_transparency = True
        wireframe_mat.alpha = wire_color_alpha
        wireframe_mat.use_shadeless = True
        wireframe_mat.offset_z = 0.03

    bpy.context.object.data.materials.append(wireframe_mat)
    bpy.ops.object.material_slot_copy()

    return wireframe_mat


def add_wireframe_modifier(scene_instance):
    """Creates and sets the wireframe modifier and material to all selected objects in cycles.

    Args:
        scene_instance: An instance of the class BlenderSceneW.

    Returns:
        The wireframe material data object.
    """
    scene = scene_instance.set_as_active()

    if bpy.context.scene.CheckboxUseMatWire:
        wireframe_mat = wvariables.wire_mat_set

    else:
        wire_color = wvariables.original_scene.ColorWire
        # separating rgb from alpha
        wireframe_color_rgb = wire_color[0:3]

        wireframe_mat = bpy.data.materials.new('wireframe')

        wireframe_mat.use_nodes = True
        tree = wireframe_mat.node_tree
        tree.nodes.clear()

        # creating the nodes
        diffuse_node = tree.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse_node.location = -150, 50
        diffuse_node.inputs['Color'].default_value = wire_color
        diffuse_node.inputs['Roughness'].default_value = 0.05
        diffuse_node.color = wireframe_color_rgb

        output_node = tree.nodes.new('ShaderNodeOutputMaterial')
        output_node.location = 150, 50

        # sets the viewport color
        wireframe_mat.diffuse_color = wireframe_color_rgb

        # connecting the nodes.
        tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

        for node in tree.nodes:
            node.select = False

    fillout_mat = bpy.data.materials.new('fillout')

    for obj in scene.objects:
        if obj.select:
            scene.objects.active = obj

            if len(bpy.context.object.data.materials) == 0:
                obj.data.materials.append(fillout_mat)

            obj.data.materials.append(wireframe_mat)
            bpy.context.object.active_material_index = btools.find_material_index(obj, wireframe_mat)

            wireframe_modifier = obj.modifiers.new(name='Wires', type='WIREFRAME')
            wireframe_modifier.use_even_offset = False
            wireframe_modifier.use_replace = False
            wireframe_modifier.material_offset = bpy.context.object.active_material_index
            wireframe_modifier.thickness = wvariables.original_scene.SliderWireThicknessModifier

    return wireframe_mat


def add_wireframe_freestyle(scene_instance):
    """Enables and sets up freestyle wireframing in cycles.

    Args:
        scene_instance: An instance of the class BlenderSceneW.

    Returns:
        The linestyle data object used in the freestyle rendering.
    """
    scene = scene_instance.set_as_active()

    BlenderSceneW.select(scene_instance, 'SELECT', ['MESH'], ['ELSE'])

    for obj in scene.objects:
        if obj.select:
            scene.objects.active = obj

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            bpy.ops.mesh.mark_freestyle_edge()

            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

    scene.render.use_freestyle = True

    scene.render.layers.active = scene.render.layers[wvariables.rlname]

    for n in scene.render.layers.active.freestyle_settings.linesets:
        scene.render.layers.active.freestyle_settings.linesets.remove(n)

    lineset = scene.render.layers.active.freestyle_settings.linesets.new('wires')
    lineset.select_edge_mark = True
    lineset.select_crease = False

    wire_color = wvariables.original_scene.ColorWire
    wire_thickness = wvariables.original_scene.SliderWireThicknessFreestyle

    wire_color_rgb = wire_color[0:3]
    wire_color_alpha = wire_color[-1]

    linestyle = bpy.data.linestyles.new('wire_style')
    linestyle.color = wire_color_rgb
    linestyle.alpha = wire_color_alpha
    linestyle.thickness = wire_thickness

    scene.render.layers.active.freestyle_settings.linesets.active.linestyle = linestyle

    return linestyle


def set_up_world_ao(scene_instance):
    """Sets up a new world for the ambient occlusion (AO) effect in cycles.

    Args:
        scene_instance: An instance of the class BlenderSceneW.
    """
    scene = scene_instance.set_as_active()

    new_world = bpy.context.blend_data.worlds.new('World of Wireframe')
    new_world.use_nodes = True
    new_world.node_tree.nodes[1].inputs[0].default_value = 1, 1, 1, 1
    new_world.light_settings.use_ambient_occlusion = True
    new_world.light_settings.ao_factor = 0.3

    for node in new_world.node_tree.nodes:
        node.select = False

    scene.world = new_world


def clean_objects_bi(scene_instance):
    """Deletes all objects in blender internal that is not going to get wireframed.

    This is for the wireframe type 'Blender Internal'.

    Args:
        scene_instance: An instance of the class BlenderSceneW.
    """
    scene = scene_instance.set_as_active()
    previous_layers = list(scene.layers)
    scene.layers = (True,)*20

    if wvariables.original_scene.CheckboxOnlySelected:
        for obj in scene.objects:
            if obj not in wvariables.only_selected and obj.type != 'CAMERA':
                obj.select = True
                bpy.ops.object.delete()

    else:
        for obj in scene.objects:
            if (BlenderSceneW.object_on_layer(scene_instance, obj, wvariables.all_layers_used_numbers) is False
                    or obj.type != 'MESH') and obj.type != 'CAMERA':
                obj.select = True
                bpy.ops.object.delete()

    scene.layers = previous_layers


def set_layers_used():
    """Sets all layers who will be affected by this add-on to a list.

    Returns:
        A list with booleans representing all the layers that will be affected by this add-on.
    """
    layers_used = [False, ]*20

    if wvariables.original_scene.CheckboxOnlySelected:
        for obj in bpy.context.scene.objects:
            if obj.select:
                layers_used = btools.add_layerlists(layers_used, obj.layers)

        layers_used = btools.add_layerlists(layers_used, wvariables.original_scene.LayersOther)

    else:
        layers_used = btools.add_layerlists(wvariables.original_scene.LayersAffected,
                                            wvariables.original_scene.LayersOther)

    return layers_used


def set_layers_affected():
    """Sets all layers who will be affected by wireframing and/or clay material to a list.

    Returns:
        A list with booleans representing all the layers that will be affected affected by
            wireframing and/or clay material.
    """
    layers_affected = [False, ]*20

    if wvariables.original_scene.CheckboxOnlySelected:
        for obj in bpy.context.scene.objects:
            if obj.select:
                layers_affected = btools.add_layerlists(layers_affected, obj.layers)

    else:
        layers_affected = list(wvariables.original_scene.LayersAffected)

    return layers_affected


def set_layers_other():
    """Sets all layers who will be included in the render layer just as they are in a list.

    Returns:
        A list with booleans representing all the layers that will be included in the render layer-just as they are.
    """
    layers_other = list(wvariables.original_scene.LayersOther)
    
    for index in range(0, 20):
        if layers_other[index] and wvariables.original_scene.LayersAffected[index]:
            layers_other[index] = False

    return layers_other
