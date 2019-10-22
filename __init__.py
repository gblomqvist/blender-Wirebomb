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

bl_info = {
    "name": "Wirebomb",
    "description": "Setting up wireframe renders has never been easier!",
    "author": "Gustaf Blomqvist",
    "version": (2, 0, 0),
    "blender": (2, 82, 0),
    "location": "Properties > Render Properties > Wirebomb",
    "warning": "Beta",
    "wiki_url": "https://blendermarket.com/products/wirebomb/docs",
    "tracker_url": "https://github.com/gblomqvist/blender-Wirebomb/issues",
    "support": "COMMUNITY",
    "category": "Render",
}

import importlib

# note that the registration order matters
module_names = (
    'ops',
    'props',
    'ui',
    'ui_presets',
    'utils',
    'wirebomb'
)
modules = []

for mod_name in module_names:
    modules.append(importlib.import_module(f'{__name__}.{mod_name}'))

loc = locals()
if 'bpy' in loc:
    for mod in modules:
        if mod.__name__ in loc:
            importlib.reload(mod)


def register():
    # noinspection PyShadowingNames
    for mod in modules:
        mod.register()


def unregister():
    # noinspection PyShadowingNames
    for mod in modules:
        mod.unregister()


if __name__ == '__main__':
    register()
