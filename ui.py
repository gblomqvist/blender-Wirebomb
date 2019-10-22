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

from . import ops
from . import ui_presets
from . import utils


def update_list_collection(scene, list_prop):
    collections = getattr(scene.wirebomb, list_prop)
    if collections:
        # FIXME: For some reason, the master collection data block fails to save with the file in a CollectionItem
        #  (saves as None in Blender 2.82a). This will do until the issue is fixed in Blender.
        for collection in collections:
            if collection.name == scene.collection.name:
                collection.value = scene.collection

        indexes_of_removed = [i for i, collection in enumerate(collections) if collection.value is None]

        for i in indexes_of_removed:
            ops.list_remove_collection(scene, list_prop, i)


@bpy.app.handlers.persistent
def update_list_affected(scene):
    update_list_collection(scene, 'collections_affected')


class WIREBOMB_UL_collections(bpy.types.UIList):
    @staticmethod
    def draw_item(_self, context, layout, _data, item, _icon, _active_data):
        if item.value:
            text = item.value.name if item.value != context.scene.collection else utils.SCENE_COLL_NAME
            layout.label(text=text, icon='GROUP')
        else:
            # this should only happen if someone has removed the list's app handler
            bpy.app.timers.register(lambda: update_list_affected(context.scene), first_interval=0)

            if update_list_affected not in bpy.app.handlers.depsgraph_update_pre:
                bpy.app.handlers.depsgraph_update_pre.append(update_list_affected)

            layout.label(text='...')


class WIREBOMB_PT_main(bpy.types.Panel):
    """The top-level panel."""
    bl_label = "Wirebomb"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw_header(self, _context):
        layout = self.layout
        layout.label(icon='SHADING_WIRE')

    def draw(self, context):
        wirebomb = context.scene.wirebomb
        layout = self.layout
        layout.use_property_split = True

        layout.operator(operator=ops.WIREBOMB_OT_set_up.bl_idname, icon='SHADING_WIRE')

        grid = layout.grid_flow()
        grid.prop(wirebomb, property='use_ao')
        grid.prop(wirebomb, property='use_clear_materials')


class WIREBOMB_PT_new_scene(bpy.types.Panel):
    bl_label = " "
    bl_parent_id = WIREBOMB_PT_main.__name__
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 0

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.wirebomb, property='use_new_scene')

    def draw(self, context):
        wirebomb = context.scene.wirebomb
        layout = self.layout
        layout.active = wirebomb.use_new_scene
        layout.use_property_split = True

        layout.prop(wirebomb, property='new_scene_name')


class WIREBOMB_PT_mesh_selection(bpy.types.Panel):
    bl_label = "Mesh Selection"
    bl_parent_id = WIREBOMB_PT_main.__name__
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = set()
    bl_order = 1

    def draw(self, context):
        wirebomb = context.scene.wirebomb
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.use_property_split = False
        row.prop(wirebomb, property='affect_mode', expand=True)

        layout.prop(wirebomb, property='use_affect_selected')


class WIREBOMB_PT_collections(bpy.types.Panel):
    bl_label = " "
    bl_parent_id = WIREBOMB_PT_mesh_selection.__name__
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.wirebomb, property='use_affect_collections')

    def draw(self, context):
        wirebomb = context.scene.wirebomb
        layout = self.layout
        layout.active = wirebomb.use_affect_collections
        row = layout.row()
        row.template_list(WIREBOMB_UL_collections.__name__,
                          '',
                          wirebomb,
                          'collections_affected',
                          wirebomb,
                          'collections_affected_active',
                          rows=3)

        sub = row.column(align=True)
        sub.operator(ops.WIREBOMB_OT_add_collection.bl_idname, text='', icon='ADD').list = 'collections_affected'
        sub_sub = sub.row()
        sub_sub.operator(ops.WIREBOMB_OT_remove_collection.bl_idname, text='',
                         icon='REMOVE').list = 'collections_affected'
        sub_sub.enabled = bool(wirebomb.collections_affected)


class WIREBOMB_PT_wireframe(bpy.types.Panel):
    bl_label = " "
    bl_parent_id = WIREBOMB_PT_main.__name__
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = set()
    bl_order = 2

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.wirebomb, property='use_wireframe')

    def draw(self, context):
        wirebomb = context.scene.wirebomb
        layout = self.layout
        layout.active = wirebomb.use_wireframe
        layout.use_property_split = True
        layout.prop(wirebomb, property='wireframe_method', expand=True)


class WIREBOMB_PT_wireframe_thickness(bpy.types.Panel):
    bl_label = "Thickness"
    bl_parent_id = WIREBOMB_PT_wireframe.__name__
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = set()
    bl_order = 0

    def draw_header_preset(self, _context):
        ui_presets.WIREBOMB_PT_wireframe_thickness_presets.draw_panel_header(self.layout)

    def draw(self, context):
        wirebomb = context.scene.wirebomb
        layout = self.layout
        layout.active = wirebomb.use_wireframe
        layout.use_property_split = True

        prop = 'thickness_freestyle' if wirebomb.wireframe_method == 'FREESTYLE' else 'thickness_modifier'
        layout.prop(wirebomb, property=prop)


class WIREBOMB_PT_wireframe_material(bpy.types.Panel):
    bl_label = "Material"
    bl_parent_id = WIREBOMB_PT_wireframe.__name__
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = set()
    bl_order = 1

    def draw_header_preset(self, _context):
        ui_presets.WIREBOMB_PT_wireframe_material_presets.draw_panel_header(self.layout)

    def draw(self, context):
        wirebomb = context.scene.wirebomb
        layout = self.layout
        layout.active = wirebomb.use_wireframe
        layout.use_property_split = True

        if wirebomb.wireframe_method == 'MODIFIER':
            row = layout.row()
            row.use_property_split = False
            row.prop(wirebomb.material_wireframe, property='mode', expand=True)

        if wirebomb.material_wireframe.mode == 'COLOR' or wirebomb.wireframe_method == 'FREESTYLE':
            # wireframe color
            layout.prop(wirebomb.material_wireframe, property='color')
        else:
            # wireframe material
            layout.prop_search(wirebomb.material_wireframe, 'material', bpy.data, 'materials')


class WIREBOMB_PT_base_material(bpy.types.Panel):
    bl_label = " "
    bl_parent_id = WIREBOMB_PT_main.__name__
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = set()
    bl_order = 3

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.wirebomb, property='use_base')

    def draw_header_preset(self, _context):
        ui_presets.WIREBOMB_PT_base_material_presets.draw_panel_header(self.layout)

    def draw(self, context):
        wirebomb = context.scene.wirebomb
        layout = self.layout
        layout.active = wirebomb.use_base
        layout.use_property_split = True

        row = layout.row()
        row.use_property_split = False
        row.prop(wirebomb.material_base, property='mode', expand=True)

        if wirebomb.material_base.mode == 'COLOR':
            # base color
            layout.prop(wirebomb.material_base, property='color')
        else:
            # base material
            layout.prop_search(wirebomb.material_base, 'material', bpy.data, 'materials')


classes = (
    WIREBOMB_UL_collections,
    WIREBOMB_PT_main,
    WIREBOMB_PT_new_scene,
    WIREBOMB_PT_mesh_selection,
    WIREBOMB_PT_collections,
    WIREBOMB_PT_wireframe,
    WIREBOMB_PT_wireframe_thickness,
    WIREBOMB_PT_wireframe_material,
    WIREBOMB_PT_base_material,
)
register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    register_classes()
    bpy.app.handlers.depsgraph_update_pre.append(update_list_affected)


def unregister():
    bpy.app.handlers.depsgraph_update_pre.remove(update_list_affected)
    unregister_classes()
