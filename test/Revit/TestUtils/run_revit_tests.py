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

from duHast.Utilities.Objects import result as res
from duHast.Utilities.Objects import base
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
        try:
            for revit_test in self.tests:
                # initialise test class with current document
                try:
                    if(len(revit_test)>=2):
                        test_class = revit_test[1](doc)
                        # run the test
                        result_test = test_class.test()
                        # update overall status with test outcome
                        return_value.update(result_test)
                        # add string to the result for later processing
                        return_value.result.append(
                            [
                                pad_header_no_time_stamp(revit_test[0]), # test name formatted as a header
                                result_test, # result object
                                pad_string(
                                    "{} completed status [{}]".format(revit_test[0], result_test.status)
                                ), # completed message
                                revit_test[0], # test name
                                str(result_test.status), # test outcome
                                result_test.message, # test result message object
                            ]
                        )
                    else:
                        raise ValueError ("Malformed test data: {}".format(revit_test))
                except Exception as e:
                    return_value.update_sep(False, 'An exception ocurred when executing test: {}'.format(e))
        except Exception as e:
            return_value.update_sep(False, 'An exception ocurred when marshalling tests: {}'.format(e))
        return return_value
