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
# Copyright © 2023, Jan Christel
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
from duHast.Revit.Common import delete as rDel

from duHast.Utilities import files_get as fileGet
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family import family_utils as rFamUtil
from duHast.Revit.Family import family_load_option as famLoadOpt
from duHast.Revit.Family.family_load_option import *
from duHast.Revit.Family.Utility import loadable_family_categories as rFamLoadable

import Autodesk.Revit.DB as rdb

# --------------------------------------------------- Family Loading / inserting -----------------------------------------


def reload_all_families(doc, library_location, include_sub_folders):
    """
    Reloads a number of families with setting: parameter values overwritten: True


    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param library_location: _description_
    :type library_location: str
    :param include_sub_folders: _description_
    :type include_sub_folders: bool

    :raises UserWarning: _description_

    :return: Returns True if any of the reload actions was successful.
    :rtype: bool
    """

    result = res.Result()
    # if a family is reloaded it may bring in new types not present in the model at reload
    # this list contains the ids of those types (symbols)
    # so they can be deleted if so desired
    symbol_ids_to_be_deleted = []
    try:
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
        if len(family_ids) > 0:
            result.append_message(
                "Found:  {} loadable families in file.".format(len(family_ids))
            )
            for fam_id in family_ids:
                fam = doc.GetElement(fam_id)
                fam_name = rdb.Element.Name.GetValue(fam)
                if fam_name in library:
                    result.append_message("Found match for: {}".format(fam_name))
                    if len(library[fam_name]) == 1:
                        # found single match for family by name
                        result.update_sep(
                            True, "Found single match: {}".format(library[fam_name][0])
                        )
                        # get all symbols attached to this family by name
                        prior_load_symbol_ids = fam.GetFamilySymbolIds()
                        # reload family
                        result_load = rFamUtil.load_family(doc, library[fam_name][0])
                        result.append_message(result_load.message)
                        if result_load.status == True:
                            # make sure that if a single reload was successful that this method returns true
                            result.status = True
                            # remove symbols (family types) added through reload process
                            if (
                                result_load.result != None
                                and len(result_load.result) > 0
                            ):
                                fam_loaded = result_load.result[0]
                                after_load_symbol_ids = fam_loaded.GetFamilySymbolIds()
                                new_symbol_ids = get_new_symbol_ids(
                                    prior_load_symbol_ids, after_load_symbol_ids
                                )
                                if len(new_symbol_ids) > 0:
                                    symbol_ids_to_be_deleted = (
                                        symbol_ids_to_be_deleted + new_symbol_ids
                                    )
                    else:
                        matches_message = ""
                        for path in library[fam_name]:
                            matches_message = matches_message + "..." + path + "\n"
                        matches_message = "Found multiple matches for {} \n {}".format(
                            fam_name, matches_message
                        )
                        matches_message = matches_message.strip()
                        # found multiple matches for family by name only...aborting reload
                        result.append_message(matches_message)
                else:
                    result.update_sep(
                        result.status, "Found no match for: {}".format(fam_name)
                    )
            # delete any new symbols introduced during the reload
            if len(symbol_ids_to_be_deleted) > 0:
                result_delete = rDel.delete_by_element_ids(
                    doc,
                    symbol_ids_to_be_deleted,
                    "Delete new family types",
                    "Family types",
                )
                result.append_message(result_delete.message)
            else:
                message = "No need to delete any new family types since no new types where created."
                result.append_message(message)  # make sure not to change the status
        else:
            message = "Found no loadable families in file!"
            result.update_sep(False, message)
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


def get_new_symbol_ids(pre_load_symbol_id_list, after_load_symbol_list):
    """
    Returns a list of symbol ids not present prior to reload.

    Compares past in list of id's and returns ids not in preloadSymbolIdList

    :param pre_load_symbol_id_list: List of Ids of symbols prior the reload.
    :type pre_load_symbol_id_list: list of Autodesk.Revit.DB.ElementId
    :param after_load_symbol_list: List of ids of symbols after the reload.
    :type after_load_symbol_list: list of Autodesk.Revit.DB.ElementId

    :return: List of element ids representing Family Symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    for id in after_load_symbol_list:
        if id not in pre_load_symbol_id_list:
            ids.append(id)
    return ids
