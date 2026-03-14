# Document Manager

**Panel:** Export | **Menu:** DocManager

Integration with the Document Manager system for managing document numbering, metadata, and export workflows at a project level.

---

## DocManager

Opens the main Document Manager interface, which reads sheet data from the current Revit project and provides document-level management tools.

- Lists all sheets with their current document numbers and metadata.
- Allows bulk updates to document numbering based on configured rules.
- Integrates with the document numbering settings defined in **Settings** (see below).

---

## Settings

Opens the [DocManagerSettingsUI](../../VS/duHastUI/DocManagerSettingsUI/docs/01_main_ui.md) configuration window.

- Select the CSV database file that contains the project's document register.
- Build document numbering rules by combining sheet properties (sheet number, revision, discipline code, etc.) with prefixes, suffixes, and separators.
- Rules can be exported to or imported from a JSON file for reuse across projects.
- Click **Save To Project** to store the configuration in the Revit project file.

**Run Settings first** on any project before using the main DocManager tool.

---

## POC (Proof of Concept)

A lightweight demonstration of the Document Manager integration. Shows how document numbers are generated from the current settings without writing any data to the model.

**Use when:** You want to preview the effect of a numbering rule configuration before committing it to the project.

---

## Notes

- Document numbering settings are stored per-project in the Revit model.
- The CSV database file path is also stored in the project settings and must be accessible from all workstations that use the tool.
