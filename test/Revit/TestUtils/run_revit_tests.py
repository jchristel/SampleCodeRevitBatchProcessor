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
# BSD License
# Copyright © 2023, Jan Christel
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
