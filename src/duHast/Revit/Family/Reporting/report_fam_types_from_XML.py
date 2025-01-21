"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing reporting family type reporting functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reports:

- if family does not exist in library
- if type does not exist in library
- if a parameter value for a given type is different to the parameter value for that type in the library

"""

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

import os

from Autodesk.Revit.DB import Family

from duHast.Revit.Family.Utility.xml_family_type_reader import read_xml_into_storage
from duHast.Revit.Family.family_types_get_data_from_xml import get_type_data_via_XML_from_family_object
from duHast.Revit.Family.family_functions import get_name_to_family_dict
from duHast.Utilities.files_xml import read_xml_file, get_xml_files_from_directory
from duHast.Utilities.files_io import get_file_name_without_ext, get_directory_path_from_file_path
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects.result import Result
from duHast.UI.Objects.ProgressBase import ProgressBase


def get_all_xml_files_from_directories(process_directories):

    files_found = []
    try:
        # get all xml files from the directory
        for directory in process_directories:
            files = get_xml_files_from_directory(directory)
            files_found = files_found + files
    except Exception as e:
        raise Exception("Failed to gather xml files with exception: {}".format(e))
    return files_found


def get_type_data_from_library(xml_files_in_libraries, progress_callback=None):

    return_value = Result()
    type_data = []
    try:

        # set progress counter
        counter = 0
        max_value_xml = len(xml_files_in_libraries)

        # update progress
        if progress_callback:
            progress_callback.update(counter, max_value_xml)

        # get the type data from the library
        for xml_file in xml_files_in_libraries:

            # update progress
            if progress_callback:
                progress_callback.update(counter,  max_value_xml )

            # read xml file
            xml_doc_status = read_xml_file(xml_file.name)
            if(xml_doc_status == False):
                return_value.update_sep(False, "Failed to read xml file: {} with exception: {}".format(xml_file.name, xml_doc_status.message))
                # update progress
                counter = counter + 1
                continue
            
            # get the xml document
            xml_doc = xml_doc_status.result
            if  xml_doc is None:
                return_value.update_sep(False, "Failed to read xml file: {}".format(xml_file.name))
                # update progress
                counter = counter + 1
                continue

            # build the family path (required for xml data)
            fam_name = get_file_name_without_ext(xml_file.name)
            fam_directory = get_directory_path_from_file_path(xml_file.name)
            fam_path = os.path.join(fam_directory, fam_name + ".rfa")
            
            # load xml data into storage
            return_value.append_message("loading family: {}".format(fam_name))
            xml_data_family = read_xml_into_storage(xml_doc, fam_name, fam_path)
            
            # add storage to global list
            type_data.append(xml_data_family)

            # update progress
            counter = counter + 1

            # check for user cancel
            if progress_callback != None:
                if progress_callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break
    
    except Exception as e:
        return_value.update_sep(False, "Failed to gather family data with exception: {}".format(e))
    
    # store data to be returned
    return_value.result = type_data

    return return_value


def get_type_data_from_project_file(doc, type_data_from_library, progress_callback=None):
    return_value = Result()
    matched_data = []
    try:
        
        # get all families in the project
        families_loaded = get_name_to_family_dict(doc)

        # set progress counter
        counter = 0
        max_value_xml = len(families_loaded)

        # loop over loaded families and search for matches based on name and category
        for fam_name, revit_family in families_loaded.items():
            
            # update progress
            if progress_callback:
                progress_callback.update(counter,  max_value_xml )

            # check this is a family
            if isinstance(revit_family, Family) is False:
                return_value.append_message("skipping family: {} as it is not a family".format(fam_name))
                continue

            # ignore in place families
            if revit_family.IsInPlace:
                continue

            # get the family category
            fam_cat = revit_family.FamilyCategory.Name

            # get the family type data storage from the library
            found_match = False
            match_library = None
            for type_data_storage_manager_library in type_data_from_library:
                if type_data_storage_manager_library.family_type_data_storage[0].family_name == fam_name and type_data_storage_manager_library.family_type_data_storage[0].root_category_path == fam_cat:
                    # found a match...
                    found_match = True
                    match_library = type_data_storage_manager_library
                    break

            # check if match in library was found
            if found_match is False:
                # no match found
                matched_data.append(([fam_name,fam_cat ], None))
                continue

            # create temp xml files from laoded family
            type_data_result = get_type_data_via_XML_from_family_object(revit_family=revit_family)
            if (type_data_result.status == False):
                return_value.update_sep(False,"Failed to get type data from family: {} with exception: {}".format(fam_name, type_data_result.message))
                matched_data.append((type_data_storage_manager_loaded_fam, None))
                continue

            # get the type data of the family
            type_data_storage_manager_loaded_fam = type_data_result.result[0]
            # add to matched data
            matched_data.append((type_data_storage_manager_loaded_fam, match_library))

            # update progress
            counter = counter + 1

            # check for user cancel
            if progress_callback != None:
                if progress_callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break

    except Exception as e:
        return_value.update_sep(False, "Failed to gather family data with exception: {}".format(e))
    
    # store data to be returned
    return_value.result = matched_data

    return return_value


def build_comparison_report(type_data_matches, ignore_list_path):

    not_in_library = []
    diff = []
    return_value = Result()
    try:

        # get ignore data
        ignore_data = []
        if(ignore_list_path != None):
            ignore_data_result = read_csv_file(ignore_list_path)
            if ignore_data_result.status == False:
                return_value.update_sep(False, ignore_data_result.message)
                return return_value
            else:
                ignore_data = ignore_data_result.result

        # loop over the data and compare
        for entry in type_data_matches:
            fam_name = ""
            fam_category = ""

            # get name and catgegory ( for non matched familie this may just be a list of name and category rather than a storage object)
            if (isinstance(entry[0], list)):
                fam_name = entry[0][0]
                fam_category = entry[0][1]
            else: 
                # assume there is at least one entry in the storage object
                fam_name = entry[0].family_type_data_storage[0].family_name
                fam_category = entry[0].family_type_data_storage[0].root_category_path


            # check if the family is in ignore list based on name and category
            ignore = False
            for ignore_entry in ignore_data:
                if ignore_entry[0] == fam_name and ignore_entry[1] == fam_category:
                    ignore = True
                    break
            if ignore:
                continue

            if (entry[1] == None):
                if("{}{}".format(fam_name, fam_category) not in not_in_library):
                    not_in_library.append("{}{}".format(fam_name, fam_category))
                    # family not found in library
                    diff.append([fam_name,  fam_category, "No match in library"])
                continue
            else:
                # compare the two data sets
                diff = diff + entry[0].get_difference(entry[1])

    except Exception as e:
        return_value.update_sep(False, "Failed to gather family data with exception: {}".format(e))
    
    # store data to be returned
    return_value.result = diff

    return return_value


def compare_family_files_against_library(doc, process_directories, ignore_list_path = None, progress_callback=None):

    return_value = Result()

    # check callback class
    if progress_callback and isinstance(progress_callback, ProgressBase) == False:
        raise TypeError(
            "progress_callback needs to be inherited from ProgressBase. Got : {} instead.".format(
                type(progress_callback)
            )
        )
    
    #set up a timer
    t=Timer()
    t.start()

    try:

        # get all xml files from the directory representing families in the library (point of truth)
        xml_files_in_libraries = get_all_xml_files_from_directories(process_directories)

        # check if any xml files were found
        if len(xml_files_in_libraries) == 0:
            return_value.update_sep(False, "No XML files found in the directories: {}".format(process_directories))
            return_value.append_message(t.stop())
            return return_value
        else:
            return_value.append_message("Found {} XML files in the directories: {}".format(len(xml_files_in_libraries), process_directories))

        # get the type data from the library
        type_data_from_library_result = get_type_data_from_library(xml_files_in_libraries, progress_callback)

        # check if the type data from the library was successfully gathered
        if type_data_from_library_result.status == False or len(type_data_from_library_result.result)==0:
            return_value.update_sep(False, type_data_from_library_result.message)
            return_value.append_message(t.stop())
            return return_value
        else:
            return_value.append_message("Successfully gathered family type data from the library.")

        # get type data from the family files in project file
        type_data_from_project_result = get_type_data_from_project_file(doc, type_data_from_library_result.result, progress_callback)

        # check if the type data from the project file was successfully gathered
        if type_data_from_project_result.status == False or len(type_data_from_project_result.result)==0:
            return_value.update_sep(False, type_data_from_project_result.message)
            return_value.append_message(t.stop())
            return return_value
        else:
            return_value.append_message("Successfully gathered family type data from the project file.")

        # compare the data
        comparison_report_result = build_comparison_report(type_data_from_project_result.result, ignore_list_path)
        if comparison_report_result.status == False:
            return_value.update_sep(False, comparison_report_result.message)
            return_value.append_message(t.stop())
            return return_value
        else:
            return_value.append_message("Successfully compared family type data from project file against library.")
            return_value.append_message(t.stop())

        # store the comparison report as sorted list by family name
        sorted_list = sorted(comparison_report_result.result, key=lambda x: x[0])
        return_value.result = sorted_list

    except Exception as e:
        return_value.update_sep(
            False, "Failed to gather family data with exception: {}".format(e)
        )
        return_value.append_message(t.stop())
    
    return return_value