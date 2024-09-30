"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit category overrides in views. 
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
#

from duHast.Revit.Views.Objects.category_override_storage import RevitCategoryOverride
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common.transaction import in_transaction
from Autodesk.Revit.DB import Transaction


def get_categories_and_subcategories_from_model(doc):
    """
    Returns all categories and sub categories in a model in a dictionary:

    Dictionary:

        - key is same format as list: main category name::sub category name
        - value is a named tuple category_storage instance

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: dictionary of categories
    :rtype: {str:category_storage}
    """

    categories_dic = {}
    document_settings = doc.Settings
    cats = document_settings.Categories
    for main_category in cats:
        # add the main category
        categories_dic[
            "{}::{}".format(main_category.Name, main_category.Name)
        ] = RevitCategoryOverride(
            main_category_name=main_category.Name,
            sub_category_name=main_category.Name,
            category=main_category,
            category_id=main_category.Id,
            category_override=None,
            is_category_hidden=False,
        )
        # loop over the sub categories
        for sub_cat in main_category.SubCategories:
            categories_dic[
                "{}::{}".format(main_category.Name, sub_cat.Name)
            ] = RevitCategoryOverride(
                main_category_name=main_category.Name,
                sub_category_name=sub_cat.Name,
                category=sub_cat,
                category_id=sub_cat.Id,
                category_override=None,
                is_category_hidden=False,
            )

    return categories_dic


def update_category_override_from_view(view, category_storage_instance):
    """
    Populates the category_override and is_category_hidden field of a 'category_storage' instance based on the view past in.

    :param view: The view from which the category override is to be used.
    :type view: Autodesk.Revit.DB.View
    :param category_storage_instance: An instances of revit category storage containing no view specific information.
    :type category_storage_instance: :class:`.RevitCategoryOverride`

    :return: An updated instances of revit category storage now containing the override, category visibility flags.
    :rtype: :class:`.RevitCategoryOverride`
    """

    category_storage_instance.revit_override = view.GetCategoryOverrides(
        category_storage_instance.category_id
    )

    category_storage_instance.is_category_hidden = view.GetCategoryHidden(
        category_storage_instance.category_id
    )

    return category_storage_instance


def get_category_overrides_from_view(view, category_storage_instances):
    """
    Populates the category_override and is_category_hidden fields of a list of 'category_storage' instances based on the view past in.

    :param view: The view from which the category override is to be used.
    :type view: Autodesk.Revit.DB.View
    :param category_storage_instances: A list of instances of class 'RevitCategoryOverride'
    :type category_storage_instances: [:class:`.RevitCategoryOverride`]

    :return: A list of instances of revit category storage now containing the override, category visibility flags.
    :rtype: [:class:`.RevitCategoryOverride`]
    """

    updated_category_storage_instances = []
    for category_storage_instance in category_storage_instances:
        updated_category_instance = update_category_override_from_view(
            view, category_storage_instance
        )
        updated_category_storage_instances.append(updated_category_instance)

    return updated_category_storage_instances


def apply_graphic_override_to_view(doc, view, category_storage_instances):
    """
    Applies graphic override(s) to a single view

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view on which the category override is to be used.
    :type view: Autodesk.Revit.DB.View
    :param category_storage_instances: A list of instances of class 'RevitCategoryOverride'
    :type category_storage_instances: [:class:`.RevitCategoryOverride`]

    return:
        Result class instance.

        - Apply override status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message 'Successfully set category override...' for each override applied.
        - result.result will be an empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    for category_storage_instance in category_storage_instances:

        def action():
            action_return_value = res.Result()
            try:
                # apply category override
                view.SetCategoryOverrides(
                    category_storage_instance.category_id,
                    category_storage_instance.revit_override,
                )
                action_return_value.update_sep(
                    True,
                    "Successfully set category override {} :: {} in view {} ".format(
                        category_storage_instance.main_category_name,
                        category_storage_instance.sub_category_name,
                        view.Name,
                    ),
                )

                # set category visibility
                view.SetCategoryHidden(
                    category_storage_instance.category_id,
                    category_storage_instance.is_category_hidden,
                )
                action_return_value.update_sep(
                    True,
                    "Successfully set category hidden status {} :: {} in view {} to: {}".format(
                        category_storage_instance.main_category_name,
                        category_storage_instance.sub_category_name,
                        view.Name,
                        category_storage_instance.is_category_hidden,
                    ),
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to apply override: {} :: {} to view: {} with exception: {}".format(
                        category_storage_instance.main_category_name,
                        category_storage_instance.sub_category_name,
                        view.Name,
                        e,
                    ),
                )
            return action_return_value

        transaction = Transaction(
            doc,
            "Updating category override {} :: {}".format(
                category_storage_instance.main_category_name,
                category_storage_instance.sub_category_name,
            ),
        )
        update_category_override = in_transaction(transaction, action)
        return_value.update(update_category_override)

    return return_value
