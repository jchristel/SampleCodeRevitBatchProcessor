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
from duHast.APISamples import RevitCommonAPI as com
from duHast.Utilities import Utility as util
from duHast.Utilities import Result as res
from duHast.APISamples import RevitFamilyUtils as rFamUtil
from duHast.APISamples import RevitFamilyLoadOption as famLoadOpt
from duHast.APISamples.RevitFamilyLoadOption import *

import Autodesk.Revit.DB as rdb

# --------------------------------------------------- Family Loading / inserting -----------------------------------------

def ReloadAllFamilies(doc, libraryLocation, includeSubFolders):
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
        library = util.FilesAsDictionary(libraryLocation,'','','.rfa',includeSubFolders)
        if(len(library) == 0):
            result.UpdateSep(False, 'Library is empty!')
            # get out...
            raise UserWarning('Empty Library')
        else:
            result.AppendMessage('Found ' + str(len(library)) + ' families in Library!')
        # get all families in file:
        familyIds = getFamilyIdsFromSymbols(doc)
        if(len(familyIds) > 0):
            result.AppendMessage('Found ' + str(len(familyIds)) + ' loadable families in file.')
            for famId in familyIds:
                fam = doc.GetElement(famId)
                famName = rdb.Element.Name.GetValue(fam)
                if(famName in library):
                    result.AppendMessage('Found match for: ' + famName)
                    if(len(library[famName]) == 1 ):
                        # found single match for family by name
                        result.UpdateSep(True, 'Found single match: ' + library[famName][0])
                        # get all symbols attached to this family by name
                        priorLoadSymbolIds = fam.GetFamilySymbolIds()
                        # reload family
                        resultLoad = rFamUtil.LoadFamily(doc, library[famName][0])
                        result.AppendMessage(resultLoad.message)
                        if(resultLoad.status == True):
                            # make sure that if a single reload was successful that this method returns true
                            result.status = True
                            # remove symbols (family types) added through reload process
                            if (resultLoad.result != None and len(resultLoad.result) > 0):
                                famLoaded = resultLoad.result.First()
                                afterLoadSymbolIds = famLoaded.GetFamilySymbolIds()
                                newSymbolIds = getNewSymbolIds(priorLoadSymbolIds, afterLoadSymbolIds)
                                if(len(newSymbolIds) > 0):
                                    symbolIdsToBeDeleted = symbolIdsToBeDeleted + newSymbolIds
                    else:
                        matchesMessage = ''
                        for path in library[famName]:
                            matchesMessage = matchesMessage + '...' + path + '\n'
                        matchesMessage = 'Found multiple matches for ' + famName + '\n' + matchesMessage
                        matchesMessage = matchesMessage.strip()
                        # found multiple matches for family by name only...aborting reload
                        result.AppendMessage(matchesMessage)
                else:
                    result.UpdateSep(result.status,'Found no match for ' + famName)
            # delete any new symbols introduced during the reload
            if(len(symbolIdsToBeDeleted)>0):
                resultDelete = com.DeleteByElementIds(doc, symbolIdsToBeDeleted, 'Delete new family types', 'Family types')
                result.AppendMessage (resultDelete.message)
            else:
                message = 'No need to delete any new family types since no new types where created.'
                result.AppendMessage(message) # make sure not to change the status
        else:
            message = 'Found no loadable families in file!'
            result.UpdateSep(False, message)
    except Exception as e:
        message = 'Failed to load families with exception: '+ str(e)
        result.UpdateSep(False, message)
    return result

def getFamilyIdsFromSymbols(doc):
    '''
    Get all loadable family ids in file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing loadable families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    familyIds = []
    # build list of all categories we want families to be reloaded of
    famCats = List[rdb.BuiltInCategory] (rFamUtil.catsLoadableTags)
    famCats.AddRange(rFamUtil.catsLoadableTagsOther) 
    famCats.AddRange(rFamUtil.catsLoadableThreeD)
    famCats.AddRange(rFamUtil.catsLoadableThreeDOther)
    # get all symbols in file
    famSymbols = rFamUtil.GetFamilySymbols(doc, famCats)
    # get families from symbols and filter out in place families
    for famSymbol in famSymbols:
        if (famSymbol.Family.Id not in familyIds and famSymbol.Family.IsInPlace == False):
            familyIds.append(famSymbol.Family.Id)
    return familyIds

def getNewSymbolIds(preLoadSymbolIdList, afterLoadSymbolList):
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