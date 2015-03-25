from .bscene import BlenderScene
from . import wvariables


class BlenderSceneW(BlenderScene):
    """A version of the class BlenderScene that is specific for this add-on."""

    def select(self, mode, types, exclude_types=None, layers=None, exclude_layers=None, objects=None):
        """Selects or deselects objects, a special version of BlenderScene's select and deselect functions.

        Args:
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
                layers = wvariables.affected_layers_numbers

            else:
                layers = all_layer_numbers

        elif layers == ['EVERY']:
            layers = all_layer_numbers

        if wvariables.original_scene.CheckboxOnlySelected:
            objects = wvariables.only_selected

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

            elif len(objects) > 0:
                for obj in scene.objects:
                    if obj in objects:
                        obj.select = True

            else:
                for obj in scene.objects:
                    if (obj.type in types and obj.type not in exclude_types
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

            elif len(objects) > 0:
                for obj in scene.objects:
                    if obj in objects:
                        obj.select = False

            else:
                for obj in scene.objects:
                    if (obj.type in types and obj.type not in exclude_types
                        and self.object_on_layer(obj, layers)
                            and not self.object_on_layer(obj, exclude_layers)):
                        obj.select = False

        else:
            return "Error: No such mode as '{}'.".format(mode)

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
            visible_layers = wvariables.all_layers_used_numbers

        if include_layers is None:
            include_layers = wvariables.all_layers_used_numbers

        if mask_layers is None:
            mask_layers = []

        if wvariables.original_scene.CheckboxClearRLayers:
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

        if wvariables.rlname is None:
            wvariables.rlname = new_rlayer.name

        # only used for blender internal wireframe, two scenes --> two render layer names
        else:
            wvariables.rlname_2 = new_rlayer.name

        # there needs to be two render layers for freestyle compositing
        if (wvariables.original_scene.CheckboxComp
                and wvariables.original_scene.WireframeType == 'WIREFRAME_FREESTYLE'):
            new_rlayer = scene.render.layers.new(rlname_other)
            wvariables.rlname_other = new_rlayer.name

        if wvariables.original_scene.CheckboxUseAO:
            scene.render.layers[rlname].use_pass_ambient_occlusion = True

            if (wvariables.original_scene.CheckboxComp
                    and wvariables.original_scene.WireframeType == 'WIREFRAME_FREESTYLE'):
                scene.render.layers[rlname_other].use_pass_ambient_occlusion = True

        for i in layer_numbers:
            if (wvariables.original_scene.CheckboxComp
                    and wvariables.original_scene.WireframeType == 'WIREFRAME_FREESTYLE'):
                if wvariables.other_layers_numbers is not None:
                    if i in wvariables.other_layers_numbers:
                        scene.render.layers[rlname].layers_zmask[i] = True
                        scene.render.layers[rlname_other].layers[i] = True

                    else:
                        scene.render.layers[rlname].layers_zmask[i] = False
                        scene.render.layers[rlname_other].layers[i] = False

                if wvariables.affected_layers_numbers is not None:
                    if i in wvariables.affected_layers_numbers:
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