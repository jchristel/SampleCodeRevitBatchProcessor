#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a post process script after xml part atoms are created.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- combines part atoms into one csv report

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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
import os
import csv

import settings as settings  # sets up all commonly used variables and path locations!

# import script_util
import script_util
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.console_out import output
from duHast.Revit.Family.Reporting.report_fam_types_from_XML import get_family_type_data_from_library_xml
from duHast.Revit.Family.Reporting.families_report_header import LIBRARY_FAMILIES_HEADER
from duHast.Revit.RBP.Objects.ProgressRBPConsole import ProgressRBPConsole
from duHast.Utilities.files_csv import write_report_data_as_csv

# directories to process
PROCESS_DIRECTORIES = [
    settings.PATH_TO_CLINICAL_LIBRARY, 
    settings.PATH_TO_BESPOKE_JOINERY_LIBRARY, 
    settings.PATH_TO_UNIONS_LIBRARY,
]

def report_families_in_library_entry(process_directories):
    """
    Combines part atoms into one csv report

    :param process_directories: list of directories to process
    :type process_directories: [str]

    :return: Result object
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()
    family_data= []

    validated_directories = []

    output("Checking directories", script_util.Output)
    # check if directories exist
    for process_dir in process_directories:
        if not os.path.exists(process_dir):
            output("Directory does not exist: {}".format(process_dir), script_util.Output)
        else:
            output("Processing directory: {}".format(process_dir), script_util.Output)
            validated_directories.append(process_dir)

    if len(validated_directories) == 0:
        return_value.update_sep(False, "No directories to process left after validation.")
        return return_value
    
    try:

        # set up a call back for pyRevit progressbar
        progress_callback = ProgressRBPConsole(script_util.Output)

        output("Reporting families in library:", script_util.Output)
        report_result = get_family_type_data_from_library_xml( 
            process_directories=validated_directories,
            progress_callback=progress_callback
        )

        output("Finished reading families in library", script_util.Output)

        # update return value with comparison result
        return_value.update(report_result)
        if report_result.status == False:
            output("Failed to get family data from library with exception: {}".format(report_result.message), script_util.Output)
            return return_value

        # store report result
        family_data = report_result.result
       
        output("Rows before filter: {}".format(len(family_data)), script_util.Output)

        # filter data
        family_data = settings.filter_xml_data(family_data)

        output("Rows after filter: {}".format(len(family_data)), script_util.Output)
       
        output("Finished reading families in library with status: {}".format(report_result.status), script_util.Output)

        output("Writing report to csv file", script_util.Output)

        # pop a warning to user that this might take a while if rows exceed 10000
        if len(family_data) > 10000:
            output("This might take a while...rows to save: {}".format(len(family_data)), script_util.Output)

        # save report to csv file
        file_path = os.path.join(settings.OUTPUT_FOLDER, settings.COMBINED_REPORT_NAME_LIBRARY_FAMILIES)

        if (file_path and len(file_path) > 0):
            write_result = write_report_data_as_csv(file_name=file_path, header= LIBRARY_FAMILIES_HEADER,  data=family_data, quoting=csv.QUOTE_MINIMAL)
            if(write_result.status):
                return_value.append_message("Succefully wrote families report to: {} ".format(file_path))
            else:
                return_value.update_sep(False, "Failed to write families report to: {} ".format(write_result.status))
            output("Finished writing report to csv file: {} with status: {}".format(file_path, write_result.status), script_util.Output)
                
        else:
            return_value.append_message("No file path selected")
    
    except Exception as e:
        return_value.update_sep(
            False, "Failed to compare families with exception: {}".format(e)
        )

    output("{}".format(return_value.message), script_util.Output)
    output("Finished", script_util.Output)

    return return_value

# run the script to combine part atom exports into one csv report
report_families_in_library_entry(PROCESS_DIRECTORIES)