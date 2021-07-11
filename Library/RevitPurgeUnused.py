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

# purges unplaced model groups from a model
# doc   current document
def PurgeUnplacedModelGroupsInModel(doc, transactionName):
    resultValue = res.Result()
    try:
        unused = rGrp.GetUnplacedModelGroups(doc)
        ids = []
        groupNames = ['Model Groups:']
        for unusedGroup in unused:
            ids.append(unusedGroup.Id)
            groupNames.append(Element.Name.GetValue(unusedGroup))
        purgeResult = com.DeleteByElementIds(doc, ids, transactionName, '\n'.join( groupNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused model groups with exception: '+ str(e))
    return resultValue

# purges unplaced detail groups from a model
# doc   current document
def PurgeUnplacedDetailGroupsInModel(doc, transactionName):
    resultValue = res.Result()
    try:
        unused = rGrp.GetUnplacedDetailGroups(doc)
        ids = []
        groupNames = ['Detail Groups:']
        for unusedGroup in unused:
            ids.append(unusedGroup.Id)
            groupNames.append(Element.Name.GetValue(unusedGroup))
        purgeResult = com.DeleteByElementIds(doc, ids, transactionName, '\n'.join( groupNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused detail groups with exception: '+ str(e))
    return resultValue

# --------------------------------------------- Main ---------------------------------------------

# list containing purge action names and the purge action method
PURGE_ACTIONS = [
    ['Purge Unused Model Groups', PurgeUnplacedModelGroupsInModel],
    ['Purge Unused Detail Groups', PurgeUnplacedDetailGroupsInModel]
]

# updates any instances of model health tracking family in a project
# doc   current document
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