'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is the actual script batch processor executes per family file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It reads the report file and saves out any nested family found not present in report.

Host families are not saved.

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




# --------------------------
# Imports
# --------------------------

# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_rrFiles.rvt'

import clr
import System

import utilDataBVN as utilData # sets up all commonly used variables and path locations!
import Utility as util
import Result as res
import UtilBatchP as utilBP


# family data processors
import RevitFamilyBaseDataProcessor as rFamBaseProcessor

# family data collector class
import RevitFamilyDataCollector as rFamCol

from Autodesk.Revit.DB import *

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
    # get the session Id
    sessionId_ = revit_script_util.GetSessionId()
else:
    # get default revit file name
    revitFilePath_ = debugRevitFileName_
    sessionId_ = "123"

# store output here:
rootPath_ = utilData.OUTPUT_FOLDER

# -------------
# my code here:
# -------------


def Output(message = ''):
    '''
    Prints message either to revit batch processor console or sceen. (Depends on global debug_ flag)
    To batch processor (debug = False) or console (debug = True)

    :param message: The message to be printed, defaults to ''
    :type message: str, optional
    '''

    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# main:
# -------------

# save revit file to new location
Output('Writing out missing families .... start')

# check whether missing families are to be written to file
# missing families are families which do not appear as root families in base family data report
saveOutMissingFamilies, baseDataReportFilePath, familyOutRootDirectory = utilData.SaveOutMissingFamiliesCheck()
# update available processor instances accordingly
if(saveOutMissingFamilies):
    # Set up list containing all family processor instances to be executed per family.
    procs = [ 
        rFamBaseProcessor.FamilyBaseProcessor(
            baseDataReportFilePath, # reference list of known families
            familyOutRootDirectory, # where to write families to
            sessionId_ # session id to make sure families are written to unique folder
        )
    ]
    familyCategoryName = doc.OwnerFamily.FamilyCategory.Name
    famName = doc.Title
    # strip .rfa of name
    if(famName.lower().endswith('.rfa')):
        famName = famName[:-4]
    
    # process family (and save missing fams out)
    collector = rFamCol.RevitFamilyDataCollector(procs)
    flagDataCollection_ = collector.processFamily(doc, famName, familyCategoryName)

    Output (flagDataCollection_.message + '.... status: ' + str(flagDataCollection_.status))

else:
    Output('Failed to read data required to save out missing families!')