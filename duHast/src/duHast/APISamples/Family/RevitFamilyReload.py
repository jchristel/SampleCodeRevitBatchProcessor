'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to load or reload families 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

clr.AddReference('System')
from System.Collections.Generic import List


# import common library
from duHast.APISamples.Common import RevitDeleteElements as rDel

from duHast.Utilities import Result as res , FilesGet as fileGet
from duHast.APISamples.Family import RevitFamilyUtils as rFamUtil
from duHast.APISamples.Family import RevitFamilyLoadOption as famLoadOpt
from duHast.APISamples.Family.RevitFamilyLoadOption import *
from duHast.APISamples.Family.Utility import LoadableFamilyCategories as rFamLoadable

import Autodesk.Revit.DB as rdb

# --------------------------------------------------- Family Loading / inserting -----------------------------------------

def reload_all_families(doc, libraryLocation, includeSubFolders):
    '''
    Reloads a number of families with setting: parameter values overwritten: True


    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param libraryLocation: _description_
    :type libraryLocation: str
    :param includeSubFolders: _description_
    :type includeSubFolders: bool
    
    :raises UserWarning: _description_
    
    :return: Returns True if any of the reload actions was successful.
    :rtype: bool
    '''

    result = res.Result()
    # if a family is reloaded it may bring in new types not present in the model at reload
    # this list contains the ids of those types (symbols)
    # so they can be deleted if so desired
    symbolIdsToBeDeleted = []   
    try:
        # build library
        library = fileGet.files_as_dictionary(libraryLocation,'','','.rfa',includeSubFolders)
        if(len(library) == 0):
            result.update_sep(False, 'Library is empty!')
            # get out...
            raise UserWarning('Empty Library')
        else:
            result.append_message('Found: {} families in Library!'.format(len(library)))
        # get all families in file:
        familyIds = get_family_ids_from_symbols(doc)
        if(len(familyIds) > 0):
            result.append_message('Found:  {} loadable families in file.'.format(len(familyIds)))
            for famId in familyIds:
                fam = doc.GetElement(famId)
                famName = rdb.Element.Name.GetValue(fam)
                if(famName in library):
                    result.append_message('Found match for: {}'.format(famName))
                    if(len(library[famName]) == 1 ):
                        # found single match for family by name
                        result.update_sep(True, 'Found single match: {}'.format(library[famName][0]))
                        # get all symbols attached to this family by name
                        priorLoadSymbolIds = fam.GetFamilySymbolIds()
                        # reload family
                        resultLoad = rFamUtil.load_family(doc, library[famName][0])
                        result.append_message(resultLoad.message)
                        if(resultLoad.status == True):
                            # make sure that if a single reload was successful that this method returns true
                            result.status = True
                            # remove symbols (family types) added through reload process
                            if (resultLoad.result != None and len(resultLoad.result) > 0):
                                famLoaded = resultLoad.result.First()
                                afterLoadSymbolIds = famLoaded.GetFamilySymbolIds()
                                newSymbolIds = get_new_symbol_ids(priorLoadSymbolIds, afterLoadSymbolIds)
                                if(len(newSymbolIds) > 0):
                                    symbolIdsToBeDeleted = symbolIdsToBeDeleted + newSymbolIds
                    else:
                        matchesMessage = ''
                        for path in library[famName]:
                            matchesMessage = matchesMessage + '...' + path + '\n'
                        matchesMessage = 'Found multiple matches for {} \n {}'.format(famName, matchesMessage)
                        matchesMessage = matchesMessage.strip()
                        # found multiple matches for family by name only...aborting reload
                        result.append_message(matchesMessage)
                else:
                    result.update_sep(result.status,'Found no match for: {}'.format(famName))
            # delete any new symbols introduced during the reload
            if(len(symbolIdsToBeDeleted)>0):
                resultDelete = rDel.delete_by_element_ids(doc, symbolIdsToBeDeleted, 'Delete new family types', 'Family types')
                result.append_message (resultDelete.message)
            else:
                message = 'No need to delete any new family types since no new types where created.'
                result.append_message(message) # make sure not to change the status
        else:
            message = 'Found no loadable families in file!'
            result.update_sep(False, message)
    except Exception as e:
        message = 'Failed to load families with exception: {}'.format(e)
        result.update_sep(False, message)
    return result

def get_family_ids_from_symbols(doc):
    '''
    Get all loadable family ids in file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing loadable families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    familyIds = []
    # build list of all categories we want families to be reloaded of
    famCats = List[rdb.BuiltInCategory] (rFamLoadable.CATEGORIES_LOADABLE_TAGS)
    famCats.AddRange(rFamLoadable.CATEGORIES_LOADABLE_TAGS_OTHER) 
    famCats.AddRange(rFamLoadable.CATEGORIES_LOADABLE_3D)
    famCats.AddRange(rFamLoadable.CATEGORIES_LOADABLE_3D_OTHER)
    # get all symbols in file
    famSymbols = rFamUtil.get_family_symbols(doc, famCats)
    # get families from symbols and filter out in place families
    for famSymbol in famSymbols:
        if (famSymbol.Family.Id not in familyIds and famSymbol.Family.IsInPlace == False):
            familyIds.append(famSymbol.Family.Id)
    return familyIds

def get_new_symbol_ids(preLoadSymbolIdList, afterLoadSymbolList):
    '''
    Returns a list of symbol ids not present prior to reload.

    Compares past in list of id's and returns ids not in preloadSymbolIdList

    :param preLoadSymbolIdList: List of Ids of symbols prior the reload.
    :type preLoadSymbolIdList: list of Autodesk.Revit.DB.ElementId
    :param afterLoadSymbolList: List of ids of symbols after the reload.
    :type afterLoadSymbolList: list of Autodesk.Revit.DB.ElementId
    
    :return: List of element ids representing Family Symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for id in afterLoadSymbolList:
        if (id not in preLoadSymbolIdList):
            ids.append(id)
    return ids