"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit family change category helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
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

from duHast.Revit.Categories.Utility.category_properties_get_utils import (
    get_category_graphic_style_ids,
    get_category_properties,
)
from duHast.Revit.Categories.Utility.elements_by_category_utils import (
    get_elements_by_category,
    move_elements_to_category,
)
from duHast.Revit.Categories.categories import (
    get_main_sub_categories,
    set_family_category,
)
from duHast.Revit.Categories.family_sub_categories import (
    create_new_category_from_saved_properties,
)
from duHast.Utilities.Objects import result as res


def change_family_category(doc, new_category_name):
    """
    Changes the current family category to the new one specified.

    Revit's default behavior when changing the category of a family is to discard all custom subcategories created and assign elements which are on those custom subcategories to the new family category. This function will also re-create any user-created subcategories under the new category and assign elements to them to match the subcategory they were on before the category change.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param new_category_name: The new family category.
    :type new_category_name: str

    :return: Result class instance.
        - `result.status` (bool): True if all custom subcategories were re-created under the new family category and elements were moved to those subcategories, otherwise False.
        - `result.message` (str): Confirmation of successful creation of subcategories and element move.
        - `result.result` (list): Empty list.

    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # get sub categories in family
    sub_cats = get_main_sub_categories(doc)

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

    if change_fam.status:
        # re-create custom sub categories
        for sub_cat in sub_cats:
            # only re-create custom sub categories (id greater then 0)
            if sub_cats[sub_cat].Id.IntegerValue > 0:
                # create new sub categories with flag: ignore if cut graphic style is missing set to true!
                create_cat = create_new_category_from_saved_properties(
                    doc, sub_cat, props[sub_cat], True
                )
                return_value.update(create_cat)
                if create_cat.status:
                    # get the graphic style ids of the new subcategory for elements to use
                    destination_cat_ids = get_category_graphic_style_ids(
                        create_cat.result
                    )
                    # move elements back onto custom subcategories
                    move_el = move_elements_to_category(
                        doc, elements[sub_cat], sub_cat, destination_cat_ids
                    )
                    return_value.update(move_el)
                else:
                    return_value.update(create_cat)
    else:
        return_value.update_sep(
            False, "Failed to change family category: {}".format(change_fam.message)
        )
    return return_value
