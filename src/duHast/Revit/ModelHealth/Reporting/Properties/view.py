"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions - views.
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
from duHast.Revit.Views.sheets import get_all_sheets
from duHast.Revit.Views.views import get_views_in_model, get_views_not_on_sheet
from duHast.Revit.Views.templates import (
    get_view_templates_ids,
    get_all_unused_view_template_ids,
)
from duHast.Revit.Views.filters import get_all_filters, get_all_unused_view_filters

# --------------------------------------------- VIEWS ---------------------------------------------


def get_number_of_sheets(doc):
    """
    Gets the number of sheets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of sheets in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_sheets(doc).ToList())
    except Exception as e:
        raise ValueError("Failed to get number of sheets: {}".format(e))
    return number


def _view_filter(view):
    """
    generic view filter allowing all views to be selected

    :param view: not used!
    :type view: Autodesk.Revit.DB.View

    :return: returns always True
    :rtype: bool
    """
    return True


def get_number_of_views(doc):
    """
    Gets the number of views in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of views in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_views_in_model(doc, _view_filter))
    except Exception as e:
        raise ValueError("Failed to get number of views: {}".format(e))
    return number


def get_number_of_unplaced_views(doc):
    """
    Gets the number of unplaced views in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced views in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_views_not_on_sheet(doc))
    except Exception as e:
        raise ValueError("Failed to get number of unplaced views: {}".format(e))
    return number


def get_number_of_view_templates(doc):
    """
    Gets the number of view templates in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of view templates in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_view_templates_ids(doc))
    except Exception as e:
        raise ValueError("Failed to get number of view templates: {}".format(e))
    return number


def get_number_of_unused_view_templates(doc):
    """
    Gets the number of unplaced view templates in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced view templates in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_unused_view_template_ids(doc))
    except Exception as e:
        raise ValueError("Failed to get number of unused view templates: {}".format(e))
    return number


def get_number_of_view_filters(doc):
    """
    Gets the number of view filters in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of number of view filters in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_filters(doc).ToList())
    except Exception as e:
        raise ValueError("Failed to get number of view filters: {}".format(e))
    return number


def get_number_of_unused_view_filters(doc):
    """
    Gets the number of unused view filters in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unused view filters in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_unused_view_filters(doc))
    except Exception as e:
        raise ValueError("Failed to get number of unused view filters: {}".format(e))
    return number
