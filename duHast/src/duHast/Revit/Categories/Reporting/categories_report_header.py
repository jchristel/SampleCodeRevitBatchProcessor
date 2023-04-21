'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category report headers.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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
#: Header used in report files
from duHast.Revit.LinePattern import RevitLineStylesPatterns as rPat
from duHast.Revit.Categories.Utility.category_property_names import CATEGORY_GRAPHIC_STYLE_3D, CATEGORY_GRAPHIC_STYLE_CUT, CATEGORY_GRAPHIC_STYLE_PROJECTION, PROPERTY_LINE_COLOUR_BLUE_NAME, PROPERTY_LINE_COLOUR_GREEN_NAME, PROPERTY_LINE_COLOUR_RED_NAME, PROPERTY_LINE_WEIGHT_CUT_NAME, PROPERTY_LINE_WEIGHT_PROJECTION_NAME,PROPERTY_MATERIAL_ID, PROPERTY_MATERIAL_NAME

REPORT_CATEGORIES_HEADER = [
    'HOSTFILE',
    'FAMILY CATEGORY',
    'MAINCATEGORYNAME',
    'SUBCATEGORYNAME',
    'CATEGORYID',
    PROPERTY_MATERIAL_NAME.upper(),
    PROPERTY_MATERIAL_ID.upper(),
    rPat.PROPERTY_PATTERN_NAME.upper(),
    rPat.PROPERTY_PATTERN_ID.upper(),
    PROPERTY_LINE_WEIGHT_PROJECTION_NAME.upper(),
    PROPERTY_LINE_WEIGHT_CUT_NAME.upper(),
    PROPERTY_LINE_COLOUR_RED_NAME.upper(),
    PROPERTY_LINE_COLOUR_GREEN_NAME.upper(),
    PROPERTY_LINE_COLOUR_BLUE_NAME.upper(),
    CATEGORY_GRAPHIC_STYLE_3D.upper(),
    CATEGORY_GRAPHIC_STYLE_PROJECTION.upper(),
    CATEGORY_GRAPHIC_STYLE_CUT.upper()
]