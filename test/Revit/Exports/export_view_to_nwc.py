"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit export model view to nwc tests . 
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

from duHast.Revit.Exports.export_navis import (
    export_3d_views_to_nwc,
    setup_nwc_custom_export_option,
)

from test.Revit.Exports.exports import NWC_TEST_FILE_NAME
from duHast.Utilities.files_io import file_exist

import Autodesk.Revit.DB as rdb

class ExportViewToNWC(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(ExportViewToNWC, self).__init__(doc=doc, test_name="export_3d_views_to_nwc",requires_temp_dir=True)

    def view_name(name):
        return NWC_TEST_FILE_NAME
    
    def test(self):
        """
        export_3d_views_to_nwc test

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
            # get navis export config
            test_data = setup_nwc_custom_export_option(
                using_shared_coordinates=True,
                export_entire_model=False,
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
                    result = export_3d_views_to_nwc(
                        doc=self.document,
                        view_filter="export",
                        nwc_export_option=test_data,
                        directory_path=self.tmp_dir,
                        do_something_with_view_name=self.view_name
                    )
                    action_return_value.append_message('Export view to nwc completed with status: {} and message: {}'.format(result.status, result.message))
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

        return return_value
