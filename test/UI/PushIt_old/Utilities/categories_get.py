# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module containing helper function to retrieve the available categories from the revit model. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


from duHast.Revit.Categories.categories_model import get_main_categories_in_model
from PushIt_old.Models.RevitCategory import RCategory

SUPPORTED_CATEGORIES =[
    "Ceilings",
    "Columns",
    "Mass",
    "Walls",
]

def get_revit_categories(doc):
    """
    Get all main categories in the model.
    
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: List of RCategory instances.
    :rtype: [RCategory]
    """
    
    cats = []
    
    revit_category_data = get_main_categories_in_model(doc)
    for category in revit_category_data:
        # filter out the "Tags" category
        if category.category_name in SUPPORTED_CATEGORIES:
            dummy = RCategory(category_name=category.category_name)
            cats.append(dummy)
            #print("Category: {}".format(dummy))
    return cats