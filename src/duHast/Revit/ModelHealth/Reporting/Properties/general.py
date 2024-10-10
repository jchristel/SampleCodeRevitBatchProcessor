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
