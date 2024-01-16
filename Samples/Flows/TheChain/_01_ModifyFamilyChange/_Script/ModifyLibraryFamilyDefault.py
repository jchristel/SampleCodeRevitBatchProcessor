'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is used to make changes to families.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The changes made to families do not require any further input (from another script / text file):

- Purge unused (requires Autodesk eTransmit)
- Purge unused sub categories
- purge unused line patterns
- purge unused shared parameter definitions

- Saves marker files:
    - to help copy family back to origin in post process
    - change family log which can be used is reload advanced flows

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

# ---------------------------
# default file path locations
# ---------------------------

import clr
import System

import utilModifyBVN as utilR # sets up all commonly used variables and path locations!
# import common library

import Result as res
import RevitCommonAPI as com
import Utility as util
import RevitFamilyUtils as rFamUtils
import RevitFamilyDataCollector as rFamCol
import RevitPurgeUnusedeTransmit as lePurge
import RevitLinePatternDataProcessor as rLinePatProcessor
import RevitCategoryDataProcessor as rCatProcessor
import RevitSharedParameters as rSharedP
import RevitSharedParameterDataProcessor as rSharedParaProcessor
import RevitCategoryDataPurgeUnused as rCatDataPu
import RevitLinePatternDataPurgeUnused as rLinePatDataPu
import RevitSharedParameterDataPurgeUnused as rSharedParaDataPu
import ModifyLibraryFamilyDefaultParameters as rParameterDefaultActions

from timer import Timer

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
else:
    #get default revit file name
    revitFilePath_ = utilR.DEBUG_REVIT_FILE_NAME

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        try:
            revit_script_util.Output(message)
        except Exception as e:
            revit_script_util.Output('Exception in Output() ' + str(e))
    else:
        print (message)

def _writeCopyMarkerFile(fileName):
    '''
    Write marker file containing copy from and copy to path.

    :param fileName: Marker file name.
    :type fileName: str
    '''

    fileNameMarker = utilR.WORKING_DIRECTORY + '\\' + fileName + '_marker_.temp'
    try:
        util.writeReportDataAsCSV(
            fileNameMarker, 
            ['Copy From', 'Copy To'], 
            [[revitFilePathNew_, revitFilePath_]]
            )
        Output('Wrote marker file: ' + str(fileNameMarker) + ' :: '  + str(True)) 
    except Exception as e:
        Output('Wrote marker file: ' + str(fileNameMarker) + ' :: '  + str(False) + '  Exception: ' + str(e))

def _writeChangedFamilyMarkerFile(fileName, revitCategoryName):
    '''
    Write changed file marker file containing: file name, file path, revit category name

    :param fileName: Marker file name.
    :type fileName: str
    :param revitCategoryName: The family revit category.
    :type revitCategoryName: str
    '''
    
    fileNameMarker = utilR.WORKING_DIRECTORY + '\\' + fileName + '_changed_.temp'
    try:
        util.writeReportDataAsCSV(
            fileNameMarker, 
            ['file Name', 'file Path', 'revit category'], 
            [[fileName, revitFilePath_, revitCategoryName]]
            )
        Output('Wrote changed family file: ' + str(fileNameMarker) + ' :: '  + str(True)) 
    except Exception as e:
        Output('Wrote changed family file: ' + str(fileNameMarker) + ' :: '  + str(False) + '  Exception: ' + str(e))

def _processFamily (doc, processor):
    # get the family category
    familyCategoryName = doc.OwnerFamily.FamilyCategory.Name
    collector = rFamCol.RevitFamilyDataCollector([processor])
    famName = doc.Title
    # strip .rfa of name
    if(famName.lower().endswith('.rfa')):
        famName = famName[:-4]
    # process family
    flagDataCollection_ = collector.processFamily(doc, famName, familyCategoryName)
    return processor, flagDataCollection_

# ----------------------------------------------------- default family actions ------------------------------------------

def PurgeUnused (doc):
    '''
    Purges family unless a nested family which is label driven is present.

    :param doc: Current family document.
    :type doc: AutoDesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status. True if purge unused was undertaken and successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # check if any nested family instance placed is label driven...if True do not purge!
    isInstanceLabelDriven = rFamUtils.IsAnyNestedFamilyInstanceLabelDriven(doc)

    if(isInstanceLabelDriven == False):
        # purge unused
        returnValue = lePurge.PurgeUnusedETransmit(doc)
    else:
        returnValue.UpdateSep(False,'Nested family which is Label driven found. Nothing was purged.')
    
    return returnValue

def _UpdatePurgeStatus(returnValue, actionStatus):
    '''
    Check if both purge actions succseeded...if only one do not change the status to false since the 
    family still requires to be saved!

    :param returnValue: The overall action to be updated with new action status.
    :type returnValue: :class:`.Result`
    :param actionStatus: The new action status.
    :type actionStatus: :class:`.Result`

    :return: The updated overall action status.
    :rtype: :class:`.Result`
    '''
    try:
        if(returnValue.status and actionStatus.status):
            returnValue.Update(actionStatus)
        elif(returnValue.status == False and actionStatus.status == True):
            returnValue.status = True
            returnValue.AppendMessage(actionStatus.message)
        else:
            returnValue.AppendMessage(actionStatus.message)
    except Exception as e:
        Output ('Exception in _UpdatePurgeStatus: ' + str(e))
    return returnValue

def PurgeUnusedOthers(doc):
    '''
    Purges out unused sub categories and line patterns in a family.

    Uses family processor modules to determine which categories or line patterns are not used.

    :param doc: Current family document.
    :type doc: AutoDesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status. True if purge unused categories and line patterns was undertaken and successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        # process categories first
        processorCategories, procesStatus = _processFamily(doc, rCatProcessor.CategoryProcessor())
        if(procesStatus):
            data = processorCategories.get_Data()
            returnValue.AppendMessage('data length categories: ' + str(len(data)))
            # purge unused categories
            outcomePurgeCats = rCatDataPu.PurgeUnused(doc, processorCategories)
            returnValue.Update(outcomePurgeCats)
        else:
            returnValue.UpdateSep(False,'Category processor failed...nothing was purged.')
    except Exception as e:
        Output ('Exception in purge categories: ' + str(e))
    
    try:
        # process line patterns 
        processorLinePatterns, procesStatus = _processFamily(doc, rLinePatProcessor.LinePatternProcessor())
        if(procesStatus):
            data = processorLinePatterns.get_Data()
            returnValue.AppendMessage('data length line patterns: ' + str(len(data)))
            # purge unused categories
            outcomePurgeLinepats = rLinePatDataPu.PurgeUnused(doc, processorLinePatterns)
            # check if both purge actions succseeded...if only one do not change the status to false since the 
            # family still requires to be saved!
            returnValue = _UpdatePurgeStatus(returnValue, outcomePurgeLinepats)
        else:
            # no need to update the status at this point as if true family needs to be saved even if the line pattern purge failed.
            returnValue.AppendMessage('Line pattern processor failed...nothing was purged.')
    except Exception as e:
        Output ('Exception in purge line patterns: ' + str(e))

    try:
        # process shared parameters
        processorSharedParameters, processStatus = _processFamily(doc, rSharedParaProcessor.SharedParameterProcessor())
        if(processStatus):
            data = processorSharedParameters.get_Data()
            returnValue.AppendMessage('data length shared paras: ' + str(len(data)))
            # purge unused shared parameter definitions
            outcomePurgeSharedParas = rSharedParaDataPu.PurgeUnused(doc, processorSharedParameters)
            # check if both purge actions succseeded...if only one do not change the status to false since the 
            # family still requires to be saved!
            returnValue = _UpdatePurgeStatus(returnValue, outcomePurgeSharedParas)
        else:
            # no need to update the status at this point as if true family needs to be saved even if the shared parameter purge failed.
            returnValue.AppendMessage('Shared parameter processor failed...nothing was purged.')
    except Exception as e:
        Output ('Exception in purge unused shared parameters: ' + str(e))
    
    
    try:
        # delete any unwanted shared parameters
        outcomePurgeUnwantedSharedParas = rParameterDefaultActions.DeleteUnwantedSharedParameters(doc)
        # check if both purge actions succseeded...if only one do not change the status to false since the 
        # family still requires to be saved!
        returnValue = _UpdatePurgeStatus(returnValue, outcomePurgeUnwantedSharedParas)
    except Exception as e:
        Output ('Exception in purge unwanted shared parameters: ' + str(e))
    
    try:
        # change shared parameter to family parameters
        outcomeChangeSharedParas = rParameterDefaultActions.ChangeParamterToFamilyParameter(doc)
        # check if both purge actions succseeded...if only one do not change the status to false since the 
        # family still requires to be saved!
        returnValue = _UpdatePurgeStatus(returnValue, outcomeChangeSharedParas)
    except Exception as e:
        Output ('Exception in changing shared parameters to family parameters: ' + str(e))
    
    try:
        # swap shared parameters
        outcomeSwapSharedParas = rParameterDefaultActions.SwapSharedParameters(doc)
        # check if both actions succseeded...if only one do not change the status to false since the 
        # family still requires to be saved!
        returnValue = _UpdatePurgeStatus(returnValue, outcomeSwapSharedParas)
    except Exception as e:
        Output ('Exception in changing shared parameters to family parameters: ' + str(e))
    
    try:
        # add default parameters
        outcomeAddDefaultParas = rParameterDefaultActions.AddDefaultParameters(doc, rParameterDefaultActions.sharedParametersToAdd_)
        # check if both actions succseeded...if only one do not change the status to false since the 
        # family still requires to be saved!
        returnValue = _UpdatePurgeStatus(returnValue, outcomeAddDefaultParas)
    except Exception as e:
        Output ('Exception in adding default shared parameters: ' + str(e))
    
    return returnValue

def UpdateReferenceStatus(doc):
    '''
    Set the reference status to not a reference for all weak reference planes and any lines.

    :param doc: Current family document.
    :type doc: AutoDesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status. True if reference status was set succesfully, otherwise False.
        - result.message be generic success message.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    returnValue.Update(rFamUtils.SetRefPlanesToNotAReference(doc))
    returnValue.Update(rFamUtils.SetSymbolicAndModelLinesToNotAReference(doc))
    return returnValue
# -----------------------------------------------------------------------------------------------------------------------------------------------
# main:
# -------------

# setup timer
t = Timer()
t.start()

overAllStatus_= res.Result()
# assume no change, therefore file needs nod to be saved
overAllStatus_.status = False

# actions to be executed per family
familyActions =[
    PurgeUnused, # purge first :)
    PurgeUnusedOthers, # purge other things
    UpdateReferenceStatus # fix up ref planes
    ]

# debug test 
Output('Script directory: ' + utilR.SCRIPT_DIRECTORY)

Output('Modifying Revit File.... start')

# loop over all family actions and execute them
# check for each action if family needs to be saved
for famAction in familyActions:
    resultFamAction = famAction(doc)
    if(resultFamAction.status):
        # need to save family
        overAllStatus_.status = True
    overAllStatus_.AppendMessage(resultFamAction.message)
    Output (resultFamAction.message)
    Output (str(resultFamAction.status))

Output (str(t.stop()))

# -------------
# Saving file after changes have been made
# -------------

# get the file name
fileName = util.GetFileNameWithoutExt(revitFilePath_)
revitFilePathNew_ = utilR.WORKING_DIRECTORY + '\\' + fileName + '.rfa'

# save file if required
if (overAllStatus_.status):
    # save family file
    Output('Saving family file: start')
    syncing_ = com.SaveAsFamily(
        doc, 
        utilR.WORKING_DIRECTORY, 
        revitFilePath_, 
        [[fileName, fileName]],
        '.rfa',
        True
    )

    Output('Saving family file: finished ' + str(syncing_.message) + ' :: '  + str(syncing_.status))
    # save marker file
    if(syncing_.status == False):
        Output(str(syncing_.message))
    else:
        # write copy marker file
        _writeCopyMarkerFile(fileName)
        # write family has changed marker file
        famCatName = doc.OwnerFamily.FamilyCategory.Name
        _writeChangedFamilyMarkerFile(fileName, famCatName)