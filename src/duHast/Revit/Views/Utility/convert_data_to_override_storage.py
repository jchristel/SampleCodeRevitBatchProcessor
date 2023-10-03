from duHast.Revit.Views.Objects.category_override_storage import RevitCategoryOverride
from duHast.Revit.Categories.categories_model import get_category_by_names


def convert_to_category_override_storage(doc, category_data_instance):
    return_value = None
    # get the category
    category_in_model = get_category_by_names(
        doc=doc,
        main_category_name=category_data_instance.category_name,
        sub_category_name=category_data_instance.sub_category_name,
    )
    if category_in_model:
        return_value = RevitCategoryOverride(
            main_category_name=category_data_instance.category_name,
            sub_category_name=category_data_instance.sub_category_name,
            category=category_in_model,
            category_id=category_in_model.Id,
            revit_override=None,
            is_category_hidden=category_data_instance.is_visible,
        )
    return return_value


def convert_to_category_override_storage_objects(doc, category_data_objects):
    return_value = []
    for cat_instance in category_data_objects:
        converted = convert_to_category_override_storage(
            doc=doc, category_data_instance=cat_instance
        )
        if converted:
            return_value.append(converted)
    return return_value
