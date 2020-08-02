import bpy
import sys


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]
    install_zip_path = argv[0]
    addon_name = argv[1]

    bpy.ops.preferences.addon_install(filepath=install_zip_path)
    bpy.ops.preferences.addon_enable(module=addon_name)
    bpy.ops.wm.save_userpref()


if __name__ == '__main__':
    main()
