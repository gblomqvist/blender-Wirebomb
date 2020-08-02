#  Copyright (C) 2020  Gustaf Blomqvist
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# <pep8 compliant>

import bpy

# name of the master collection used in the UI
SCENE_COLL_NAME = 'Scene Collection'


def get_collection_hierarchy(root_collection):
    """
    Yields the root collection and all its children recursively.

    :param root_collection: The topmost collection to yield.
    :return: Yields the root collection and all its children, one collection at a time.
    """
    yield root_collection
    for collection in root_collection.children:
        yield from get_collection_hierarchy(collection)


def create_basic_material(name, rgba):
    # separating rgb and alpha
    color_rgb = rgba[0:3]
    color_alpha = rgba[-1]
    material = bpy.data.materials.new(name)

    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()

    # creating the nodes
    node_transparent = tree.nodes.new('ShaderNodeBsdfTransparent')
    node_transparent.location = -300, 100

    node_diffuse = tree.nodes.new('ShaderNodeBsdfDiffuse')
    node_diffuse.location = -300, -100
    node_diffuse.inputs[0].default_value = color_rgb + (1.0,)
    node_diffuse.name = 'color'  # referencing to this ID in the real-time change

    node_mix_shader = tree.nodes.new('ShaderNodeMixShader')
    node_mix_shader.location = 0, 50
    node_mix_shader.inputs[0].default_value = color_alpha
    node_mix_shader.name = 'alpha'  # referencing to this ID in the real-time change

    node_output = tree.nodes.new('ShaderNodeOutputMaterial')
    node_output.location = 300, 50

    # connecting the nodes
    tree.links.new(node_transparent.outputs[0], node_mix_shader.inputs[1])
    tree.links.new(node_diffuse.outputs[0], node_mix_shader.inputs[2])
    tree.links.new(node_mix_shader.outputs[0], node_output.inputs[0])

    for node in tree.nodes:
        node.select = False

    # sets the viewport color
    material.diffuse_color = color_rgb + (1.0,)

    return material


def clear_materials(meshes):
    """
    Clears materials from given meshes.

    :param meshes: The meshes whose materials to clear.
    """
    for obj in meshes:
        obj.data.materials.clear()


def collection_from_name(scene, coll_name):
    if coll_name == scene.collection.name:
        collection = scene.collection
    else:
        collection = bpy.data.collections.get(coll_name)

    return collection


register, unregister = bpy.utils.register_classes_factory(())
