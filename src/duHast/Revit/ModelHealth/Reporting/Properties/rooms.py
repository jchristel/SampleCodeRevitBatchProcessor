"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions - rooms.
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


# import System
# clr.AddReference("System.Core")
# from System import Linq
# clr.ImportExtensions(Linq)


from duHast.Revit.ModelHealth.Reporting.Properties.constants import (
    FAILED_TO_RETRIEVE_VALUE,
)

from duHast.Revit.Rooms.rooms import (
    get_all_rooms,
    get_unplaced_rooms,
    get_redundant_rooms,
    get_not_enclosed_rooms,
)


# ---------------------------------------------  Rooms  ---------------------------------------------


def get_number_of_rooms(doc):
    """
    Gets the number of rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of rooms in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_all_rooms(doc))
    except Exception as e:
        raise ValueError("Failed to get number of rooms: {}".format(e))
    return number


def get_number_of_unplaced_rooms(doc):
    """
    Gets the number of unplaced rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced rooms in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_unplaced_rooms(doc))
    except Exception as e:
        raise ValueError("Failed to get number of unplaced rooms: {}".format(e))
    return number


def get_number_of_redundant_rooms(doc):
    """
    Gets the number of redundant rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of redundant rooms in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_redundant_rooms(doc))
    except Exception as e:
        raise ValueError("Failed to get number of redundant rooms: {}".format(e))
    return number


def get_number_of_not_enclosed_rooms(doc):
    """
    Gets the not enclosed number of rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of not enclosed rooms in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_not_enclosed_rooms(doc))
    except Exception as e:
        raise ValueError("Failed to get number of rooms not enclosed: {}".format(e))
    return number
