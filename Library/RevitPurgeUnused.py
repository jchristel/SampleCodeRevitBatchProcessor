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
import RevitAnnotation as rAnn
import RevitBuildingPads as rBuildP
import RevitCeilings as rCeil
import RevitFamilyUtils as rFamU
import RevitFloors as rFlo
import RevitGroups as rGrp
import RevitLinks as rLink
import RevitRamps as rRam
import RevitRoofs as rRoof
import RevitStairs as rStair
import RevitViews as rView
import RevitWalls as rWall
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
def PurgeUnplacedElements (doc, 
    getUnusedElementIds, 
    transactionName, 
    unUsedElementNameHeader,
    isDebug = False):
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
        if(isDebug and purgeResult.status == False):
            print('second debug run')
            purgeResult = com.DeleteByElementIdsOneByOne(doc, unusedElementIds, transactionName, '\n'.join( unusedElementNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused ' + unUsedElementNameHeader + ' with exception: '+ str(e))
    return resultValue

# --------------------------------------------- Groups ---------------------------------------------

# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedModelGroupsInModel(doc, transactionName, isDebug):
    """purges unplaced model groups from a model"""
    return PurgeUnplacedElements(
        doc, 
        rGrp.GetUnplacedModelGroupIds, 
        transactionName,
        'Model Group(s)',
        isDebug)

# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedDetailGroupsInModel(doc, transactionName, isDebug):
    """purges unplaced detail groups from a model"""
    return PurgeUnplacedElements(
        doc, 
        rGrp.GetUnplacedDetailGroupIds, 
        transactionName,
        'Detail Group(s)',
        isDebug)

# doc   current document
# transactionName   the transaction name to be used when deleting elements by Id
def PurgeUnplacedNestedDetailGroupsInModel(doc, transactionName, isDebug):
    """purges unplaced nested detail groups from a model"""
    return PurgeUnplacedElements(
        doc, 
        rGrp.GetUnplacedNestedDetailGroupIds, 
        transactionName,
        'Nested Detail Group(s)',
        isDebug)

# --------------------------------------------- Views ---------------------------------------------

# doc   current document
def PurgeUnusedViewFamilyTypes(doc, transactionName, isDebug):
    """purges unused view family types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rView.GetUnusedViewTypeIdsInModel, 
        transactionName,
        'View Family Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedViewTemplates(doc, transactionName, isDebug):
    """purges unused view templates from the model"""
    return PurgeUnplacedElements(
        doc, 
        rView.GetAllUnusedViewTemplateIdsInModel, 
        transactionName,
        'View Family Templates(s)',
        isDebug)

# doc   current document
def PurgeUnusedViewFilters(doc, transactionName, isDebug):
    """purges unused view filters from the model"""
    return PurgeUnplacedElements(
        doc, 
        rView.GetAllUnUsedViewFilters, 
        transactionName,
        'View Filter(s)',
        isDebug)

# --------------------------------------------- Images ---------------------------------------------

# doc   current document
def PurgeUnusedImages(doc, transactionName, isDebug):
    """purges unused images from the model"""
    return PurgeUnplacedElements(
        doc, 
        rLink.GetAllUnusedImagetypeIdsInModel, 
        transactionName,
        'Images(s)',
        isDebug)

# --------------------------------------------- Dimensions ---------------------------------------------

# doc   current document
def PurgeUnusedMultiRefDimTypes(doc, transactionName, isDebug):
    """purges unused MultiRef Dimension Types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rAnn.GetAllUnusedMultiRefDimTypeIdsInModel, 
        transactionName,
        'MultiRef Dimension Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedDimTypes(doc, transactionName, isDebug):
    """purges unused Dimension Types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rAnn.GetAllUnusedDimTypeIdsInModel, 
        transactionName,
        'Dimension Type(s)',
        isDebug)

# --------------------------------------------- text ---------------------------------------------

# doc   current document
def PurgeUnusedTextTypes(doc, transactionName, isDebug):
    """purges unused Text Types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rAnn.GetAllUnusedTextTypeIdsInModel, 
        transactionName,
        'Text Type(s)',
        isDebug)

# --------------------------------------------- Arrow Heads ---------------------------------------------

# doc   current document
def PurgeUnusedArrowHeadTypes(doc, transactionName, isDebug):
    """purges unused arrow head types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rAnn.GetAllUnusedArrowTypeIdsInModel, 
        transactionName,
        'Arrow Head Type(s)',
        isDebug)

# ---------------------------------------------wall types ---------------------------------------------

# doc   current document
def PurgeUnusedStackedWallTypes(doc, transactionName, isDebug):
    """purges unused stacked wall types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rWall.GetUnusedStackedWallTypeIdsToPurge, 
        transactionName,
        'Stacked Wall Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedInPlaceWallTypes(doc, transactionName, isDebug):
    """purges unused inPlace wall types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rWall.GetUnusedInPlaceWallIdsForPurge, 
        transactionName,
        'InPlace Wall Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedCurtainWallTypes(doc, transactionName, isDebug):
    """purges unused curtain wall types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rWall.GetUnUsedCurtainWallTypeIdsToPurge, 
        transactionName,
        'Curtain Wall Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedBasicTypes(doc, transactionName, isDebug):
    """purges unused basic wall types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rWall.GetUnUsedBasicWallTypeIdsToPurge, 
        transactionName,
        'Basic Wall Type(s)',
        isDebug)

# ---------------------------------------------ceiling types ---------------------------------------------

# doc   current document
def PurgeUnusedCeilingTypes(doc, transactionName, isDebug):
    """purges unused ceiling types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rCeil.GetUnusedNonInPlaceCeilingTypeIdsToPurge, 
        transactionName,
        'Ceiling Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedInPlaceCeilingTypes(doc, transactionName, isDebug):
    """purges unused inPlace ceiling types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rCeil.GetUnusedInPlaceCeilingIdsForPurge, 
        transactionName,
        'InPlace Ceiling Type(s)',
        isDebug)

# ---------------------------------------------floor types ---------------------------------------------

# doc   current document
def PurgeUnusedFloorTypes(doc, transactionName, isDebug):
    """purges unused floor types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rFlo.GetUnusedNonInPlaceFloorTypeIdsToPurge, 
        transactionName,
        'Floor Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedInPlaceFloorTypes(doc, transactionName, isDebug):
    """purges unused inPlace floor types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rFlo.GetUnusedInPlaceFloorIdsForPurge, 
        transactionName,
        'InPlace Floor Type(s)',
        isDebug)

# ---------------------------------------------roof types ---------------------------------------------

# doc   current document
def PurgeUnusedRoofTypes(doc, transactionName, isDebug):
    """purges unused roof types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rRoof.GetUnusedNonInPlaceRoofTypeIdsToPurge, 
        transactionName,
        'Roof Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedInPlaceRoofTypes(doc, transactionName, isDebug):
    """purges unused inPlace roof types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rRoof.GetUnusedInPlaceRoofIdsForPurge, 
        transactionName,
        'InPlace Roof Type(s)',
        isDebug)

# ---------------------------------------------stair types ---------------------------------------------

# doc   current document
def PurgeUnusedStairTypes(doc, transactionName, isDebug):
    """purges unused stair types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rStair.GetUnusedNonInPlaceStairTypeIdsToPurge, 
        transactionName,
        'Stair Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedPathTypes(doc, transactionName, isDebug):
    """purges unused stair path types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rStair.GetUnusedStairPathTypeIdsToPurge, 
        transactionName,
        'Stair Path Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedLandingTypes(doc, transactionName, isDebug):
    """purges unused stair landing types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rStair.GetUnusedStairLandingTypeIdsToPurge, 
        transactionName,
        'Stair Landing Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedRunTypes(doc, transactionName, isDebug):
    """purges unused stair run types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rStair.GetUnusedStairRunTypeIdsToPurge, 
        transactionName,
        'Stair Run Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedStringerCarriageTypes(doc, transactionName, isDebug):
    """purges unused stair stringer and carriage types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rStair.GetUnusedStairStringersCarriageTypeIdsToPurge, 
        transactionName,
        'Stair Stringers and Carriage Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedStairCutMarkTypes(doc, transactionName, isDebug):
    """purges unused stair cut mark types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rStair.GetUnusedStairCutMarkTypeIdsToPurge, 
        transactionName,
        'Stair Cut Mark Type(s)',
        isDebug)

# doc   current document
def PurgeUnusedInPlaceStairTypes(doc, transactionName, isDebug):
    """purges unused inPlace stair types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rStair.GetUnusedInPlaceStairIdsForPurge, 
        transactionName,
        'InPlace Stair Type(s)',
        isDebug)

# ---------------------------------------------ramp types ---------------------------------------------

# doc   current document
def PurgeUnusedRampTypes(doc, transactionName, isDebug):
    """purges unused ramp types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rRam.GetUnusedNonInPlaceRampTypeIdsToPurge, 
        transactionName,
        'Ramp Type(s)',
        isDebug)

# ---------------------------------------------building pad types ---------------------------------------------

# doc   current document
def PurgeUnusedBuildingPadTypes(doc, transactionName, isDebug):
    """purges unused building pad types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rBuildP.GetUnusedNonInPlaceBuildingPadTypeIdsToPurge, 
        transactionName,
        'Building Pad Type(s)',
        isDebug)

# ---------------------------------------------loadable families ---------------------------------------------

# doc   current document
def PurgeUnusedLoadableFamilyTypes(doc, transactionName, isDebug):
    """purges unused loadable family types from the model"""
    return PurgeUnplacedElements(
        doc, 
        rFamU.GetUnusedFamilySymbolsAndTypeIdsToPurge, 
        transactionName,
        'Loadable Family Type(s)',
        isDebug)

# --------------------------------------------- Main ---------------------------------------------

# list containing purge action names and the purge action method
PURGE_ACTIONS = [
    ['Purge Unused Model Group(s)', PurgeUnplacedModelGroupsInModel],
    ['Purge Unused Detail Group(s)', PurgeUnplacedDetailGroupsInModel],
    ['Purge Unused Nested Detail Group(s)', PurgeUnplacedNestedDetailGroupsInModel],
    ['Purge Unused View Family Types', PurgeUnusedViewFamilyTypes],
    ['Purge Unused View Templates', PurgeUnusedViewTemplates],
    ['Purge Unused View Filters', PurgeUnusedViewFilters],
    ['Purge Unused Image Links', PurgeUnusedImages],
    ['Purge Unused MultiRef Dimension Types', PurgeUnusedMultiRefDimTypes],
    ['Purge Unused Dimension Types', PurgeUnusedDimTypes],
    ['Purge Unused Text Types', PurgeUnusedTextTypes],
    ['Purge Unused Arrow Heads', PurgeUnusedArrowHeadTypes],
    ['Purge Unused Stacked Wall Types', PurgeUnusedStackedWallTypes],
    ['Purge Unused InPlace Wall Types', PurgeUnusedInPlaceWallTypes],
    ['Purge Unused Curtain Wall Types', PurgeUnusedCurtainWallTypes],
    ['Purge Unused Basic Types', PurgeUnusedBasicTypes],
    ['Purge Unused Ceiling Types', PurgeUnusedCeilingTypes],
    ['Purge Unused InPlace Ceiling Types', PurgeUnusedInPlaceCeilingTypes],
    ['Purge Unused Floor Types', PurgeUnusedFloorTypes],
    ['Purge Unused InPlace Floor Types', PurgeUnusedInPlaceFloorTypes],
    ['Purge Unused Roof Types', PurgeUnusedRoofTypes],
    ['Purge Unused InPlace Roof Types', PurgeUnusedInPlaceRoofTypes],
    ['Purge Unused Stair Types', PurgeUnusedStairTypes],
    ['Purge Unused Path Types', PurgeUnusedPathTypes],
    ['Purge Unused Landing Types', PurgeUnusedLandingTypes],
    ['Purge Unused Run Types', PurgeUnusedRunTypes],
    ['Purge Unused Stringers and Carriage Types', PurgeUnusedStringerCarriageTypes],
    ['Purge Unused InPlace Stair Types', PurgeUnusedInPlaceStairTypes],
    ['Purge Unused Ramp Types', PurgeUnusedRampTypes],
    ['Purge Unused Stair Cut Mark Types', PurgeUnusedStairCutMarkTypes], # might need to be moved after ramp type purge
    ['Purge Unused Building Pad Types', PurgeUnusedBuildingPadTypes]#,
    #['Purge Unused Loadable Family Types', PurgeUnusedLoadableFamilyTypes]
]

# indentation for names of items purged
SPACER = '...'

# set up a timer objects
t = Timer()
tOverall = Timer()

# doc   current document
# returns a Result object
def PurgeUnused(doc, revitFilePath, isDebug):
    """calls all available purge actions defined in global list """
    # the current file name
    revitFileName = util.GetFileNameWithoutExt(revitFilePath)
    resultValue = res.Result()
    tOverall.start()
    for purgeAction in PURGE_ACTIONS:
        try:
            t.start()
            purgeFlag = purgeAction[1](
                doc, 
                purgeAction[0], 
                isDebug)
            purgeFlag.AppendMessage(SPACER + str(t.stop()))
            resultValue.Update(purgeFlag)
        except Exception as e:
            resultValue.UpdateSep(False,'Terminated purge unused actions with exception: '+ str(e))
    resultValue.AppendMessage('purge duration: '+ str(tOverall.stop()))
    return resultValue