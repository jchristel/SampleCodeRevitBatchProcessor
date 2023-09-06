"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions - annotation types.
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

from duHast.Revit.Annotation.text import get_all_text_types
from duHast.Revit.Annotation.purge_unused_annotation_types import (
    get_all_unused_text_type_ids_in_model,
    get_all_unused_dim_type_ids_in_model,
    get_all_unused_arrow_type_ids_in_model,
)

from duHast.Revit.Annotation.dimensions import get_dim_types
from duHast.Revit.Annotation.arrow_heads import get_arrow_types_in_model


# ----------------------------- text -----------------------------------------------
def get_number_of_text_types(doc):
    """
    Gets the number of text types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of text types in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_text_types(doc).ToList())
    except Exception as e:
        raise ValueError("Failed to get number of text types: {}".format(e))
    return number


def get_number_of_unused_text_types(doc):
    """
    Gets the number of unused text types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unused text types in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_unused_text_type_ids_in_model(doc))
    except Exception as e:
        raise ValueError("Failed to get number of unused text types: {}".format(e))
    return number


# ----------------------------- dimensions -----------------------------------------------


def get_number_of_dimension_types(doc):
    """
    Gets the number of dimension types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of dimension types in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_dim_types(doc).ToList())
    except Exception as e:
        raise ValueError("Failed to get number of dimension types: {}".format(e))
    return number


def get_number_of_unused_dimension_types(doc):
    """
    Gets the number of unused dimension types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unused dimension types in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_unused_dim_type_ids_in_model(doc))
    except Exception as e:
        raise ValueError("Failed to get number of unused dimension types: {}".format(e))
    return number

# ----------------------------- arrow heads -----------------------------------------------

def get_number_of_arrow_head_types(doc):
    """
    Gets the number of arrow head types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of arrow head types in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_arrow_types_in_model(doc))
    except Exception as e:
        raise ValueError("Failed to get number of arrow head types: {}".format(e))
    return number


def get_number_of_unused_arrow_head_types(doc):
    """
    Gets the number of unused arrow head types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unused arrow head types in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_unused_arrow_type_ids_in_model(doc))
    except Exception as e:
        raise ValueError("Failed to get number of unused arrow head types: {}".format(e))
    return number