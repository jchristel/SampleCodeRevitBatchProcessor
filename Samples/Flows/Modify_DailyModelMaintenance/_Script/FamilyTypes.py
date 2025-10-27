#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as the task script in Revit batch processor.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- creates family types XML exports from families in library directory

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

# import common library
import settings as settings  # sets up all commonly used variables and path locations!
from duHast.Utilities.console_out import output
from duHast.Utilities.Objects.result import Result
from duHast.Revit.RBP.Objects.ProgressRBPConsole import ProgressRBPConsole
from duHast.Revit.Family.Utility.xml_create_atom_exports import create_family_xml_files
from duHast.Revit.Family.Utility.xml_remove_obsolete_exports import remove_obsolete_part_atom_exports


# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\Users\jchristel\Documents\Temp\Debug.rvt"

import clr

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util

    clr.AddReference("RevitAPI")
    clr.AddReference("RevitAPIUI")
    # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name
    revitFilePath_ = DEBUG_REVIT_FILE_NAME



# directories to process
PROCESS_DIRECTORIES = [
    settings.PATH_TO_CLINICAL_LIBRARY, 
    settings.PATH_TO_BESPOKE_JOINERY_LIBRARY, 
    settings.PATH_TO_UNIONS_LIBRARY,
]


def create_part_atom_exports_in_library_entry(doc , process_directories):
    """
    Entry point for creating family types XML exports from families in library directory.

    :param doc: Revit document
    :param type: Document
    :param process_directories: directories to process
    :type process_directories: [str]

    :return: Result object
    :rtype: Result
    """
    
    # set up a status tracker
    return_value = Result()

    try:

        output("Processing directories:", revit_script_util.Output)
        for directory in process_directories:
            output("...{}".format(directory), revit_script_util.Output)

        # set up a call back for pyRevit progressbar
        progress_callback = ProgressRBPConsole(revit_script_util.Output)

        output("Creating family xml exports in library:", revit_script_util.Output)

        # create the xml files
        create_result = create_family_xml_files(
            revit_application=doc.Application,
            process_directories=process_directories,
            process_directories_to_local_directories_mapper=settings.NETWORK_PATH_MAPPER,
            use_temp_directory=False,
            progress_callback=progress_callback
        )

        return_value.update(create_result)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to create families exports exception: {}".format(e)
        )

    output("{}".format(return_value.message), revit_script_util.Output)
    
    return return_value

def remove_orphaned(process_directories):
    """
    Remove any orphaned xml files from the directories.

    :param process_directories: directories to process
    :type process_directories: [str]

    :return: None
    """
    remove_result = remove_obsolete_part_atom_exports(
        process_dirs=process_directories
    )
    output("{}".format(remove_result.message), revit_script_util.Output)


try:
    output("Starting FamilyTypes script", revit_script_util.Output)
    output("Revit File: {}".format(revitFilePath_), revit_script_util.Output)
    if debug_:
        output("Running in Debug mode", revit_script_util.Output)
    else:
        output("Running in Batch Processor mode", revit_script_util.Output)
    
    # run the script to create family types XML exports from families in library directory
    create_part_atom_exports_in_library_entry(doc, PROCESS_DIRECTORIES)

    # remove any orphaned xml files
    remove_orphaned(PROCESS_DIRECTORIES)

except Exception as e:
    output("error {}".format(e), revit_script_util.Output)
    import traceback
    stack_trace = traceback.format_exc()
    output(stack_trace, revit_script_util.Output)
