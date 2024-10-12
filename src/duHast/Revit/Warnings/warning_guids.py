"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a warning guids of specific Revit warnings. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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


# area line is slightly off axis:
AREA_LINE_OFF_AXIS = "77535238-e93a-46c4-9822-97072116aefc"

# area separation lines overlap
AREA_SEPARATION_LINES_OVERLAP = "6891f0e6-5858-4e2f-bb34-801e0b87f60d"

# room tag outside room
ROOM_TAG_OUTSIDE_ROOM = "4f0bba25-e17f-480a-a763-d97d184be18a"

# room separation line overlaps
# Highlighted room separation lines overlap. One of them may be ignored when Revit finds room boundaries. Delete one of the lines.
ROOM_SEPARATION_LINES_OVERLAP = "374396c0-984d-4f72-a081-30ab7dacb66d"

# a room separation line and wall overlap
# A wall and a room separation line overlap. One of them may be ignored when Revit finds room boundaries. Shorten or delete the room separation line to remove the overlap.
ROOM_AND_WALL_SEPARATION_LINE_OVERLAP = "f7b3a015-c3eb-4a3f-b345-c474ec07d43f"

# Room separation line is slightly off axis and may cause inaccuracies.
ROOM_LINE_OFF_AXIS = "f657364a-e0b7-46aa-8c17-edd8e59683b9"

# Room is not in a properly enclosed region
ROOM_NOT_ENCLOSED = "ce3275c6-1c51-402e-8de3-df3a3d566f5c"

# duplicate mark value
DUPLICATE_MARK_VALUE = "6e1efefe-c8e0-483d-8482-150b9f1da21a"

# Element owned by others
# Can't edit the element until \"somebody\" re-saves the element to central and relinquishes it and you Reload Latest.
ELEMENTS_OWNED_BY_OTHER = "3b7fcaec-c01e-4c2e-819f-67ddd102ce1f"

# Elements have duplicate "Number" values.
ELEMENTS_DUPLICATE_NUMBER_VALUES = "6e1efefe-c8e0-483d-8482-150b9f1da21a"

# There are identical instances in the same place. This will result in double counting in schedules. You can tab-select one of the overlapping elements to exclude it from the group instance.
IDENTICAL_INSTANCES_IN_SAME_PLACE = "b4176cef-6086-45a8-a066-c3fd424c9412"

# Highlighted lines overlap. Lines may not form closed loops. You can tab-select one of the overlapping elements to exclude it from the group instance.
LINES_OVERLAP = "6891f0e6-5858-4e2f-bb34-801e0b87f60d"

# Line in Sketch is slightly off axis and may cause inaccuracies.
LINE_IN_SKETCH_OFF_AXIS = "ec905b6a-064b-48e1-a6c7-51e2cf092490"

# Line in Massing Sketch is slightly off axis and may cause inaccuracies.
LINE_IN_MASSING_SKETCH_OFF_AXIS = "e4b4847a-1cbc-4283-854e-85431403a2a0"

# Line is slightly off axis and may cause inaccuracies.
LINE_OFF_AXIS = "7b8f75b6-a3f2-48a4-8b5d-d767c9a20b32"

# Wall is slightly off axis and may cause inaccuracies.
WALL_OFF_AXIS = "fb1d4583-6b62-4ccb-9cb8-7c2e849b4d43"

# Ref Plane is slightly off axis and may cause inaccuracies.
REF_PLANE_OFF_AXIS = "ce961443-d03b-4cda-94c9-6b9beab9d2a6"

# Curve-Based Family is slightly off axis and may cause inaccuracies.
FAMILY_CURVE_BASED_OFF_AXIS = "e9b42850-030f-4909-990b-cf7cddf165a6"
