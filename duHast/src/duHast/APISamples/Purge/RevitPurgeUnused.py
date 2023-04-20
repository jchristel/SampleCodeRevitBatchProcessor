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

from duHast.Utilities import FilesIO as util
from duHast.Utilities import Result as res

from duHast.APISamples.Annotation import RevitSpotDimensions as rAnnoSpot
from duHast.APISamples.Annotation import RevitGenericAnnotation as rGAnno

from duHast.APISamples.Family import RevitFamilyUtils as rFamUPurge
from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge

from duHast.APISamples.Common import RevitGroups as rGrp
from duHast.APISamples.Common import RevitDeleteElements as rDel

from duHast.APISamples.Views import RevitViews as rView
from duHast.APISamples.Views import RevitViewReferencing as rViewRef
from duHast.APISamples.Views import RevitViewFilters as rViewFilter
from duHast.APISamples.Views import RevitViewsPurgeUnused as rViewPurge
from duHast.APISamples.Views import RevitViewTemplates as rViewTemp

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

def purge_unplaced_elements (doc, 
    get_unused_element_ids, 
    transaction_name, 
    unused_element_name_header,
    is_debug = False):
    '''
    
    Purges all unplaced elements provided through a passed in element id getter method from a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param get_unused_element_ids: A function accepting the current document as the argument and returning element ids which can be purged.
    :type get_unused_element_ids: func (doc) returning list of Autodesk.Revit.DB.ElementId
    :param transaction_name: A human readable description of the transaction containing the purge action.
    :type transaction_name: str
    :param unused_element_name_header: The text to be displayed at the start of the list containing the deleted element names.
    :type unused_element_name_header: str
    :param is_debug: True: will return detailed report and attempt to try to delete elements one by one if an exception occurs, defaults to False\
        Will attempt to delete all elements at once.
    :type is_debug: bool, optional

    :return: 
        Result class instance.
        
        - .result = True if all purge actions completed successfully. Otherwise False.
        - .message will be listing each purge action and its status
    
    :rtype: :class:`.Result`
    '''

    resultValue = res.Result()
    try:
        unusedElementIds = get_unused_element_ids(doc)
        unusedElementNames = []
        ifis_debug:
            unusedElementNames.append(unused_element_name_header)
            for unusedId in unusedElementIds:
                unusedElementNames.append(SPACER + 'ID:\t' + str(unusedId) + ' Name:\t'+ rdb.Element.Name.GetValue(doc.GetElement(unusedId)))
        else:
            unusedElementNames.append(unused_element_name_header + ': ' + str(len(unusedElementIds)) + ' Element(s) purged.')
        purgeResult = rDel.delete_by_element_ids(doc, unusedElementIds, transaction_name, '\n'.join( unusedElementNames ))
        # check if an exception occurred and in debug mode, purge elements one by one
        if(is_debug and purgeResult.status == False):
            #pass
            print('second debug run')
            purgeResult = rDel.delete_by_element_ids_one_by_one(doc, unusedElementIds, transaction_name, '\n'.join( unusedElementNames ))
        resultValue.update(purgeResult)
    except Exception as e:
        resultValue.update_sep(False,'Terminated purge unused ' + unused_element_name_header + ' with exception: '+ str(e))
    return resultValue

# --------------------------------------------- Main ---------------------------------------------

#: list containing purge action names and the purge action method
PURGE_ACTIONS = []
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Model Group(s)', rGrp.get_unplaced_model_group_ids, 'Model Group(s)', 'Model Group(s)', rGrp.get_model_group_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Detail Group(s)', rGrp.get_unplaced_detail_group_ids, 'Detail Group(s)', 'Detail Group(s)', rGrp.get_detail_group_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Nested Detail Group(s)', rGrp.get_unplaced_nested_detail_group_ids, 'Nested Detail Group(s)', 'Nested Detail Group(s)', rGrp.get_nested_detail_group_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Family Types', rViewPurge.get_unused_view_type_ids, 'View Family Type(s)', 'View Family Type(s)', rView.get_view_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Templates', rViewTemp.get_all_unused_view_template_ids, 'View Family Templates(s)', 'View Family Templates(s)', rViewTemp.get_view_templates_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Filters', rViewFilter.get_all_unused_view_filters, 'View Filter(s)', 'View Filter(s)', rViewFilter.get_all_filter_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Image Links', rLinkPurge.get_all_unused_image_type_ids_in_model, 'Images(s)', 'Images(s)', rImageLink.get_images_type_ids_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Stacked Wall Types', rWallPurge.get_unused_stacked_wall_type_ids_to_purge, 'Stacked Wall Type(s)', 'Stacked Wall Type(s)', rStackedWall.get_all_stacked_wall_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Wall Types', rWallPurge.get_unused_in_place_wall_ids_for_purge, 'InPlace Wall Type(s)', 'InPlace Wall Type(s)', rWall.get_all_in_place_wall_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Curtain Wall Types', rWallPurge.get_unused_curtain_wall_type_ids_to_purge, 'Curtain Wall Type(s)', 'Curtain Wall Type(s)', rCurtainWall.get_all_curtain_wall_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Basic Types', rWallPurge.get_unused_basic_wall_type_ids_to_purge, 'Basic Wall Type(s)', 'Basic Wall Type(s)', rWall.get_all_basic_wall_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Curtain Wall Element Types', rCurtainWallElemPurge.get_unused_non_symbol_curtain_wall_element_type_ids_to_purge,'Curtain Wall Element Type(s)', 'Curtain Wall Element Type(s)', rCurtainWallElem.get_all_curtain_wall_element_type_ids_by_category_excl_symbols))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Loadable Curtain Wall Symbol (Types)', rCurtainWallElemPurge.get_unused_curtain_wall_symbol_ids_for_purge,'Curtain Wall Loadable Symbols (Type(s))', 'Curtain Wall Loadable Symbols (Type(s))', rCurtainWallElem.get_all_curtain_wall_non_shared_symbol_ids_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Ceiling Types', rCeilingPurge.get_unused_non_in_place_ceiling_type_ids_to_purge, 'Ceiling Type(s)', 'Ceiling Type(s)', rCeil.get_all_ceiling_type_ids_in_model_by_class)) # used by class filter to avoid in place families listed
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Ceiling Types', rCeilingPurge.get_unused_in_place_ceiling_ids_for_purge, 'InPlace Ceiling Type(s)', 'InPlace Ceiling Type(s)', rCeil.get_all_in_place_ceiling_type_ids_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Floor Types', rFloorPurge.get_unused_non_in_place_floor_type_ids_to_purge, 'Floor Type(s)', 'Floor Type(s)', rFlo.get_all_floor_type_ids_in_model_by_class)) #TODO check why this is using by class...
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Floor Types', rFloorPurge.get_unused_in_place_floor_ids_for_purge, 'InPlace Floor Type(s)', 'InPlace Floor Type(s)', rFlo.get_all_in_place_floor_type_ids_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Roof Types', rRoofPurge.get_unused_non_in_place_roof_type_ids_to_purge, 'Roof Type(s)', 'Roof Type(s)', rRoof.get_all_roof_type_ids_by_class)) #TODO check why by class
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Roof Types', rRoofPurge.get_unused_in_place_roof_type_ids_for_purge, 'InPlace Roof Type(s)', 'InPlace Roof Type(s)', rRoof.get_all_in_place_roof_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Stair Types', rStairPurge.get_unused_non_in_place_stair_type_ids_to_purge, 'Stair Type(s)', 'Stair Type(s)', rStair.get_all_stair_type_ids_by_class)) #TODO check why by class
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Path Types', rStairPurge.get_unused_stair_path_type_ids_to_purge, 'Stair Path Type(s)', 'Stair Path Type(s)', rStairPath.get_stair_path_types_ids_by_class))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Landing Types', rStairPurge.get_unused_stair_landing_type_ids_to_purge, 'Stair Landing Type(s)', 'Stair Landing Type(s)', rStairLanding.get_stair_landing_types_ids_by_class))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Run Types', rStairPurge.get_unused_stair_run_type_ids_to_purge, 'Stair Run Type(s)', 'Stair Run Type(s)', rStairRun.get_stair_run_types_ids_by_class))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Stringers and Carriage Types', rStairPurge.get_unused_stair_stringers_carriage_type_ids_to_purge, 'Stair Stringers and Carriage Type(s)', 'Stair Stringers and Carriage Type(s)', rStairStringerAndCarriage.get_all_stair_stringers_carriage_type_ids_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Stair Types', rStairPurge.get_unused_in_place_stair_type_ids_for_purge,'InPlace Stair Type(s)', 'InPlace Stair Type(s)', rStair.get_all_in_place_stair_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Ramp Types', rRampPurge.get_unused_non_in_place_ramp_type_ids_to_purge, 'Ramp Type(s)', 'Ramp Type(s)', rRam.get_all_ramp_types_ids_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Stair Cut Mark Types', rStairPurge.get_unused_stair_cut_mark_type_ids_to_purge, 'Stair Cut Mark Type(s)', 'Stair Cut Mark Type(s)', rStairCutMark.get_stair_cut_mark_types_ids_by_class))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Building Pad Types', rBuildingPadPurge.get_unused_non_in_place_building_pad_type_ids_to_purge, 'Building Pad Type(s)', 'Building Pad Type(s)', rBuildP.get_all_building_pad_type_ids_in_model_by_class))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Railing Types', rRailPurge.get_unused_non_in_place_railing_type_ids_to_purge, 'Railing Type(s)','Railing Type(s)', rRail.get_all_railing_type_ids_by_class_and_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused InPlace Railing Types', rRailPurge.get_unused_in_place_railing_ids_for_purge,'In Place Railing Type(s)','In Place Railing Type(s)',rRail.get_in_place_railing_type_ids_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Baluster Types', rRailPurge.get_unused_baluster_type_ids_for_purge,'Baluster Type(s)','Baluster Type(s)',rBal.get_all_baluster_symbols_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Cable Tray Types', rMEPTypePurge.get_unused_cable_tray_type_ids_to_purge,'Cable Tray Type(s)','Cable Tray Type(s)', rCableTray.get_all_cable_tray_type_ids_in_model_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Conduit Types', rMEPTypePurge.get_unused_conduit_type_ids_to_purge,'Conduit Type(s)','Conduit Type(s)', rConduit.get_all_conduit_type_ids_in_model_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Duct Types', rMEPTypePurge.get_unused_duct_type_ids_to_purge,'Duct Type(s)','Duct Type(s)', rDuct.get_all_duct_type_ids_in_model_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Pipe Types', rMEPTypePurge.get_unused_pipe_type_ids_to_purge,'Pipe Type(s)','Pipe Type(s)', rPipe.get_all_pipe_type_ids_in_model_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Cable Tray Symbols and Families', rMEPSymbolPurge.get_unused_cable_tray_symbol_ids_for_purge,'Cable Tray Symbols and Family(s)','Cable Tray Symbols and Family(s)', rCableTray.get_symbol_ids_for_cable_tray_types_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Conduit Symbols and Families', rMEPSymbolPurge.get_unused_conduit_symbol_ids_for_purge,'Conduit Symbols and Family(s)','Conduit Symbols and Family(s)', rConduit.get_symbol_ids_for_conduit_types_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Duct Symbols and Families', rMEPSymbolPurge.get_unused_duct_and_flex_duct_symbol_ids_for_purge,'Duct Symbols and Family(s)','Duct Symbols and Family(s)', rDuct.get_symbol_ids_for_duct_types_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Pipe Symbols and Families', rMEPSymbolPurge.get_unused_pipe_symbol_ids_for_purge,'Pipe Symbols and Family(s)','Pipe Symbols and Family(s)', rPipe.get_symbol_ids_for_pipe_types_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Level Types', rLevelPurge.get_unused_level_types_for_purge, 'Level Type(s)', 'Level Type(s)',rLev.get_all_level_type_ids_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Level Head Types', rLevelPurge.get_unused_level_head_families_for_purge, 'Level Head family Type(s)', 'Level Head family Type(s)', rLev.get_all_level_head_family_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Grid Types', rGridPurge.get_unused_grid_types_for_purge, 'Grid Type(s)', 'Grid Type(s)', rGrid.get_all_grid_type_ids_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Grid Head Types', rGridPurge.get_unused_grid_head_families_for_purge, 'Grid Head family Type(s)', 'Grid Head family Type(s)', rGrid.get_all_grid_head_family_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Reference Types', rViewPurge.get_unused_view_reference_type_ids_for_purge, 'View Ref Type(s)', 'View Ref Type(s)', rViewRef.get_all_view_reference_type_id_data_as_list))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Continuation Types', rViewPurge.get_unused_continuation_marker_type_ids_for_purge, 'View Continuation Type(s)', 'View Continuation Type(s)', rViewRef.get_all_view_continuation_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused View Reference Families', rViewPurge.get_unused_view_ref_and_continuation_marker_families_for_purge, 'View Ref and Continuation Marker families(s)', 'View Ref and Continuation Marker families(s)', rViewRef.get_all_view_reference_symbol_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Repeating Details', rDetailItemPurge.get_unused_repeating_detail_type_ids_for_purge, 'Repeating Detail Type(s)', 'Repeating Detail Type(s)', rDet.get_all_repeating_detail_type_ids_available))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Filled Regions', rDetailItemPurge.get_unused_filled_region_type_ids_for_purge, 'Filled Region Type(s)', 'Filled Region Type(s)', rDet.get_all_filled_region_type_ids_available))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Details Symbols', rDetailItemPurge.get_all_unused_detail_symbol_ids_for_purge, 'Detail Symbol(s)', 'Detail Symbol(s)', rDet.get_all_detail_symbol_ids_available))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused MultiRef Dimension Types', rAnnoPurge.get_all_unused_multi_ref_dim_type_ids_in_model,'MultiRef Dimension Type(s)', 'MultiRef Dimension Type(s)', rMultiRefAnno.get_all_multi_ref_annotation_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Dimension Types', rAnnoPurge.get_all_unused_dim_type_ids_in_model, 'Dimension Type(s)', 'Dimension Type(s)', rDim.get_dim_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Text Types', rAnnoPurge.get_all_unused_text_type_ids_in_model,'Text Type(s)', 'Text Type(s)', rText.get_all_text_type_ids))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Arrow Heads', rAnnoPurge.get_all_unused_arrow_type_ids_in_model, 'Arrow Head Type(s)', 'Arrow Head Type(s)', rArrow.get_arrow_type_ids_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Generic Annotation',  rAnnoPurge.get_unused_generic_annotation_ids_for_purge, 'Generic Anno Type(s)', 'Generic Anno Type(s)',  rGAnno.get_all_generic_annotation_type_ids_by_category))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused SpotElevation Symbols',  rAnnoPurge.get_unused_symbol_ids_from_spot_types_to_purge, 'Spot Elevation Symbol(s)', 'Spot Elevation Symbol(s)',  rAnnoSpot.get_all_spot_elevation_symbol_ids_in_model))
PURGE_ACTIONS.append( pA.PurgeAction('Purge Unused Loadable Family Types', rFamPurge.get_unused_non_shared_family_symbols_and_type_ids_to_purge, 'Loadable Non Shared Family Type(s)', 'Loadable Non Shared Family Type(s)', rFamUPurge.get_all_non_shared_family_symbol_ids)) #TODO check its not deleting to much


#: indentation for names of items purged
SPACER = '...'

# set up a timer objects
TIMER_TASK = Timer()
TIMER_OVERALL = Timer()

def purge_unused(doc, revit_file_path, is_debug):
    '''
    Calls all available purge actions defined in global list.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: Fully qualified file path of current model document. (Not used)
    :type revit_file_path: str
    :param is_debug: True: will return detailed report and attempt to try to delete elements one by one if an exception occurs. False\
        Will attempt to delete all elements at once, less detailed purge report.
    :type is_debug: bool

    :return: 
        Result class instance.
        
        - .result = True if all purge actions completed successfully. Otherwise False.
        - .message will be listing each purge action and its status
    
    :rtype: :class:`.Result`
    '''

    # the current file name
    revitFileName = util.get_file_name_without_ext(revit_file_path)
    result_value = res.Result()
    TIMER_OVERALL.start()
    for pA in PURGE_ACTIONS:
        try:
            TIMER_TASK.start()
            purge_flag = purge_unplaced_elements(
                doc,
                pA.purgeIdsGetter,
                pA.purgeTransactionName,
                pA.purgeReportHeader,
                is_debug
            )
            purge_flag.append_message('{}{}'.format(SPACER,TIMER_TASK.stop()))
            result_value.update(purge_flag)
        except Exception as e:
            result_value.update_sep(False,'Terminated purge unused actions with exception: {}'.format(e))
    result_value.append_message('purge duration: {}'.formatTIMER_OVERALL.stop())
    return result_value