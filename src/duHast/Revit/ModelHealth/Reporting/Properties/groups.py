"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions - groupes.
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

from duHast.Revit.Common.groups import (
    get_detail_groups,
    get_model_groups,
    get_unplaced_detail_groups,
    get_unplaced_model_groups,
)

from duHast.Revit.ModelHealth.Reporting.Properties.constants import (
    FAILED_TO_RETRIEVE_VALUE,
)

# ---------------------------------------------  Groups  ---------------------------------------------


def get_number_of_detail_groups(doc):
    """
    Gets the number of detail group definitions the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of detail group definitions in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_detail_groups(doc))
    except Exception as e:
        raise ValueError("Failed to get number of detail groups: {}".format(e))
    return number


def get_number_of_model_groups(doc):
    """
    Gets the number of model group definitions in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of model group definitions in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_model_groups(doc))
    except Exception as e:
        raise ValueError("Failed to get number of model groups: {}".format(e))
    return number


def get_number_of_unplaced_detail_groups(doc):
    """
    Gets the number of unplaced detail group definitions in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced detail group definitions in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_unplaced_detail_groups(doc))
    except Exception as e:
        raise ValueError("Failed to get number of unplaced detail groups: {}".format(e))
    return number


def get_number_of_unplaced_model_groups(doc):
    """
    Gets the number of unplaced model group definitions in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced model group definitions in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_unplaced_model_groups(doc))
    except Exception as e:
        raise ValueError("Failed to get number of unplaced model groups: {}".format(e))
    return number
