"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as the task script in Revit batch processor.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- creates family types XML exports from families in library directory

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
from duHast.UI.file_list import  get_revit_files
from duHast.Revit.RBP.Objects.ProgressRBPConsole import ProgressRBPConsole
from duHast.Revit.Family.family_types_get_data_from_xml import write_data_to_xml_file
from duHast.Utilities.files_io import get_file_name_without_ext

# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\Users\jchristel\Documents\Temp\Debug.rvt"

import clr
import System
import os

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

# process all files in a given directory
# processes all files in a given directory
# works with one revit session only (might be slow for large directories with many files at initial run)
# get family files in directory
# get XML files in directory
# checks if XML type file exists:
# if not, creates XML type file
# if it does: check if XML file is older than family file
# if it is, update XML file
# if not, skip

def get_families_from_directory(directory):
    family_files = get_revit_files(directory, "*.rfa")
    return family_files

def get_xml_files_from_directory(directory):
    xml_files = get_revit_files(directory, "*.xml")
    return xml_files

def get_families_requiring_update(family_files, xml_files):

    family_files_to_update = []
    # loop over family files
    for fam_file in family_files:
        #output("checking family: {}".format(fam_file.name), revit_script_util.Output)
        # and find a matching xml file
        xml_file = os.path.splitext(fam_file.name)[0] + ".xml"
        #output("...looking for xml: {}".format(xml_file), revit_script_util.Output)
        # if the xml file does not exist
        if xml_file in xml_files:
            #output("...found matching xml file", revit_script_util.Output)
            # if the xml file is older than the family file
            if os.path.getmtime(xml_file) < os.path.getmtime(fam_file.name):
                #output("...xml file is older than family file, needs updating", revit_script_util.Output)
                # family xml file is older than family file, needs updating
                family_files_to_update.append(fam_file.name)
            else:
                # family xml file is up to date
                pass
                #output("...xml file is up to date", revit_script_util.Output)
                
        else:
            #output("...no matching xml file found", revit_script_util.Output)
            # no matching xml file found
            family_files_to_update.append(fam_file.name)
    return family_files_to_update

def create_xml_file(revit_application, family_file):
    xml_file = os.path.splitext(family_file)[0] + ".xml"
    result = write_data_to_xml_file(revit_application, family_file, xml_file)
    print(result)
    

# directories to process
PROCESS_DIRECTORIES = [
    settings.PATH_TO_CLINICAL_LIBRARY, 
    settings.PATH_TO_BESPOKE_JOINERY_LIBRARY, 
    settings.PATH_TO_UNIONS_LIBRARY,
]

output("Processing directories: {}".format(PROCESS_DIRECTORIES), revit_script_util.Output)

# loop through directories
for directory in PROCESS_DIRECTORIES:
    output("Processing directory: {}".format(directory), revit_script_util.Output)
    
    families = get_families_from_directory(directory=directory)
    output("Families found: {}".format(len(families)), revit_script_util.Output)
    
    xml_files = get_xml_files_from_directory(directory=directory)
    output("XML files found: {}".format(len(xml_files)), revit_script_util.Output)

    families_to_update = get_families_requiring_update(families, xml_files)
    output("Families requiring update: {}".format(len(families_to_update)), revit_script_util.Output)

    if families_to_update:
        
        # set up progress 
        fam_counter = 0
        max_fam = len(families_to_update)
        progress = ProgressRBPConsole(revit_script_util.Output)
        progress.update(0,max_fam,"Creating XML file(s) for families:")
        
        
        # iterate through families
        for family in families_to_update:
            fam_name = get_file_name_without_ext(family)
            progress.update(fam_counter, max_fam, "Creating XML file for: {}".format(fam_name))
            create_xml_file(doc.Application, family)
            # update counter
            fam_counter += 1

