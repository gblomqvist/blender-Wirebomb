# noinspection PyUnresolvedReferences
import bpy
from . import b_tools
from . import w_var


def set_layers_used():
    """Sets all layers who will be affected by this add-on to a list.

    Returns:
        A list with booleans representing all the layers that will be affected by this add-on.
    """
    layers_used = [False, ]*20

    if w_var.cb_only_selected:
        for obj in bpy.context.scene.objects:
            if obj.select:
                layers_used = b_tools.manipulate_layerlists('add', layers_used, obj.layers)

        layers_used = b_tools.manipulate_layerlists('add', layers_used, w_var.original_scene.layers_other)

    else:
        layers_used = b_tools.manipulate_layerlists('add', w_var.original_scene.layers_affected,
                                                    w_var.original_scene.layers_other)

    return layers_used


def set_layers_affected():
    """Sets all layers who will be affected by wireframing and/or clay material to a list.

    Returns:
        A list with booleans representing all the layers that will be affected affected by
            wireframing and/or clay material.
    """
    layers_affected = [False, ]*20

    if w_var.cb_only_selected:
        for obj in bpy.context.scene.objects:
            if obj.select:
                layers_affected = b_tools.manipulate_layerlists('add', layers_affected, obj.layers)

    else:
        layers_affected = list(w_var.original_scene.layers_affected)

    return layers_affected


def set_layers_other():
    """Sets all layers who will be included in the render layer just as they are in a list.

    Returns:
        A list with booleans representing all the layers that will be included in the render layer-just as they are.
    """
    layers_other = list(w_var.original_scene.layers_other)
    
    for index in range(0, 20):
        if layers_other[index] and w_var.original_scene.layers_affected[index]:
            layers_other[index] = False

    return layers_other
