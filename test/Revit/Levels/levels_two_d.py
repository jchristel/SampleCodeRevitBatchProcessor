"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit levels in view to 2D tests . 
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

from test.Revit.TestUtils import revit_test
from duHast.Revit.Levels.levels import get_levels_in_model
from duHast.Revit.Levels.levels_appearance import change_levels_2D
from duHast.Revit.Views.views import get_views_in_model
from duHast.Utilities.Objects import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb
from duHast.Utilities.console_out import output
import revit_script_util


class LevelsTwoD(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(LevelsTwoD, self).__init__(doc=doc, test_name="change_levels_2D")

    def test(self):
        """
        change_levels_2D test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if levels where set to 2D successfully, otherwise False
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
            if x.Name == "Section - Level Test":
                return True

        try:
            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    # get all levels in the model
                    levels = get_levels_in_model(self.document)
                    # get sample view
                    views = get_views_in_model(self.document, action_name_check)

                    if len(views) >= 1:
                        # set all levels to 2D in view
                        set_levels_2d = change_levels_2D(
                            self.document, levels, views[0]
                        )
                        # check for any exceptions
                        action_return_value.append_message(
                            "result: {} vs expected: {} result message: {}".format(
                                set_levels_2d.status, True, set_levels_2d.message
                            )
                        )
                        assert set_levels_2d.status == True
                        # check levels
                        for level in levels:
                            action_return_value.append_message(
                                "id: {} result: {} vs expected: {}".format(
                                    level.Id,
                                    level.GetDatumExtentTypeInView(
                                        rdb.DatumEnds.End0, views[0]
                                    ),
                                    rdb.DatumExtentType.ViewSpecific,
                                )
                            )
                            action_return_value.append_message(
                                "id: {} result: {} vs expected: {}".format(
                                    level.Id,
                                    level.GetDatumExtentTypeInView(
                                        rdb.DatumEnds.End0, views[0]
                                    ),
                                    rdb.DatumExtentType.ViewSpecific,
                                )
                            )
                            assert (
                                level.GetDatumExtentTypeInView(
                                    rdb.DatumEnds.End0, views[0]
                                )
                                == rdb.DatumExtentType.ViewSpecific
                            )
                            assert (
                                level.GetDatumExtentTypeInView(
                                    rdb.DatumEnds.End1, views[0]
                                )
                                == rdb.DatumExtentType.ViewSpecific
                            )
                    else:
                        raise ValueError(
                            "No view found in which to change level appearance!"
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
