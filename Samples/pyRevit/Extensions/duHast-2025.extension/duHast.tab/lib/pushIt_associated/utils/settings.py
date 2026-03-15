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

from Autodesk.Revit.DB import BuiltInParameter

# pushit parameters in use:

# overall dimension parameter names
WIDTH_PARAMETER_NAME = "duHast_width"
DEPTH_PARAMETER_NAME = "duHast_depth"
HEIGHT_PARAMETER_NAME = "duHast_height"
WALL_THICKNESS_PARAMETER_NAME = "duHast_wall_thickness"

# identity parameter names
DEPARTMENT_NAME_PARAMETER_NAME="duHast_department_name"
DEPARTMENT_CODE_PARAMETER_NAME="duHast_department_code"
SUB_DEPARTMENT_NAME_PARAMETER_NAME="duHast_sub_department_name"
SUB_DEPARTMENT_CODE_PARAMETER_NAME="duHast_sub_department_code"
FUNCTIONAL_GROUP_NAME_PARAMETER_NAME="duHast_functional_group_name"
FUNCTIONAL_GROUP_CODE_PARAMETER_NAME="duHast_functional_group_code"
ROOM_NAME_PARAMETER_NAME="duHast_room_name"
ROOM_NAME_ABBREVIATED_PARAMETER_NAME="duHast_room_name_abbreviated"
ROOM_ID_PARAMETER_NAME="duHast_room_id"
ROOM_NUMBER_PARAMETER_NAME="duHast_room_number"

# area parameter names
AREA_DESIGNED_TO_AREA_BRIEFED_AS_PERCENTAGE_PARAMETER_NAME="duHast_area_designed_to_area_briefed_as_percentage"
AREA_DESIGNED_PARAMETER_NAME = "duHast_area_designed_centre_wall"
AREA_DESIGNED_MINUS_AREA_BRIEFED_DIFFERENCE_PARAMETER_NAME="duHast_area_designed_minus_area_briefed_difference"
AREA_BRIEFED_PARAMETER_NAME="duHast_area_briefed"
AREA_BY_REVIT_ROOM_PARAMETER_NAME="duHast_area_by_revit_room"


# mapper to transfer parameter data from a shared parameter on a push it instance to a built in room parameter
push_it_shared_parameter_to_build_in_parameter_mapper = {
    ROOM_NUMBER_PARAMETER_NAME: BuiltInParameter.ROOM_NUMBER,
    ROOM_NAME_PARAMETER_NAME : BuiltInParameter.ROOM_NAME,
    DEPARTMENT_NAME_PARAMETER_NAME : BuiltInParameter.ROOM_DEPARTMENT,
}