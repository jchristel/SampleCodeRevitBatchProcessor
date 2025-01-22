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
import datetime

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
    """
    Get all family files from a directory. (ignores subdirectories)
    
    :param directory: directory to search for family files
    :type directory: str

    :return: list of family files
    :rtype: [FileItem]
    """

    family_files = get_revit_files(directory, "*.rfa")
    return family_files

def get_xml_files_from_directory(directory):
    """
    Get all xml files from a directory. (ignores subdirectories)

    :param directory: directory to search for xml files
    :type directory: str

    :return: list of xml files
    :rtype: [FileItem]
    """

    xml_files = get_revit_files(directory, "*.xml")
    return xml_files

def check_file_item_exists(instances, name_to_check):
    """
    Check if a file item exists in a list of file items based on the name property.

    :param instances: list of file items
    :type instances: [FileItem]
    :param name_to_check: name to check
    :type name_to_check: str

    :return: True if a file item with the name exists, False otherwise
    :rtype: bool
    """

    return any(instance.name == name_to_check for instance in instances)

def get_families_requiring_update(family_files, xml_files):

    """
    Get all family files that require updating. A family file requires updating if the corresponding xml file does not exist or is older than the family file.

    :param family_files: list of family files
    :type family_files: [FileItem]
    :param xml_files: list of xml files
    :type xml_files: [FileItem]

    :return: list of family files that require updating
    :rtype: [str]
    """

    family_files_to_update = []
    # loop over family files
    for fam_file in family_files:

        # and find a matching xml file
        xml_file = os.path.splitext(fam_file.name)[0] + ".xml"
       
        # check if the xml file does exist
        if check_file_item_exists(xml_files,xml_file):
            
            # get time stamp of files
            xml_file_time_stamp = os.path.getmtime(xml_file)
            rfa_file_time_stamp = os.path.getmtime(fam_file.name)
            
            # convert to something human readable
            xml_formatted_time = datetime.datetime.fromtimestamp(xml_file_time_stamp)
            rfa_formatted_time = datetime.datetime.fromtimestamp(rfa_file_time_stamp)
            
            # if the xml file is older than the family file
            if xml_file_time_stamp < rfa_file_time_stamp:
                
                output("...xml file is older than family file, needs updating. [xml: {} vs rfa: {}]".format(xml_formatted_time, rfa_formatted_time), revit_script_util.Output)
                # family xml file is older than family file, needs updating
                family_files_to_update.append(fam_file.name)
            else:
                # family xml file is up to date
                pass
                
        else:
            # no matching xml file found
            family_files_to_update.append(fam_file.name)

    return family_files_to_update

def create_xml_file(revit_application, family_file):
    """
    Create an xml file for a given family file.

    :param revit_application: revit application object
    :type revit_application: Application
    :param family_file: family file to create xml file for
    :type family_file: str
    """

    xml_file = os.path.splitext(family_file)[0] + ".xml"
    result = write_data_to_xml_file(revit_application, family_file, xml_file)
    print(result)
    

# directories to process
PROCESS_DIRECTORIES = [
    settings.PATH_TO_CLINICAL_LIBRARY, 
    settings.PATH_TO_BESPOKE_JOINERY_LIBRARY, 
    settings.PATH_TO_UNIONS_LIBRARY,
]

output("Processing directories: \n{}".format("\n".join(PROCESS_DIRECTORIES)), revit_script_util.Output)

# loop through directories
for directory in PROCESS_DIRECTORIES:
    output("Processing directory: {}".format(directory), revit_script_util.Output)
    
    families = get_families_from_directory(directory=directory)
    output("Families found: {}".format(len(families)), revit_script_util.Output)
    
    xml_files = get_xml_files_from_directory(directory=directory)
    output("XML files found: {}".format(len(xml_files)), revit_script_util.Output)

    families_to_update = get_families_requiring_update(families, xml_files)
    output("Families requiring update: {}".format(len(families_to_update)), revit_script_util.Output)

    # if there are families to update
    if families_to_update:
        
        # set up progress 
        fam_counter = 0
        max_fam = len(families_to_update)
        # create progress , and pipe messages to Revit BatchProcessor console
        progress = ProgressRBPConsole(revit_script_util.Output)
        progress.update(0,max_fam,"Creating XML file(s) for families:")
        
        # iterate through families
        for family in families_to_update:
            fam_name = get_file_name_without_ext(family)
            progress.update(fam_counter, max_fam, "Creating XML file for: {}".format(fam_name))
            create_xml_file(doc.Application, family)
            # update counter
            fam_counter += 1

