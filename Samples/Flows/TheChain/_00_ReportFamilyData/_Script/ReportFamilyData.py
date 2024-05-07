"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is the actual script batch processor executes per family file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It runs a number of reports and saves them out into a temp working directory.

Families are not saved.

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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


# --------------------------
# Imports
# --------------------------

import clr
import System
from os import path

import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.Objects.result import Result as res
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.date_stamps import (
    get_file_date_stamp,
    FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC,
)
from duHast.Utilities.util_batch_p import adjust_session_id_for_directory_name
from duHast.Utilities.directory_io import create_target_directory
from duHast.Utilities.console_out import output
from duHast.Revit.BIM360.bim_360 import get_bim_360_path, convert_bim_360_file_path

# family data processors

from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor import (
    SharedParameterProcessor,
)
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor import (
    LinePatternProcessor,
)
from duHast.Revit.Categories.Data.Objects.category_data_processor import (
    CategoryProcessor,
)
from duHast.Revit.Family.Data.Objects.family_base_data_processor import (
    FamilyBaseProcessor,
)
from duHast.Revit.Warnings.Data.Objects.warnings_data_processor import WarningsProcessor

# family data collector class
from duHast.Revit.Family.Data.Objects.family_data_collector import (
    RevitFamilyDataCollector,
)


import revit_script_util
import revit_file_util

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
# NOTE: these only make sense for batch Revit file processing mode.
doc = revit_script_util.GetScriptDocument()
REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()
# get the session Id
SESSION_ID = revit_script_util.GetSessionId()


# store output here:
ROOT_PATH = settings.OUTPUT_FOLDER

# update to cope with cloud based file path
if settings.IS_CLOUD_PROJECT:
    cloudPath = get_bim_360_path(doc)
    REVIT_FILE_PATH = convert_bim_360_file_path(cloudPath)
# -------------
# my code here:
# -------------


def check_file_path_length(file_extension):
    """
    Attempts to auto truncate to the revit document file path if, after the extension suffix is added, it is longer then 248 characters.
    If longer then 248 characters the actual file name is omitted in favour of a time stamp...hoping that this will reduce the name length.
    This may still be to long.

    :param fileExtension: A file name suffix. Will be appended to file name in format name_suffix
    :type fileExtension: str

    :return: Fully qualified file path to where the file extension is added to a file name.
    :rtype: str
    """

    if len(ROOT_PATH) < 248:
        # build output file name
        file_name = path.join(
            ROOT_PATH,
            "{}_{}{}".format(
                get_file_name_without_ext(REVIT_FILE_PATH),
                file_extension,
                settings.REPORT_FILE_EXTENSION,
            ),
        )
        # check for to long file name and try to reduce
        if len(file_name) > 250:
            output(
                "File path to long: {}  attempting to truncate name...".format(
                    len(file_name)
                ),
                revit_script_util.Output,
            )
            file_name = path.join(
                ROOT_PATH,
                "{}_{}{}".format(
                    get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC),
                    file_extension,
                    settings.REPORT_FILE_EXTENSION,
                ),
            )
    else:
        # this will cause an exception which will be reported ... but not much can be done here if the output directory is to long to start off with
        file_name = path.join(
            ROOT_PATH,
            "{}_{}{}".format(
                get_file_name_without_ext(REVIT_FILE_PATH),
                file_extension,
                settings.REPORT_FILE_EXTENSION,
            ),
        )
    return file_name


def report_data(processor, file_name_prefix):
    """
    Writes report data per family and report type to file.

    :param processor: A processor object containing data collected from family
    :type processor: _type_
    :param fileNamePrefix: A prefix to be added to the report file name.
    :type fileNamePrefix: str

    :return:
        Result class instance.

        - result.status. True if data file was written successfully, otherwise False.
        - result.message will contain messages in format: 'Successfully wrote ' + fileNamePrefix + ' data to file.'.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    result = res()
    if len(ROOT_PATH) < 248:
        # build output file name
        file_name = check_file_path_length(file_name_prefix)
        try:
            write_report_data_as_csv(
                file_name,
                processor.get_data_headers(),
                processor.get_data_string_list(),
            )
            result.update_sep(
                True, "Successfully wrote  data to file {}".format(file_name)
            )
        except Exception as e:
            result.update_sep(
                False,
                "Failed to write {}  data with exception: {}".format(file_name, e),
            )
    return result


# -------------
# main:
# -------------

# save revit file to new location
output("Reporting On Revit File.... start", revit_script_util.Output)

# build separate folder with session ID to avoid parallel running revit session interfering
# when writing data to file
SESSION_ID = adjust_session_id_for_directory_name(SESSION_ID)
RESULT_DIRECTORY = create_target_directory(ROOT_PATH, str(SESSION_ID))

# Set up list containing all family processor instances to be executed per family.
processor_instances = [
    FamilyBaseProcessor(),
    SharedParameterProcessor(),
    LinePatternProcessor(),
    CategoryProcessor(),
    WarningsProcessor(),
]

# check if output folder was created and go ahead if so
if RESULT_DIRECTORY:
    # update root path to include session ID folder
    ROOT_PATH = path.join(ROOT_PATH, str(SESSION_ID))
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    # does folder exist?
    result_category = create_target_directory(
        root_path=ROOT_PATH, folder_name=family_category_name
    )
    if result_category:
        # update root path:
        ROOT_PATH = path.join(ROOT_PATH, family_category_name)
        # process family
        collector = RevitFamilyDataCollector(processor_instances)
        family_name = doc.Title
        # strip .rfa of name
        if family_name.lower().endswith(".rfa"):
            family_name = family_name[:-4]

        flag_data_collection = collector.process_family(
            doc=doc, root_name=family_name, root_category=family_category_name
        )

        output(
            "{}.... status: {}".format(
                flag_data_collection.message, flag_data_collection.status
            ),
            revit_script_util.Output,
        )
        # write data to file
        for p in processor_instances:
            processor = next(
                processor
                for processor in processor_instances
                if processor.data_type == p.data_type
            )
            flag_report = report_data(processor, p.data_type)
            output(
                "{}.... status: {}".format(flag_report.message, flag_report.status),
                revit_script_util.Output,
            )
    else:
        output("Failed to create by category output folder!", revit_script_util.Output)
else:
    output("Failed to create by session ID output folder!", revit_script_util.Output)
