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
# checkboxes
cb_backup = None
cb_clear_rlayers = None
cb_only_selected = None
cb_ao = None
cb_clay = None
cb_clay_only = None
cb_comp = None
cb_mat_wire = None
cb_mat_clay = None

cb_comp_active = False

# selected materials
wire_mat_set = None
clay_mat_set = None

# layers selected
other_layers_numbers = []
affected_layers_numbers = []
all_layers_used_numbers = []

# custom scene-naming fields
scene_name_1 = None
scene_name_2 = None
