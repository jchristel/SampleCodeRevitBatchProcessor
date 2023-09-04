"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions - cad links.
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

from duHast.Revit.Links.cad_links import (
    get_cad_type_imports_only,
    get_all_cad_link_type_in_model_only,
    get_all_cad_link_type_by_view_only,
)

# --------------------------------------------- CAD links  ---------------------------------------------


def get_number_of_cad_imports(doc):
    """
    Gets the number of CAD imports in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of CAD imports in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_cad_type_imports_only(doc))
    except Exception as e:
        raise ValueError("Failed to get number of cad imports: {}".format(e))
    return number


def get_number_of_cad_links_to_model(doc):
    """
    Gets the number of CAD links by model in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of CAD links by model in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_cad_link_type_in_model_only(doc))
    except Exception as e:
        raise ValueError("Failed to get number of cad links to model: {}".format(e))
    return number


def get_number_of_cad_links_to_view(doc):
    """
    Gets the number of CAD links by view in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of CAD links by view in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_cad_link_type_by_view_only(doc))
    except Exception as e:
        raise ValueError("Failed to get number of cad links to views: {}".format(e))
    return number
