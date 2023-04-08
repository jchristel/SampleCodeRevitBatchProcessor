'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a purge unused function using standard revit api functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some functionality provided here exceeds the Revit purge unused or e-transmit purge unused command:

- view types
- view templates
- view filters

Others definitely lack:

- Materials
- Appearance assets
- loadable Families
- some MEP systems

Future: just provide improvements over e-transmit purge unused in this code section.

'''

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

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.Utilities import Utility as util
from duHast.Utilities import Result as res
from duHast.APISamples.Annotation import RevitSpotDimensions as rAnnoSpot
from duHast.APISamples.Annotation import RevitGenericAnnotation as rGAnno

from duHast.APISamples.Family import RevitFamilyUtils as rFamU

from duHast.APISamples.Common import RevitGroups as rGrp

from duHast.APISamples.Views import RevitViews as rView
from duHast.APISamples.Views import RevitViewReferencing as rViewRef

from duHast.APISamples.Walls import RevitWalls as rWall
from duHast.APISamples.Walls import PurgeUnusedWallTypes as rWallPurge
from duHast.APISamples.Walls import RevitCurtainWallElements as rCurtainWallElem
from duHast.APISamples.Walls import RevitCurtainWalls as rCurtainWall
from duHast.APISamples.Walls import RevitStackedWalls as rStackedWall
from duHast.APISamples.Walls import PurgeUnusedCurtainWallElementTypes as rCurtainWallElemPurge

from duHast.APISamples.Annotation import PurgeUnusedAnnoTypes as rAnnoPurge
from duHast.APISamples.Annotation import RevitArrowHeads as rArrow
from duHast.APISamples.Annotation import RevitDimensions as rDim
from duHast.APISamples.Annotation import RevitMultiRefAnno as rMultiRefAnno
from duHast.APISamples.Annotation import RevitText as rText

from duHast.APISamples.Stairs import PurgeUnusedStairTypes as rStairPurge
from duHast.APISamples.Stairs import RevitStairs as rStair
from duHast.APISamples.Stairs import RevitStairRuns as rStairRun
from duHast.APISamples.Stairs import RevitStairLandings as rStairLanding
from duHast.APISamples.Stairs import RevitStairPath as rStairPath
from duHast.APISamples.Stairs import RevitStairStringersAndCarriages as rStairStringerAndCarriage
from duHast.APISamples.Stairs import RevitStairCutMarks as rStairCutMark

from duHast.APISamples.BuildingPads import RevitBuildingPads as rBuildP
from duHast.APISamples.BuildingPads import PurgeUnusedBuildingPadTypes as rBuildingPadPurge

from duHast.APISamples.Ceilings import RevitCeilings as rCeil
from duHast.APISamples.Ceilings import PurgeUnusedCeilingTypes as rCeilingPurge

from duHast.APISamples.DetailItems import RevitDetailItems as rDet
from duHast.APISamples.DetailItems import PurgeUnusedDetailItemTypes as rDetailItemPurge

from duHast.APISamples.Floors import RevitFloors as rFlo
from duHast.APISamples.Floors import PurgeUnusedFloorTypes as rFloorPurge

from duHast.APISamples.Grids import RevitGrids as rGrid
from duHast.APISamples.Grids import PurgeUnusedGridTypes as rGridPurge

from duHast.APISamples.Levels import RevitLevels as rLev
from duHast.APISamples.Levels import PurgeUnusedLevelTypes as rLevelPurge

from duHast.APISamples.Links import RevitImageLinks as rImageLink
from duHast.APISamples.Links import PurgeUnusedImageLinkTypes as rLinkPurge

from duHast.APISamples.Railings import RevitRailings as rRail
from duHast.APISamples.Railings import RevitBalusters as rBal
from duHast.APISamples.Railings import PurgeUnusedRailingAndBalusterTypes as rRailPurge

from duHast.APISamples.MEP_Systems import PurgeUnusedMEPSymbols as rMEPSymbolPurge
from duHast.APISamples.MEP_Systems import PurgeUnusedMEPTypes as rMEPTypePurge
from duHast.APISamples.MEP_Systems import RevitCableTrays as rCableTray
from duHast.APISamples.MEP_Systems import RevitConduits as rConduit
from duHast.APISamples.MEP_Systems  import RevitDucts as rDuct
from duHast.APISamples.MEP_Systems import RevitPipes as rPipe

from duHast.APISamples.Ramps import RevitRamps as rRam
from duHast.APISamples.Ramps import PurgeUnusedRampTypes as rRampPurge

from duHast.APISamples.Roofs import RevitRoofs as rRoof
from duHast.APISamples.Roofs import PurgeUnusedRoofTypes as rRoofPurge

from duHast.Utilities.timer import Timer
from duHast.APISamples.Purge import RevitPurgeAction as pA

import Autodesk.Revit.DB as rdb
from System.Collections.Generic import List



# --------------------------------------------- Purge - utility ---------------------------------------------

def PurgeUnplacedElements (doc, 
    getUnusedElementIds, 
    transactionName, 
    unUsedElementNameHeader,
    isDebug = False):
    '''
    
    Purges all unplaced elements provided through a passed in element id getter method from a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param getUnusedElementIds: A function accepting the current document as the argument and returning element ids which can be purged.
    :type getUnusedElementIds: func (doc) returning list of Autodesk.Revit.DB.ElementId
    :param transactionName: A human readable description of the transaction containing the purge action.
    :type transactionName: str
    :param unUsedElementNameHeader: The text to be displayed at the start of the list containing the deleted element names.
    :type unUsedElementNameHeader: str
    :param isDebug: True: will return detailed report and attempt to try to delete elements one by one if an exception occurs, defaults to False\
        Will attempt to delete all elements at once.
    :type isDebug: bool, optional

    :return: 
        Result class instance.
        
        - .result = True if all purge actions completed successfully. Otherwise False.
        - .message will be listing each purge action and its status
    
    :rtype: :class:`.Result`
    '''

    resultValue = res.Result()
    try:
        unusedElementIds = getUnusedElementIds(doc)
        unusedElementNames = []
        if(isDebug):
            unusedElementNames.append(unUsedElementNameHeader)
            for unusedId in unusedElementIds:
                unusedElementNames.append(SPACER + 'ID:\t' + str(unusedId) + ' Name:\t'+ rdb.Element.Name.GetValue(doc.GetElement(unusedId)))
        else:
            unusedElementNames.append(unUsedElementNameHeader + ': ' + str(len(unusedElementIds)) + ' Element(s) purged.')
        purgeResult = com.DeleteByElementIds(doc, unusedElementIds, transactionName, '\n'.join( unusedElementNames ))
        # check if an exception occurred and in debug mode, purge elements one by one
        if(isDebug and purgeResult.status == False):
            #pass
            print('second debug run')
            purgeResult = com.DeleteByElementIdsOneByOne(doc, unusedElementIds, transactionName, '\n'.join( unusedElementNames ))
        resultValue.Update(purgeResult)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused ' + unUsedElementNameHeader + ' with exception: '+ str(e))
    return resultValue

# --------------------------------------------- Main ---------------------------------------------

#: list containing purge action names and the purge action method
PURGE_ACTIONS = []
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Model Group(s)', rGrp.GetUnplacedModelGroupIds, 'Model Group(s)', 'Model Group(s)', rGrp.GetModelGroupIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Detail Group(s)', rGrp.GetUnplacedDetailGroupIds, 'Detail Group(s)', 'Detail Group(s)', rGrp.GetDetailGroupIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Nested Detail Group(s)', rGrp.GetUnplacedNestedDetailGroupIds, 'Nested Detail Group(s)', 'Nested Detail Group(s)', rGrp.GetNestedDetailGroupIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Family Types', rView.GetUnusedViewTypeIdsInModel, 'View Family Type(s)', 'View Family Type(s)', rView.GetViewTypeIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Templates', rView.GetAllUnusedViewTemplateIdsInModel, 'View Family Templates(s)', 'View Family Templates(s)', rView.GetViewsTemplateIdsInInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Filters', rView.GetAllUnUsedViewFilters, 'View Filter(s)', 'View Filter(s)', rView.GetAllAvailableFilterIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Image Links', rLinkPurge.GetAllUnusedImageTypeIdsInModel, 'Images(s)', 'Images(s)', rImageLink.GetImagesTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Stacked Wall Types', rWallPurge.GetUnusedStackedWallTypeIdsToPurge, 'Stacked Wall Type(s)', 'Stacked Wall Type(s)', rStackedWall.GetAllStackedWallTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Wall Types', rWallPurge.GetUnusedInPlaceWallIdsForPurge, 'InPlace Wall Type(s)', 'InPlace Wall Type(s)', rWall.GetAllInPlaceWallTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Curtain Wall Types', rWallPurge.GetUnUsedCurtainWallTypeIdsToPurge, 'Curtain Wall Type(s)', 'Curtain Wall Type(s)', rCurtainWall.GetAllCurtainWallTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Basic Types', rWallPurge.GetUnUsedBasicWallTypeIdsToPurge, 'Basic Wall Type(s)', 'Basic Wall Type(s)', rWall.GetAllBasicWallTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Curtain Wall Element Types', rCurtainWallElemPurge.GetUnusedNonSymbolCurtainWallElementTypeIdsToPurge,'Curtain Wall Element Type(s)', 'Curtain Wall Element Type(s)', rCurtainWallElem.GetAllCurtainWallElementTypeIdsByCategoryExclSymbols))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Loadable Curtain Wall Symbol (Types)', rCurtainWallElemPurge.GetUnusedICurtainWallSymbolIdsForPurge,'Curtain Wall Loadable Symbols (Type(s))', 'Curtain Wall Loadable Symbols (Type(s))', rCurtainWallElem.GetAllCurtainWallNonSharedSymbolIdsByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Ceiling Types', rCeilingPurge.GetUnusedNonInPlaceCeilingTypeIdsToPurge, 'Ceiling Type(s)', 'Ceiling Type(s)', rCeil.GetAllCeilingTypeIdsInModelByClass)) # used by class filter to avoid in place families listed
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Ceiling Types', rCeilingPurge.GetUnusedInPlaceCeilingIdsForPurge, 'InPlace Ceiling Type(s)', 'InPlace Ceiling Type(s)', rCeil.GetAllInPlaceCeilingTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Floor Types', rFloorPurge.GetUnusedNonInPlaceFloorTypeIdsToPurge, 'Floor Type(s)', 'Floor Type(s)', rFlo.GetAllFloorTypeIdsInModelByClass)) #TODO check why this is using by class...
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Floor Types', rFloorPurge.GetUnusedInPlaceFloorIdsForPurge, 'InPlace Floor Type(s)', 'InPlace Floor Type(s)', rFlo.GetAllInPlaceFloorTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Roof Types', rRoofPurge.GetUnusedNonInPlaceRoofTypeIdsToPurge, 'Roof Type(s)', 'Roof Type(s)', rRoof.GetAllRoofTypeIdsInModelByClass)) #TODO check why by class
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Roof Types', rRoofPurge.GetUnusedInPlaceRoofIdsForPurge, 'InPlace Roof Type(s)', 'InPlace Roof Type(s)', rRoof.GetAllInPlaceRoofTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Stair Types', rStairPurge.GetUnusedNonInPlaceStairTypeIdsToPurge, 'Stair Type(s)', 'Stair Type(s)', rStair.GetAllStairTypeIdsInModelByClass)) #TODO check why by class
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Path Types', rStairPurge.GetUnusedStairPathTypeIdsToPurge, 'Stair Path Type(s)', 'Stair Path Type(s)', rStairPath.GetAllStairPathTypeIdsInModelByClass))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Landing Types', rStairPurge.GetUnusedStairLandingTypeIdsToPurge, 'Stair Landing Type(s)', 'Stair Landing Type(s)', rStairLanding.GetAllStairLandingTypeIdsInModelByClass))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Run Types', rStairPurge.GetUnusedStairRunTypeIdsToPurge, 'Stair Run Type(s)', 'Stair Run Type(s)', rStairRun.GetAllStairRunTypeIdsInModelByClass))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Stringers and Carriage Types', rStairPurge.GetUnusedStairStringersCarriageTypeIdsToPurge, 'Stair Stringers and Carriage Type(s)', 'Stair Stringers and Carriage Type(s)', rStairStringerAndCarriage.GetAllStairStringCarriageTypeIdsInModelByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Stair Types', rStairPurge.GetUnusedInPlaceStairIdsForPurge,'InPlace Stair Type(s)', 'InPlace Stair Type(s)', rStair.GetAllInPlaceStairTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Ramp Types', rRampPurge.GetUnusedNonInPlaceRampTypeIdsToPurge, 'Ramp Type(s)', 'Ramp Type(s)', rRam.GetAllRampTypeIdsInModelByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Stair Cut Mark Types', rStairPurge.GetUnusedStairCutMarkTypeIdsToPurge, 'Stair Cut Mark Type(s)', 'Stair Cut Mark Type(s)', rStairCutMark.GetAllStairCutMarkTypeIdsInModelByClass))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Building Pad Types', rBuildingPadPurge.GetUnusedNonInPlaceBuildingPadTypeIdsToPurge, 'Building Pad Type(s)', 'Building Pad Type(s)', rBuildP.GetAllBuildingPadTypeIdsInModelByClass))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Railing Types', rRailPurge.GetUnusedNonInPlaceRailingTypeIdsToPurge, 'Railing Type(s)','Railing Type(s)', rRail.GetAllRailingTypeIdsInModelByClassAndCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Railing Types', rRailPurge.GetUnusedInPlaceRailingIdsForPurge,'In Place Railing Type(s)','In Place Railing Type(s)',rRail.GetAllInPlaceRailingTypeIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Baluster Types', rRailPurge.GetUnUsedBalusterTypeIdsForPurge,'Baluster Type(s)','Baluster Type(s)',rBal.GetAllBalusterSymbolIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Cable Tray Types', rMEPTypePurge.GetUnUsedCableTrayTypeIdsToPurge,'Cable Tray Type(s)','Cable Tray Type(s)', rCableTray.GetAllCableTrayTypeIdsInModelByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Conduit Types', rMEPTypePurge.GetUnUsedConduitTypeIdsToPurge,'Conduit Type(s)','Conduit Type(s)', rConduit.GetAllConduitTypeIdsInModelByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Duct Types', rMEPTypePurge.GetUnUsedDuctTypeIdsToPurge,'Duct Type(s)','Duct Type(s)', rDuct.GetAllDuctTypeIdsInModelByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Pipe Types', rMEPTypePurge.GetUnUsedPipeTypeIdsToPurge,'Pipe Type(s)','Pipe Type(s)', rPipe.GetAllPipeTypeIdsInModelByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Cable Tray Symbols and Families', rMEPSymbolPurge.GetUnUsedCableTraySymbolIdsForPurge,'Cable Tray Symbols and Family(s)','Cable Tray Symbols and Family(s)', rCableTray.GetSymbolIdsForCableTrayTypesInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Conduit Symbols and Families', rMEPSymbolPurge.GetUnUsedConduitSymbolIdsForPurge,'Conduit Symbols and Family(s)','Conduit Symbols and Family(s)', rConduit.GetSymbolIdsForConduitTypesInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Duct Symbols and Families', rMEPSymbolPurge.GetUnUsedDuctAndFlexDuctSymbolIdsForPurge,'Duct Symbols and Family(s)','Duct Symbols and Family(s)', rDuct.GetSymbolIdsForDuctTypesInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Pipe Symbols and Families', rMEPSymbolPurge.GetUnUsedPipeSymbolIdsForPurge,'Pipe Symbols and Family(s)','Pipe Symbols and Family(s)', rPipe.GetSymbolIdsForPipeTypesInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Level Types', rLevelPurge.GetUnusedLevelTypesForPurge, 'Level Type(s)', 'Level Type(s)',rLev.GetAllLevelTypeIdsByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Level Head Types', rLevelPurge.GetUnusedLevelHeadFamiliesForPurge, 'Level Head family Type(s)', 'Level Head family Type(s)', rLev.GetAllLevelHeadFamilyTypeIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Grid Types', rGridPurge.GetUnusedGridTypesForPurge, 'Grid Type(s)', 'Grid Type(s)', rGrid.GetAllGridTypeIdsByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Grid Head Types', rGridPurge.GetUnusedGridHeadFamiliesForPurge, 'Grid Head family Type(s)', 'Grid Head family Type(s)', rGrid.GetAllGridHeadFamilyTypeIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Reference Types', rViewRef.GetUnusedViewReferenceTypeIdsForPurge, 'View Ref Type(s)', 'View Ref Type(s)', rViewRef.GetAllViewReferenceTypeIdDataAsList))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Continuation Types', rViewRef.GetUnusedContinuationMarkerTypeIdsForPurge, 'View Continuation Type(s)', 'View Continuation Type(s)', rViewRef.GetAllViewContinuationTypeIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Reference Families', rViewRef.GetUnusedViewRefAndContinuationMarkerFamiliesForPurge, 'View Ref and Continuation Marker families(s)', 'View Ref and Continuation Marker families(s)', rViewRef.GetAllViewReferenceSymbolIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Repeating Details', rDetailItemPurge.GetUnUsedRepeatingDetailTypeIdsForPurge, 'Repeating Detail Type(s)', 'Repeating Detail Type(s)', rDet.GetAllRepeatingDetailTypeIdsAvailable))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Filled Regions', rDetailItemPurge.GetUnUsedFilledRegionTypeIdsForPurge, 'Filled Region Type(s)', 'Filled Region Type(s)', rDet.GetAllFilledRegionTypeIdsAvailable))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Details Symbols', rDetailItemPurge.GetAllUnUsedDetailSymbolIdsForPurge, 'Detail Symbol(s)', 'Detail Symbol(s)', rDet.GetAllDetailSymbolIdsAvailable))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused MultiRef Dimension Types', rAnnoPurge.GetAllUnusedMultiRefDimTypeIdsInModel,'MultiRef Dimension Type(s)', 'MultiRef Dimension Type(s)', rMultiRefAnno.GetAllMultiRefAnnotationTypeIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Dimension Types', rAnnoPurge.GetAllUnusedDimTypeIdsInModel, 'Dimension Type(s)', 'Dimension Type(s)', rDim.GetDimTypeIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Text Types', rAnnoPurge.GetAllUnusedTextTypeIdsInModel,'Text Type(s)', 'Text Type(s)', rText.GetAllTextTypeIds))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Arrow Heads', rAnnoPurge.GetAllUnusedArrowTypeIdsInModel, 'Arrow Head Type(s)', 'Arrow Head Type(s)', rArrow.GetArrowTypesIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Generic Annotation',  rAnnoPurge.GetUnusedGenericAnnotationIdsForPurge, 'Generic Anno Type(s)', 'Generic Anno Type(s)',  rGAnno.GetAllGenericAnnotationTypeIdsByCategory))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused SpotElevation Symbols',  rAnnoPurge.GetUnusedSymbolIdsFromSpotTypesToPurge, 'Spot Elevation Symbol(s)', 'Spot Elevation Symbol(s)',  rAnnoSpot.GetAllSpotElevationSymbolIdsInModel))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Loadable Family Types', rFamU.GetUnusedNonSharedFamilySymbolsAndTypeIdsToPurge, 'Loadable Non Shared Family Type(s)', 'Loadable Non Shared Family Type(s)', rFamU.GetAllNonSharedFamilySymbolIds)) #TODO check its not deleting to much


#: indentation for names of items purged
SPACER = '...'

# set up a timer objects
t = Timer()
tOverall = Timer()

def PurgeUnused(doc, revitFilePath, isDebug):
    '''
    Calls all available purge actions defined in global list.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: Fully qualified file path of current model document. (Not used)
    :type revitFilePath: str
    :param isDebug: True: will return detailed report and attempt to try to delete elements one by one if an exception occurs. False\
        Will attempt to delete all elements at once, less detailed purge report.
    :type isDebug: bool

    :return: 
        Result class instance.
        
        - .result = True if all purge actions completed successfully. Otherwise False.
        - .message will be listing each purge action and its status
    
    :rtype: :class:`.Result`
    '''

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
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Purge unit testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#: list containing keys to be ignored in comparison code
#: these keys do not get purged by Revit's native purge unused and would therefore show up as false positives
COMPARISON_IGNORE= [
    'View Family Type(s)',
    'View Family Templates(s)',
    'View Filter(s)'
]

# doc                       current document
# typeIdGetter              function which returns all available type ids
# reportHeader              the first entry per row written to file
# outputFilePath            location of file
# counter                   action counter, if 0 the report file will be created from scratch, any other value means append to existing report file
def WriteAvailableTypeIds(doc, typeIdGetter, reportHeader, outputFilePath, counter):
    '''gets all available type ids from passed in type id getter and writes result to file'''
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
        resultValue.UpdateSep(True,'Added type group ' + reportHeader + ' with ' + str(len(typeIds)) + ' entries ' +  writeType)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused ' + reportHeader + ' with exception: '+ str(e))
    return resultValue

# first     base line dictionary
# second    dictionary to be checked against base line
def CompareReportDictionaries(first,second):
    '''comparison will return all elements which are in first dictionary only, True if none are missing'''
    resultValue = res.Result()
    for key,value in first.items():
        if(key not in COMPARISON_IGNORE):
            if(second.has_key(key)):
                # check whether all values in base line key are in matching comparison key
                notInList = []
                for d in first[key]:
                    if d not in second[key]:
                        notInList.append(d)
                if(len(notInList) > 0):
                    resultValue.status = False
                    resultValue.AppendMessage(key + ' has different ids!')
                    data = [key] + notInList
                    resultValue.result.append(data)
            else:
                # entire key is missing!
                resultValue.AppendMessage(key + ' is missing!')
                resultValue.status = False
                data = [key] + first[key]
                resultValue.result.append(data)
    # check whether any dif was found
    if(len(resultValue.result) == 0):
        resultValue.UpdateSep(True, "All elements from first dictionary are in second dictionary")
    return resultValue

# data      list of list of strings
def ConvertReportDataIntoDictionary(data):
    '''build a dictionary where key is the first entry in each list, values are all subsequent entries in the same list'''
    dic = {}
    for d in data:
        dic[d[0]] = []
        for i in range(0,len(d)-1):
            if(i>0):
                dic[d[0]].append(d[i])
    return dic

# fileSource            bench mark type ids file
# fileTest              file to check against the benchmark
def CompareReportData(fileSource, fileTest):
    resultValue = res.Result()
    '''used to compare a bench mark results file containing type ids against a new results file
    will report missing or additional ids in results file'''
    sourceRows = util.ReadTabSeparatedFile(fileSource)
    testRows = util.ReadTabSeparatedFile(fileTest)
    sourceDic = ConvertReportDataIntoDictionary(sourceRows)
    testDic = ConvertReportDataIntoDictionary(testRows)
    # check benchmark against test
    statusSource = CompareReportDictionaries(sourceDic, testDic)
    # update overall status
    resultValue.UpdateStatus(statusSource.status)
    if(statusSource.status == True):
        resultValue.message ='Benchmark contains no additional ids'
    else:
        resultValue.message ='Benchmark contains additional ids'
        resultValue.AppendMessage(statusSource.message)
        resultValue.result.append({'Benchmark':statusSource.result})
    
    # check test against benchmark
    statusTest = CompareReportDictionaries(testDic, sourceDic)

    resultValue.UpdateStatus(statusTest.status)
    # update overall message with data from test benchmark comparison
    if(statusTest.status == True):
        resultValue.AppendMessage('\n' + 'Test contains no additional ids')
    else:
        resultValue.AppendMessage('\n' + 'Test contains additional ids')
        resultValue.AppendMessage(statusTest.message)
        resultValue.result.append({'Test':statusTest.result})

    return resultValue

# doc           current document
# filePath      fully qualified report file path
def ReportAvailableTypeIds(doc, filePath):
    '''calls all available type id getter functions and writes results to file'''
    resultValue = res.Result()
    tOverall.start()
    counter = 0 #any counter value greater then 0 means append to report file rather then creating a new file
    for pA in PURGE_ACTIONS:
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
