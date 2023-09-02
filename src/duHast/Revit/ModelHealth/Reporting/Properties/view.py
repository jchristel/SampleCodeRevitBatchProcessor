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
