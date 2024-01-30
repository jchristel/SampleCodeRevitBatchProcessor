"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is the actual script batch processor executes per family file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It reads the report file and saves out any nested family found not present in report.

Host families are not saved.

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

import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.console_out import output

# family data processors
from duHast.Revit.Family.Data.Objects.family_base_data_processor import (
    FamilyBaseProcessor,
)

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

# -------------
# my code here:
# -------------

# -------------
# main:
# -------------

# save revit file to new location
output(
    "Writing out missing families .... start",
    revit_script_util.Output,
)

# check whether missing families are to be written to file
# missing families are families which do not appear as root families in base family data report
(
    save_out_missing_families,
    base_data_report_file_path,
    family_out_root_directory,
) = settings.SaveOutMissingFamiliesCheck()

# update available processor instances accordingly
if save_out_missing_families:
    # Set up list containing all family processor instances to be executed per family.
    processors = [
        FamilyBaseProcessor(
            base_data_report_file_path,  # reference list of known families
            family_out_root_directory,  # where to write families to
            SESSION_ID,  # session id to make sure families are written to unique folder
        )
    ]
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    fam_name = doc.Title
    # strip .rfa of name
    if fam_name.lower().endswith(".rfa"):
        fam_name = fam_name[:-4]

    # process family (and save missing fams out)
    collector = RevitFamilyDataCollector(processors)
    flag_data_collection = collector.processFamily(doc, fam_name, family_category_name)

    output(
        "{} .... status: {}".format(
            flag_data_collection.message, flag_data_collection.status
        ),
        revit_script_util.Output,
    )

else:
    output(
        "Failed to read data required to save out missing families!",
        revit_script_util.Output,
    )
