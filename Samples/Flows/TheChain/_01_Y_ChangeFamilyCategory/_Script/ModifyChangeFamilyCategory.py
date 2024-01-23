'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is used to change the category of a family.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default Revit behaviour, when changing the category of a family, is to drop all custom subcategories and any element which used to be of a specific subcategory to be moved onto the
family category itself.

More often than not this means the custom subcategories need to be re-created and elements need to be re-assigned to them.

This script will:

- record all custom subcategories, their appearance properties and elements using them
- change the existing family category, if permitted
- re-create custom subcategories recorded
- re-assign elements to their respective subcategories


Corner cases:

- change of category is not permitted: e.g. an annotation family is to be changed to a model family (category Furniture): 

    - script will record an exception only and will not save out a new family

- model family category allowed for section views of families but new family category only allows for elevation views of family: 

    - script will place all elements which used the 'cut' property of a subcategory on the 'elevation' property instead


Outcomes:

- Saves marker files:
    - to help copy family back to origin in post process
    - change family log which can be used is reload advanced flows

'''

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


# ----------------------------------------------------- default family actions ------------------------------------------

def UpdateFamilyCategory(doc):
    '''
    Changes family category as per change directive.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status. True if change of family category was successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # read change family directives
    subCatChangeDirectives = rCatReportTools.ReadOverallFamilyCategoryChangeDirectivesFromDirectory(utilM.FAMILY_CHANGE_DIRECTIVE_DIRECTORY)
    # get the family category ( this is a dictionary where key is the cat name )
    famCat = rCats.GetFamilyCategory(doc)
    famCatName = list(famCat.keys())[0]
    foundCategoryMatch = False
    newCategoryName = 'no change directive found.'
    # loop over change directives and find the ones applicable to the current family
    for catChangeDirective in subCatChangeDirectives:
        # check if family in list and if the category needs changing
        if(catChangeDirective.filePath == revitFilePath_ ) :
            # save the new category name for later
            newCategoryName = catChangeDirective.newCategoryName
            if(catChangeDirective.newCategoryName !=famCatName):
                # store marker for later
                foundCategoryMatch = True
                returnValue.append_message('Attempting to change category from: {} to: {}.'.format(famCatName, catChangeDirective.newCategoryName))
                try:
                    # attempt to update the family category
                    returnValue.update(rCats.ChangeFamilyCategory(doc,catChangeDirective.newCategoryName))
                except Exception as e:
                    returnValue.update_sep(
                        False,
                        '{}: failed to change family category with exception: {}'.format(fileName_, e)
                    )
    # check if a category mismatch was found at all
    if(foundCategoryMatch == False):
        returnValue.update_sep(False, '{} :No category change required for this family. Current category: {} Category in change directive: {}'.format(fileName_, famCatName, newCategoryName))
    return returnValue

# -----------------------------------------------------------------------------------------------------------------------------------------------
# main:
# -------------

# get the file name
fileName_ = util.GetFileNameWithoutExt(revitFilePath_)

# setup timer
t = Timer()
t.start()

overAllStatus_= res.Result()
# assume no change, therefore file needs nod to be saved
overAllStatus_.status = False

# actions to be executed per family
familyActions =[
    UpdateFamilyCategory # change family category
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
    Output ('Messages from change family category action: {}'.format(resultFamAction.message))
    Output ('Overall status: {} (If false, this will not save the family)'.format(resultFamAction.status))

Output (str(t.stop()))

# -------------
# Saving file after changes have been made
# -------------

# get the file name
revitFilePathNew_ = utilM.WORKING_DIRECTORY + '\\' + fileName_ + '.rfa'

# save file if required
if (overAllStatus_.status):
    # save family file
    Output('Saving family file: start')
    syncing_ = com.SaveAsFamily(
        doc, 
        utilM.WORKING_DIRECTORY, 
        revitFilePath_, 
        [[fileName_, fileName_]],
        '.rfa',
        True
    )

    Output('Saving family file: finished ' + str(syncing_.message) + ' :: '  + str(syncing_.status))
    # save marker file
    if(syncing_.status == False):
        Output(str(syncing_.message))
    else:
        # write copy marker file
        _writeCopyMarkerFile(fileName_)
        # write family has changed marker file
        famCatName = doc.OwnerFamily.FamilyCategory.Name
        _writeChangedFamilyMarkerFile(fileName_, famCatName)
else:
    Output('Family was not saved.')