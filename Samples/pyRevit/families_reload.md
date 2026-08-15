# Reload

**Panel:** Families | **Button:** Reload

<img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reload.pushbutton/Icon.png" width="40" alt="button icon">

Batch-reloads families from a library directory into the current project, through the
FamilyReloaderUI window.

## What it does

1. Lists every family in the open document in a grid.
2. You enter a **library path** and click **Update**; the tool searches that directory for
   `.rfa` files matching the family names and fills in a match status and the library file's
   last-modified date.
3. You tick the families to reload and click **Reload Families**.
4. The window closes and the families are reloaded, with a cancellable progress bar.

## Match status

| Status | Meaning |
|---|---|
| `SingleMatch` | Exactly one matching file found — this family can be reloaded |
| `MultipleMatches` | More than one file of that name found; the match is ambiguous |
| `NoMatch` | No file of that name found in the library |

Only families showing **`SingleMatch`** should be ticked. Resolve duplicates in the library
before reloading the rest.

## Library path

- Type or paste a path, or use **Browse**.
- **Incl Sub Directories** is a checkbox — subdirectory searching is optional, not automatic.
- The Reload button stays disabled while the path is empty or does not exist.

## Reload mode

The window offers two modes:

- **Import All Types On Reload** — all types in the library file are loaded, including types
  the project does not already have.
- **Reload Existing Types Only** — only types already in the project are updated; any type
  the library file introduces is removed again after the reload.

The mode chosen is reported in the output window before the reload starts.

## Requirements

- A library directory of `.rfa` files reachable from your workstation.
- The extension's `bin` folder must be present — the window is a .NET UI loaded from there.

## Notes

- Right-click a column header for a filter menu; single-click to sort.
- Library path, subdirectory setting, reload mode and column layout persist between sessions
  in `%LocalAppData%\duHast\Reloader_settings.json`.
- Full interface documentation: [FamilyReloaderUI user guide](../../VS/duHastUI/FamilyReloaderUI/docs/01_main_ui.md).
