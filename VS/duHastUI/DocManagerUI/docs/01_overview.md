# DocManagerUI — Library Overview

## Overview

DocManagerUI is a .NET class library that provides the core data models and validation logic for the Document Manager Revit integration. It has no user interface of its own — it is referenced by other projects (such as DocManagerSettingsUI) that expose the UI layer.

---

## Purpose

The library handles the in-memory representation of Revit document data — sheets, revisions, revision-on-sheet relationships, and custom document properties. It enforces uniqueness constraints and raises typed exceptions when conflicts are detected, allowing calling code to handle errors consistently.

---

## Key Data Models

### RevitDataModel

The top-level container for a Revit document's managed data.

| Property | Type | Description |
|---|---|---|
| ModelName | string | Name of the Revit document |
| SettingsAsJson | string | Current document numbering settings serialised as JSON |

**Methods:**
- `AddSheet(RevitSheet)` — adds a sheet; throws if the sheet number is not unique
- `AddRevision(RevitRevision)` — adds a revision
- `GetRevisionByRevitElementId(Int64)` — retrieves a revision by its Revit element ID

---

### RevitSheet

Represents a single sheet in the Revit document.

| Property | Type | Description |
|---|---|---|
| SheetNumber | string | Unique sheet identifier within the model |
| SheetName | string | Display name of the sheet |
| RevisionsOnSheet | List\<RevitRevisionOnSheet\> | Revisions marked on this sheet |
| DocumentProperties | List\<RevitDocumentProperty\> | Custom properties attached to the sheet |

**Methods:**
- `AddRevisionOnSheet(RevitRevisionOnSheet)` — adds a revision; throws `RevisionOnSheetDuplicateException` if the revision indicator already exists on this sheet
- `AddDocumentProperty(RevitDocumentProperty)` — adds a property; throws `DocumentPropertyDuplicateException` if the property name already exists on this sheet

---

### RevitRevision

Represents a revision defined in the Revit document.

| Property | Type | Description |
|---|---|---|
| RevitRevisionElementId | Int64 | Unique Revit element ID (must be > 0 and unique within the model) |
| RevisionDate | string | Date of the revision |
| RevisionDescription | string | Description text |

---

### RevitRevisionOnSheet

Represents a revision marker on a specific sheet.

| Property | Type | Description |
|---|---|---|
| RevisionIndicator | string | The revision indicator shown on the sheet (e.g., `1`, `2A`) — must be unique within the sheet |
| RevitRevision | RevitRevision | Reference to the revision object |

---

### RevitDocumentProperty

A custom key-value property attached to a sheet.

| Property | Type | Description |
|---|---|---|
| Name | string | Property name — must be unique within the sheet |
| Value | string | Property value |

---

## Validation and Exceptions

The library uses typed exceptions to signal data integrity violations. All exceptions include references to both the existing and the conflicting object.

| Exception | Thrown when |
|---|---|
| `DocumentPropertyDuplicateException` | A property with the same name already exists on the sheet |
| `RevisionDuplicateException` | A revision with the same Revit element ID already exists in the model |
| `RevisionOnSheetDuplicateException` | A revision with the same indicator already exists on the sheet |

---

## Usage

DocManagerUI is consumed as a project reference by DocManagerSettingsUI and any other component that needs to build or inspect the in-memory representation of Revit document data. Callers are responsible for handling the typed exceptions and presenting appropriate feedback to the user.
