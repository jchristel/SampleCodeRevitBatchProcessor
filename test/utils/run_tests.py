"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains test base class . 
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

from duHast.Utilities.Objects import base


class RunTest(base.Base):
    def __init__(self,tests):
        """
        Class constructor.

        """

        # initialise base class
        super(RunTest, self).__init__()
        self.tests = tests


    def run_tests(self):
        
        """
        Runs all tests.

        :param doc: Current Revit document.
        :type doc: Autodesk.Revit.DB.Document

        :return: True if all tests completed successfully, otherwise False.
        :rtype: bool
        """
        test_data = {}
        for test in self.tests:
            test_class = test[1]()
            test_data[test_class.test_name] = test_class.test()
            
        return test_data
