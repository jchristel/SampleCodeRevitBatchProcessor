"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions - line styles and types.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Model health report metrics can either be displayed in a family where each parameter is assigned to a metric 
and or data can be exported to text files which can be used to visualize key metrics over time.

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

import clr


import System

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)


from duHast.Revit.ModelHealth.Reporting.Properties.constants import (
    FAILED_TO_RETRIEVE_VALUE,
)

from duHast.Revit.LinePattern.line_patterns import get_all_line_patterns
from duHast.Revit.LinePattern.line_styles import get_all_line_style_ids
from duHast.Revit.LinePattern.fill_patterns import get_all_fill_pattern


# --------------------------------------------- LINE STYLES / TYPES  ---------------------------------------------


def get_number_of_line_styles(doc):
    """
    Gets the number of line styles in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of line styles in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_line_style_ids(doc))
    except Exception as e:
        raise ValueError("Failed to get number of line styles: {}".format(e))
    return number


def get_number_of_line_patterns(doc):
    """
    Gets the number of line patterns in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of line patterns in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_line_patterns(doc).ToList())
    except Exception as e:
        raise ValueError("Failed to get number of line patterns: {}".format(e))
    return number


def get_number_of_fill_patterns(doc):
    """
    Gets the number of fill pattern in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of fill pattern in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_fill_pattern(doc).ToList())
    except Exception as e:
        raise ValueError("Failed to get number of fill patterns: {}".format(e))
    return number
