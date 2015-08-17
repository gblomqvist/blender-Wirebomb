created_scenes = set()

# TODO: how can I reload everything below?
original_scene = None

error_101 = False  # no mesh selected
error_201 = False  # no clay material selected
error_202 = False  # no clay material selected
error_301 = False  # no wire scene name
error_302 = False  # no clay scene name

# render layer names
rlname = ''
rlname_2 = ''
rlname_other = ''

# objects selected
only_selected = []

# materials
wire_freestyle_linestyle = None
wire_modifier_mat = None
wire_bi_mat = None
clay_mat = None

# from interface:
# wireframe type
wireframe_type = None

# checkboxes
cb_backup = None
cb_clear_rlayers = None
cb_clear_mats = None
cb_only_selected = None
cb_ao = None
cb_clay = None
cb_clay_only = None
cb_comp = None
cb_mat_wire = None
cb_mat_clay = None

cb_clay_only_active = None
cb_comp_active = None
cb_mat_wire_active = None
cb_mat_clay_active = None

# colors set
color_wire = None
color_clay = None

# materials set
mat_wire_name = None
mat_clay_name = None

# sliders
slider_wt_freestyle = 0.0
slider_wt_modifier = 0.0

# layers selected
layer_numbers_other = set()
layer_numbers_affected = set()

# affected and other layers together
layer_numbers_all_used = set()

# scene names set
scene_name_1 = ''
scene_name_2 = ''
