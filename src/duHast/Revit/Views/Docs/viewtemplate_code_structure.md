# View Templates

TODO:
---

## Graphic Overrides

There are 2 distinctive flows:
- using _storage classes 
- using JSON files


### Storage classes

This flow is primarily used when existing overrides are to be applied within the same file and therefore wrapper requirements of native Revit objects are minimal.


| Content                     | Module Handling Conversion       |
|----------------------------|-----------------------------------|
| Category overrides         | `Views.visibility_graphics_categories` | 
| Filter overrides           | `Views.visibility_graphics_filters`    | 

Class hierarchy:

- Views.Objects.category_override_storage.RevitCategoryOverride
- Views.Objects.filter_override_storage.RevitFilterOverride

### JSON files

When persisting Revit objects to file, more advanced classes are used to store all aspects of those objects to file via JSON serialization and de-serialization. 
When applying object retrieved from disk in this way, to views in Revit, storage classes are used.


| Content                     | Module Handling Conversion       |
|----------------------------|-----------------------------------|
| Combination of overrides   | `Views.visibility_graphics`     (import only)       |


Class hierarchy:

- Views.Objects.view_graphics_settings.ViewGraphicsSettings
    - Views.Objects.Data.OverrideByCategory
        - inherits from Views.Objects.Data.OverrideByBase
    - Views.Objects.Data.OverrideByFilter
        - inherits from Views.Objects.Data.OverrideByBase
    





---

   



Flow to convert Revit overrides to data which can be stored on disk and back to native Revit objects

1. Views.Utility.convert_revit_override_to_data
2. Views.Utility.convert_data_to_revit_override

To apply an override, filter or category, duHast uses storage classes:

- Views.Objects.filter_override_storage.RevitFilterOverride
- Views.Objects.category_override_storage.RevitCategoryOverride

Functions to apply overrides to views are

- visibility_graphics_filter.apply_filter_override_to_view
- visibility_graphics_categories.apply_graphic_override_to_view

Flow to read a data object from file, create a native Revit category override object and apply to a view:

1. convert json to duHast objects
    1.1 Views.Utility.convert_data_to_override_storage.convert_to_category_override_storage_objects
    1.2 Views.Utility.convert_data_to_override_storage.convert_to_filter_override_storage_objects
2. Views.Utility.convert_data_to_revit_override (returns native Revit objects)
3. Views.visibility_graphics.apply_filter_override_to_view

---

## Category Graphics and Filter Overrides - Import

The `duHast.Revit.Views.visibility_graphics` module contains functions to import category and filter overrides from a JSON file and apply them to view templates in Revit.

### `visibility_graphics.apply_overrides_from_file(doc, file_path)`

This function combines all the necessary steps to import category and filter overrides from a JSON file and applies them to view templates in a Revit document.

**Purpose:**  
Applies category and filter overrides to view templates based on data imported from a JSON file.

**Parameters:**  
- `doc`: The current Revit document.  
- `file_path`: Path to the JSON file containing override data.  

**Logic:**  
- Loads override data from the JSON file using `import_graphic_overrides`. (Stores json data into storage classes.)
- Checks if the required line and fill patterns exist in the model using `check_all_line_and_fill_pattern_in_model`.  
- If patterns exist, it proceeds to find matching templates (by the exported template name) using `get_matching_templates`.  
- Calls `apply_overrides_to_views` to apply the overrides to the found templates.  

---

### `visibility_graphics.apply_overrides_to_views(doc, view_data)`

This function applies graphic and filter overrides to multiple view templates in a Revit document.  
It assumes that the `view_data` has already been prepared and validated. Validation must include checking for the existence of required line and fill patterns in the model.

**Purpose:**  
Applies category and filter overrides to multiple view templates in a Revit document.

**Parameters:**  
- `doc`: The current Revit document.  
- `view_data`: A dictionary where keys are view template names, and values are lists containing the Revit view object and the view override object.  

**Logic:**  
- Iterates over the `view_data` dictionary.  
- Calls `apply_override_to_view` for each view and updates the result object.  

---

## Category Graphics and Filter Overrides - Export

Views.Utility.get_views_graphic_settings_data(doc, views, progress_callback=None) is used to convert Revit category and filter overrides to storage class instances which can be written to JSON files.









---

# View Filters

There is currently now overarching storage class for multiple view filters. Instead they are just stored as a list of duHast ViewFilter objects. Those objects contain Containers which in turn contain the actual filter rule. This is done to represent the rule nesting setup in Revit.

| Content                     | Module Name                        | Storage Class                |
|----------------------------|-----------------------------------|-----------------------------|
| view filters        | `Views.Objects.Data.view_filter` | `Views.Objects.Data.view_filter.ViewFilter` |
| view filter logic containers        | `Views.Objects.Data.view_filter_logic_container` | `Views.Objects.Data.view_filter_logic_container.ViewFilterLogicContainer` |
| filter rules | `Views.Objects.Data.view_filter_rule` | `Views.Objects.Data.view_filter_rule.ViewFilterRule` |

Class hierarchy:

- Views.Objects.Data.ViewFilter
    - Views.Objects.Data.ViewFilterLogicContainer
        - Views.Objects.Data.ViewFilterRule


## View Filters - import

The module Views.Import.read_filter_storage_from_file.py reads .JSON file, and converts the appropriate node into duHast ViewFilter objects. Those objects can be converted into Revit ElemenFilters using  Views.Import.create_filter_from_storage

Flow:

- read json file using Views.Import.read_filter_storage_from_file.read_filter_storage_from_file(...) into duHast ViewFilter objects

- convert duHast ViewFilter objects into Revit ElementFilters using  Views.Import.create_filter_from_storage.import_view_filters_from_data (...)
    - conversion uses a number of utility modules:
        - Views.Utility.convert_data_to_filter_rule
        - Views.Utility.convert_data_to_filter_evaluator
        - Views.Utility.convert_data_to_filter_logic_filter
        - Views.Utility.convert_data_to_filter_value_provider
        
---

## View Filters - export

---

# TODO

- Stream line namespaces of classes used, currently they are scattered all over the Views namespace.

- Move `duHast.Revit.Views.visibility_graphics.import_graphic_overrides(file_path, call_back)` into the `Views.Import` namespace to be consistent with other import functions.

---