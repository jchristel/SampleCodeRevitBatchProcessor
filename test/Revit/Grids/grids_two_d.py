"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit grids in view to 2D tests . 
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
from duHast.Revit.Grids.grids import get_grids_in_model
from duHast.Revit.Grids.grids_appearance import change_grids_2D
from duHast.Revit.Views.views import get_views_in_model
from duHast.Utilities.Objects import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb


class GridsTwoD(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GridsTwoD, self).__init__(doc=doc, test_name="change_grids_2D")

    def test(self):
        """
        change_grids_2D test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if grid data was retrieved successfully, otherwise False
                - .message will contain result(s) vs expected result(s)
                - . result (empty list)

                on exception:

                - .result Will be False
                - .message will contain exception message.
                - . result (empty list)
        :rtype: :class:`.Result`
        """

        return_value = res.Result()

        # set up a return specific plan return filter
        def action_name_check(x):
            if x.Name == "Level 00":
                return True

        try:
            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    # get all grids in the model
                    grids = get_grids_in_model(self.document)
                    # get sample view
                    views = get_views_in_model(self.document, action_name_check)

                    if len(views) >= 1:
                        # set all grids to 2D in view
                        set_grids_2d = change_grids_2D(self.document, grids, views[0])
                        # check for any exceptions
                        action_return_value.append_message(
                            "result: {} vs expected: {}".format(
                                set_grids_2d.status, True
                            )
                        )
                        assert set_grids_2d.status == True
                        # check grids
                        for grid in grids:
                            action_return_value.append_message(
                                "id: {} result: {} vs expected: {}".format(
                                    grid.Id,
                                    grid.GetDatumExtentTypeInView(
                                        rdb.DatumEnds.End0, views[0]
                                    ),
                                    rdb.DatumExtentType.ViewSpecific,
                                )
                            )
                            action_return_value.append_message(
                                "id: {} result: {} vs expected: {}".format(
                                    grid.Id,
                                    grid.GetDatumExtentTypeInView(
                                        rdb.DatumEnds.End0, views[0]
                                    ),
                                    rdb.DatumExtentType.ViewSpecific,
                                )
                            )
                            assert (
                                grid.GetDatumExtentTypeInView(
                                    rdb.DatumEnds.End0, views[0]
                                )
                                == rdb.DatumExtentType.ViewSpecific
                            )
                            assert (
                                grid.GetDatumExtentTypeInView(
                                    rdb.DatumEnds.End1, views[0]
                                )
                                == rdb.DatumExtentType.ViewSpecific
                            )
                    else:
                        raise ValueError(
                            "No view found in which to change grid appearance!"
                        )

                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in function {}: {}".format(
                            self.test_name, e
                        ),
                    )
                return action_return_value

            return_value.update(self.in_transaction_group(action))

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )
        return return_value
