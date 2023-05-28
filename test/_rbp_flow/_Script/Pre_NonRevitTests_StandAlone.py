"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a pre process script outside the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- this module gets executed first in the test chain
- it runs any non Revit related code tests

- if any test fails it will terminate with an exit code greater than 0, indicating to the powershell script to terminate

"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# this sample shows how to write out a number of task files using bucket distribution

# --------------------------
# default file path locations
# --------------------------

import sys
import datetime
import utilRevitTests as utilM  # sets up all commonly used variables and path locations!

from duHast.Utilities.console_out import output
from test.Utility import run_test_classes as run_util_tests

def time_stamp():
        """
        2023-05-17 17:36:50
        """
        d = datetime.datetime.now()
        return d.strftime('%Y-%m-%d %H:%M:%S : \t')

# -------------
# my code here:
# -------------

#: tests to be executed
all_tests = [
        run_util_tests,
    ]

#: will contain the outcome of all tests
all_results = []


# run tests
for test_result in all_tests:
    result = test_result.run_tests()
    all_results.append(result)

#: overall tests outcome: true of all tests successfully executed, otherwise False
its_all_good = True

# print("all_results \n",all_results)
# check out what came back
for batch_result in all_results:
    # print('batch result\n', batch_result)
    for result in batch_result:
        #print('result\n', result)
        # print(batch_result[result])
        its_all_good = its_all_good & batch_result[result][0]
        # write to log
        if(batch_result[result][0] == False):
            output("{} - Test: {} failed with message {}".format(time_stamp(), result, batch_result[result][1]))
        else:
            output("{} - Test: {} [{}]".format(time_stamp(), result, batch_result[result][0]))
        

# pass any error back to caller in powershell script
if(its_all_good):
    #sys.exit(1)
    sys.exit(0)
else:
    sys.exit(1)