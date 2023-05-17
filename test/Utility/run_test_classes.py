"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all revit revision related tests . 
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


from test.utils.run_tests import RunTest

# import test classes
from test.Utility import get_date_stamp_directory, get_date_stamp_file, file_csv_read


def run_tests():
    """
    Runs all utility related tests.

    :return: dictionary containing
         - the test name as key and as values
         - a flag (true if test completed successfully, otherwise false)
         - message string
    :rtype: {str:bool,str}
    """

    # start tests

    run_tests = [
        ["Directory Get Date Stamp", get_date_stamp_directory.GetDateStampDirectory],
        ["File Get Date Stamp", get_date_stamp_file.GetDateStampFile],
        ["Read CSV File", file_csv_read.FileCSVRead],
    ]

    runner = RunTest(run_tests)
    return_value = runner.run_tests()

    return return_value
