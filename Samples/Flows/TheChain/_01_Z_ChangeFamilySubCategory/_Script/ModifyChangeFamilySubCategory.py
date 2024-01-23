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

import utilModifyBVN as utilM # sets up all commonly used variables and path locations!
# import common library

import Result as res
import RevitCommonAPI as com
import Utility as util
import RevitFamilyCategoryDataUtils as rCatReportTools
import RevitCategories as rCats

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
    revitFilePath_ = utilM.DEBUG_REVIT_FILE_NAME

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

    fileNameMarker = utilM.WORKING_DIRECTORY + '\\' + fileName + '_marker_.temp'
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
    
    fileNameMarker = utilM.WORKING_DIRECTORY + '\\' + fileName + '_changed_.temp'
    try:
        util.writeReportDataAsCSV(
            fileNameMarker, 
            ['file Name', 'file Path', 'revit category'], 
            [[fileName, revitFilePath_, revitCategoryName]]
            )
        Output('Wrote changed family file: ' + str(fileNameMarker) + ' :: '  + str(True)) 
    except Exception as e:
        Output('Wrote changed family file: ' + str(fileNameMarker) + ' :: '  + str(False) + '  Exception: ' + str(e))


def UpdateSubCategoryNames(doc):
    '''
    Renames subcategories as per rename directives.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status. True if all subcategories, requiring a rename, where renamed successfully, otherwise False.
        - result.message be generic success message.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''
    
    returnValue = res.Result()
    # read rename directives
    subCatChangeDirectives = rCatReportTools.ReadOverallFamilySubCategoryChangeDirectivesFromDirectory(utilM.FAMILY_CHANGE_DIRECTIVE_DIRECTORY)
    # get the family category ( this is a dictionary where key is the cat name )
    famCat = rCats.GetFamilyCategory(doc)
    famCatName = list(famCat.keys())[0]
    foundCategoryMatch = False
    foundSubCatMatch = False
    # loop over change directives and find the ones applicable to the category of the current family
    for subCatChangeDirective in subCatChangeDirectives:
        if(subCatChangeDirective.familyCategory in famCat):
            foundCategoryMatch = True
            # check if old subcategory name is in family to start with
            allreadyInFamilyOld = rCats.DoesMainSubCategoryExists(
                doc, 
                subCatChangeDirective.oldSubCategoryName)
            # if a name match attempt to rename
            if(allreadyInFamilyOld):
                foundSubCatMatch = True
                returnValue.update(rCats.RenameSubCategory(
                    doc, 
                    subCatChangeDirective.oldSubCategoryName, 
                    subCatChangeDirective.newSubCategoryName)
            )
            else:
                returnValue.append_message('Subcategory: '+ subCatChangeDirective.oldSubCategoryName + ' does not exist in family file.')
    if(foundCategoryMatch == False):
        returnValue.update_sep(False, 'No change directive found matching family category: ' + famCatName)
    if(foundCategoryMatch and foundSubCatMatch == False):
        returnValue.update_sep(False, 'No change directive found matching any family subcategory!')
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
    UpdateSubCategoryNames # rename family subcategories
    ]

# debug test 
Output('Script directory: ' + utilM.SCRIPT_DIRECTORY)

Output('Modifying Revit File.... start')

# loop over all family actions and execute them
# check for each action if family needs to be saved
for famAction in familyActions:
    resultFamAction = famAction(doc)
    if(resultFamAction.status):
        # need to save family
        overAllStatus_.status = True
    overAllStatus_.append_message(resultFamAction.message)
    Output (resultFamAction.message)
    Output (str(resultFamAction.status))

Output (str(t.stop()))

# -------------
# Saving file after changes have been made
# -------------

# get the file name
fileName = util.GetFileNameWithoutExt(revitFilePath_)
revitFilePathNew_ = utilM.WORKING_DIRECTORY + '\\' + fileName + '.rfa'

# save file if required
if (overAllStatus_.status):
    # save family file
    Output('Saving family file: start')
    syncing_ = com.SaveAsFamily(
        doc, 
        utilM.WORKING_DIRECTORY, 
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