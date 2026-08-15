# docManager

**Panel:** Export | **Menu:** docManager

<img src="Extensions/duHast-2025.extension/duHast.tab/Export.panel/docManager.pulldown/Icon.png" width="40" alt="button icon">

Integration between Revit and the Document Manager system: it reads sheets and revisions from
the model and synchronises them to a Document Manager database.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Export.panel/docManager.pulldown/Settings.pushbutton/Icon.png" width="24" alt="Settings icon"> Settings

Configures how document numbers are built, and stores that configuration **in the model**.

- Opens the [DocManagerSettingsUI](../../VS/duHastUI/DocManagerSettingsUI/docs/01_main_ui.md)
  window.
- Select the **CSV database file** holding the project's document register.
- Build the document numbering rule by selecting and ordering sheet properties — sheet number,
  revision, discipline code, custom sheet parameters — with prefixes, suffixes and separators.
- Rules can be exported to and imported from JSON for reuse across projects.
- **Save** commits the configuration and closes.

Settings are written to a **extensible schema in the Revit model** as a JSON string, so they
travel with the file — which is why this must be run **once per model** before DocManager
itself will start.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Export.panel/docManager.pulldown/DocManager.pushbutton/Icon.png" width="24" alt="DocManager icon"> DocManager

Opens the main [Document Manager Revit integration](../../VS/duHastApplications/duHastNet.DocManager/duHastNet.DocManager.Revit/docs/01_main_ui.md)
window.

Before the window opens, the tool reads from the model:

- the sheet data, and
- the **revision data** on those sheets.

The window then shows two panels, switched with a navigation toggle:

- **Sheets** — lists sheets with their generated document numbers and metadata, and lets you
  import new sheets into the Document Manager database.
- **Revisions** — records revision history against the database entries.

The header strip shows the connected database path and the connection status.

**If the settings schema is missing**, the tool exits with a message telling you to run
Settings first.

---

## Requirements

- **Settings** must have been run on this model.
- The CSV database file must be reachable from the workstation — its path is stored in the
  model settings, so it must be valid for everyone who uses the tool.
- The extension's `bin` folder must be present; the windows are .NET UIs loaded from there.

## Notes

- Document numbering settings are per-model. A new model needs its own Settings run, or an
  imported rule JSON.
- Changing the numbering rule changes the document numbers generated for every sheet — review
  the Sheets panel before importing into the database.
