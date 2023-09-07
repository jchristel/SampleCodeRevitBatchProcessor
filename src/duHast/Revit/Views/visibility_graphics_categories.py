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
            category_id=main_category.Id,
            category_override=[],
            is_category_hidden=[],
        )
        # loop over the sub categories
        for sub_cat in main_category.SubCategories:
            categories_dic[
                "{}::{}".format(main_category.Name, sub_cat.Name)
            ] = RevitCategoryOverride(
                main_category_name=main_category.Name,
                sub_category_name=sub_cat.Name,
                category_id=[sub_cat.Id],
                category_override=[],
                is_category_hidden=[],
            )

    return categories_dic


def update_category_override_from_view(view, category_storage_instance):
    """
    Populates the category_override and is_category_hidden field of a 'category_storage' instance based on the view past in.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view from which the category override is to be used.
    :type view: Autodesk.Revit.DB.View
    :param category_storage_instance: An instances of a named tuple: category_storage
    :type category_storage_instance: category_storage

    :return: An instances of a named tuple: category_storage where category_overrides field (a list) and is_category_hidden (also a list) has been updated with a category override.
    :rtype: category_storage
    """

    overrides_by_view = view.GetCategoryOverrides(category_storage_instance.category_id)
    category_storage_instance.category_override = overrides_by_view
    is_category_hidden = view.GetCategoryHidden(category_storage_instance.category_id)
    category_storage_instance.is_category_hidden = is_category_hidden
    return category_storage_instance


def get_category_overrides_from_view(view, category_storage_instances):
    """
    Populates the category_override and is_category_hidden fields of a list of 'category_storage' instances based on the view past in.

    :param view: The view from which the category override is to be used.
    :type view: Autodesk.Revit.DB.View
    :param category_storage_instances: An list of instances of a named tuple: category_storage
    :type category_storage_instances: [category_storage]

    :return: A list of instances of a named tuple: category_storage where category_overrides field (a list) and is_category_hidden (also a list) has been updated with a category override.
    :rtype: [category_storage]
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
    :param category_storage_instances: A list of instances of a named tuple: category_storage
    :type category_storage_instances: [category_storage]

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
                view.SetCategoryOverrides(
                    category_storage_instance.category_id,
                    category_storage_instance.category_override,
                )
                action_return_value.update_sep(
                    True,
                    "Successfully set category override {} :: {} in view {} ".format(
                        category_storage_instance.main_category_name,
                        category_storage_instance.sub_category_name,
                        view.Name,
                    ),
                )
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