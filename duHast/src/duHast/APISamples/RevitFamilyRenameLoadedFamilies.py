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

import clr
import System

from duHast.APISamples import RevitFamilyRenameFilesUtils as rFamRenameUtils
from duHast.APISamples import RevitFamilyUtils as rFamUtils
from duHast.APISamples import RevitTransaction as rTran
from duHast.Utilities import Result as res

# import Autodesk Revit DataBase namespace
import Autodesk.Revit.DB as rdb

def _renameLoadedFamilies(doc, renameDirectives, familyIds):
    '''
    Loops over nested families and if a match in rename directives is found will rename the family accordingly.

    :param doc: The current family document.
    :type doc: Autodesk.Revit.DB.Document
    :param renameDirectives: List of rename directives.
    :type renameDirectives: [renameDirective]
    :param familyIds: List of all nested family ids.
    :type familyIds: [Autodesk.Revit.DB.ElementId]

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

    returnValue = res.Result()
    returnValue.status = False
    renameMatchCounter = 0
    # loop over families and check for match in rename directives
    for famId in familyIds:
        family = doc.GetElement(famId)
        familyName = family.Name
        if(family.IsEditable and family.IsValidObject):
            familyCategoryName = family.FamilyCategory.Name
            # loop over rename directives and look for match in family name and category
            for renameDirective in renameDirectives:
                if(renameDirective.name == familyName and renameDirective.category == familyCategoryName):
                    renameMatchCounter = renameMatchCounter + 1
                    # rename this family
                    def action():
                        actionReturnValue = res.Result()
                        try:
                            family.Name = renameDirective.newName
                            actionReturnValue.UpdateSep(
                                True, 
                                'Renamed family of category [' + familyCategoryName + '] vs directive category [' + renameDirective.category + '] from: ' + renameDirective.name + ' to: ' + renameDirective.newName)
                        except Exception as e:
                            actionReturnValue.UpdateSep(
                                False, 
                                'Failed to rename family of category [' + familyCategoryName + '] vs directive category [' + renameDirective.category + '] from: ' + renameDirective.name + ' to: ' + renameDirective.newName)
                        return actionReturnValue
                    transaction = rdb.Transaction(doc, 'Renaming: ' + renameDirective.name)
                    renameResult = rTran.in_transaction(transaction, action)
                    if(renameResult.status):
                        # make sure that this returns true as soon as one family renamed successfully
                        returnValue.status = True
                    # update messages
                    returnValue.AppendMessage(renameResult.message)
                    break
    # check if anything got renamed at all
    if(renameMatchCounter == 0):
        returnValue.AppendMessage('No match for rename directives found. Nothing was renamed.')
    return returnValue


def RenameLoadedFamilies(doc, directoryPath):
    '''
    Entry point for this module. Will read rename directives files in given directory and attempt to rename
    loaded families accordingly.

    :param directoryPath: Fully qualified directory path to where rename directive files are located.
    :type directoryPath: str
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

    returnValue = res.Result()
    # get directives from folder
    renameDirectivesResult = rFamRenameUtils.GetRenameDirectives(directoryPath)
    # check if anything came back
    if(renameDirectivesResult.status):
        renameDirectives = renameDirectivesResult.result
        # get all family ids in file
        familyIds = rFamUtils.GetAllLoadableFamilyIdsThroughTypes(doc)
        if(len(familyIds) > 0):
            # rename files as per directives
            returnValue = _renameLoadedFamilies(doc, renameDirectives, familyIds)
        else:
            returnValue.UpdateSep(True, 'Mo loadable families in file.')
    else:
        returnValue = renameDirectivesResult

    return returnValue