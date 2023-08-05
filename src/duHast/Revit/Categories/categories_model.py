"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category helper functions for project files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
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

from collections import namedtuple




# tuples containing categories data
category_data = namedtuple("category_data", "category_name sub_category_name id")

def get_categories_in_model(doc):
    """
    Returns all categories and subcategories in a model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of named tuples of type category_data
    :rtype: [category_data]
    """

    cats = doc.Settings.Categories
    categories = []
    for main_category in cats:
        categories.append(category_data(category_name=main_category.Name, sub_category_name=main_category.Name, id=main_category.Id))
        for sub_cat in main_category.SubCategories:
            categories.append(category_data(category_name=main_category.Name, sub_category_name=sub_cat.Name, id=sub_cat.Id))
    
    return categories