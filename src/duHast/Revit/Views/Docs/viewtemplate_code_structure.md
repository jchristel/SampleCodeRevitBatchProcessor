
# Graphic Overrides

These are currently split into two modules, one for category overrides and one for filter overrides.
In addition, a third module is used to combine both when applying them to views.

| Content                     | Module Name                        | Storage Class                |
|----------------------------|-----------------------------------|-----------------------------|
| Category overrides         | `Views.visibility_graphics_categories` | `Views.Objects.category_override_storage.RevitCategoryOverride` |
| Filter overrides           | `Views.visibility_graphics_filters`    | `Views.Objects.filter_override_storage.RevitFilterOverride`   |
| Combination of overrides   | `Views.visibility_graphics`            | `Views.Objects.view_graphics_settings.ViewGraphicsSettings`    |

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
---

Views.Utility.get_views_graphic_settings_data(doc, views, progress_callback=None) is used to convert Revit category and filter overrides to storage class instances which can be written to JSON files.




# View Filters


There is currently now overarching storage class for multiple view filters. Instead they are just stored as a list of ViewFilter objects.

| Content                     | Module Name                        | Storage Class                |
|----------------------------|-----------------------------------|-----------------------------|
| view filters        | `Views.Objects.Data.view_filter` | `Views.Objects.Data.view_filter.ViewFilter` |



# TODO

- Stream line namespaces of classes used, currently they are scattered all over the Views namespace.

- Move `duHast.Revit.Views.visibility_graphics.import_graphic_overrides(file_path, call_back)` into the `Views.Import` namespace to be consistent with other import functions.
