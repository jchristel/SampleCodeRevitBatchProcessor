# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import os

from duHast.Utilities.files_io import get_directory_path_from_file_path

# add path to ifc dll
SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)

# location of family templates
FAMILY_TEMPLATE_DIRECTORY = os.path.join(get_directory_path_from_file_path(__file__),"templates")

# template name for a room with walls
FAMILY_TEMPLATE_WALL_ROOM_NAME = "WLL_room_template"
FAMILY_TEMPLATE_WALL_ROOM_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_WALL_ROOM_NAME+".rfa")
# template name for a bay (no walls)
FAMILY_TEMPLATE_WALL_BAY_NAME = "WLL_bay_template"
FAMILY_TEMPLATE_WALL_BAY_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_WALL_BAY_NAME+".rfa")

# template name for nested generic family when in a room
FAMILY_TEMPLATE_GENERIC_ROOM_NESTED = "GEN_Inner_Nested_template"
FAMILY_TEMPLATE_GENERIC_ROOM_NESTED_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_GENERIC_ROOM_NESTED+".rfa")
# template name for nested generic family when in a bay
FAMILY_TEMPLATE_GENERIC_BAY_NESTED = "GEN_Inner_Nested_Bay_template"
FAMILY_TEMPLATE_GENERIC_BAY_NESTED_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_GENERIC_BAY_NESTED+".rfa")

# template name for nested generic family when in a coarse view for a room
FAMILY_TEMPLATE_GENERIC_NESTED_ROOM_COARSE = "GEN_Inner_Nested_Coarse_template"
FAMILY_TEMPLATE_GENERIC_NESTED_ROOM_COARSE_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_GENERIC_NESTED_ROOM_COARSE+".rfa")
# template name for nested generic family when in a coarse view for a bay
FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE = "GEN_Inner_Nested_Coarse_Bay_template"
FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE+".rfa")

# schema name
GET_A_ROOM_ADD_IN_SCHEMA_NAME = "Get_A_Room_Settings"

#schema documentation
GET_A_ROOM_ADD_IN_SCHEMA_DOCUMENTATION = "This schema contains settings for the get a room add in."

# guid of the schema to use for the Get A Room add-in
GET_A_ROOM_ADD_IN_GUID= "d17b7416-53d7-46dc-8df7-b6624743a6b8"
# schema field names
DU_HAST_GET_A_ROOM_FAMILY_OUT_DIRECTORY_FIELD_NAME = "DU_HAST_GET_A_ROOM_FAMILY_OUT_DIRECTORY"

# overall dimension parameter names
WIDTH_PARAMETER_NAME = "HSL_WIDTH"
DEPTH_PARAMETER_NAME = "HSL_DEPTH"
HEIGHT_PARAMETER_NAME = "HSL_HEIGHT"
AREA_PARAMETER_NAME = "HSL_GROSS_FLOOR_AREA"