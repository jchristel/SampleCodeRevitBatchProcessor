#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

import RevitCommonAPI as com
import Utility as util
import Result as res
import RevitGroups as rGrp
import RevitViews as rView
from timer import Timer

from Autodesk.Revit.DB import *
from System.Collections.Generic import List

# ----------------------------------------------
# model properties 
# ----------------------------------------------


# doc   current document
# getGroups     expects a method which has to
#   - return a list of either: model groups, detail groups or nested detail groups. 
#   - excepts as a single argument the current document
# transactionName   the transaction name to be used when deleting elements by Id
# groupNameHeader   the text to be displayed at the start of the list containing the deleted group names
def PurgeUnplacedElements (doc:'Autodesk.Revit.DB.Document', 
    getUnusedElementIds, 
    transactionName:str, 
    unUsedElementNameHeader:str,
    isDebug = False) -> 'res.Result':
    """purges all unplaced elements provided through a passed in element id getter method from a model"""
    resultValue = res.Result()
    try:
        unusedElementIds = getUnusedElementIds(doc)
        unusedElementNames = []
        if(isDebug):
            unusedElementNames.append(unUsedElementNameHeader)
            for unusedId in unusedElementIds:
                unusedElementNames.append(SPACER + Element.Name.GetValue(doc.GetElement(unusedId)))
        else:
            unusedElementNames.append(unUsedElementNameHeader + ': ' + str(len(unusedElementIds)) + ' Element(s) purged.')
        purgeResult = com.DeleteByElementIds(doc, unusedElementIds, transactionName, '\n'.join( unusedElementNames ))
        # check if an exception occured and in debug mode, purge elements one by one
        if(isDebug & purgeResult.status == False):
            purgeResult = com.DeleteByElementIdsOneByOne(doc, unusedElementIds, transactionName, '\n'.join( unusedElementNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused ' + unUsedElementNameHeader + ' with exception: '+ str(e))
    return resultValue

# --------------------------------------------- Groups ---------------------------------------------

# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedModelGroupsInModel(doc, transactionName:str) -> res.Result:
    """purges unplaced model groups from a model"""
    return PurgeUnplacedElements(
        doc, 
        rGrp.GetUnplacedModelGroups, 
        transactionName, 
        'Model Group(s)')


# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedDetailGroupsInModel(doc, transactionName:str) -> res.Result:
    """purges unplaced detail groups from a model"""
    return PurgeUnplacedElements(
        doc, 
        rGrp.GetUnplacedDetailGroups, 
        transactionName, 
        'Detail Group(s)')

# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedNestedDetailGroupsInModel(doc, transactionName:str) -> res.Result:
    """purges unplaced nested detail groups from a model"""
    return PurgeUnplacedElements(
        doc, 
        rGrp.GetUnplacedNestedDetailGroups, 
        transactionName, 
        'Nested Detail Group(s)')

# --------------------------------------------- Views ---------------------------------------------

# doc   current document
def PurgeUnusedViewFamilyTypes(doc, transactionName:str) -> res.Result:
    """purges unused view family types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rView.GetUnusedViewTypeIdsInModel(doc), 
        transactionName, 
        'View Family Type(s)')

# doc   current document
def PurgeUnusedViewTemplates(doc, transactionName:str) -> res.Result:
    """purges unused view templates from the model"""
    return PurgeUnplacedElements(
        doc, 
        rView.GetAllUnusedViewTemplateIdsInModel(doc), 
        transactionName, 
        'View Family Templates(s)')

# doc   current document
def PurgeUnusedViewFilters(doc, transactionName) -> res.Result:
    """purges unused view filters from the model"""
    return PurgeUnplacedElements(
        doc, 
        rView.GetAllUnUsedViewFilters(doc), 
        transactionName, 
        'View Filter(s)')

# --------------------------------------------- Main ---------------------------------------------

# list containing purge action names and the purge action method
PURGE_ACTIONS = [
    ['Purge Unused Model Group(s)', PurgeUnplacedModelGroupsInModel],
    ['Purge Unused Detail Group(s)', PurgeUnplacedDetailGroupsInModel],
    ['Purge Unused Nested Detail Group(s)', PurgeUnplacedNestedDetailGroupsInModel],
    ['Purge Unused View Family Types', PurgeUnusedViewFamilyTypes],
    ['Purge Unused View Templates', PurgeUnusedViewTemplates],
    ['Purge Unused View Filters', PurgeUnusedViewFilters]
]

# indentation for names of items purged
SPACER = '...'

# set up a timer object
t = Timer()

# doc   current document
# returns a Result object
def PurgeUnused(doc, revitFilePath: str) -> res.Result:
    """calls all available purge actions defined in global list """
    # the current file name
    revitFileName = util.GetFileNameWithoutExt(revitFilePath)
    resultValue = res.Result()
    for purgeAction in PURGE_ACTIONS:
        try:
            t.start()
            purgeFlag = purgeAction[1](doc, purgeAction[0])
            purgeFlag.AppendMessage(SPACER + str(t.stop()))
            resultValue.Update(purgeFlag)
        except Exception as e:
            resultValue.UpdateSep(False,'Terminated purge unused actions with exception: '+ str(e))
    return resultValue