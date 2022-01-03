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

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)
clr.AddReference('System')
from System.Collections.Generic import List


# import common library
import RevitCommonAPI as com
import Utility as util
import Result as res
import RevitFamilyUtils as rFamUtil
import RevitFamilyLoadOption as famLoadOpt
from RevitFamilyLoadOption import *

from Autodesk.Revit.DB import *

# --------------------------------------------------- Family Loading / inserting -----------------------------------------

def ReloadAllFamilies(doc, libraryLocation, includeSubFolders):
    """reloads a number of families with settings:
    - parameter values overwritten: true
    retuns True if any of the reload actions was succesful"""
    result = res.Result()
    # if a family is reloaded it may bring in new typs not present in the model at reload
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
            result.UpdateSep(True,'Found ' + str(len(library)) + ' families in Library!')
        # get all families in file:
        familyIds = getFamilyIdsFromSymbols(doc)
        if(len(familyIds) > 0):
            result.UpdateSep(True, 'Found ' + str(len(familyIds)) + ' loadable families in file.')
            for famId in familyIds:
                fam = doc.GetElement(famId)
                famName = Element.Name.GetValue(fam)
                if(famName in library):
                    result.UpdateSep(True, 'Found match for: ' + famName)
                    if(len(library[famName]) == 1 ):
                        # found single match for family by name
                        result.UpdateSep(True, 'Found single match: ' + library[famName][0])
                        # get all symbols attached to this family by name
                        priorLoadSymbolIds = fam.GetFamilySymbolIds()
                        # reload family
                        resultLoad = rFamUtil.LoadFamily(doc, library[famName][0])
                        result.Update(resultLoad)
                        if(resultLoad.status == True):
                            # make sure that if a single reload was succesfull that this method returns true
                            result.status = True
                            # remove symbols (family types) added through reload process
                            if (resultLoad.result != None and len(resultLoad.result) > 0):
                                famLoaded = resultLoad.result.First()
                                afterLoadSymbolIds = famLoaded.GetFamilySymbolIds()
                                newSymbolIds = getNewSymboldIds(priorLoadSymbolIds, afterLoadSymbolIds)
                                if(len(newSymbolIds) > 0):
                                    symbolIdsToBeDeleted = symbolIdsToBeDeleted + newSymbolIds
                    else:
                        matchesMessage = ''
                        for path in library[famName]:
                            matchesMessage = matchesMessage + '...' + path + '\n'
                        matchesMessage = 'Found multiple matches for ' + famName + '\n' + matchesMessage
                        matchesMessage = matchesMessage.strip()
                        # found mutliple matches for family by name only...aborting reload
                        result.UpdateSep(False, matchesMessage)
                else:
                    result.UpdateSep(False,'Found no match for ' + famName)
            # delete any new symbols introduced during the reload
            if(len(symbolIdsToBeDeleted)>0):
                resultDelete = com.DeleteByElementIds(doc, symbolIdsToBeDeleted, 'Delete new family types', 'Family types')
                result.Update(resultDelete)
            else:
                message = 'No need to delete any new family typese since no new types where created.'
                result.UpdateSep(True, message)
        else:
            message = 'Found no loadable families in file!'
            result.UpdateSep(True, message)
    except Exception as e:
        message = 'Failed to load families with exception: '+ str(e)
        result.UpdateSep(False, message)
    return result

# doc       current document
def getFamilyIdsFromSymbols(doc):
    ''' get all loadable family ids in file'''
    familyIds = []
    # build list of all categories we want families to be reloaded of
    famCats = List[BuiltInCategory] (rFamUtil.catsLoadableTags)
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

# preLoadSymbolIdList      list of Ids of symbols prior the reload
# afterLoadSymbolList       list of ids of symbols after the reload
def getNewSymboldIds(preLoadSymbolIdList, afterLoadSymbolList):
    """returns a list of symbol ids not present prior to reload"""
    ids = []
    for id in afterLoadSymbolList:
        if (id not in preLoadSymbolIdList):
            ids.append(id)
    return ids