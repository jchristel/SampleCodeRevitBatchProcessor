"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to load or reload families 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

clr.AddReference("System")
from System.Collections.Generic import List


# import common library

from duHast.Utilities import files_get as fileGet
from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_io import was_file_edited_in_time_span, time_span_file_edited_last
from duHast.Revit.Family import family_utils as rFamUtil
from duHast.Revit.Family.family_load_option import *
from duHast.Revit.Family.family_reload_single import reload_family

from duHast.Revit.Family.Utility import loadable_family_categories as rFamLoadable
from duHast.UI.Objects.ProgressBase import ProgressBase

import Autodesk.Revit.DB as rdb

# --------------------------------------------------- Family Loading / inserting -----------------------------------------





def reload_all_families(doc, library_location, include_sub_folders=False, time_span_in_minutes=None, progress_callback=None, delete_new_types=True, report_matches_only=False):
    """
    Reloads a number of families with setting: parameter values overwritten: True


    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param library_location: _description_
    :type library_location: str
    :param include_sub_folders: _description_
    :type include_sub_folders: bool
    :param time_span_in_minutes: the span of time in which the file was modified to be considered for reload, defaults to None
    :type time_span_in_minutes: int, optional
    :param progress_callback: a progress call back function, defaults to None
    :type progress_callback: ProgressBase, optional
    :param delete_new_types: If true, any new family types introduced during the reload will be deleted from the project. Default is True.
    :type delete_new_types: bool
    :param report_matches_only: If true, will only report on families where a reload attempt was made, defaults to False
    :type report_matches_only: bool, optional
    
    :raises UserWarning: _description_

    :return: Returns True if any of the reload actions was successful.
    :rtype: bool
    """

    result = res.Result()
    
    try:

        # type checking
        if progress_callback != None:
            if not isinstance(progress_callback, ProgressBase):
                raise TypeError("progress_callback must be an instance of ProgressBase")
        
        # build library
        library = fileGet.files_as_dictionary(
            library_location, "", "", ".rfa", include_sub_folders
        )
        if len(library) == 0:
            result.update_sep(False, "Library is empty!")
            # get out...
            raise UserWarning("Empty Library")
        else:
            result.append_message("Found: {} families in Library!".format(len(library)))
        
        # get all families in file:
        family_ids = get_family_ids_from_symbols(doc)

        # check if anything to reload
        if len(family_ids)==0:
            message = "Found no loadable families in file!"
            result.update_sep(False, message)
            return result

        # update result
        result.append_message(
            "Found:  {} loadable families in file.".format(len(family_ids))
        )

        # set up progress
        progress_max = len(family_ids)
        callback_counter = 0

        # loop over families in file and attempt reload
        for fam_id in family_ids:

            # progress call back
            callback_counter += 1

            # get the family
            fam = doc.GetElement(fam_id)
            # get the family name
            fam_name = rdb.Element.Name.GetValue(fam)

            # check if family name exists in library
            if fam_name not in library:
                # set appropriate message
                message = "Family: {} not found in library.".format(fam_name)
                # check if progress reporting is desired
                if progress_callback != None:
                    # only report progress if not in report matches only mode
                    if not (report_matches_only):
                        progress_callback.update(callback_counter, progress_max, message)
                
                result.update_sep(
                    result.status, message
                )

                # skip to next family
                continue

            # proceed with reload
            # check if progress callback is set
            if progress_callback != None:
                # only report progress if not in report matches only mode
                if not (report_matches_only):
                    progress_callback.update(callback_counter, progress_max, "Found match for: {}".format(fam_name))

            result.append_message("Found match for: {}".format(fam_name))

            # check number of matches found
            if len(library[fam_name]) != 1:
                matches_message = ""
                for path in library[fam_name]:
                    matches_message = matches_message + "..." + path + "\n"
                matches_message = "Found multiple matches for {} \n {}".format(
                    fam_name, matches_message
                )
                matches_message = matches_message.strip()
                # found multiple matches for family by name only...aborting reload
                result.append_message(matches_message)

                # check if progress callback is set
                if progress_callback != None:
                    progress_callback.update(callback_counter, progress_max, matches_message)
                
                # skip to next family
                continue

            # found single match for family by name
            result.update_sep(
                True, "Found single match: {}".format(library[fam_name][0])
            )

            # check if family was changed within time span, if not skip reload
            if time_span_in_minutes is not None:
                if was_file_edited_in_time_span(library[fam_name][0], time_span_in_minutes) == False:
                    time_last_edited = time_span_file_edited_last(library[fam_name][0])
                    result.append_message("Family {} was not modified within time span of {} minutes. Edited last: {} ago...skipping reload.".format(fam_name, time_span_in_minutes, time_last_edited))
                    continue

            # attempt to load the family:
            load_result = reload_family(
                doc=doc, 
                family=fam, 
                family_file_path=library[fam_name][0], 
                delete_new_types=delete_new_types
            )

            # check results
            if load_result.status == True:
                # make sure that if a single reload was successful that this method returns true
                result.status = True

            # preserve reload log messages
            result.append_message(load_result.message)

            # return the reloaded family, if there is one
            if len(load_result.result) > 0:
                result.result.append(load_result.result[0])

            # check if progress callback is set
            if progress_callback != None:
                progress_callback.update(callback_counter, progress_max, load_result.message)

        
    except Exception as e:
        message = "Failed to load families with exception: {}".format(e)
        result.update_sep(False, message)
    return result


def get_family_ids_from_symbols(doc):
    """
    Get all loadable family ids in file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing loadable families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    family_ids = []
    # build list of all categories we want families to be reloaded of
    fam_cats = List[rdb.BuiltInCategory](rFamLoadable.CATEGORIES_LOADABLE_TAGS)
    fam_cats.AddRange(rFamLoadable.CATEGORIES_LOADABLE_TAGS_OTHER)
    fam_cats.AddRange(rFamLoadable.CATEGORIES_LOADABLE_3D)
    fam_cats.AddRange(rFamLoadable.CATEGORIES_LOADABLE_3D_OTHER)
    # get all symbols in file
    fam_symbols = rFamUtil.get_family_symbols(doc, fam_cats)
    # get families from symbols and filter out in place families
    for fam_symbol in fam_symbols:
        if (
            fam_symbol.Family.Id not in family_ids
            and fam_symbol.Family.IsInPlace == False
        ):
            family_ids.append(fam_symbol.Family.Id)
    return family_ids
