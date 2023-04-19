'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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


import clr
import System
from System.Collections.Generic import List

from duHast.APISamples.Common import RevitDeleteElements as rDel
from duHast.Utilities import Result as res
from duHast.APISamples.Common import RevitTransaction as rTran

import Autodesk.Revit.DB as rdb
from duHast.APISamples.Categories.RevitFamilySubCategories import create_new_category_from_saved_properties
from duHast.APISamples.Categories.Utility.RevitCategoryPropertiesGetUtils import get_category_graphic_style_ids, get_category_properties
from duHast.APISamples.Categories.Utility.RevitElementsByCategoryUtils import get_elements_by_category, move_elements_to_category

#: subcategory renaming sampled dictionary
#: key is the current subcategory name, value is the new subcategory name 
CAT_RENAMING = {
    'Clearance Zones': 'AMAZING'
}

#: list of built in parameters attached to family elements containing subcategory ids
ELEMENTS_PARAS_SUB = [
    rdb.BuiltInParameter.FAMILY_CURVE_GSTYLE_PLUS_INVISIBLE,
    rdb.BuiltInParameter.FAMILY_CURVE_GSTYLE_PLUS_INVISIBLE_MINUS_ANALYTICAL,
    rdb.BuiltInParameter.FAMILY_ELEM_SUBCATEGORY,
    rdb.BuiltInParameter.CLINE_SUBCATEGORY
]

def get_main_sub_categories(doc):
    '''
    Returns all subcategories of the family category in a dictionary where\
        key: sub category name
        value: sub category 

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: Autodesk.Revit.DB.Category}
    '''

    cat_data = {}
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for main_cat in doc.Settings.Categories:
        # find the category matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if (main_cat.Name == family_category_name):
            # loop over all sub categories
            for sub_cat in main_cat.SubCategories:
                cat_data[sub_cat.Name] = sub_cat
    return cat_data

def does_main_sub_category_exists(doc, sub_cat_name):
    '''
    Checks whether a given subcategory exists in the family.

    Note: Only subcategory directly belonging to the family category will be checked for a match.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param subCatName: The name of the subcategory to be checked against.
    :type subCatName: str

    :return: True if subcategory exists in family, otherwise False
    :rtype: bool
    '''

    # get all sub categories belonging to family category
    sub_cats = get_main_sub_categories(doc)
    if(sub_cat_name in sub_cats):
        return True
    else:
        return False

def delete_main_sub_category(doc, sub_cat_name):
    '''
    Deletes a given subcategory from the family.

    Note: Only subcategory directly belonging to the family category will be checked for a match.

    ::param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param subCatName: The name of the subcategory to be deleted.
    :type subCatName: str

    :return: True if subcategory exists in family and was deleted successfully, otherwise False
    :rtype: bool
    '''

    # get all sub categories belonging to family category
    sub_cats = get_main_sub_categories(doc)
    if(sub_cat_name in sub_cats):
        # delete subcategory
        status_delete = rDel.delete_by_element_ids(
            doc,
            [sub_cats[sub_cat_name].Id],
            'delete subcategory: ' + sub_cat_name,
            'subcategory'
        )
        return status_delete.status
    else:
        return False


def get_family_category(doc):
    '''
    Gets the family category in a dictionary where\
        key: category name
        value: category 

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: Autodesk.Revit.DB.Category}
    '''

    cat_data = {}
    # get the family category
    current_fam_cat = doc.OwnerFamily.FamilyCategory
    cat_data [current_fam_cat.Name] = current_fam_cat
    return cat_data

def get_other_sub_categories(doc):
    '''
    Returns all family subcategories which do not belong to the actual family category.

    key: category name
    value: dictionary : key sub cat name, value: subcategory

    Note: custom subcategories have an Id greater 0
    
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: {str:Autodesk.Revit.DB.Category} }
    '''

    cat_data = {}
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for main_cat in doc.Settings.Categories:
        # find the category not matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if (main_cat.Name != family_category_name):
            if (main_cat.Name not in cat_data):
                cat_data[main_cat.Name] = {}
            # loop over all sub categories
            for sub_cat in main_cat.SubCategories:
                cat_data[main_cat.Name][sub_cat.Name] = sub_cat
              
    return cat_data

def get_other_custom_sub_categories(doc):
    '''
    Returns all family custom subcategories which do not belong to the actual family category.
    Custom categories have an Id greater then 0.

    key: category name
    value: dictionary : key sub cat name, value: subcategory

    Note: custom subcategories have an Id greater 0
    
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: {str:Autodesk.Revit.DB.Category} }
    '''

    cat_data = {}
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for main_cat in doc.Settings.Categories:
        # find the category not matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if (main_cat.Name != family_category_name):
            if (main_cat.Name not in cat_data):
                cat_data[main_cat.Name] = {}
            # loop over all sub categories
            for sub_cat in main_cat.SubCategories:
                if(sub_cat.Id.IntegerValue > 0):
                    cat_data[main_cat.Name][sub_cat.Name] = sub_cat
    return cat_data

def get_other_categories(doc):
    '''
    Returns all family pre defined categories which do not belong to the actual family category.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of categories.
    :rtype: [Autodesk.Revit.DB.Category]
    '''

    cat_data = []
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for main_cat in doc.Settings.Categories:
        # find the category not matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if (main_cat.Name != family_category_name):
            if (main_cat not in cat_data):
                cat_data.append(main_cat)
    return cat_data

def get_category_by_built_in_def_name(doc, built_in_defs):
    '''
    Returns categories by their built in definition 

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param builtInDefs: list of BuiltInCategory Enumeration values
    :type builtInDefs: [Autodesk.Revit.DB.BuiltInCategory]

    :return: list of categories
    :rtype: [Autodesk.Revit.DB.Category]
    '''

    cats = []
    document_settings = doc.Settings
    groups = document_settings.Categories
    for built_in_def in built_in_defs:
        cat = groups.get_Item(built_in_def)
        if cat!=None:
            cats.append(cat)
    return cats
   
def set_family_category(doc, new_category_name):
    '''
    Changes the family category to new one specified by name. (this will not re-instate any custom sub categories created under the new family category)
    
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newCategoryName: The name of the new family category.
    :type newCategoryName: str
    
    :return: True only if the category was changed successfully. Any other case False! (That includes situations when the family is already of the new category)
    :rtype: bool
    '''
    
    return_value = res.Result()
    cat = doc.OwnerFamily.FamilyCategory
    if (cat.Name != new_category_name):
        if (doc.Settings.Categories.Contains(new_category_name)):
            def action():
                doc.OwnerFamily.FamilyCategory = doc.Settings.Categories.get_Item(new_category_name)
            transaction = rdb.Transaction(doc,'Changing family category to:' + str(new_category_name))
            change_cat = rTran.in_transaction(transaction, action)
            if(change_cat.status):
                return_value.update_sep(True, 'Successfully changed family category to: {}'.format(new_category_name))
            else:
                return_value.update(change_cat)
        else:
            return_value.update_sep(False, 'Invalid Category name supplied: {}'.format(new_category_name))
    else:
        return_value.update_sep(False, 'Family is already of category: {}'.format(new_category_name))
    return return_value
   
# --------------------------------------- family category  --------------------------------------------------------------

def change_family_category(doc, new_category_name):
    '''
    Changes the current family category to the new one specified.

    Revit's default behavior when changing the category of a family is to discard all custom subcategories created and assign elements which are on those custom subcategories\
        to the new family category.
    
    This function will also re-create any user created subcategories under the new category and assign elements to it to match the subcategory they where on before\
         the category change.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newCategoryName: The new family category
    :type newCategoryName: str

    :return: 
        Result class instance.

        - result.status. True if all custom subcategories where re-created under the new family category and elements where moved to those subcategories, otherwise False.
        - result.message will confirm successful creation of subcategories and element move.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
        
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # get sub categories in family
    sub_cats = get_main_sub_categories (doc)
    
    # get all elements on custom subcategories
    elements = {}
    for sub_cat in sub_cats:
        el = get_elements_by_category(doc, sub_cats[sub_cat])
        elements[sub_cat] = el
    
    # get properties of all custom sub categories
    props = {}
    for sub_cat in sub_cats:
        prop = get_category_properties(sub_cats[sub_cat], doc)
        props[sub_cat] = prop
    
    # change family category
    change_fam = set_family_category(doc, new_category_name)
    return_value.update(change_fam)

    if(change_fam.status):
        # re-create custom sub categories
        for sub_cat in sub_cats:
            # only re-create custom sub categories (id greater then 0)
            if(sub_cats[sub_cat].Id.IntegerValue > 0):
                # create new sub categories with flag: ignore if cut graphic style is missing set to true!
                create_cat = create_new_category_from_saved_properties(doc, sub_cat, props[sub_cat], True)
                return_value.update(create_cat)
                if(create_cat.status):
                    # get the graphic style ids of the new subcategory for elements to use
                    destination_cat_ids = get_category_graphic_style_ids(create_cat.result)
                    # move elements back onto custom subcategories
                    move_el = move_elements_to_category(doc, elements[sub_cat], sub_cat, destination_cat_ids)
                    return_value.update(move_el)
                else:
                    return_value.update(create_cat)
    else:
        return_value.update_sep(False, 'Failed to change family category: {}'.format(change_fam.message))
    return return_value