# noinspection PyUnresolvedReferences
import bpy
import constants


class BlenderScene:
    """Contains useful functions and methods for modifying a scene.

    Attributes:
        name: The name of the scene.
    """

    def __init__(self, scene, new_scene, new_name=None, renderer='CYCLES'):
        """Creates a full copy of scene if new_scene is set to True.

        Args:
            scene: A scene object which represents the scene to start from.
            new_scene: A boolean that if True, a full copy of scene will be created.
            new_name: An optional string representing the name for the (new) scene. Must be given if new_scene is set
                to True.
            renderer: A string representing the (new) scene's render engine, e.g. 'CYCLES'.
        """
        if new_scene:
            self.name = self.copy_scene(scene, new_name, renderer)

        else:
            if new_name is not None:
                scene.name = new_name
            self.name = scene.name

        self.space_data = None

    @staticmethod
    def copy_scene(scene, new_name, renderer='CYCLES'):
        """Creates a full copy of the scene.

        Args:
            scene: A scene object which represents the scene to copy.
            new_name: A string representing the new scene's name.
            renderer: A string representing the new scene's render engine, e.g. 'CYCLES'.

        Returns:
            A string that is the new scene's name.
        """
        bpy.context.screen.scene = scene
        bpy.ops.scene.new(type='FULL_COPY')
        bpy.context.screen.scene.name = new_name
        bpy.data.scenes[new_name].render.engine = renderer

        return new_name

    def set_as_active(self):
        """Sets the scene as active.

        Returns:
            The scene object.
        """
        current_scene = bpy.data.scenes[self.name]
        bpy.context.screen.scene = current_scene

        return current_scene

    def set_active_object(self, obj_types=constants.obj_types):
        """Sets the active object to be one among the selected objects.

        Args:
            obj_types: An optional sequence consisting of strings representing the object type(s)
                that the active object is allowed to be. If none specified, all types count.
        """
        scene = self.set_as_active()
        # TODO: Should I do like this and keep 'ALL'?
        if obj_types == ['ALL']:
            obj_types = constants.obj_types

        for obj in scene.objects:
            if obj.select is True and obj.type in obj_types:
                scene.objects.active = obj
                break

    def object_on_layer(self, obj, layer_numbers):
        """Checks if an object is on any of the layers represented by layer_numbers.

        Args:
            obj: The object it will check.
            layer_numbers: A list consisiting of integers representing the layers that it will check
                if the object is on.

        Returns:
            True if the object is on any of the layers represented by layer_numbers, False otherwise.
        """
        scene = self.set_as_active()

        if obj in [e for e in scene.objects]:
            for n in layer_numbers:
                if obj.layers[n]:
                    return True

        return False

    def check_any_selected(self, obj_types=constants.obj_types):
        """Checks the scene if any object is selected.

        Args:
            obj_types: An optional sequence consisting of strings representing the object type(s)
                that the object is allowed to be. If none specified, all types count.

        Returns:
            True if any object is selected, False otherwise.
        """
        scene = self.set_as_active()

        for obj in scene.objects:
            if obj.type in obj_types and obj.select is True:
                return True

        return False

    def select(self, mode, types=None, types_excluded=None, layers=None, layers_excluded=None, objects=None):
        """Selects or deselects objects.

        (De)selects specific objects or objects by object types and layers.

        Args:
            mode: A string representing the mode, either 'SELECT' to select objects or 'DESELECT' to deselect objects.
            types: An optional set consisting of strings representing the object types that are to be (de)selected.
                If none specified, objects variable needs to be set.
            types_excluded: An optional set consisting of strings representing the object types that are to be
                deselected or left out if mode is set to 'DESELECT', these types will not be included among the
                select_types.
            layers: An optional set consisting of integers representing the layers whose objects
                are up for (de)selection.
            layers_excluded: An optional set consisting of integers representing the layers whose objects
                will be deselected or left out if mode is set to 'DESELECT', these layers will not be included among
                the layer_numbers.
            objects: An optional sequence consisting of specific objects that are to be (de)selected, need to be set if
                types variable is not set. If set, types variable will not matter.
        """
        scene = self.set_as_active()
        layer_numbers = constants.layer_numbers
        obj_types = set(constants.obj_types)

        # setting up types and types excluded
        if types is None:
            types = set()
        elif types == {'ALL'}:
            types = obj_types

        if types_excluded is None:
            types_excluded = set()
        elif types_excluded == {'ELSE'}:
            types_excluded = obj_types - types

        types = types - types_excluded

        # setting up layers and layers excluded
        if layers is None or layers == {'ALL'}:
            layers = layer_numbers

        if layers_excluded is None:
            layers_excluded = set()
        elif layers_excluded == {'ELSE'}:
            layers_excluded = layer_numbers - layers

        layers = layers - layers_excluded

        if objects is None:
            objects = set()

        previous_area = bpy.context.area.type

        # can't be in 'PROPERTY' space when changing object select property
        bpy.context.area.type = 'VIEW_3D'

        if mode == 'SELECT':
            if len(objects) > 0:
                for obj in scene.objects:
                    if obj in objects:
                        obj.select = True
            else:
                for obj in scene.objects:
                    if obj.type in types and self.object_on_layer(obj, layers):
                        obj.select = True
                    elif obj.type in types_excluded or self.object_on_layer(obj, layers_excluded):
                        obj.select = False

        elif mode == 'DESELECT':
            if len(objects) > 0:
                for obj in scene.objects:
                    if obj in objects:
                        obj.select = False
            else:
                for obj in scene.objects:
                    if obj.type in types and self.object_on_layer(obj, layers):
                        obj.select = False

        else:
            raise ValueError("Error: No such mode as '{}'.".format(mode))

        bpy.context.area.type = previous_area
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
        previous_area = bpy.context.area.type

        bpy.context.area.type = 'VIEW_3D'
        bpy.ops.object.duplicate()
        self.move_selected_to_layer(to_layer)

        bpy.context.area.type = previous_area
        scene.layers = previous_layers

    def clear_all_materials(self):
        """Removes all materials from all the meshes in the scene."""
        scene = self.set_as_active()
        previous_layers = list(scene.layers)
        scene.layers = (True,) * 20

        self.select('SELECT', {'MESH'}, {'ELSE'})
        bpy.context.active_object.data.materials.clear()
        bpy.ops.object.material_slot_copy()

        scene.layers = previous_layers

    def selected_objects_to_list(self, obj_types=constants.obj_types):
        """Puts all the selected objects in a list.

        Args:
            obj_types: An optional sequence consisting of strings representing the object type(s) it will affect
                of the selected objects. If none specified, all types count.

        Returns:
            A list with the selected objects.
        """
        scene = self.set_as_active()
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
        layer_numbers = constants.layer_numbers

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

    def view3d_pivotpoint(self, action, pivotpoint=None):
        """Manipulates the 3D view's pivot point by setting it or getting it.

        Args:
            action: A string representing the action. Either 'set' to set the pivot point
                or 'get' to get the current pivot point.
            pivotpoint: If action equals 'set', this string represents the pivot point you want to set.

        Returns:
            If action equals 'get', returns a string representing the 3D view's current pivot point.
        """
        self.set_as_active()
        previous_area = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'

        if action == 'set':
            bpy.context.space_data.pivot_point = pivotpoint
            bpy.context.area.type = previous_area

        elif action == 'get':
            pivotpoint = bpy.context.space_data.pivot_point
            bpy.context.area.type = previous_area
            return pivotpoint
