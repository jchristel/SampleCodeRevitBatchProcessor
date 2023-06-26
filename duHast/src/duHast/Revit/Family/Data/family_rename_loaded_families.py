'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to rename family loaded families in a project file or family file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This helper function expect a folder containing rename directive files. For format of those files refer to module RevitFamilyRenameFilesUtils


'''



#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

#import clr
#import System

from duHast.Revit.Family import family_rename_files_utils as rFamRenameUtils
from duHast.Revit.Family import family_utils as rFamUtils
from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res

# import Autodesk Revit DataBase namespace
import Autodesk.Revit.DB as rdb

def _rename_loaded_families(doc, rename_directives, family_ids):
    '''
    Loops over nested families and if a match in rename directives is found will rename the family accordingly.

    :param doc: The current family document.
    :type doc: Autodesk.Revit.DB.Document
    :param rename_directives: List of rename directives.
    :type rename_directives: [rename_directive]
    :param family_ids: List of all nested family ids.
    :type family_ids: [Autodesk.Revit.DB.ElementId]

    :return: 
        Result class instance.

        - result.status. True if all families where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'Renamed family from :' +current Name + ' to ' + newName.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to rename family from :' + currentName + ' to ' + newName
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    return_value.status = False
    rename_match_counter = 0
    # loop over families and check for match in rename directives
    for fam_id in family_ids:
        family = doc.GetElement(fam_id)
        family_name = family.Name
        if(family.IsEditable and family.IsValidObject):
            family_category_name = family.FamilyCategory.Name
            # loop over rename directives and look for match in family name and category
            for rename_directive in rename_directives:
                if(rename_directive.name == family_name and rename_directive.category == family_category_name):
                    rename_match_counter = rename_match_counter + 1
                    # rename this family
                    def action():
                        action_return_value = res.Result()
                        try:
                            family.Name = rename_directive.newName
                            action_return_value.update_sep(
                                True, 
                                'Renamed family of category [' + family_category_name + '] vs directive category [' + rename_directive.category + '] from: ' + rename_directive.name + ' to: ' + rename_directive.newName)
                        except Exception as e:
                            action_return_value.update_sep(
                                False, 
                                'Failed to rename family of category [' + family_category_name + '] vs directive category [' + rename_directive.category + '] from: ' + rename_directive.name + ' to: ' + rename_directive.newName)
                        return action_return_value
                    transaction = rdb.Transaction(doc, 'Renaming: ' + rename_directive.name)
                    rename_result = rTran.in_transaction(transaction, action)
                    if(rename_result.status):
                        # make sure that this returns true as soon as one family renamed successfully
                        return_value.status = True
                    # update messages
                    return_value.append_message(rename_result.message)
                    break
    # check if anything got renamed at all
    if(rename_match_counter == 0):
        return_value.append_message('No match for rename directives found. Nothing was renamed.')
    return return_value


def rename_loaded_families(doc, directory_path):
    '''
    Entry point for this module. Will read rename directives files in given directory and attempt to rename
    loaded families accordingly.

    :param directory_path: Fully qualified directory path to where rename directive files are located.
    :type directory_path: str
    :return: 
        Result class instance.

        - result.status. True if a single families was renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'Renamed family from :' +current Name + ' to ' + newName.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to rename family from :' + currentName + ' to ' + newName
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # get directives from folder
    rename_directives_result = rFamRenameUtils.get_rename_directives(directory_path)
    # check if anything came back
    if(rename_directives_result.status):
        rename_directives = rename_directives_result.result
        # get all family ids in file
        family_ids = rFamUtils.get_all_loadable_family_ids_through_types(doc)
        if(len(family_ids) > 0):
            # rename files as per directives
            return_value = _rename_loaded_families(doc, rename_directives, family_ids)
        else:
            return_value.update_sep(True, 'Mo loadable families in file.')
    else:
        return_value = rename_directives_result

    return return_value