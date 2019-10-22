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


def gen_material_props(default_color):
    class MaterialData(bpy.types.PropertyGroup):
        mode: bpy.props.EnumProperty(
            items=[('COLOR', 'New From Color', 'Create a new material from the specified color'),
                   ('EXISTING', 'Existing', 'Choose an existing material')],
            name='Source',
            description="Material source",
            default='COLOR',
            options=set(),
        )
        color: bpy.props.FloatVectorProperty(
            name='Color',
            subtype='COLOR',
            min=0,
            max=1,
            size=4,
            default=default_color,
            description="Color (updates real-time)"
        )
        material: bpy.props.PointerProperty(type=bpy.types.Material, name='Material', options=set())

    return MaterialData


MaterialWireframeData = gen_material_props((0.009, 0.787, 0.787, 0.9))
MaterialBaseData = gen_material_props((0.209, 0.009, 0.787, 1.0))


class CollectionItem(bpy.types.PropertyGroup):
    value: bpy.props.PointerProperty(type=bpy.types.Collection)


class WirebombData(bpy.types.PropertyGroup):
    """Stores add-on data."""
    use_clear_materials: bpy.props.BoolProperty(
        name='Clear Old Materials',
        default=True,
        description="Remove all previous materials from objects",
        options=set()
    )
    use_ao: bpy.props.BoolProperty(
        name='Basic AO Light',
        default=False,
        description="Use basic ambient occlusion lighting setup",
        options=set()
    )
    use_new_scene: bpy.props.BoolProperty(
        name='New Scene',
        default=True,
        description="Preserve the current scene by operating on a copy of it",
        options=set()
    )
    new_scene_name: bpy.props.StringProperty(
        name='Name',
        default='Wireframe',
        maxlen=47,
        description="The new scene's name",
        options=set()
    )

    affect_mode: bpy.props.EnumProperty(
        items=[('INCLUSIVE', 'Inclusive', 'Affect the meshes indicated by the following options'),
               ('EXCLUSIVE', 'Exclusive',
                'Affect all meshes in the scene except for the meshes indicated by the following options')],
        name='Mode',
        description="Selection mode",
        default='EXCLUSIVE',
        options=set()
    )
    use_affect_selected: bpy.props.BoolProperty(
        name='Selected',
        default=False,
        description="Selected meshes",
        options=set()
    )
    use_affect_collections: bpy.props.BoolProperty(
        name='In Collections',
        default=False,
        description="All meshes in these collections",
        options=set()
    )

    collections_affected: bpy.props.CollectionProperty(type=CollectionItem)

    # important that these only differ by the suffix "_active"
    collections_affected_active: bpy.props.IntProperty(name="", description="Index of active affected collection.")

    use_base: bpy.props.BoolProperty(
        name='Base Material',
        default=True,
        description="Enable the use of a base material",
        options=set()
    )

    use_wireframe: bpy.props.BoolProperty(
        name='Wireframe',
        default=True,
        description="Enable the use of wireframe",
        options=set()
    )
    wireframe_method: bpy.props.EnumProperty(
        items=[('FREESTYLE', 'Freestyle', 'Create wireframe using freestyle'),
               ('MODIFIER', 'Modifier', 'Create wireframe using the wireframe modifier')],
        name='Method',
        description='The method used to create the wireframe effect',
        default='FREESTYLE',
        options=set()
    )
    thickness_freestyle: bpy.props.FloatProperty(
        name='Thickness',
        subtype='NONE',
        precision=3,
        step=10,
        min=0,
        max=10000,
        default=1,
        description="Wireframe thickness (updates real-time)"
    )
    thickness_modifier: bpy.props.FloatProperty(
        name='Thickness',
        subtype='NONE',
        precision=4,
        step=0.01,
        soft_min=0,
        soft_max=1,
        default=0.008,
        description="Wireframe thickness (updates real-time)"
    )
    material_wireframe: bpy.props.PointerProperty(type=MaterialWireframeData)
    material_base: bpy.props.PointerProperty(type=MaterialBaseData)


classes = (
    MaterialWireframeData,
    MaterialBaseData,
    CollectionItem,
    WirebombData,
)
register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    register_classes()
    bpy.types.Scene.wirebomb = bpy.props.PointerProperty(type=WirebombData)


def unregister():
    del bpy.types.Scene.wirebomb
    unregister_classes()
