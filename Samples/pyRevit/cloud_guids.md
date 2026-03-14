# Cloud GUIDs

**Panel:** Cloud | **Button:** GUIDs

Retrieves the Autodesk cloud GUIDs associated with the current Revit model and displays them in the pyRevit output window.

## What it does

- Reads the cloud project GUID and model GUID from the open Revit document.
- Displays both values in the pyRevit output window so they can be copied.

## When to use this

Use this button when you need to reference the current model in a **Revit Batch Processor** task file that targets cloud-hosted models. The GUIDs returned here are the exact identifiers required by the batch processor to open the model from Autodesk Construction Cloud or BIM 360.

## Notes

- This tool only works when the active document is hosted on Autodesk Construction Cloud or BIM 360 (a cloud workshared model).
- Local models and locally-hosted central files do not have cloud GUIDs; the tool will report nothing or an error for those models.
- Copy the GUIDs from the output window and paste them into the relevant Revit Batch Processor configuration file.
