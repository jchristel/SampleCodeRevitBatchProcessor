'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module builds the list of families to be processed for sub category name changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- it reads 

    - the categroy report and 
    - change sub category directive files

- builds a file list and saves it into the task file directory

- returns a 0 if everything went ok othersie a 2 ( an exception occured or no files required changing)

'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# this sample shows how to write out a number of task files using bucket distribution

# --------------------------
# default file path locations1
# --------------------------

import sys, os
import utilModifyBVN as utilM # sets up all commonly used variables and path locations!
import RevitFamilyCategoryDataUtils as rCatReportTools
import Utility as util

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    print (message)

# -------------
# main:
# -------------
Output( 'Python pre process script: Task list builder start ...')
Output('Using path: ' + utilM.FAMILY_CHANGE_DIRECTIVE_DIRECTORY)

try:
    rootFams,nestedFams = rCatReportTools.ReadOverallFamilyCategoryDataFromDirectory(utilM.FAMILY_CHANGE_DIRECTIVE_DIRECTORY)
    # check if any root families where found
    if(len(rootFams) > 0):
        subCatChangeDirectives = rCatReportTools.ReadOverallFamilySubCategoryChangeDirectivesFromDirectory(utilM.FAMILY_CHANGE_DIRECTIVE_DIRECTORY)
        rootFamsNeedingChange = rCatReportTools.GetFamiliesRequiringSubCategoryChange(
            rootFams,
            subCatChangeDirectives)
        Output(' matches found: ' + str(len(rootFamsNeedingChange)))
        if(len(rootFamsNeedingChange)> 0 ):

            # writer expects a list of lists...
            rootFams = []
            for rf in rootFamsNeedingChange:
                rootFams.append([rf])
            try:
                taskfileName = utilM.TASK_FILE_DIRECTORY + '\\' + utilM.PREDEFINED_TASK_FILE_NAME_PREFIX + utilM.PREDEFINED_TASK_FILE_EXTENSION
                # write out task file list into task folder
                util.writeReportDataAsCSV (
                    taskfileName,
                    [], 
                    rootFams)
                # user feed back
                Output('Succesfully wrote task file: ' + taskfileName)
                sys.exit(0)
            except Exception as e:
                Output("failed to write task file name with exception: " + str(e))
                sys.exit(2)
        else:
            # do nothing...
            Output ('No root families requiring a sub category renamed found. Terminating without proceeding...')
            sys.exit(2)
    else:
        # do nothing...
        Output ('No root families in report found. Terminating without proceeding...')
        sys.exit(2)
except Exception as e:
    Output ('An exception occured when building task list: '+ str(e))
    Output ('Terminating without proceeding...')
    sys.exit(2)