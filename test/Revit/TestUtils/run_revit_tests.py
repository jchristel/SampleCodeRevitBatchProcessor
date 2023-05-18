"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit test base class . 
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

from duHast.Utilities import result as res
from duHast.Utilities import base
from duHast.Utilities.padding import pad_header_no_time_stamp, pad_string


class RevitRunTest(base.Base):
    def __init__(self,tests):
        """
        Class constructor.

        """

        # initialise base class
        super(RevitRunTest, self).__init__()
        self.tests = tests


    def run_tests(self, doc):
        
        """
        Runs all tests.

        :param doc: Current Revit document.
        :type doc: Autodesk.Revit.DB.Document

        :return: True if all tests completed successfully, otherwise False.
        :rtype: bool
        """

        return_value = res.Result()

        for revit_test in self.tests:
            test_class = revit_test[1](doc)
            result_test = test_class.test()
            return_value.update(result_test)
            print('test0',revit_test[0])
            return_value.result.append(
                [
                    pad_header_no_time_stamp(revit_test[0]),
                    result_test,
                    pad_string(
                        "{} completed status [{}]".format(revit_test[0], result_test.status)
                    ),
                    revit_test[0],
                    str(result_test.status),
                ]
            )

        return return_value
