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

# this sample shows how to write out a number of task files using bucket distribution

# --------------------------
# default file path locations
# --------------------------

import sys
import datetime
import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.console_out import output
from test.Utility import run_test_classes as run_util_tests
from test.UI import run_test_classes as run_ui_tests

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
        run_ui_tests,
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