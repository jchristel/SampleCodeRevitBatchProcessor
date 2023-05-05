'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains all tests for non revit related functions of the duHast library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
#
#License:
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

from Utility import date_stamps
from Utility import files_get
from Utility import files_io
from Utility import utility
from Utility import files_csv
from Utility import directory_io

from utils.output import out_message, out_header

from colorama import init, Fore, Back, Style

#: overall debug flag. If False no messages from tests will be printed to console. If True messages will be printed.
IS_DEBUG = False


def out(func_name, result_flag, message):
    """
    Output to console

    :param func_name: the function name to be printed
    :type func_name: str
    :param result_flag: The test function result to be printed.
    :type result_flag: bool
    :param message: Any messages from the test function to be printed in debug mode.
    :type message: str
    """

    out_message("{} [{}]".format(func_name, result_flag))
    if IS_DEBUG:
        out_message(message)


#: colour coding for console output
init()

#: overall test status
OVERALL_STATUS = True

#: list of test names and associated test functions
TESTS = [
    ["date_stamps", date_stamps.run_tests],
    ["files_get", files_get.run_tests],
    ["files_io",files_io.run_tests],
    ["files_csv",files_csv.run_tests],
    ["directory_io",directory_io.run_tests],
    ["utility",utility.run_tests],
]

#: run tests in all modules
for test in TESTS:
    out_header(test[0])
    status = test[1](output=out)
    out("{} completed with status".format(test[0]), status, "")

out_header("FINISHED")
print("All tests completed with [{}]".format(OVERALL_STATUS))