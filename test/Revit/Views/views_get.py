"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit get view tests . 
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

from test.Revit.TestUtils import revit_test
from duHast.Revit.Views.views import get_views_in_model
from duHast.Utilities.Objects import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb


class GetViews(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetViews, self).__init__(doc=doc, test_name="get_views_in_model")

    def test(self):
        """
        get views in model test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .status True if views where retrieved successfully, otherwise False
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
            # set up a return all views filter
            def action(x):
                return True

            views_in_model = [
                ["TEST", rdb.ViewType.DraftingView],
                ["Wall Schedule", rdb.ViewType.Schedule],
                ["Level 00", rdb.ViewType.FloorPlan],
                ["Section - Level Test", rdb.ViewType.Section],
                ["Export Model", rdb.ViewType.ThreeD],
            ]
            # get all views in model (only 1 in test model)
            result = get_views_in_model(self.document, action)

            # check against expected views
            counter = 0
            for view_retrieved in result:
                return_value.append_message(
                    " view name: {}, view type: {}, ".format(
                        view_retrieved.Name, view_retrieved.ViewType
                    )
                )
                assert view_retrieved.Name == views_in_model[counter][0]
                assert view_retrieved.ViewType == views_in_model[counter][1]

                counter = counter + 1

            # check overall number of views retrieved matches expected
            return_value.append_message(
                " number of retrieved views: {}, number of expected views: {}, ".format(
                    len(result), len(views_in_model)
                )
            )
            assert len(result) == len(views_in_model)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )

        return return_value
