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

from collections import defaultdict
from itertools import chain
from operator import attrgetter

import bpy

from . import utils


class Wirebomb:
    def __init__(self, scene):
        self.scene = self.original_scene = scene
        self.wirebomb = scene.wirebomb
        self.meshes_affected = self.find_meshes_affected()
        self.progress = -1

    def begin_progress(self, min_val, max_val):
        bpy.context.window_manager.progress_begin(min_val, max_val)
        self.progress = min_val

    @staticmethod
    def end_progress():
        bpy.context.window_manager.progress_end()

    def update_progress(self, value):
        bpy.context.window_manager.progress_update(value)
        self.progress = value

    def increment_progress(self, step):
        bpy.context.window_manager.progress_update(self.update_progress(self.progress + step))

    def set_up_new(self):
        self.begin_progress(0, 101)
        error_msg = self.error_check()
        if error_msg:
            return error_msg

        if self.wirebomb.use_new_scene:
            self.copy_scene(self.wirebomb.new_scene_name)
        self.update_progress(26)

        if self.wirebomb.use_clear_materials:
            utils.clear_materials(self.meshes_affected)
        self.update_progress(48)

        if self.wirebomb.use_base:
            # sets up base material
            self.set_up_base_material()
        self.update_progress(64)

        if self.wirebomb.use_wireframe:
            # sets up wireframe
            wireframe_method = self.wirebomb.wireframe_method
            if wireframe_method == 'MODIFIER':
                self.set_up_wireframe_modifier()
            elif wireframe_method == 'FREESTYLE':
                self.set_up_wireframe_freestyle()
        self.update_progress(80)

        if self.wirebomb.use_ao:
            self.set_up_ao()
        self.end_progress()

        return None

    def copy_scene(self, new_scene_name):
        tag = 'wirebomb'

        # tagging all affected meshes to be able to track their copies in the new scene
        for obj in self.meshes_affected:
            obj[tag] = None

        bpy.ops.scene.new(type='FULL_COPY')
        new_scene = bpy.context.window.scene
        new_scene.name = new_scene_name

        # removing tags because no longer needed
        for obj in self.meshes_affected:
            del obj[tag]

        # storing the tagged copies
        new_meshes_affected = []

        for obj in [obj for obj in new_scene.objects if tag in obj]:
            del obj[tag]
            new_meshes_affected.append(obj)

        self.meshes_affected = new_meshes_affected
        self.scene = new_scene
        self.wirebomb = new_scene.wirebomb

    def set_up_ao(self):
        self.scene.eevee.use_gtao = True
        bpy.context.window.view_layer.use_pass_ambient_occlusion = True
        self.set_up_world_ao()
        self.set_up_comp_ao()

    def set_up_comp_ao(self):
        """Sets up the compositor nodes for the ambient occlusion (AO) effect."""
        if not self.scene.use_nodes:
            self.scene.use_nodes = True
            if self.wirebomb.use_new_scene:
                # this addresses weird edge case where if nodes weren't used,
                # view layer nodes are not automatically updated to use the new scene instead of the original
                # (possibly a Blender bug)
                for node in [node for node in self.scene.node_tree.nodes
                             if node.type == 'R_LAYERS' and node.scene is self.original_scene]:
                    node.scene = self.scene

        tree = self.scene.node_tree

        v_layer_nodes_links = defaultdict(list)
        for link in tree.links:
            # only care about view layer nodes whose image socket has some link
            if link.from_node.type == 'R_LAYERS' and link.from_socket.identifier == 'Image':
                v_layer_nodes_links[link.from_node].append(link)

        group_tree = bpy.data.node_groups.new('AO Effect', 'CompositorNodeTree')
        node_group = tree.nodes.new('CompositorNodeGroup')
        node_group.node_tree = group_tree

        group_outputs = group_tree.nodes.new('NodeGroupOutput')
        group_outputs.location.x = 400
        group_inputs = group_tree.nodes.new('NodeGroupInput')
        group_inputs.location.x = -400
        fac_socket_name = 'Fac'
        group_tree.inputs.new('NodeSocketFloatFactor', fac_socket_name)
        group_tree.inputs[fac_socket_name].min_value = 0
        group_tree.inputs[fac_socket_name].max_value = 1
        node_group.inputs[fac_socket_name].default_value = 0.730

        y_location = 0

        for node_n, (node_v_layer, links) in enumerate(v_layer_nodes_links.items()):
            # creating mix node
            node_mix = group_tree.nodes.new('CompositorNodeMixRGB')
            node_mix.blend_type = 'MULTIPLY'
            node_mix.location.y = y_location
            y_location -= 200

            # linking mix factor
            group_tree.links.new(group_inputs.outputs[fac_socket_name], node_mix.inputs['Fac'])

            # unique i/o socket names
            image_socket_name = 'Image ' + str(node_n)
            ao_socket_name = 'AO ' + str(node_n)

            # linking view layer image
            group_tree.inputs.new('NodeSocketColor', image_socket_name)
            group_tree.outputs.new('NodeSocketColor', image_socket_name)
            tree.links.new(node_v_layer.outputs['Image'], node_group.inputs[image_socket_name])
            group_tree.links.new(group_inputs.outputs[image_socket_name], node_mix.inputs[1])
            group_tree.links.new(node_mix.outputs['Image'], group_outputs.inputs[image_socket_name])

            for link in links:
                tree.links.new(node_group.outputs[image_socket_name], link.to_socket)

            # linking view layer AO
            group_tree.inputs.new('NodeSocketFloatFactor', ao_socket_name)
            tree.links.new(node_v_layer.outputs['AO'], node_group.inputs[ao_socket_name])
            group_tree.links.new(group_inputs.outputs[ao_socket_name], node_mix.inputs[2])

        for node in chain(tree.nodes, group_tree.nodes):
            node.select = False

    def set_up_base_material(self):
        """Adds base material to affected meshes and saves material name."""
        base_mat = self.set_up_material("Base", self.wirebomb.material_base)

        for obj in self.meshes_affected:
            mat_index = len(obj.data.materials)
            obj.data.materials.append(base_mat)

            for polygon in obj.data.polygons:
                polygon.material_index = mat_index

    def set_up_material(self, name, material_props):
        # if the user selected a material, use it
        if material_props.mode == 'EXISTING':
            material = material_props.material

        # else, create a new one with the color selected
        else:
            material = utils.create_basic_material(name, material_props.color)
            node_tree = material.node_tree

            # driving all color channels
            driving_prop = material_props.color.path_from_id()
            for i in range(4):
                self.add_driver(driving_prop, material, 'diffuse_color', i, i)
                self.add_driver(driving_prop, node_tree, 'nodes["color"].inputs[0].default_value', i, i)
            # 3 = alpha channel index
            self.add_driver(driving_prop, material.node_tree, 'nodes["alpha"].inputs[0].default_value', 3)

        return material

    def add_driver(self, driving_prop, driven_id, driven_prop, driving_index=-1, driven_index=-1):
        driver = driven_id.driver_add(driven_prop, driven_index).driver
        driver.type = 'AVERAGE'  # any except for 'SCRIPTED' since no need for expression
        var = driver.variables.new()
        target = var.targets[0]
        target.id_type = 'SCENE'
        target.id = self.scene
        target.data_path = driving_prop if driving_index == -1 else f'{driving_prop}[{driving_index}]'

    def set_up_wireframe_modifier(self):
        wireframe_mat = self.set_up_material("Wireframe", self.wirebomb.material_wireframe)

        for obj in self.meshes_affected:
            modifier_wireframe = obj.modifiers.new(name='Wireframe', type='WIREFRAME')
            modifier_wireframe.use_even_offset = False  # causes spikes on some models
            modifier_wireframe.use_replace = False
            self.add_driver(self.wirebomb.path_from_id('thickness_modifier'), modifier_wireframe, 'thickness')

            obj.data.materials.append(wireframe_mat)
            modifier_wireframe.material_offset = len(obj.material_slots) - 1

    def set_up_wireframe_freestyle(self):
        wireframe_coll = bpy.data.collections.new('Wireframe')
        for obj in self.meshes_affected:
            wireframe_coll.objects.link(obj)
            for edge in obj.data.edges:
                edge.use_freestyle_mark = True

        self.scene.render.use_freestyle = True

        linestyle = bpy.data.linestyles.new('WireStyle')
        self.add_driver(self.wirebomb.path_from_id('thickness_freestyle'), linestyle, 'thickness')
        driving_color_prop = self.wirebomb.material_wireframe.path_from_id('color')
        for i in range(3):
            self.add_driver(driving_color_prop, linestyle, 'color', i, i)
        self.add_driver(driving_color_prop, linestyle, 'alpha', 3)

        for v_layer in self.scene.view_layers:
            line_sets = v_layer.freestyle_settings.linesets
            for line_set in line_sets:
                line_set.show_render = False
            line_set = line_sets.new('Wireframe')

            # edge types settings
            line_set.select_border = False
            line_set.select_crease = False
            line_set.select_edge_mark = True

            # collection settings
            line_set.select_by_collection = True
            line_set.collection = wireframe_coll

            line_set.linestyle = linestyle

    def set_up_world_ao(self):
        """Sets up a new world with AO."""
        new_world = bpy.data.worlds.new('World of Wirebomb')
        new_world.light_settings.use_ambient_occlusion = True
        new_world.light_settings.ao_factor = 0.3
        new_world.use_nodes = True
        new_world.node_tree.nodes[1].inputs[0].default_value = (1, 1, 1, 1)

        for node in new_world.node_tree.nodes:
            node.select = False

        self.scene.world = new_world

    def find_meshes_affected(self):
        """Finds and returns all affected meshes."""
        meshes_affected = set()

        if self.wirebomb.affect_mode == 'EXCLUSIVE':
            meshes_affected = {o for o in self.scene.objects if o.type == 'MESH'}

        update_method = 'update' if self.wirebomb.affect_mode == 'INCLUSIVE' else 'difference_update'
        update_meshes_affected = getattr(meshes_affected, update_method)

        if self.wirebomb.use_affect_selected:
            previous_area = bpy.context.area.type
            bpy.context.area.type = 'VIEW_3D'
            update_meshes_affected(o for o in self.scene.objects if o.select_get() and o.type == 'MESH')
            bpy.context.area.type = previous_area
        if self.wirebomb.use_affect_collections:
            for coll in map(attrgetter('value'), self.wirebomb.collections_affected):
                update_meshes_affected(o for o in coll.all_objects if o.type == 'MESH')

        return meshes_affected

    def error_check(self):
        """
        Checks for user configuration errors.

        :return: A string holding error messages. The string is empty iff there was no error.
        """
        error_msg = ""

        if (self.wirebomb.use_wireframe and self.wirebomb.material_wireframe.mode == 'EXISTING'
                and not self.wirebomb.material_wireframe.material):
            error_msg += '- No wireframe material selected.\n'

        if (self.wirebomb.use_base and self.wirebomb.material_base.mode == 'EXISTING'
                and not self.wirebomb.material_base.material):
            error_msg += '- No base material selected.\n'

        return error_msg.rstrip()


register, unregister = bpy.utils.register_classes_factory(())
