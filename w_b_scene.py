# noinspection PyUnresolvedReferences
import bpy
from .b_scene import BlenderScene
from . import b_tools
from . import w_var


class BlenderSceneW(BlenderScene):
    """A version of the class BlenderScene that is specific for this add-on."""

    def select(self, mode, types=None, types_excluded=None, layers=None, layers_excluded=None, objects=None):
        """Selects or deselects objects, a special version of BlenderScene's select function.

        (De)selects specific objects or objects by object types and layers.

        Args:
            mode: A string representing the mode, either 'SELECT' to select objects or 'DESELECT' to deselect objects.
            types: An optional list consisting of strings representing the object types that are to be (de)selected.
                If none specified, objects variable needs to be set.
            types_excluded: An optional list consisting of strings representing the object types that are to be
                deselected or left out if mode is set to 'DESELECT', these types will not be included among the
                select_types.
            layers: An optional list consisting of integers representing the layers whose objects
                are up for (de)selection.
            layers_excluded: An optional list consisting of integers representing the layers whose objects
                will be deselected or left out if mode is set to 'DESELECT', these layers will not be included among
                the layer_numbers.
            objects: An optional list consisting of specific objects that are to be (de)selected, need to be set if
                types variable is not set. If set, types variable will not matter.
        """
        scene = self.set_as_active()
        all_layer_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        object_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE',
                        'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER']
        if types is None:
            types = ['']

        if layers is None:
            if types != ['ALL']:
                layers = w_var.affected_layers_numbers

            else:
                layers = all_layer_numbers

        elif layers == ['EVERY']:
            layers = all_layer_numbers

        if w_var.cb_only_selected:
            objects = w_var.only_selected

        elif objects is None:
            objects = []

        if types_excluded is None:
            types_excluded = []

        elif types_excluded == ['ELSE']:
            types_excluded = [x for x in object_types if x not in types]

        if layers_excluded is None:
            layers_excluded = []

        elif layers_excluded == ['ELSE']:
            layers_excluded = [x for x in all_layer_numbers if x not in layers]

        previous_area = bpy.context.area.type
        # need 3D view space to change object select property
        bpy.context.area.type = 'VIEW_3D'

        if mode == 'SELECT':
            if types == ['ALL']:
                for obj in scene.objects:
                    if (obj.type not in types_excluded and self.object_on_layer(obj, layers)
                            and not self.object_on_layer(obj, layers_excluded)):
                        obj.select = True

                    elif obj.type in types_excluded or self.object_on_layer(obj, layers_excluded):
                        obj.select = False

            elif len(objects) > 0:
                for obj in scene.objects:
                    if obj in objects:
                        obj.select = True

            else:
                for obj in scene.objects:
                    if (obj.type in types and obj.type not in types_excluded
                            and self.object_on_layer(obj, layers)
                            and not self.object_on_layer(obj, layers_excluded)):
                        obj.select = True
                    elif obj.type in types_excluded or self.object_on_layer(obj, layers_excluded):
                        obj.select = False

        elif mode == 'DESELECT':
            if types == ['ALL']:
                for obj in scene.objects:
                    if (obj.type not in types_excluded and self.object_on_layer(obj, layers)
                            and not self.object_on_layer(obj, layers_excluded)):
                        obj.select = False

            elif len(objects) > 0:
                for obj in scene.objects:
                    if obj in objects:
                        obj.select = False

            else:
                for obj in scene.objects:
                    if (obj.type in types and obj.type not in types_excluded
                        and self.object_on_layer(obj, layers)
                            and not self.object_on_layer(obj, layers_excluded)):
                        obj.select = False

        else:
            return "Error: No such mode as '{}'.".format(mode)

        bpy.context.area.type = previous_area
        self.set_active_object(types)

    def set_up_rlayer(self, rlname, visible_layers=None, include_layers=None,
                      mask_layers=None, rlname_other=None):
        """Sets up one or two render layers, a special version of BlenderScene's set_up_rlayer function.

        Args:
            rlname: A string representing the name of the render layer you want to set up.
            visible_layers: An optional list consisting of integers representing the layers you want to be visible
                -i.e. all layers you want to render, which also will be visible in the viewport-in the new render layer.
            include_layers: An optional list consisting of integers representing the layers
                you want to be included in the new render layer (specific for this render layer).
            mask_layers: An optional list consisting of integers representing the layers
                you want to be masked in the new render layer (specific for this render layer).
            rlname_other: An optional string representing the name of the second render layer, which is needed if the
                wireframe type is 'Freestyle' and the 'Composited Wires' checkbox is checked.
        """
        scene = self.set_as_active()
        layer_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

        if visible_layers is None:
            visible_layers = w_var.all_layers_used_numbers

        if include_layers is None:
            include_layers = w_var.all_layers_used_numbers

        if mask_layers is None:
            mask_layers = []

        if w_var.cb_clear_rlayers:
            for layer in scene.render.layers[0:len(scene.render.layers)-1]:
                scene.render.layers.remove(layer)

            scene.render.layers.active.name = rlname
            scene.render.layers.active.use = True

            new_rlayer = scene.render.layers.active

        # not clearing render layers --> creates new one
        else:
            for rlayer in scene.render.layers:
                rlayer.use = False

            new_rlayer = scene.render.layers.new(rlname)
            scene.render.layers.active = new_rlayer

        if w_var.rlname is None:
            w_var.rlname = new_rlayer.name

        # only used for blender internal wireframe, two scenes --> two render layer names
        else:
            w_var.rlname_2 = new_rlayer.name

        # there needs to be two render layers for freestyle compositing
        if w_var.cb_comp and w_var.original_scene.wireframe_type == 'WIREFRAME_FREESTYLE':
            new_rlayer = scene.render.layers.new(rlname_other)
            w_var.rlname_other = new_rlayer.name

        if w_var.cb_ao:
            scene.render.layers[rlname].use_pass_ambient_occlusion = True

            if w_var.cb_comp and w_var.original_scene.wireframe_type == 'WIREFRAME_FREESTYLE':
                scene.render.layers[rlname_other].use_pass_ambient_occlusion = True

        for i in layer_numbers:
            if w_var.cb_comp and w_var.original_scene.wireframe_type == 'WIREFRAME_FREESTYLE':
                if w_var.other_layers_numbers is not None:
                    if i in w_var.other_layers_numbers:
                        scene.render.layers[rlname].layers_zmask[i] = True
                        scene.render.layers[rlname_other].layers[i] = True

                    else:
                        scene.render.layers[rlname].layers_zmask[i] = False
                        scene.render.layers[rlname_other].layers[i] = False

                if w_var.affected_layers_numbers is not None:
                    if i in w_var.affected_layers_numbers:
                        scene.render.layers[rlname_other].layers_zmask[i] = True
                        scene.render.layers[rlname].layers[i] = True

                    else:
                        scene.render.layers[rlname_other].layers_zmask[i] = False
                        scene.render.layers[rlname].layers[i] = False
            else:
                if include_layers is not None:
                    if i in include_layers:
                        scene.render.layers[rlname].layers[i] = True

                    else:
                        scene.render.layers[rlname].layers[i] = False

                if mask_layers is not None:
                    if i in mask_layers:
                        scene.render.layers[rlname].layers_zmask[i] = True

                    else:
                        scene.render.layers[rlname].layers_zmask[i] = False

            if visible_layers is not None:
                if i in visible_layers:
                    scene.layers[i] = True

                else:
                    scene.layers[i] = False

    def clean_objects(self):
        """Deletes all objects in blender internal that is not going to get wireframed.

        This is for the wireframe type 'Blender Internal'.
        """
        scene = self.set_as_active()
        previous_area = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'
        previous_layers = list(scene.layers)
        scene.layers = (True,)*20
        self.select('DESELECT', ['ALL'])

        if w_var.cb_only_selected:
            for obj in scene.objects:
                if (obj not in w_var.only_selected
                        and self.object_on_layer(obj, w_var.other_layers_numbers) is False):
                    obj.select = True
                    bpy.ops.object.delete()

        else:
            for obj in scene.objects:
                if self.object_on_layer(obj, w_var.all_layers_used_numbers) is False:
                    obj.select = True
                    bpy.ops.object.delete()

        scene.layers = previous_layers
        bpy.context.area.type = previous_area

    def comp_add_wireframe_bi(self, wire_scene_intance):
        """Sets up the compositor nodes for the wireframe type 'Blender Internal'.

        Args:
            wire_scene_instance: An instance of the class BlenderSceneW.
        """
        scene = self.set_as_active()

        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        # creating the nodes
        alphaover = tree.nodes.new('CompositorNodeAlphaOver')
        alphaover.location = -100, -80

        rlwire = tree.nodes.new('CompositorNodeRLayers')
        rlwire.location = -400, -75
        rlwire.scene = bpy.data.scenes[wire_scene_intance.name]
        rlwire.layer = w_var.rlname

        rlclay = tree.nodes.new('CompositorNodeRLayers')
        rlclay.location = -400, 250
        rlclay.scene = scene
        rlclay.layer = w_var.rlname_2

        comp = tree.nodes.new('CompositorNodeComposite')
        comp.location = 400, 65

        viewer = tree.nodes.new('CompositorNodeViewer')
        viewer.location = 400, -125

        # connecting the nodes
        links = tree.links
        links.new(rlclay.outputs[0], alphaover.inputs[1])
        links.new(rlwire.outputs[0], alphaover.inputs[2])

        if w_var.cb_ao:
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

    def comp_add_wireframe_freestyle(self):
        """Sets up the compositor nodes for the wireframe type 'Freestyle'."""
        scene = self.set_as_active()

        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        # creating the nodes
        alphaover = tree.nodes.new('CompositorNodeAlphaOver')
        alphaover.location = -25, 50

        rlwire = tree.nodes.new('CompositorNodeRLayers')
        rlwire.location = -400, 250
        rlwire.scene = scene
        rlwire.layer = w_var.rlname

        rlclay = tree.nodes.new('CompositorNodeRLayers')
        rlclay.location = -400, -75
        rlclay.scene = scene
        rlclay.layer = w_var.rlname_other

        comp = tree.nodes.new('CompositorNodeComposite')
        comp.location = 400, 65

        viewer = tree.nodes.new('CompositorNodeViewer')
        viewer.location = 400, -125

        # connecting the nodes
        links = tree.links
        links.new(rlwire.outputs[0], alphaover.inputs[1])
        links.new(rlclay.outputs[0], alphaover.inputs[2])

        if w_var.cb_ao:
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

    def comp_add_ao(self):
        """Sets up the compositor nodes for the ambient occlusion (AO) effect."""
        scene = self.set_as_active()

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
        rlayer.layer = w_var.rlname

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

    def add_clay_mat_to_selected(self):
        """Creates and sets the clay material to all selected objects in cycles.

        Returns:
            The clay material data object.
        """
        scene = self.set_as_active()

        if w_var.cb_mat_clay:
            clay_mat = w_var.clay_mat_set

        else:
            clay_color = w_var.original_scene.color_clay
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

        # 1 if all meshes is selected, 0 if not
        mesh_select = 1

        for obj in scene.objects:
            if obj.type == 'MESH':
                if not obj.select:
                    mesh_select = 0
                    break
        # todo why not in wireframe modifier?
        if mesh_select == 1: #and w_var.original_scene.wireframe_type != 'WIREFRAME_MODIFIER':
            scene.render.layers.active.material_override = clay_mat

        else:
            previous_area = bpy.context.area.type
            bpy.context.area.type = 'VIEW_3D'
            previous_layers = list(scene.layers)
            scene.layers = (True,)*20

            for obj in scene.objects:
                if obj.select:
                    scene.objects.active = obj
                    obj.data.materials.append(clay_mat)
                    clay_index = b_tools.find_material_index(obj, clay_mat)
                    obj.active_material_index = clay_index

                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')

                    bpy.ops.object.material_slot_assign()

                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')

            scene.layers = previous_layers
            bpy.context.area.type = previous_area

        return clay_mat

    def add_wireframe_bi_to_selected(self):
        """Creates and sets the wireframe material to all selected objects in blender internal.

        Returns:
            The wireframe material data object.
        """
        self.set_as_active()

        if w_var.cb_mat_wire:
            wireframe_mat = w_var.wire_mat_set

        else:
            wire_color = w_var.original_scene.color_wire
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

        bpy.context.active_object.data.materials.append(wireframe_mat)
        bpy.ops.object.material_slot_copy()

        return wireframe_mat

    def add_wireframe_modifier(self):
        """Creates and sets the wireframe modifier and material to all selected objects in cycles render engine.

        Returns:
            The wireframe material data object.
        """
        scene = self.set_as_active()

        if w_var.cb_mat_wire:
            wireframe_mat = w_var.wire_mat_set

        else:
            wire_color = w_var.original_scene.color_wire
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

                if len(bpy.context.active_object.data.materials) == 0:
                    obj.data.materials.append(fillout_mat)

                obj.data.materials.append(wireframe_mat)
                bpy.context.active_object.active_material_index = b_tools.find_material_index(obj, wireframe_mat)

                wireframe_modifier = obj.modifiers.new(name='Wires', type='WIREFRAME')
                wireframe_modifier.use_even_offset = False
                wireframe_modifier.use_replace = False
                wireframe_modifier.material_offset = bpy.context.active_object.active_material_index
                wireframe_modifier.thickness = w_var.original_scene.slider_wt_modifier

        return wireframe_mat

    def add_wireframe_freestyle(self):
        """Enables and sets up freestyle wireframing in cycles.

        Returns:
            The linestyle data object used in the freestyle rendering.
        """
        scene = self.set_as_active()
        previous_area = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'
        self.select('SELECT', ['MESH'], ['ELSE'])

        for obj in scene.objects:
            if obj.select:
                scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                bpy.ops.mesh.mark_freestyle_edge()

                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

        scene.render.use_freestyle = True
        scene.render.layers.active = scene.render.layers[w_var.rlname]

        for n in scene.render.layers.active.freestyle_settings.linesets:
            scene.render.layers.active.freestyle_settings.linesets.remove(n)

        lineset = scene.render.layers.active.freestyle_settings.linesets.new('wires')
        lineset.select_edge_mark = True
        lineset.select_crease = False

        wire_color = w_var.original_scene.color_wire
        wire_thickness = w_var.original_scene.slider_wt_freestyle

        wire_color_rgb = wire_color[0:3]
        wire_color_alpha = wire_color[-1]

        linestyle = bpy.data.linestyles.new('wire_style')
        linestyle.color = wire_color_rgb
        linestyle.alpha = wire_color_alpha
        linestyle.thickness = wire_thickness

        scene.render.layers.active.freestyle_settings.linesets.active.linestyle = linestyle
        bpy.context.area.type = previous_area

        return linestyle

    def set_up_world_ao(self):
        """Sets up a new world with the ambient occlusion (AO) effect in cycles."""
        scene = self.set_as_active()

        new_world = bpy.context.blend_data.worlds.new('World of Wireframe')
        new_world.use_nodes = True
        new_world.node_tree.nodes[1].inputs[0].default_value = 1, 1, 1, 1
        new_world.light_settings.use_ambient_occlusion = True
        new_world.light_settings.ao_factor = 0.3

        for node in new_world.node_tree.nodes:
            node.select = False

        scene.world = new_world
