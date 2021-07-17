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

# --------------------------------------------- Groups ---------------------------------------------

# doc   current document
# getGroups     expects a method which has to
#   - return a list of either: model groups, detail groups or nested detail groups. 
#   - excepts as a single argument the current document
# transactionName   the transaction name to be used when deleting elements by Id
# groupNameHeader   the text to be displayed at the start of the list containing the deleted group names
def PurgeUnplacedGroups (doc, getGroups, transactionName, groupNameHeader):
    """purges all unplaced groups provided through a passed in getter method from a model"""
    resultValue = res.Result()
    try:
        unused = getGroups(doc)
        ids = []
        groupNames = [groupNameHeader]
        for unusedGroup in unused:
            ids.append(unusedGroup.Id)
            groupNames.append(SPACER + Element.Name.GetValue(unusedGroup))
        purgeResult = com.DeleteByElementIds(doc, ids, transactionName, '\n'.join( groupNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused ' + groupNameHeader + ' with exception: '+ str(e))
    return resultValue

# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedModelGroupsInModel(doc, transactionName):
    """purges unplaced model groups from a model"""
    return PurgeUnplacedGroups(
        doc, 
        rGrp.GetUnplacedModelGroups, 
        transactionName, 
        'Model Group(s)')


# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedDetailGroupsInModel(doc, transactionName):
    """purges unplaced detail groups from a model"""
    return PurgeUnplacedGroups(
        doc, 
        rGrp.GetUnplacedDetailGroups, 
        transactionName, 
        'Detail Group(s)')

# purges unplaced nested detail groups from a model
# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedNestedDetailGroupsInModel(doc, transactionName):
    return PurgeUnplacedGroups(
        doc, 
        rGrp.GetUnplacedNestedDetailGroups, 
        transactionName, 
        'Nested Detail Group(s)')

# --------------------------------------------- Views ---------------------------------------------

# doc   current document
def PurgeUnusedViewFamilyTypes(doc, transactionName):
    """purges unused view family types from the model"""
    resultValue = res.Result()
    try:
        unused = rView.GetUnusedViewTypeIdsInModel(doc)
        ids = []
        viewTypeNames = ['View Family Types']
        for unusedvft in unused:
            ids.append(unusedvft)
            vft = doc.GetElement(unusedvft)
            viewTypeNames.append(SPACER + Element.Name.GetValue(vft))
        purgeResult = com.DeleteByElementIds(doc, ids, transactionName, '\n'.join( viewTypeNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused view family types with exception: '+ str(e))
    return resultValue

# doc   current document
def PurgeUnusedViewTemplates(doc, transactionName):
    """purges unused view family types from the model"""
    resultValue = res.Result()
    try:
        unused = rView.GetAllUnusedViewTemplateIdsInModel(doc)
        ids = []
        viewTemplateNames = ['View Templates']
        for unusedvt in unused:
            ids.append(unusedvt)
            vt = doc.GetElement(unusedvt)
            viewTemplateNames.append(SPACER + Element.Name.GetValue(vt))
        purgeResult = com.DeleteByElementIds(doc, ids, transactionName, '\n'.join( viewTemplateNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused view templates with exception: '+ str(e))
    return resultValue

# doc   current document
def PurgeUnusedViewFilters(doc, transactionName):
    """purges unused view filters from the model"""
    resultValue = res.Result()
    try:
        unused = rView.GetAllUnUsedViewFilters(doc)
        ids = []
        viewTemplateNames = ['View Filters']
        for unusedvt in unused:
            ids.append(unusedvt)
            vt = doc.GetElement(unusedvt)
            viewTemplateNames.append(SPACER + Element.Name.GetValue(vt))
        purgeResult = com.DeleteByElementIds(doc, ids, transactionName, '\n'.join( viewTemplateNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused view filters with exception: '+ str(e))
    return resultValue

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
def PurgeUnused(doc, revitFilePath):
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