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

from test.Revit.Exports.exports import IFC_TEST_FILE_NAME
from duHast.Utilities.files_io import file_exist

import Autodesk.Revit.DB as rdb

class ExportModelToIFC(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(ExportModelToIFC, self).__init__(doc=doc, test_name="export_model_to_ifc",requires_temp_dir=True)

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
            #TODO:

            
            # setup an export config by model:
            ifc_config = ifc_get_third_party_export_config_by_model(
                ifc_version=rdb.IFCVersion.IFC2x2,
                ifc_settings=""
            )
            # get ifc export config (shared coords, no view id == model export)
            test_data = setup_ifc_export_option(
                export_config=ifc_config
            )

            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    result = export_model_to_ifc(
                        doc=self.document,
                        ifc_export_option=test_data,
                        directory_path=self.tmp_dir,
                        file_name=IFC_TEST_FILE_NAME
                    )
                    action_return_value.append_message('Export model to ifc completed with status: '.format(result.status))
                    assert(result.status == True)
                    # check if file exists
                    file_created = file_exist(full_file_path=os.path.join(self.tmp_dir, IFC_TEST_FILE_NAME))
                    action_return_value.append_message('IFC file was created: {}'.format(file_created))
                    assert(file_created==True)
                    action_return_value.update_sep(
                        True, "Model was exported successfully.")
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

        return return_value
