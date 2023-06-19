"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit export model to ifc tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import os
from test.Revit.TestUtils import revit_test
from duHast.Utilities import result as res

from duHast.Revit.Exports.export_ifc import (
    export_model_to_ifc,
    setup_ifc_export_option,
    ifc_get_third_party_export_config_by_model,
)
from duHast.Revit.Exports.Utility.ifc_export_settings import IFCSettings

from test.Revit.Exports.exports import IFC_TEST_FILE_NAME
from duHast.Utilities.files_io import file_exist

import Autodesk.Revit.DB as rdb

class ExportModelToIFC(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(ExportModelToIFC, self).__init__(doc=doc, test_name="export_model_to_ifc",requires_temp_dir=True)

    def _setup_settings(self):
        name  = 'batch processor sample code'
        ifcVersion  = 'IFC2x2'
        spaceBoundaries = 1
        activePhaseId = -1
        activeViewId = -1
        exportBaseQuantities = True 
        splitWallsAndColumns = True 
        visibleElementsOfCurrentView = False 
        use2DRoomBoundaryForVolume = True
        useFamilyAndTypeNameForReference = False 
        exportInternalRevitPropertySets = True
        exportIFCCommonPropertySets = True
        export2DElements = True
        exportPartsAsBuildingElements = True
        exportBoundingBox = False
        exportSolidModelRep = False
        exportSchedulesAsPsets = False 
        exportUserDefinedPsets = False 
        exportUserDefinedPsetsFileName = '' 
        exportLinkedFiles = False 
        includeSiteElevation = True  
        useActiveViewGeometry = False # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
        exportSpecificSchedules = False 
        tessellationLevelOfDetail = 0
        storeIFCGUID = True 
        exportRoomsInView = True 
        useOnlyTriangulation = False
        includeSteelElements = True 
        cOBieCompanyInfo = 'n/a'
        cOBieProjectInfo = 'batch processor sample code'
        useTypeNameOnlyForIfcType = True
        useVisibleRevitNameAsEntityName = True
        sitePlacement = 'SiteTransformBasis.Shared'
        selectedSite = 'sample site'
        geoRefCRSName = 'geoRefCRSName'
        geoRefCRSDesc ='geoRefCRSDesc'
        geoRefEPSGCode ='geoRefEPSGCode'
        geoRefGeodeticDatum ='geoRefGeodeticDatum'
        geoRefMapUnit ='geoRefMapUnit'
        excludeFilter = ''
        
        # set up settings class
        ifc_settings_test = IFCSettings(
            name, 
            ifcVersion, 
            spaceBoundaries,
            activePhaseId,
            activeViewId,
            exportBaseQuantities,
            splitWallsAndColumns,
            visibleElementsOfCurrentView,
            use2DRoomBoundaryForVolume,
            useFamilyAndTypeNameForReference,
            exportInternalRevitPropertySets,
            exportIFCCommonPropertySets,
            export2DElements,
            exportPartsAsBuildingElements,
            exportBoundingBox,
            exportSolidModelRep,
            exportSchedulesAsPsets,
            exportUserDefinedPsets,
            exportUserDefinedPsetsFileName,
            exportLinkedFiles,
            includeSiteElevation,
            useActiveViewGeometry,
            exportSpecificSchedules,
            tessellationLevelOfDetail,
            storeIFCGUID,
            exportRoomsInView,
            useOnlyTriangulation,
            includeSteelElements,
            cOBieCompanyInfo,
            cOBieProjectInfo,
            useTypeNameOnlyForIfcType,
            useVisibleRevitNameAsEntityName,
            sitePlacement,
            selectedSite,
            geoRefCRSName,
            geoRefCRSDesc,
            geoRefEPSGCode,
            geoRefGeodeticDatum,
            geoRefMapUnit,
            excludeFilter
        )
        return ifc_settings_test

    def test(self):
        """
        export_model_to_ifc test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if model was exported successfully, otherwise False
                - .message will contain result(s) vs expected result(s)
                - . result (empty list)

                on exception:

                - .result Will be False
                - .message will contain exception message.
                - . result (empty list)
        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        try:

            # ifc settings
            ifc_export_settings= self._setup_settings()
            # setup an export config by model:
            ifc_config = ifc_get_third_party_export_config_by_model(
                doc=self.document,
                ifc_version=rdb.IFCVersion.IFC2x2,
                ifc_settings=ifc_export_settings
            )
            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    result = export_model_to_ifc(
                        doc=doc,
                        ifc_export_config=ifc_config,
                        directory_path=self.tmp_dir,
                        file_name=IFC_TEST_FILE_NAME
                    )
                    action_return_value.append_message('Export model to ifc completed with status: {} and message: {}'.format(result.status, result.message))
                    assert(result.status == True)
                    
                    # check if file exists
                    file_created = file_exist(full_file_path=os.path.join(self.tmp_dir, IFC_TEST_FILE_NAME))
                    action_return_value.append_message('IFC file was created: {} at: {}'.format(file_created, os.path.join(self.tmp_dir, IFC_TEST_FILE_NAME)))
                    assert(file_created==True)
                    
                    action_return_value.update_sep(
                        True, "IFC model was exported successfully.")
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in function {}: {}".format(
                            self.test_name, e
                        ),
                    )
                return action_return_value

            return_value = self.in_transaction_group(action)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )
        finally:
            # clean up temp directory
            clean_up = self.clean_up()
            return_value.update_sep(
                clean_up,
                "Attempted to clean up temp directory with result: {}".format(clean_up),
            )
        return return_value
