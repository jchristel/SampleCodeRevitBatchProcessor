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
# BSD License
# Copyright 2023, Jan Christel
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
        raise ValueError(
            "Failed to get number of unused arrow head types: {}".format(e)
        )
    return number
