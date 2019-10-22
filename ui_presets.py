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

import bl_operators
import bl_ui
import bpy

global_preset_defines = ['wirebomb = bpy.context.scene.wirebomb']
base_path = 'wirebomb/'


class WIREBOMB_PT_base_material_presets(bl_ui.utils.PresetPanel, bpy.types.Panel):
    bl_label = "Base Material Presets"
    preset_operator = 'script.execute_preset'
    preset_subdir = base_path + 'material-base'

    @property
    def preset_add_operator(self):
        return WIREBOMB_OT_add_preset_base_material.bl_idname


class WIREBOMB_OT_add_preset_base_material(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    """Add or remove a Base Material Preset"""
    bl_label = "Add Base Material Preset"
    bl_idname = 'wirebomb.add_preset_base_material'
    preset_menu = WIREBOMB_PT_base_material_presets.__name__
    preset_defines = global_preset_defines
    preset_values = [
        'wirebomb.material_base.mode',
        'wirebomb.material_base.color',
        'wirebomb.material_base.material',
    ]
    preset_subdir = WIREBOMB_PT_base_material_presets.preset_subdir


class WIREBOMB_PT_wireframe_material_presets(bl_ui.utils.PresetPanel, bpy.types.Panel):
    bl_label = "Wireframe Material Presets"
    preset_operator = 'script.execute_preset'
    preset_subdir = base_path + 'material-wireframe'

    @property
    def preset_add_operator(self):
        return WIREBOMB_OT_add_preset_wireframe_material.bl_idname


class WIREBOMB_OT_add_preset_wireframe_material(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    """Add or remove a Wireframe Material Preset"""
    bl_label = "Add Wireframe Material Preset"
    bl_idname = 'wirebomb.add_preset_wireframe_material'
    preset_menu = WIREBOMB_PT_wireframe_material_presets.__name__
    preset_defines = global_preset_defines
    preset_values = [
        'wirebomb.material_wireframe.mode',
        'wirebomb.material_wireframe.color',
        'wirebomb.material_wireframe.material',
    ]
    preset_subdir = WIREBOMB_PT_wireframe_material_presets.preset_subdir


class WIREBOMB_PT_wireframe_thickness_presets(bl_ui.utils.PresetPanel, bpy.types.Panel):
    """Wireframe Thickness Presets"""
    bl_label = "Wireframe Thickness Presets"
    preset_operator = 'script.execute_preset'

    @property
    def preset_add_operator(self):
        return WIREBOMB_OT_add_preset_wireframe_thickness.bl_idname

    @property
    def preset_subdir(self):
        return self.get_preset_subdir()

    @staticmethod
    def get_preset_subdir():
        return base_path + 'thickness-' + bpy.context.scene.wirebomb.wireframe_method.lower()


class WIREBOMB_OT_add_preset_wireframe_thickness(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    """Add or remove a Wireframe Thickness Preset"""
    bl_label = "Add Wireframe Thickness Preset"
    bl_idname = 'wirebomb.add_preset_wireframe_thickness'
    preset_menu = WIREBOMB_PT_wireframe_thickness_presets.__name__
    preset_defines = global_preset_defines

    @property
    def preset_values(self):
        return ['wirebomb.thickness_' + bpy.context.scene.wirebomb.wireframe_method.lower()]

    @property
    def preset_subdir(self):
        return WIREBOMB_PT_wireframe_thickness_presets.get_preset_subdir()


classes = (
    WIREBOMB_OT_add_preset_base_material,
    WIREBOMB_OT_add_preset_wireframe_material,
    WIREBOMB_OT_add_preset_wireframe_thickness,
    WIREBOMB_PT_base_material_presets,
    WIREBOMB_PT_wireframe_material_presets,
    WIREBOMB_PT_wireframe_thickness_presets,
)

register, unregister = bpy.utils.register_classes_factory(classes)
