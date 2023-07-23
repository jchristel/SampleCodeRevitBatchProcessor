"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category report headers.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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


# -------------------------------------------- common variables --------------------
#: Header used in report files
from duHast.Revit.LinePattern.line_patterns import PROPERTY_PATTERN_NAME, PROPERTY_PATTERN_ID

from duHast.Revit.Categories.Utility.category_property_names import (
    CATEGORY_GRAPHIC_STYLE_3D,
    CATEGORY_GRAPHIC_STYLE_CUT,
    CATEGORY_GRAPHIC_STYLE_PROJECTION,
    PROPERTY_LINE_COLOUR_BLUE_NAME,
    PROPERTY_LINE_COLOUR_GREEN_NAME,
    PROPERTY_LINE_COLOUR_RED_NAME,
    PROPERTY_LINE_WEIGHT_CUT_NAME,
    PROPERTY_LINE_WEIGHT_PROJECTION_NAME,
    PROPERTY_MATERIAL_ID,
    PROPERTY_MATERIAL_NAME,
)

REPORT_CATEGORIES_HEADER = [
    "HOSTFILE",
    "FAMILY CATEGORY",
    "MAINCATEGORYNAME",
    "SUBCATEGORYNAME",
    "CATEGORYID",
    PROPERTY_MATERIAL_NAME.upper(),
    PROPERTY_MATERIAL_ID.upper(),
    PROPERTY_PATTERN_NAME.upper(),
    PROPERTY_PATTERN_ID.upper(),
    PROPERTY_LINE_WEIGHT_PROJECTION_NAME.upper(),
    PROPERTY_LINE_WEIGHT_CUT_NAME.upper(),
    PROPERTY_LINE_COLOUR_RED_NAME.upper(),
    PROPERTY_LINE_COLOUR_GREEN_NAME.upper(),
    PROPERTY_LINE_COLOUR_BLUE_NAME.upper(),
    CATEGORY_GRAPHIC_STYLE_3D.upper(),
    CATEGORY_GRAPHIC_STYLE_PROJECTION.upper(),
    CATEGORY_GRAPHIC_STYLE_CUT.upper(),
]
