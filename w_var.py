# <pep8-80 compliant>

error_101 = False  # no mesh selected
error_201 = False  # no clay material selected
error_202 = False  # no clay material selected
error_301 = False  # no wire scene name
error_302 = False  # no clay scene name

# if checkboxes are active
cb_clay_only_active = None
cb_mat_wire_active = None
cb_mat_clay_active = None

# all scenes created via this add-on during this blender session (for 'Quick remove' operator)
created_scenes = set()

# the scene to set up for a wireframe/clay render
original_scene = None

# setting unique IDs for use in real-time color change and wireframe modifier thickness change
node_wireframe_diffuse = ''
node_clay_diffuse = ''
modifier_wireframe = ''

# render layer names
rlname = ''
rlname_2 = ''
rlname_other = ''

# objects selected
objects_affected = set()
objects_other = set()
objects_all_used = set()

# materials
wire_freestyle_linestyle = None
wire_modifier_mat = None
wire_bi_mat = None
clay_mat = None

# from interface:
# wireframe type
wireframe_method = None

# checkboxes
cb_backup = None
cb_clear_rlayers = None
cb_clear_materials = None
cb_composited = None
cb_only_selected = None
cb_ao = None
cb_clay = None
cb_clay_only = None

cb_mat_wire = None
cb_mat_clay = None

# colors set
color_wire = None
color_clay = None

# materials set (names)
mat_wire_name = None
mat_clay_name = None

# sliders
slider_wt_freestyle = 0.0
slider_wt_modifier = 0.0

# layers selected
layer_numbers_affected = set()
layer_numbers_other = set()

# affected and other layers together
layer_numbers_all_used = set()

# scene names set
scene_name_1 = ''
scene_name_2 = ''
