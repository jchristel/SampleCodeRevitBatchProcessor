"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit export view to ifc tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import os
from test.Revit.TestUtils import revit_test
from duHast.Utilities.Objects import result as res

from duHast.Revit.Exports.export_ifc import (
    export_3d_views_to_ifc,
    setup_ifc_export_option,
    ifc_get_third_party_export_config_by_view,
)
from duHast.Revit.Exports.Utility.ifc_export_settings import IFCSettings

from test.Revit.Exports.exports import IFC_TEST_FILE_NAME
from duHast.Utilities.files_io import file_exist

import Autodesk.Revit.DB as rdb
from revit_script_util import Output


class ExportViewToIFC(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(ExportViewToIFC, self).__init__(
            doc=doc, test_name="export_3d_views_to_ifc", requires_temp_dir=True
        )

    def _setup_settings(self):
        name = "batch processor sample code"
        ifcVersion = "IFC2x2"
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
        exportUserDefinedPsetsFileName = ""
        exportLinkedFiles = False
        includeSiteElevation = True
        useActiveViewGeometry = False  # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
        exportSpecificSchedules = False
        tessellationLevelOfDetail = 0
        storeIFCGUID = True
        exportRoomsInView = True
        useOnlyTriangulation = False
        includeSteelElements = True
        cOBieCompanyInfo = "n/a"
        cOBieProjectInfo = "batch processor sample code"
        useTypeNameOnlyForIfcType = True
        useVisibleRevitNameAsEntityName = True
        sitePlacement = "SiteTransformBasis.Shared"
        selectedSite = "sample site"
        geoRefCRSName = "geoRefCRSName"
        geoRefCRSDesc = "geoRefCRSDesc"
        geoRefEPSGCode = "geoRefEPSGCode"
        geoRefGeodeticDatum = "geoRefGeodeticDatum"
        geoRefMapUnit = "geoRefMapUnit"
        excludeFilter = ""

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
            excludeFilter,
        )
        return ifc_settings_test

    def view_name(self, name):
        return IFC_TEST_FILE_NAME

    def test(self):
        """
        export_3d_views_to_ifc test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if view was exported successfully, otherwise False
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
            ifc_export_settings = self._setup_settings()
            # setup an export config by model:
            ifc_config = ifc_get_third_party_export_config_by_view(
                doc=self.document,
                ifc_version=rdb.IFCVersion.IFC2x2,
                ifc_settings=ifc_export_settings,
            )

            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    result = export_3d_views_to_ifc(
                        doc=doc,
                        view_filter="Export",
                        ifc_export_config=ifc_config,
                        directory_path=self.tmp_dir,
                        do_something_with_view_name=self.view_name,
                    )
                    action_return_value.append_message(
                        "Export view to ifc completed with status: {} and message: {}".format(
                            result.status, result.message
                        )
                    )
                    assert result.status == True

                    # check if file exists
                    file_created = file_exist(
                        full_file_path=os.path.join(self.tmp_dir, IFC_TEST_FILE_NAME)
                    )
                    action_return_value.append_message(
                        "IFC file was created: {} at: {}".format(
                            file_created, os.path.join(self.tmp_dir, IFC_TEST_FILE_NAME)
                        )
                    )
                    assert file_created == True

                    action_return_value.update_sep(
                        True, "IFC model was exported successfully."
                    )
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
