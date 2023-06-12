"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the header row for any (future) generic annotation reports. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

# -------------------------------------------- common variables --------------------
#: header used in reports up to revit 2022
REPORT_GENERIC_ANNOTATIONS_INSTANCE_HEADER = [
    "HOST_FILE",
    "TAG_ID",
    "TAG_HAS_LEADER",
    "TAG_IS_ORPHANED",
    "TAG_IS_MATERIAL_TAG",
    "IS_MULTICATEGORY_TAG",
    "LEADER_END_CONDITION",
    "ELBOW_LOCATION",
    "LEADER_END",
    "MULTI_REFERENCE_ANNOTATION_ID",
    "TAG_TEXT",
    "TAGGED_ELEMENT_NAME",
    "TAG_HEAD_LOCATION",
    "TAG_ROTATION_ANGLE",
    "TAG_ORIENTATION",
]

#: header used in reports up to revit 2022
REPORT_GENERIC_ANNOTATIONS_INSTANCE_HEADER_2023 = [
    "TAG_PRESENTATION_MODE",
    "MERGE_ELBOWS",
]