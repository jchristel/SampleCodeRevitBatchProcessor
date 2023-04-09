'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit sub-category helper functions.
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

import Autodesk.Revit.DB as rdb

from duHast.Utilities import Result as res
from duHast.APISamples.Categories.RevitCategories import DeleteMainSubCategory, DoesMainSubCategoryExists, GetMainSubCategories
from duHast.APISamples.Categories.Utility.RevitElementsByCategoryUtils import MoveElementsFromSubCategoryToSubCategory
from duHast.APISamples.Categories.Utility.RevitCategoryPropertiesSetUtils import SetCategoryProperties
from duHast.APISamples.Categories.Utility.RevitCategoryPropertiesGetUtils import GetCategoryProperties
from duHast.APISamples.Common import RevitTransaction as rTran


def CreateNewSubCategoryToFamilyCategory(doc, newSubCategoryName):
    '''
    Creates a new subcategory to the family category and returns it.
    Note: if a subcategory with the name provided already exist it will be returned instead of trying to create another one with the same name.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newSubCategoryName: The new subcategory name
    :type newSubCategoryName: str
    :return: The new subcategory. Exception "The name 'xys' is already in use" if subcategory with the same name is already in file.
    :rtype: A category. (or str if exception occurred)
    '''

    returnValue = res.Result()
    if (doc.IsFamilyDocument):
        # check if subcategory already exists
        if(DoesMainSubCategoryExists(doc, newSubCategoryName)):
            # just return the already existing subcategory
            mainSubCategories = GetMainSubCategories(doc)
            returnValue.UpdateSep(True, 'Subcategory already in family.')
            returnValue.result = mainSubCategories[newSubCategoryName]
        else:
            # create a new subcategory
            # get the family category
            currentFamCat = doc.OwnerFamily.FamilyCategory
            parentCategory = None
            # get parent category object from Revit internal settings
            for mainCat in doc.Settings.Categories:
                if (mainCat.Name == currentFamCat.Name):
                    parentCategory = mainCat
                    break
            if(newSubCategoryName != parentCategory.Name):
                def action():
                    actionReturnValue = res.Result()
                    try:
                        newSubCategory = doc.Settings.Categories.NewSubcategory(parentCategory, newSubCategoryName)
                        actionReturnValue.UpdateSep(True, 'Created subcategory ' + str(newSubCategoryName))
                        actionReturnValue.result = newSubCategory
                    except Exception as e:
                        actionReturnValue.UpdateSep(False, 'Failed to create ' + str(newSubCategoryName) + ' with exception: ' + str(e))
                    return actionReturnValue
                transaction = rdb.Transaction(doc,'Creating subcategory: ' + str(newSubCategoryName))
                returnValue = rTran.in_transaction(transaction, action)
            else:
                returnValue.UpdateSep(False, 'Cant create subcategory with the same name as the family category!')
    else:
        returnValue.UpdateSep(False, 'This is not a family document!')
    return returnValue


def CreateNewCategoryFromSavedProperties(doc, newCatName, savedCatProps, ignoreMissingCutStyle = False):
    '''
    Creates a new category and applies properties stored.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newCatName: The new sub category name.
    :type newCatName: str
    :param savedCatProps: Dictionary containing subcategory properties.
    :type savedCatProps: list of dictionaries in format as per GetCategoryProperties(cat) method.
    :param ignoreMissingCutStyle: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignoreMissingCutStyle: bool
    :return: 
        Result class instance.
        - result.status. True if category was created or already existed in file, otherwise False.
        - result.message will contain the name of the category created.
        - result.result returns new category, if category already exists in file it will return that
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    resultNewSubCat = CreateNewSubCategoryToFamilyCategory(doc, newCatName)
    if(resultNewSubCat.status):
        newSubCat = resultNewSubCat.result
        flag = SetCategoryProperties(doc, newSubCat, savedCatProps, ignoreMissingCutStyle)
        if(flag):
            returnValue.UpdateSep(True, 'Successfully created category: '+ str(newCatName))
            returnValue.result = newSubCat
        else:
            returnValue.UpdateSep(False, 'Failed to apply properties to new category: '+ str(newCatName))
    else:
        returnValue.UpdateSep(False, 'Failed to create new subcategory: '+ str(newCatName))
    return returnValue


def CreateNewCategoryAndTransferProperties(doc, newCatName, existingCatName):
    '''
    Creates a new subcategory and transfer properties from existing subcategory.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newCatName: The new sub category name.
    :type newCatName: str
    :param existingCatName: The existing subcategory name
    :type existingCatName: str
    :return: 
        Result class instance.
        - result.status. True if category was created or already existed in file, otherwise False.
        - result.message will contain the name of the category created.
        - result.result returns new category, if category already exists in file it will return that
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    cats = GetMainSubCategories(doc)
    # check if existing category actually exists in family
    if(existingCatName in cats):
        # check whether the new category already exists!
        if (newCatName not in cats):
            copyFromCat = cats[existingCatName]
            catProps = GetCategoryProperties(copyFromCat, doc)
            resultNewSubCat = CreateNewCategoryFromSavedProperties(doc, newCatName, catProps)
            returnValue.Update(resultNewSubCat)
        else:
            returnValue.UpdateSep(True, 'Category already in file:'+ str(newCatName))
            returnValue.result = cats[newCatName]
    else:
        returnValue.UpdateSep(False, 'Template category: '+ str(existingCatName) + ' does not exist in file!')
    return returnValue


def RenameSubCategory(doc, oldSubCatName, newSubCatName):
    '''
    Renames a family custom subcategory.
    Note: Only subcategory directly belonging to the family category will be checked for a match.
    - Revit API does currently not allow to change a subcategory name. This method instead:
        - duplicates the old subcategory with the new name
        - moves all elements belonging to the old subcategory to the new subcategory
        - deletes the old subcategory
    - If the new subcategory already exists in the file:
        - moves all elements belonging to the old subcategory to the new subcategory
        - deletes the old subcategory
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param oldSubCatName: The subcategory name to be re-named
    :type oldSubCatName: str
    :param newSubCatName: The new subcategory name.
    :type newSubCatName: str
    :return: 
        Result class instance.
        - result.status. True if subcategory was renamed successfully , otherwise False.
        - result.message will contain rename process messages.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # check whether ol;d subcategory exists in family file
    alreadyInFamilyOld = DoesMainSubCategoryExists(doc, oldSubCatName)
    if(alreadyInFamilyOld):
        # check whether new subcategory already in family
        alreadyInFamily = DoesMainSubCategoryExists(doc, newSubCatName)
        if(alreadyInFamily):
            # just move elements from old sub category to new one
            returnValue.AppendMessage('Subcategory: ' + newSubCatName + ' already in family.')
        else:
            # duplicate old sub category
            createNewStatus = CreateNewCategoryAndTransferProperties(doc, newSubCatName, oldSubCatName)
            returnValue.Update(createNewStatus)
        # check if we have a subcategory to move elements to
        if(returnValue.status):
            # move elements
            moveStatus = MoveElementsFromSubCategoryToSubCategory(doc, oldSubCatName, newSubCatName)
            returnValue.Update(moveStatus)
            if(moveStatus.status):
                deletedOldSubCategory = DeleteMainSubCategory(doc, oldSubCatName)
                if(deletedOldSubCategory):
                    returnValue.UpdateSep(True, 'Subcategory: ' + oldSubCatName + ' deleted successfully.')
                else:
                    returnValue.UpdateSep(True, 'Subcategory: ' + oldSubCatName + ' failed to delete subcategory...Exiting')
            else:
                returnValue.UpdateSep(False, 'Subcategory: ' + newSubCatName + ' failed to move elements to new subcategory. Exiting...')
        else:
            returnValue.UpdateSep(False, 'Subcategory: ' + newSubCatName + ' failed to create in family. Exiting...')
    else:
        returnValue.UpdateSep(False, 'Base subcategory: ' + oldSubCatName + ' does not exist in family. Exiting...')
    return returnValue