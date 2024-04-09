"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit export model to nwc tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import os
from test.Revit.TestUtils import revit_test
from duHast.Utilities.Objects import result as res

from duHast.Revit.Exports.export_navis import (
    export_model_to_nwc,
    setup_nwc_custom_export_option,
)

from test.Revit.Exports.exports import NWC_TEST_FILE_NAME
from duHast.Utilities.files_io import file_exist

import Autodesk.Revit.DB as rdb

class ExportModelToNWC(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(ExportModelToNWC, self).__init__(doc=doc, test_name="export_model_to_nwc",requires_temp_dir=True)

    def test(self):
        """
        export_model_to_nwc test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .status True if model was exported successfully, otherwise False
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
            # get navis export config
            test_data = setup_nwc_custom_export_option(
                using_shared_coordinates=True,
                export_entire_model=True,
                export_links=False,
                split_model_by_level=True,
                export_parts=True,
                export_room_as_attributes=False,
                export_room_geometry=False,
                find_missing_materials=False,
                navis_parameters=rdb.NavisworksParameters.Elements,
                convert_element_properties=True
            )

            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    result = export_model_to_nwc(
                        doc=self.document,
                        nwc_export_option=test_data,
                        directory_path=self.tmp_dir,
                        file_name=NWC_TEST_FILE_NAME
                    )
                    action_return_value.append_message('Export model to nwc completed with status: {} and message: {}'.format(result.status, result.message))
                    assert(result.status == True)
                    # check if file exists
                    file_created = file_exist(full_file_path=os.path.join(self.tmp_dir, NWC_TEST_FILE_NAME))
                    action_return_value.append_message('NWC file was created: {} at: {}'.format(file_created, os.path.join(self.tmp_dir, NWC_TEST_FILE_NAME)))
                    assert(file_created==True)
                    action_return_value.update_sep(
                        True, "NWC model was exported successfully.")
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
