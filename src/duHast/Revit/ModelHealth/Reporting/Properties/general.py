"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions - general reports.
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

from duHast.Utilities.date_stamps import get_file_date_stamp, FILE_DATE_STAMP_YYYY_MM_DD
from duHast.Utilities.files_io import file_exist, get_file_size
from duHast.Revit.BIM360.bim_360 import get_model_file_size
from duHast.Revit.Warnings.warnings import get_warnings
from duHast.Revit.Common.worksets import get_worksets

# --------------------------------------------- GENERAL ---------------------------------------------


def get_current_date(doc):
    """
    Get the current date

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: The current date in format YYYY_MM_DD.
    :rtype: str

    """
    return get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD)


def get_workset_number(doc):
    """
    Gets the number of worksets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: The number of worksets in a model.
    :rtype: int
    """

    return len(get_worksets(doc))


def get_current_file_size(doc):
    """
    Gets the file size in MB.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: File size in MB. On exception it will return -1
    :rtype: int
    """

    size = FAILED_TO_RETRIEVE_VALUE
    try:
        # get the path from the document
        # this will fail if not a file based doc or the document is detached
        revit_file_path = doc.PathName
        try:
            # test if this is a cloud model
            path = doc.GetCloudModelPath()
            size = get_model_file_size(doc)
        except:
            # local file server model
            if file_exist(revit_file_path):
                # get file size in MB
                size = get_file_size(revit_file_path)
            else:
                raise ValueError("File not found: {}".format(revit_file_path))
    except Exception as e:
        raise ValueError("Failed to get file size with: {}".format(e))
    return size


def get_number_of_warnings(doc):
    """
    Gets the number of warnings in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of warnings in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(get_warnings(doc))
    except Exception as e:
        raise ValueError("Failed to get number of warnings: {}".format(e))
    return number
