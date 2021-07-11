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

from Autodesk.Revit.DB import *
from System.Collections.Generic import List

# ----------------------------------------------
# model properties 
# ----------------------------------------------

# --------------------------------------------- Groups ---------------------------------------------

# purges all unplaced groups provided through a passed in getter method from a model
# doc   current document
# getGroups     expects a method which has to
#   - return a list of either: model groups, detail groups or nested detail groups. 
#   - excepts as a single argument the current document
# transactionName   the transaction name to be used when deleting elements by Id
# groupNameHeader   the text to be displayed at the start of the list containing the deleted group names
def PurgeUnplacedGroups (doc, getGroups, transactionName, groupNameHeader):
    resultValue = res.Result()
    try:
        unused = getGroups(doc)
        ids = []
        groupNames = [groupNameHeader]
        for unusedGroup in unused:
            ids.append(unusedGroup.Id)
            groupNames.append(Element.Name.GetValue(unusedGroup))
        purgeResult = com.DeleteByElementIds(doc, ids, transactionName, '\n'.join( groupNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused ' + groupNameHeader + ' with exception: '+ str(e))
    return resultValue

# purges unplaced model groups from a model
# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedModelGroupsInModel(doc, transactionName):
    return PurgeUnplacedGroups(
        doc, 
        rGrp.GetUnplacedModelGroups, 
        transactionName, 
        'Model Group(s)')

# purges unplaced detail groups from a model
# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedDetailGroupsInModel(doc, transactionName):
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

# --------------------------------------------- Main ---------------------------------------------

# list containing purge action names and the purge action method
PURGE_ACTIONS = [
    ['Purge Unused Model Group(s)', PurgeUnplacedModelGroupsInModel],
    ['Purge Unused Detail Group(s)', PurgeUnplacedDetailGroupsInModel],
    ['Purge Unused Nested Detail Group(s)', PurgeUnplacedNestedDetailGroupsInModel]
]

# calls all available purge actions defined in global list 
# doc   current document
# returns a Result object
def PurgeUnused(doc, revitFilePath):
    # the current file name
    revitFileName = util.GetFileNameWithoutExt(revitFilePath)
    resultValue = res.Result()
    for purgeAction in PURGE_ACTIONS:
        try:
            purgeFlag = purgeAction[1](doc, purgeAction[0])
            resultValue.Update(purgeFlag)
        except Exception as e:
            resultValue.UpdateSep(False,'Terminated purge unused actions with exception: '+ str(e))
    return resultValue