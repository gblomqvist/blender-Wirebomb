original_scene = None

error_101 = False  # no mesh selected
error_201 = False  # no clay material selected
error_202 = False  # no clay material selected
error_301 = False  # no wire scene name
error_302 = False  # no clay scene name

# render layer names
rlname = None
rlname_2 = None
rlname_other = None

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
color_wire_set = None
color_clay_set = None

# materials set
mat_wire_set = None
mat_clay_set = None

# sliders
slider_wt_freestyle = None
slider_wt_modifier = None

# layers selected
layer_numbers_other = None
layer_numbers_affected = None

# affected and other layers together
layer_numbers_all_used = None

# scene names set
scene_name_1 = None
scene_name_2 = None
