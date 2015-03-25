# noinspection PyUnresolvedReferences
import bpy


class BlenderScene():
    """Contains useful functions and methods for modifying a scene.

    Attributes:
        name: The name of the scene.
    """

    def __init__(self, scene, new_scene, new_name, renderer):
        """Creates a copy of the scene if the 'New Scene' checkbox is checked.

        Args:
            new_name: A string representing the new scene's name.
            renderer: A string representing the new scene's render engine.
        """
        if new_scene:
            self.name = self.copy_scene(scene, new_name, renderer)
            self.parent_scene = scene

        else:
            self.name = scene.name

        self.space_data = None

    @staticmethod
    def copy_scene(scene, new_name='', renderer='CYCLES'):
        """Creates a full copy of the scene.

        Args:
            new_name: A string representing the new scene's name.
            renderer: A string representing the new scene's render engine, e.g. 'CYCLES'.

        Returns:
            A string that is the new scene's name.
        """
        bpy.context.screen.scene = scene

        # builds the new scene's name
        name = '{}_{}'.format(scene.name, new_name)
        bpy.ops.scene.new(type='FULL_COPY')
        bpy.context.scene.name = name
        bpy.data.scenes[name].render.engine = renderer

        return name

    def set_as_active(self):
        """Sets the scene as active.

        Returns:
            The scene object.
        """
        bpy.context.screen.scene = bpy.data.scenes[self.name]

        return bpy.data.scenes[self.name]

    def set_active_object(self, object_types=None):
        """Sets the active object to be one among the selected objects.

        Args:
            object_types: An optional list consisting of strings representing the object type(s)
                that the active object is allowed to be. If none specified, all types count.
        """
        scene = self.set_as_active()

        if object_types is None:
            object_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE',
                            'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER']

        for obj in scene.objects:
            if obj.select is True and obj.type in object_types:
                scene.objects.active = obj
                break

    def object_on_layer(self, obj, layer_numbers):
        """Checks if an object is on any of the layers represented by layer_numbers.

        Args:
            obj: The object it will check.
            layer_numbers: A list consisiting of integers representing the layers that it will check
                if the object is on.

        Returns:
            True if the object is on any of the layers represented by layer_numbers, else False.
        """
        scene = self.set_as_active()

        if obj in [e for e in scene.objects]:
            for n in layer_numbers:
                if obj.layers[n]:
                    return True

        return False

    def check_any_selected(self, object_types=None):
        """Checks the scene if any object is selected.

        Args:
            object_types: An optional list consisting of strings representing the object type(s)
                that the object is allowed to be. If none specified, all types count.
        """
        scene = self.set_as_active()

        if object_types is None:
            object_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE',
                            'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER']

        for obj in scene.objects:
            if obj.type in object_types and obj.select is True:
                return True

        return False

    def select(self, types, exclude_types=None, layers=None, exclude_layers=None, objects=None):
        """Selects objects.

        Selects objects by object types and layers. It can also select specific objects.

        Args:
            types: A list consisting of strings representing the object types that are to be selected.
            exclude_types: An optional list consisting of strings representing the object types that are to be
                deselected, these types will not be included among the select_types.
            layers: An optional list consisting of integers representing the layers whose objects
                are up for selection.
            exclude_layers: An optional list consisting of integers representing the layers whose objects
                will be deselected, these layers will not be included among the layer_numbers.
            objects: An optional list consisting of specific objects that are to be selected.
        """
        scene = self.set_as_active()
        all_layer_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        object_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE',
                        'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER']

        if objects is None:
            objects = []

        if exclude_types is None:
            exclude_types = []

        elif exclude_types == ['ELSE']:
            exclude_types = [x for x in object_types if x not in types]

        if layers is None or layers == ['EVERY']:
            layers = all_layer_numbers

        if exclude_layers is None:
            exclude_layers = []

        elif exclude_layers == ['ELSE']:
            exclude_layers = [x for x in all_layer_numbers if x not in layers]

        if types == ['ALL'] or types == ['OBJECT']:
            for obj in scene.objects:
                if (obj.type not in exclude_types and self.object_on_layer(obj, layers)
                        and not self.object_on_layer(obj, exclude_layers)):
                    obj.select = True

                elif obj.type in exclude_types or self.object_on_layer(obj, exclude_layers):
                    obj.select = False

        else:
            for obj in scene.objects:
                if obj in objects:
                    obj.select = True

                elif (obj.type in types and obj.type not in exclude_types
                      and self.object_on_layer(obj, layers)
                      and not self.object_on_layer(obj, exclude_layers)):
                    obj.select = True

                elif obj.type in exclude_types or self.object_on_layer(obj, exclude_layers):
                    obj.select = False

        self.set_active_object(types)

    def deselect(self, types, exclude_types=None, layers=None, exclude_layers=None, objects=None):
        """Deselects objects.

        Deselects objects by object types and layers. It can also deselect specific objects.

        Args:
            types: A list consisting of strings representing the object types that are to be deselected.
            exclude_types: An optional list consisting of strings representing the object types that are to be
                deselected, these types will not be included among the select_types.
            layers: An optional list consisting of integers representing the layers whose objects
                are up for deselection.
            exclude_layers: An optional list consisting of integers representing the layers whose objects
                will be deselected, these layers will not be included among the layer_numbers.
            objects: An optional list consisting of specific objects that are to be deselected.
        """
        scene = self.set_as_active()
        all_layer_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        object_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE',
                        'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER']

        if objects is None:
            objects = []

        if exclude_types is None:
            exclude_types = []

        elif exclude_types == ['ELSE']:
            exclude_types = [x for x in object_types if x not in types]

        if layers is None or layers == ['EVERY']:
            layers = all_layer_numbers

        if exclude_layers is None:
            exclude_layers = []

        elif exclude_layers == ['ELSE']:
            exclude_layers = [x for x in all_layer_numbers if x not in layers]

        if types == ['ALL'] or types == ['OBJECT']:
            for obj in scene.objects:
                if (obj.type not in exclude_types and self.object_on_layer(obj, layers)
                        and not self.object_on_layer(obj, exclude_layers)):
                    obj.select = False

        else:
            for obj in scene.objects:
                if obj in objects:
                    obj.select = False

                elif (obj.type in types and obj.type not in exclude_types
                      and self.object_on_layer(obj, layers)
                      and not self.object_on_layer(obj, exclude_layers)):
                    obj.select = False

        self.set_active_object(types)

    def move_selected_to_layer(self, to_layer):
        """Moves the selected objects to the given layer (to_layer).

        Args:
            to_layer: An integer representing the layer to which the objects will be moved.
        """
        scene = self.set_as_active()
        new_layers = [False, ] * 20
        new_layers[to_layer] = True

        for obj in scene.objects:
            if obj.select:
                obj.layers = new_layers

    def copy_selected_to_layer(self, to_layer):
        """Copies the selected objects to the given layer (to_layer).

        Args:
            to_layer: An integer representing the layer to which the objects will be copied.
        """
        scene = self.set_as_active()
        previous_layers = list(scene.layers)

        bpy.ops.object.duplicate()
        self.move_selected_to_layer(to_layer)
        self.select('DESELECT', ['ALL'], [to_layer])

        scene.layers = previous_layers

    def clear_all_materials(self):
        """Removes all materials from all the meshes in the scene."""
        scene = self.set_as_active()
        previous_layers = list(scene.layers)
        scene.layers = (True,) * 20

        self.select('SELECT', ['MESH'], ['ELSE'])
        bpy.context.object.data.materials.clear()
        bpy.ops.object.material_slot_copy()

        scene.layers = previous_layers

    def selected_objects_to_list(self, obj_types=None):
        """Puts all the selected objects in a list.

        Args:
            obj_types: An optional list consisting of strings representing the object types it will affect
                of the selected objects.

        Returns:
            A list with the selected objects.
        """
        scene = self.set_as_active()

        if obj_types is None:
            obj_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE',
                         'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER']

        selected_list = []

        for obj in scene.objects:
            if obj.select and obj.type in obj_types:
                selected_list.append(obj)

        return selected_list

    def set_up_rlayer(self, new, rlname, visible_layers=None, include_layers=None, mask_layers=None):
        """Sets up the scene's render layers.

        Args:
            new: A boolean which if True, a new render layer will be created. The name of this render layer is
                represented by rlname.
            rlname: A string representing the name of the render layer you want to set up.
            visible_layers: An optional list consisting of integers representing the layers you want to be visible
                -i.e. all layers you want to render, which also will be visible in the viewport-in the new render layer.
            include_layers: An optional list consisting of integers representing the layers
                you want to be included in the new render layer (specific for this render layer).
            mask_layers: An optional list consisting of integers representing the layers
                you want to be masked in the new render layer (specific for this render layer).
        """
        scene = self.set_as_active()
        layer_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

        if visible_layers is None:
            visible_layers = layer_numbers

        if include_layers is None:
            include_layers = layer_numbers

        if mask_layers is None:
            mask_layers = []

        if new:
            new_rlayer = scene.render.layers.new(rlname)
            scene.render.layers.active = new_rlayer

        for i in layer_numbers:
            if include_layers is not None:
                if i in include_layers:
                    scene.render.layers[rlname].layers[i] = True

                else:
                    scene.render.layers[rlname].layers[i] = False

            if visible_layers is not None:
                if i in visible_layers:
                    scene.layers[i] = True

                else:
                    scene.layers[i] = False

            if mask_layers is not None:
                if i in mask_layers:
                    scene.render.layers[rlname].layers_zmask[i] = True

                else:
                    scene.render.layers[rlname].layers_zmask[i] = False

    def set_area(self, area_name):
        """Sets the active screen area.

        Args:
            area_name: A string representing the name of the area you want to set, e.g. 'NODE_EDITOR'.
        """
        self.set_as_active()

        area = bpy.context.area
        # sets area
        area.type = area_name

        self.space_data = area.spaces.active

    def comp_show_backdrop(self):
        """Activates the backdrop function in the compositor."""
        self.set_as_active()

        area = bpy.context.area
        # saves the current area
        previous_area = area.type

        # change area and activate backdrop
        self.set_area('NODE_EDITOR')
        self.space_data.show_backdrop = True

        # changes back to the previous area
        area.type = previous_area