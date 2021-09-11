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
import RevitCurtainWallElements as rCWE
import RevitDetailItems as rDet
import RevitFamilyUtils as rFamU
import RevitFloors as rFlo
import RevitGroups as rGrp
import RevitGrids as rGrid
import RevitLevels as rLev
import RevitLinks as rLink
import RevitRailings as rRail
import RevitRamps as rRam
import RevitRoofs as rRoof
import RevitStairs as rStair
import RevitViews as rView
import RevitViewReferencing as rViewRef
import RevitWalls as rWall
from timer import Timer

from Autodesk.Revit.DB import *
from System.Collections.Generic import List
from collections import namedtuple

# --------------------------------------------- Purge - utility ---------------------------------------------

# doc                       current document
# getUnusedElementIds       function which returns all ids of elements to be purged
# transactionName           the transaction name to be used when deleting elements by Id
# unUsedElementNameHeader   the text to be displayed at the start of the list containing the deleted element names
# isDebug                   flag: true: will return detailed report and attempt to try to delete elements one by one if an exception occurs
#                           false:  short report and no attempt to delete elements one by one if an exception is thrown during element list delete
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

# --------------------------------------------- Main ---------------------------------------------

#set up a named tuple to store purge actions     
purgeAction = namedtuple(
    'purgeTransactionName', # the revit transaction name for the purge action
    'purgeIdsGetter', # the function which returns all element ids to be purged
    'purgeReportHeader', # human readable repport header for each purge action
    'testReportHeader',  # human readable repport header for each test action
    'testIdsGetter') # functions which returns all availble type ids in model of same category as purge action. To be used to compare ids before and after coded purge with ids before and after revit built in purge

# list containing purge action names and the purge action method
PURGE_ACTIONS = [
    purgeAction('Purge Unused Model Group(s)', rGrp.GetUnplacedModelGroupIds, 'Model Group(s)', 'Model Group(s)', rGrp.GetModelGroupIds),
    purgeAction('Purge Unused Detail Group(s)', rGrp.GetUnplacedDetailGroupIds, 'Detail Group(s)', 'Detail Group(s)', rGrp.GetDetailGroupIds),
    purgeAction('Purge Unused Nested Detail Group(s)', rGrp.GetUnplacedNestedDetailGroupIds, 'Nested Detail Group(s)', 'Nested Detail Group(s)', rGrp.GetNestedDetailGroupIds),
    purgeAction('Purge Unused View Family Types', rView.GetUnusedViewTypeIdsInModel, 'View Family Type(s)', 'View Family Type(s)', rView.GetViewTypeIds),
    purgeAction('Purge Unused View Templates', rView.GetAllUnusedViewTemplateIdsInModel, 'View Family Templates(s)', 'View Family Templates(s)', rView.GetViewsTemplateIdsInInModel),
    purgeAction('Purge Unused View Filters', rView.GetAllUnUsedViewFilters, 'View Filter(s)', 'View Filter(s)', rView.GetAllAvailableFilterIdsInModel),
    purgeAction('Purge Unused Image Links', rLink.GetAllUnusedImagetypeIdsInModel, 'Images(s)', 'Images(s)', rLink.GetImagesTypeIdsInModel),
    purgeAction('Purge Unused MultiRef Dimension Types', rAnn.GetAllUnusedMultiRefDimTypeIdsInModel,'MultiRef Dimension Type(s)', 'MultiRef Dimension Type(s)', rAnn.GetAllMultiRefAnnotationTypeIds),
    purgeAction('Purge Unused Dimension Types', rAnn.GetAllUnusedDimTypeIdsInModel, 'Dimension Type(s)', 'Dimension Type(s)', rAnn.GetDimTypeIds),
    purgeAction('Purge Unused Text Types', rAnn.GetAllUnusedTextTypeIdsInModel,'Text Type(s)', 'Text Type(s)', rAnn.GetAllTextTypeIds),
    purgeAction('Purge Unused Arrow Heads', rAnn.GetAllUnusedArrowTypeIdsInModel, 'Arrow Head Type(s)', 'Arrow Head Type(s)', rAnn.GetArrowTypesIdsInModel),
    purgeAction('Purge Unused Stacked Wall Types', rWall.GetUnusedStackedWallTypeIdsToPurge, 'Stacked Wall Type(s)', 'Stacked Wall Type(s)', rWall.GetAllStackedWallTypeIdsInModel),
    purgeAction('Purge Unused InPlace Wall Types', rWall.GetUnusedInPlaceWallIdsForPurge, 'InPlace Wall Type(s)', 'InPlace Wall Type(s)', rWall.GetAllInPlaceWallTypeIdsInModel),
    purgeAction('Purge Unused Curtain Wall Types', rWall.GetUnUsedCurtainWallTypeIdsToPurge, 'Curtain Wall Type(s)', 'Curtain Wall Type(s)', rWall.GetAllCurtainWallTypeIdsInModel),
    purgeAction('Purge Unused Basic Types', rWall.GetUnUsedBasicWallTypeIdsToPurge, 'Basic Wall Type(s)', 'Basic Wall Type(s)', rWall.GetAllBasicWallTypeIdsInModel),
    purgeAction('Purge Unused Curtain Wall Element Types', rCWE.GetUnusedNonInPlaceCurtainWallElementTypeIdsToPurge,'Curtain Wall Element Type(s)', 'Curtain Wall Element Type(s)', rCWE.GetAllCurtainWallElementTypeIdsInModelByCategory),
    purgeAction('Purge Unused Ceiling Types', rCeil.GetUnusedNonInPlaceCeilingTypeIdsToPurge, 'Ceiling Type(s)', 'Ceiling Type(s)', rCeil.GetAllCeilingTypeIdsInModelByCategory),
    purgeAction('Purge Unused InPlace Ceiling Types', rCeil.GetUnusedInPlaceCeilingIdsForPurge, 'InPlace Ceiling Type(s)', 'InPlace Ceiling Type(s)', rCeil.GetAllInPlaceCeilingTypeIdsInModel),
    purgeAction('Purge Unused Floor Types', rFlo.GetUnusedNonInPlaceFloorTypeIdsToPurge, 'Floor Type(s)', 'Floor Type(s)', rFlo.GetAllFloorTypeIdsInModelByClass), #TODO check why this is using by class...
    purgeAction('Purge Unused InPlace Floor Types', rFlo.GetUnusedInPlaceFloorIdsForPurge, 'InPlace Floor Type(s)', 'InPlace Floor Type(s)', rFlo.GetAllInPlaceFloorTypeIdsInModel),
    purgeAction('Purge Unused Roof Types', rRoof.GetUnusedNonInPlaceRoofTypeIdsToPurge, 'Roof Type(s)', 'Roof Type(s)', rRoof.GetAllRoofTypeIdsInModelByClass), #TODO check why by class
    purgeAction('Purge Unused InPlace Roof Types', rRoof.GetUnusedInPlaceRoofIdsForPurge, 'InPlace Roof Type(s)', 'InPlace Roof Type(s)', rRoof.GetAllInPlaceRoofTypeIdsInModel),
    purgeAction('Purge Unused Stair Types', rStair.GetUnusedNonInPlaceStairTypeIdsToPurge, 'Stair Type(s)', 'Stair Type(s)', rStair.GetAllStairTypeIdsInModelByClass), #TODO check why by class
    purgeAction('Purge Unused Path Types', rStair.GetUnusedStairPathTypeIdsToPurge, 'Stair Path Type(s)', 'Stair Path Type(s)', rStair.GetAllStairPathTypeIdsInModelByClass),
    purgeAction('Purge Unused Landing Types', rStair.GetUnusedStairLandingTypeIdsToPurge, 'Stair Landing Type(s)', 'Stair Landing Type(s)',rStair.GetAllStairLandingTypeIdsInModelByClass),
    purgeAction('Purge Unused Run Types', rStair.GetUnusedStairRunTypeIdsToPurge, 'Stair Run Type(s)', 'Stair Run Type(s)', rStair.GetAllStairRunTypeIdsInModelByClass),
    purgeAction('Purge Unused Stringers and Carriage Types', rStair.GetUnusedStairStringersCarriageTypeIdsToPurge, 'Stair Stringers and Carriage Type(s)', 'Stair Stringers and Carriage Type(s)', rStair.GetAllStairstringCarriageTypeIdsInModelByCategory),
    purgeAction('Purge Unused InPlace Stair Types', rStair.GetUnusedInPlaceStairIdsForPurge,'InPlace Stair Type(s)', 'InPlace Stair Type(s)', rStair.GetAllInPlaceStairTypeIdsInModel),
    purgeAction('Purge Unused Ramp Types', rRam.GetUnusedNonInPlaceRampTypeIdsToPurge, 'Ramp Type(s)', 'Ramp Type(s)', rRam.GetAllRampTypeIdsInModelByCategory),
    purgeAction('Purge Unused Stair Cut Mark Types', rStair.GetUnusedStairCutMarkTypeIdsToPurge, 'Stair Cut Mark Type(s)', 'Stair Cut Mark Type(s)', rStair.GetAllStairCutMarkTypeIdsInModelByClass),
    purgeAction('Purge Unused Building Pad Types', rBuildP.GetUnusedNonInPlaceBuildingPadTypeIdsToPurge, 'Building Pad Type(s)', 'Building Pad Type(s)', rBuildP.GetAllBuildingPadTypeIdsInModelByClass),
    purgeAction('Purge Unused Railing Types', rRail.GetUnusedNonInPlaceRailingTypeIdsToPurge, 'Railing Type(s)','Railing Type(s)', rRail.GetAllRailingTypeIdsInModelByClassAndCategory),
    purgeAction('Purge Unused InPlace Railing Types', rRail.GetUnusedNonInPlaceRailingTypeIdsToPurge,'Railing Type(s)','Railing Type(s)',rRail.GetAllInPlaceRailingTypeIdsInModel),
    purgeAction('Purge Unused Level Types', rLev.GetUnusedLevelTypesForPurge, 'Level Type(s)', 'Level Type(s)',rLev.GetAllLevelTypeIdsByCategory),
    purgeAction('Purge Unused Level Head Types', rLev.GetUnusedLevelHeadFamiliesForPurge, 'Level Head family Type(s)', 'Level Head family Type(s)', rLev.GetAllLevelHeadfamilyTypeIds),
    purgeAction('Purge Unused Grid Types', rGrid.GetUnusedGridTypesForPurge, 'Grid Type(s)', 'Grid Type(s)', rGrid.GetAllGridTypeIdsByCategory),
    purgeAction('Purge Unused Grid Head Types', rGrid.GetUnusedGridHeadFamiliesForPurge, 'Grid Head family Type(s)', rGrid.GetAllGridHeadFamilyTypeIds),
    purgeAction('Purge Unused View Reference Types', rViewRef.GetUnusedViewReferenceTypeIdsForPurge, 'View Ref Type(s)', 'View Ref Type(s)', rViewRef.GetAllViewReferenceTypeIdDataAsList),
    purgeAction('Purge Unused View Continuation Types', rViewRef.GetUnusedContinuationMarkerTypeIdsForPurge, 'View Continuation Type(s)', 'View Continuation Type(s)', rViewRef.GetAllViewContinuationTypeIds),
    purgeAction('Purge Unused View Reference Families', rViewRef.GetUnusedViewRefAndContinuationMarkerFamiliesForPurge, 'View Ref and Continuation Marker families(s)', 'View Ref and Continuation Marker families(s)', rViewRef.GetAllViewReferenceSymbolIds),
    purgeAction('Purge Unused Repeating Details', rDet.GetUnUsedRepeatingDetailTypeIdsForPurge, 'Repeating Detail Type(s)', 'Repeating Detail Type(s)', rDet.GetAllRepeatingDetailTypeIdsAvailable),
    purgeAction('Purge Unused Filled Regions', rDet.GetUnUsedFilledRegionTypeIdsForPurge, 'Filled Region Type(s)', 'Filled Region Type(s)', rDet.GetAllFilledRegionTypeIdsAvailable),
    purgeAction('Purge Unused Loadable Family Types', rFamU.GetUnusedFamilySymbolsAndTypeIdsToPurge, 'Loadable Family Type(s)', 'Loadable Family Type(s)', rFamU.GetAllFamilySymbolIds)
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
    for pA in PURGE_ACTIONS:
        try:
            t.start()
            purgeFlag = PurgeUnplacedElements(
                doc,
                pA.purgeIdsGetter,
                pA.purgeTransactionName,
                pA.purgeReportHeader,
                isDebug
            )
            purgeFlag.AppendMessage(SPACER + str(t.stop()))
            resultValue.Update(purgeFlag)
        except Exception as e:
            resultValue.UpdateSep(False,'Terminated purge unused actions with exception: '+ str(e))
    resultValue.AppendMessage('purge duration: '+ str(tOverall.stop()))
    return resultValue

# --------------------------------------------- Testing ---------------------------------------------

# doc                       current document
# typeIdGetter              function which returns all available type ids
# reportHeader              the first entry per row written to file
# outputFilePath            location of file
# counter                   action counter, if 0 the report file will be created from scratch, any othe value means append to existing report file
def WriteAvailableTypeIds(doc, typeIdGetter, reportHeader, outputFilePath, counter):
    """gets all available type ids from passed in type id getter and writes result to file"""
    resultValue = res.Result()
    writeType = 'a'
    if(counter == 0):
        writeType = 'w'
    try:
        typeIds = typeIdGetter(doc)
        # convert data to list of lists of strings for report writer
        data = []
        typeIdsAsString = [reportHeader]
        for tId in typeIds:
            typeIdsAsString.append(str(tId))
        data.append(typeIdsAsString)
        # writer data to file
        util.writeReportData(
            outputFilePath,
            '',
            data,
            writeType)
        resultValue.UpdateSep(True,'Added type group ' + reportHeader + ' with ' + str(len(typeIds) + ' entries'))
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused ' + reportHeader + ' with exception: '+ str(e))
    return resultValue

# fileSource            bench mark type ids file
# fileTest              file to check against the benchmark
def CompareReportData(fileSource, fileTest):
    """used to compare a bench mark results file containing type ids against a new results file
    will report missing or additional ids in results file"""
    pass

# doc           current document
# filePath      fully qualified report file path
def ReportAvailableTypeIds(doc, filePath):
    """calls all available type id getter functions and writes results to file"""
    resultValue = res.Result()
    tOverall.start()
    for pA in PURGE_ACTIONS:
        counter = 0 #any counter value greater then 0 means append to report file rather then creating a new file
        try:
            t.start()
            reportFlag = WriteAvailableTypeIds(
                doc,
                pA.testIdsGetter,
                pA.testReportHeader,
                filePath,
                counter
            )
            reportFlag.AppendMessage(SPACER + str(t.stop()))
            resultValue.Update(reportFlag)
        except Exception as e:
            resultValue.UpdateSep(False,'Terminated get available type id actions with exception: '+ str(e))
        counter = counter + 1
    resultValue.AppendMessage('Report available types duration: '+ str(tOverall.stop()))
    return resultValue