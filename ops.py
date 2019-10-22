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

from operator import attrgetter
from time import time

import bpy

from . import utils
from . import wirebomb


class WIREBOMB_OT_set_up(bpy.types.Operator):
    """Set up scene"""
    bl_label = "Set Up"
    bl_idname = 'wirebomb.set_up'

    def execute(self, context):
        start = time()
        wirebomb_scene = wirebomb.Wirebomb(context.scene)
        error_msg = wirebomb_scene.set_up_new()
        if error_msg:
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}

        self.report({'INFO'}, "Setup done in {} seconds!".format(round(time() - start, 3)))
        return {'FINISHED'}


def list_add_collection(scene, list_prop, collection):
    """
    Adds a collection to a list in the addon's UI.

    :param scene: The Blender scene.
    :param list_prop: Name of the property for the UI list, e.g. 'collections_affected'.
    :param collection: The collection to add to the list.
    """
    master_coll = scene.collection
    ui_list = getattr(scene.wirebomb, list_prop)

    if collection not in map(attrgetter('value'), ui_list):
        item = ui_list.add()
        # FIXME: See FIXME in ui.py
        if collection == master_coll:
            item.value = master_coll
            item.name = master_coll.name
        else:
            # not using item.name since it's not necessary, and hard to update when changed elsewhere
            item.value = collection

        setattr(scene.wirebomb, list_prop + '_active', len(ui_list) - 1)


def list_remove_collection(scene, list_prop, collection_index):
    """
    Removes a collection from one of the lists in the UI.

    :param scene: The Blender scene.
    :param list_prop: Name of the property for the UI list, e.g. 'collections_affected'.
    :param collection_index: Index of the collection to remove from the list.
    """
    ui_list = getattr(scene.wirebomb, list_prop)
    ui_list.remove(collection_index)

    # decrement active index if last was removed
    attr_active_index = list_prop + '_active'
    active_index = getattr(scene.wirebomb, attr_active_index)

    if len(ui_list) == active_index:
        setattr(scene.wirebomb, attr_active_index, active_index - 1)


# TODO: Handle warning in API:
# There is a known bug with using a callback,
# Python must keep a reference to the strings returned by the callback or Blender will misbehave or even crash.
def get_collections(_self, context):
    # according to docs, context may be None
    if not context:
        return ()
    master_coll = context.scene.collection
    scene_collections = utils.get_collection_hierarchy(master_coll)
    next(scene_collections)
    collection_tuples = [(master_coll.name, utils.SCENE_COLL_NAME, '', 'GROUP', 0)]
    collection_tuples.extend([(col.name, col.name, '', 'GROUP', i) for i, col in enumerate(scene_collections, 1)])
    return collection_tuples


class WIREBOMB_OT_add_collection(bpy.types.Operator):
    """Add a collection from this scene"""
    bl_label = "Add Collection"
    bl_idname = 'wirebomb.add_collection'
    bl_property = 'collection'

    list: bpy.props.StringProperty()
    collection: bpy.props.EnumProperty(items=get_collections)

    def invoke(self, context, _event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        list_add_collection(context.scene, self.list, utils.collection_from_name(context.scene, self.collection))
        return {'FINISHED'}


class WIREBOMB_OT_remove_collection(bpy.types.Operator):
    """Remove the selected collection"""
    bl_label = "Remove Collection"
    bl_idname = 'wirebomb.remove_collection'

    list: bpy.props.StringProperty()

    def execute(self, context):
        list_remove_collection(context.scene, self.list, getattr(context.scene.wirebomb, self.list + '_active'))
        return {'FINISHED'}


classes = (
    WIREBOMB_OT_set_up,
    WIREBOMB_OT_add_collection,
    WIREBOMB_OT_remove_collection,
)
register, unregister = bpy.utils.register_classes_factory(classes)
