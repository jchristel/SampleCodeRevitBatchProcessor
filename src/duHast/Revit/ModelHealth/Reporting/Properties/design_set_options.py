"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions - design set and options.
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

from duHast.Revit.Common.design_set_options import get_design_sets, get_design_options

# ---------------------------------------------  design sets and options  ---------------------------------------------

def get_number_of_design_sets(doc):
    """
    Gets the number of design sets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of design sets in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_design_sets(doc))
    except Exception as e:
        raise ValueError ("Failed to get number of design sets: {}".format(e))
    return number


def get_number_of_design_options(doc):
    """
    Gets the number of design options in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of design option in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_design_options(doc).ToList())
    except Exception as e:
        raise ValueError ("Failed to get number of design options: {}".format(e))
    return number