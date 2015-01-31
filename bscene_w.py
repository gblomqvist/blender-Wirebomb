from .bscene import BlenderScene


class BlenderSceneW(BlenderScene):
    """A version of the class BlenderScene that is specific for this add-on."""

    def select(self, scene_instance, mode, types, exclude_types=None, layers=None, exclude_layers=None, objects=None):
        """Selects or deselects objects, a special version of BlenderScene's select and deselect functions.

        The difference is that this one is specific for this add-on.

        Args:
            scene_instance: An instance of the class BlenderSceneW.
            mode: A string representing the mode, either 'SELECT' or 'DESELECT'.
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

        if layers is None:
            if types != ['ALL'] and types != ['OBJECT']:
                layers = BlenderSceneW.affected_layers_numbers

        elif layers == ['EVERY']:
            layers = all_layer_numbers

        if BlenderSceneW.original_scene.CheckboxOnlySelected:
            objects = BlenderSceneW.only_selected

        elif objects is None:
            objects = []

        if exclude_types is None:
            exclude_types = []

        elif exclude_types == ['ELSE']:
            exclude_types = [x for x in object_types if x not in types]

        if exclude_layers is None:
            exclude_layers = []

        elif exclude_layers == ['ELSE']:
            exclude_layers = [x for x in all_layer_numbers if x not in layers]

        if mode == 'SELECT':
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

        elif mode == 'DESELECT':
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

        else:
            return "Error: No such mode as '{}'.".format(mode)

        self.set_active_object(types)