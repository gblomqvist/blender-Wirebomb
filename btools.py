# noinspection PyUnresolvedReferences
import bpy


def object_on_layer(scene, obj, layer_numbers):
        """Checks if an object is on any of the layers represented by layer_numbers.

        Args:
            scene: The scene it will look in.
            obj: The object it will check.
            layer_numbers: A list consisiting of integers representing the layers that it will check
                if the object is on.

        Returns:
            True if the object is on any of the layers represented by layer_numbers, else False.
        """
        if obj in [e for e in scene.objects]:
            for n in layer_numbers:
                if obj.layers[n]:
                    return True

        return False


def check_any_selected(scene, object_types=None):
    """Checks the scene if any object is selected.

    Args:
        scene: The scene to be checked.
        object_types: An optional list consisting of strings representing the object type(s)
            that the object is allowed to be. If none specified, all types count.
    """
    if object_types is None:
        object_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE',
                        'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER']

    for obj in scene.objects:
        if obj.type in object_types and obj.select is True:
            return True

    return False


def layerlist_to_numberlist(layer_list):
    """Converts a layer list to a number list.

    Converts a layer list consisting of booleans to a number list consisting of integers,
    representing the layers that are True in layer_list.

    Example:
        >>> print(layerlist_to_numberlist[False, True, False, False, True])
        [1, 4]

        This because layer 2 (index 1) and layer 3 (index 4) are both True.

    Args:
        layers: A list with booleans representing which layers are True and which are not.
            The first item represents the first layer and so on.

    Returns:
        A list consisting of integers representing the layers that are True in layer_list.
    """
    number_list = []

    for i in range(0, 20):
        if layer_list[i]:
            number_list.append(i)

    return number_list


def find_material_index(obj, material):
    """Finds the material slot index of a material in an object.

    Args:
        obj: The object it will look through.
        material: The material whose material slot index you want.

    Returns:
        An integer representing the material's material slot index in the object.
    """
    mat_index = 0

    for mat in obj.data.materials:
        if mat == material:
            break

        mat_index += 1

    return mat_index


def add_layerlists(list1, list2):
    """Combines two layer lists into one.

    Example:
        >>> print(add_layerlists([False, True, True, False], [True, True, False, False]))
        [True, True, True, False]

    Args:
        list1: One of the layer lists you want to combine.
        list2: The other one of the layer lists you want to combine.

    Returns:
        The combined layer list.
    """
    added_layers = []

    for i in range(20):
        if list1[i] is True or list2[i] is True:
            added_layers.append(True)

        else:
            added_layers.append(False)

    return added_layers