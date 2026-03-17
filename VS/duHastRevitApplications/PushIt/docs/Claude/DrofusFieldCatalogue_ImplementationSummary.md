# drofus Field Catalogue & Attribute Configuration — Implementation Summary

## Overview

This document describes the changes required to replace the current "read field names
off the first live room object" approach with a proper field catalogue backed by the
drofus OPTIONS endpoint, and to introduce attribute configuration selection as a
project-level filter over that catalogue in the mapping dialog.

---

## Background

### Current behaviour

`GetAvailableFields` fires a `GET /rooms?$top=1` call and extracts JSON property names
from the first room object. This means:

- Only fields that have a non-null value on that first room are discoverable.
- `room_data_*` and other extended fields are invisible unless that specific room
  happens to have data in them.
- There is no human-readable label — the raw JSON key (`room_data_10151910`) is what
  the user sees in the mapping dialog dropdown.
- `GetRoomsData` does not use `$select`, so extended fields are never returned even
  if they are mapped.

### Target behaviour

- The full field catalogue is fetched from `OPTIONS /api/{db}/{pr}/rooms` once per
  Connect and once at startup. It is the authoritative, complete, always-accurate
  list of every mappable room property.
- Each field has a stable `id` (the JSON key, stored in `DrofusPropertyMap.DrofusFieldName`),
  a human-readable `name` shown in the UI, a `propertyGroup` for grouping, a
  `dataType`, and a `unit`.
- Attribute configurations fetched from `GET /api/{db}/{pr}/attributeconfigurations`
  act as named subsets of the catalogue. The user picks one at the project level; the
  mapping dialog filters the available field list to that configuration's fields.
  Base room fields (from the catalogue) are always available on top.
- The selected configuration id is persisted to settings so it is restored on next
  session without a user action.
- `GetRoomsData` appends `$select` built from the active mapping field ids so that
  extended fields are actually returned in the rooms payload.

---

## New Models

### `DrofusRoomField`

Runtime-only (never serialised). Represents one entry from the OPTIONS catalogue response.

| Property | Type | Notes |
|---|---|---|
| `Id` | `string` | The JSON key — stored in `DrofusPropertyMap.DrofusFieldName` |
| `Name` | `string` | Human-readable label — shown in the mapping dialog dropdown |
| `PropertyGroup` | `string` | Used for optional grouping in the UI |
| `DataType` | `string` | e.g. `"string"`, `"boolean"`, `"number"`, `"integer"`, `"array"` |
| `Unit` | `string` | e.g. `"SquareMeters"`, `"Undefined"` |

### `DrofusAttributeConfigurationElement`

Runtime-only. Represents one element within a configuration.

| Property | Type | Notes |
|---|---|---|
| `DrofusAttributeId` | `string` | Maps to `DrofusRoomField.Id` in the catalogue |
| `DrofusAttributeLabel` | `string` | Display label from the configuration (may differ from catalogue `Name`) |
| `Direction` | `string` | Raw direction string from the API: `"Key"`, `"ToExternalApplication"`, or `"ToDrofus"` |

**Direction mapping to PushIt concepts:**

| API `direction` value | PushIt meaning |
|---|---|
| `"Key"` | This element is the unique identifier — sets `IsUniqueId = true` on the mapping |
| `"ToExternalApplication"` | drofus → Revit — maps to `MappingFlowDirection.DrofusToRevit` |
| `"ToDrofus"` | Revit → drofus — maps to `MappingFlowDirection.RevitToDrofus` |

`external_attribute_id` and `external_attribute_label` are present in the API response
but are ignored — they reference Revit built-in parameters which PushIt does not use
(PushIt uses shared parameters selected manually by the user).

### `DrofusAttributeConfiguration`

Runtime-only. Represents one configuration from the `/attributeconfigurations` response.

| Property | Type | Notes |
|---|---|---|
| `Id` | `int` | The configuration's integer id — persisted as `SelectedAttributeConfigurationId` |
| `Name` | `string` | The configuration name shown in the selector dropdown |
| `IsDefault` | `bool` | Whether this is the project default configuration |
| `Elements` | `List<DrofusAttributeConfigurationElement>` | The fields this configuration includes |

---

## Changes to Existing Models

### `DrofusDataSourceSettings`

One new serialised property and two new runtime-only properties:

| Property | Serialised | Type | Notes |
|---|---|---|---|
| `SelectedAttributeConfigurationId` | Yes | `int?` | The integer id of the last chosen attribute configuration. `null` means no configuration selected — full catalogue shown. |
| `StartupAttributeConfigurations` | No (`[JsonIgnore]`) | `List<DrofusAttributeConfiguration>` | Populated during startup so `DrofusDataSourceControlViewModel` does not need a second API call on construction. Mirrors the existing `StartupAvailableFields` pattern. |
| `StartupFieldCatalogue` | No (`[JsonIgnore]`) | `List<DrofusRoomField>` | Same purpose — caches the catalogue fetched at startup for use by the ViewModel. Replaces `StartupAvailableFields`. |

`StartupAvailableFields` is retired — replaced by `StartupFieldCatalogue`. It is kept
in the class marked `[JsonIgnore]` and `[Obsolete]` during the migration step, then
removed once all callers are updated.

### `DrofusPropertyMap`

No changes. `DrofusFieldName` already stores the field `id` string. The human-readable
label is resolved at display time from the catalogue — it is never stored in the mapping.

---

## Changes to `DrofusDataSource`

### New method: `GetFieldCatalogue`

Calls `OPTIONS /api/{db}/{pr}/rooms` with the same `Authorization: Reference {ApiToken}`
header as all other calls. Uses the new `ExecuteOptions` private helper (see updated
HTTP helpers section below). Parses the JSON array into `List<DrofusRoomField>`. No
paging needed — the full catalogue is returned in a single response without a `depth`
parameter (confirmed: the default response is already the complete room property set).

### New method: `GetAttributeConfigurations`

Calls `GET /api/{db}/{pr}/attributeconfigurations` with the same auth header.
Uses `FetchAllPages` for correctness (the endpoint supports `$top`/`$skip`), though
in practice the number of configurations per project is small.

**Filtering:** `applicable_to` is always `null` in live responses — it cannot be used
as a filter. The correct filter is `config_type == "room"`, applied **client-side**
after parsing. Known `config_type` values observed in live data: `"room"`,
`"revit-occurrence"`, `"standardroom"`, `"article"`, `"space"`. Only `"room"`
configurations are relevant to PushIt. No server-side `$filter` is used — fetch all
and discard non-room configurations in the parser.

Parses the response into `List<DrofusAttributeConfiguration>`, retaining only entries
where `config_type == "room"`.

### Updated method: `GetRoomsData`

Appends `$select={comma-separated DrofusFieldName values}` to the rooms endpoint URL.
This ensures extended fields (`room_data_*`, `room_measurement_*`, etc.) are returned
in the rooms payload. The `id` field is always returned by the API regardless of
`$select` so there is no risk of losing the room identifier.

`$select` is built from all mappings in `DrofusDataSourceSettings.PropertyMappings`
at the start of `GetRoomsData`, before the paging loop. The base URL passed to
`FetchAllPages` will already contain `?$select=...`. `FetchAllPages` must therefore
detect whether a `?` is already present and append paging parameters with `&` rather
than `?`. This is a small fix to `FetchAllPages` — check for `url.Contains('?')` and
use `&$top=...&$skip=...` vs `?$top=...&$skip=...` accordingly.

### Updated private HTTP helpers

`ExecuteGet` is **not** modified. Instead the private helper layer is restructured
as follows:

```
CreateRequest(url, apiToken)   → HttpWebRequest   // common setup: auth header, Accept header
ExecuteGet(url, apiToken)      → string           // GET  — reads response body
ExecuteOptions(url, apiToken)  → string           // OPTIONS — reads response body
ExecutePatch(url, body, apiToken) → string        // PATCH — sends body, reads response (future, stubbed)
```

`CreateRequest` is a new private static helper that constructs the `HttpWebRequest`
with the `Authorization: Reference {apiToken}` header and `Accept: application/json`
header. It does not set the verb — each Execute* method sets its own `Method` after
calling `CreateRequest`.

`ExecuteGet` is refactored to call `CreateRequest` internally — no change to its
signature or any of its call sites. `FetchAllPages` continues to call `ExecuteGet`
unchanged.

`ExecuteOptions` is a new private static method. Calls `CreateRequest`, sets
`Method = "OPTIONS"`, reads and returns the response body. Called only by
`GetFieldCatalogue`.

`ExecutePatch` is stubbed now — signature defined, body throws
`NotImplementedException` with a comment noting it is reserved for the future
drofus write-back path. This reserves the pattern without any risk of accidental use.

This structure means each method is honest about what it does, call sites are
self-documenting, and future divergence in headers or response handling per verb
requires no refactoring.

### Retired method: `GetAvailableFields`

Marked `[Obsolete]` immediately and removed once `ValidateDrofusOnStartup` and
`DrofusDataSourceControlViewModel` are updated to use `GetFieldCatalogue` instead.

---

## Changes to `DrofusPropertyMapper`

### `AvailableFields` type change

`IReadOnlyList<string>` → `IReadOnlyList<DrofusRoomField>`.

All internal usages updated: `HasValidationWarnings`, `GetValidationState`, and
`CleanupStaleMappings` all compare against `DrofusRoomField.Id` rather than a raw string.

`UpdateAvailableFields(List<string>)` → `UpdateAvailableFields(List<DrofusRoomField>)`.

### New state: available configurations

| Member | Type | Notes |
|---|---|---|
| `AvailableConfigurations` | `IReadOnlyList<DrofusAttributeConfiguration>` | Populated by `UpdateAvailableConfigurations` |
| `UpdateAvailableConfigurations(List<DrofusAttributeConfiguration>)` | method | Called after each successful Connect and at startup |
| `SelectedConfigurationId` | `int?` | Synced to/from `DrofusDataSourceSettings.SelectedAttributeConfigurationId` |
| `SelectConfiguration(int? configurationId)` | method | Sets `SelectedConfigurationId` and syncs to settings |

### New method: `GetFieldsForSelectedConfiguration`

Returns `IReadOnlyList<DrofusRoomField>` — the catalogue entries whose `Id` appears
in the selected configuration's `Elements`. If no configuration is selected
(`SelectedConfigurationId == null`), returns the full catalogue. This is what
`DrofusDataSourceControlViewModel` passes to the mapping dialog as the available
drofus fields list.

### New method: `GetElementForField`

`GetElementForField(int configurationId, string fieldId)` — returns the
`DrofusAttributeConfigurationElement` from the selected configuration whose
`DrofusAttributeId` matches `fieldId`, or `null` if no match. Used by
`DrofusPropertyMappingDialogViewModel` to pre-populate `FlowDirection` and
`IsUniqueId` when the user selects a field that originates from a configuration
element, saving them from having to set these manually.

### Label resolution helper

`GetFieldLabel(string fieldId)` — looks up a `DrofusRoomField` by `Id` and returns
its `Name`. Returns the raw `fieldId` as fallback if the catalogue has not been loaded
or the id is not found. Used by `DrofusPropertyMapViewModel` to display the human-readable
label in the mapping list without coupling the ViewModel to the full catalogue.

---

## Changes to `ValidateDrofusOnStartup`

Step 2 is expanded. After the credential check it now:

1. Calls `GetFieldCatalogue` → populates `_mapper` via `UpdateAvailableFields` and
   caches on `DrofusDataSourceSettings.StartupFieldCatalogue`.
2. Calls `GetAttributeConfigurations` → populates `_mapper` via
   `UpdateAvailableConfigurations` and caches on
   `DrofusDataSourceSettings.StartupAttributeConfigurations`.
3. Restores `_mapper.SelectedConfigurationId` from
   `DrofusDataSourceSettings.SelectedAttributeConfigurationId`.

The status message in Step 2 changes from reporting the number of fields returned by
the first room object to reporting the number of fields in the catalogue.

Step 3 field validation changes: `availableFields.Contains(mapping.DrofusFieldName)`
is replaced with a catalogue id lookup — checking whether any `DrofusRoomField.Id`
in the catalogue matches `mapping.DrofusFieldName`. The semantics are the same; the
source of truth is now the catalogue rather than a live room object.

The old `GetAvailableFields` call is removed.

---

## Changes to `DrofusDataSourceControlViewModel`

### Connect flow

The call to `GetAvailableFields` is replaced with sequential calls to `GetFieldCatalogue`
and `GetAttributeConfigurations`, both results passed to the mapper.

`Mapper.CleanupStaleMappings` now compares against catalogue ids — no change to the
call site, but the mapper's internal logic is updated as described above.

### New observable state

| Member | Type | Notes |
|---|---|---|
| `AvailableConfigurations` | `ObservableCollection<DrofusAttributeConfiguration>` | Bound to a ComboBox in the settings panel |
| `SelectedConfiguration` | `DrofusAttributeConfiguration?` | When changed: calls `Mapper.SelectConfiguration`, saves to settings, notifies `AddMappingCommand.CanExecute` |
| `HasConfigurations` | `bool` | `true` when `AvailableConfigurations.Count > 0` — controls visibility of the configuration selector |

The configuration selector is shown only after a successful Connect (same visibility
rule as the mapping list). It sits above the mapping list in the UI.

`OnStartupCompleted` is updated to rebuild `AvailableConfigurations` from
`DrofusDataSourceSettings.StartupAttributeConfigurations` and restore the selected
configuration from `DrofusDataSourceSettings.SelectedAttributeConfigurationId`.

### `HasAvailableFields` remains unchanged

Its behaviour — enabling the Add Mapping button — does not depend on whether a
configuration is selected. Fields are always available once the catalogue is loaded.

---

## Changes to `DrofusPropertyMappingDialogViewModel`

### Constructor signature

`IReadOnlyList<string> availableFields` → `IReadOnlyList<DrofusRoomField> availableFields`.

The caller (`DrofusDataSourceControlViewModel.AddMapping` / `EditMapping`) passes
`Mapper.GetFieldsForSelectedConfiguration()` rather than `Mapper.AvailableFields`
directly.

### `AvailableDrofusFields`

`ObservableCollection<string>` → `ObservableCollection<DrofusRoomField>`.

The ComboBox in the view binds `DisplayMemberPath="Name"` so the user sees the
human-readable label. The selected item is a `DrofusRoomField`.

### `SelectedDrofusField`

`string?` → `DrofusRoomField?`.

The `Ok` command writes `SelectedDrofusField!.Id` (not `.Name`) to
`DrofusPropertyMap.DrofusFieldName`, preserving the existing persisted format.

### Direction and IsUniqueId pre-population

When the user selects a drofus field in the dialog and a configuration is active,
`OnSelectedDrofusFieldChanged` calls `Mapper.GetElementForField(selectedConfigId, fieldId)`.
If a matching element is found, `SelectedFlowDirection` and `IsUniqueId` are
automatically set from the element's `Direction` value:

- `"Key"` → `IsUniqueId = true`, `FlowDirection = DrofusToRevit`
- `"ToExternalApplication"` → `IsUniqueId = false`, `FlowDirection = DrofusToRevit`
- `"ToDrofus"` → `IsUniqueId = false`, `FlowDirection = RevitToDrofus`

If no matching element is found (field selected from the full catalogue with no active
configuration, or a field not in the configuration), the direction and unique-id fields
remain at their current values — the user sets them manually as before.

The `IsUniqueIdEnabled` guard remains — if another mapping already holds `IsUniqueId`,
the checkbox stays disabled regardless of the pre-populated value.

### Edit mode pre-population

In edit mode, `SelectedDrofusField` is pre-populated by finding the `DrofusRoomField`
in `AvailableDrofusFields` whose `Id` matches `existingMapping.DrofusFieldName`. If
the field is no longer in the catalogue (stale mapping), it is added as a synthetic
entry with `Name = Id` so the dialog does not break.

### `CanExecuteOk`

Now checks `SelectedDrofusField != null` (was `!string.IsNullOrWhiteSpace(SelectedDrofusField)`).
Semantically identical.

---

## Changes to `DrofusPropertyMapViewModel`

The mapping ListView currently displays `DrofusFieldName` (the raw id) in the drofus
Field column. It should now display the human-readable label.

`DrofusPropertyMapViewModel` receives a `Func<string, string> fieldLabelResolver` in
its constructor — a delegate that calls `DrofusPropertyMapper.GetFieldLabel(fieldId)`.
This avoids coupling the ViewModel to the full catalogue or the mapper directly.

A new `DrofusFieldLabel` property replaces the direct `DrofusFieldName` display binding
in the ListView column. `DrofusFieldName` (the raw id) is still accessible for
internal use (duplicate detection, stale mapping checks) but is not displayed.

---

## Serialisation Impact

Only `DrofusDataSourceSettings.SelectedAttributeConfigurationId` is new serialised
state. It defaults to `null`, so existing settings files deserialise cleanly — a
project with no saved configuration simply shows the full catalogue in the mapping
dialog, which is the correct upgrade behaviour.

`StartupFieldCatalogue` and `StartupAttributeConfigurations` carry `[JsonIgnore]` and
are never written to disk.

All existing `DrofusPropertyMap` entries round-trip unchanged — `DrofusFieldName`
already holds the catalogue `id` string.

---

## Configuration Resilience — Edge Case Handling

These four scenarios are handled explicitly at Connect time and at startup. The
behaviour differs slightly between the two contexts: at **startup** the user is not
present so destructive actions (clearing mappings) happen automatically with a
prominent message; at **Connect** the same automatic actions apply since the user has
just explicitly reconnected and is present to observe the result.

---

### Scenario 1 — No room attribute configurations exist in drofus

**Detection:** `GetAttributeConfigurations` returns an empty list after the
`config_type == "room"` filter is applied.

**Behaviour:**
- A warning message is shown: *"No room attribute configurations are set up in drofus.
  At least one is required to configure mappings. Please create a room attribute
  configuration in drofus and reconnect."*
- `AvailableConfigurations` is empty.
- The mapping interface (configuration selector, mapping list, Add/Edit/Remove buttons)
  is **disabled** until a successful Connect returns at least one configuration.
- Any existing mappings are preserved in settings — they are not cleared, since the
  absence of configurations is a drofus-side setup problem, not a data integrity
  problem.
- Room data cannot be loaded until at least one configuration exists and mappings are
  configured.

**Implementation touch points:** `DrofusDataSourceControlViewModel` — `HasConfigurations`
drives the disabled state of the mapping interface. `ValidateDrofusOnStartup` — returns
`Warning` with the above message and skips Steps 3 and 4 (mapping validation and room
load) when no configurations are available.

---

### Scenario 2 — Selected configuration was renamed in drofus

**Detection:** Not detectable as a problem — `SelectedAttributeConfigurationId` stores
the integer `id`, which is stable across renames. The renamed configuration is found
normally by id; its updated `Name` is displayed in the selector.

**Behaviour:** Fully transparent. No message, no action. The new name appears in the
configuration selector on next Connect or startup.

**No implementation changes required for this scenario.**

---

### Scenario 3 — Selected configuration was deleted in drofus

**Detection:** After fetching configurations, `SelectedAttributeConfigurationId` is
set in settings but no configuration in the returned list has a matching `id`.

**Behaviour:**
- All existing mappings are **cleared automatically**.
- `SelectedAttributeConfigurationId` is reset to `null` in settings.
- A warning message is shown: *"The previously selected attribute configuration no
  longer exists in drofus. All mappings have been cleared. Please select a
  configuration and reconfigure your mappings."*
- The configuration selector is shown with no selection.
- The mapping list is empty.
- Settings are saved immediately after the clear so the deleted state is not
  re-encountered on next startup.

**Rationale:** Mappings reference field ids that were part of the deleted
configuration. Without the configuration context those mappings cannot be validated or
augmented. A clean reset is safer than leaving orphaned mappings that may point to
fields no longer intended for this project's sync profile.

**Startup vs Connect:** Behaviour is identical in both contexts — the cleared state
is visible to the user immediately when the window opens (startup) or after the
Connect completes (Connect flow).

**Implementation touch points:** `DrofusPropertyMapper` — new method
`HandleDeletedConfiguration()` clears `_mappings`, resets `SelectedConfigurationId`
to `null`, and returns a message string for the caller to surface. Called from both
`ValidateDrofusOnStartup` (Step 2, after configurations are fetched) and
`DrofusDataSourceControlViewModel.Connect` (after `UpdateAvailableConfigurations`).
`SaveMappingsToSettings` and `SelectConfiguration(null)` are called immediately after
to persist the reset state.

---

### Scenario 4 — Selected configuration was modified in drofus (fields added or removed)

**Detection:** The configuration is found by id (it exists), but after comparing its
current `Elements` against `PropertyMappings`, some mapped `DrofusFieldName` values
are no longer present as `DrofusAttributeId` values in the configuration's elements.

**Behaviour:**
- Mappings whose `DrofusFieldName` is no longer in the configuration's elements are
  **removed automatically** via `CleanupStaleMappings`.
- A warning message lists the removed mappings: *"N mapping(s) removed — the following
  drofus fields are no longer part of the selected configuration: [field names]."*
- Mappings that are still valid are preserved.
- Fields newly added to the configuration become available immediately in the Add
  Mapping dialog — no user action needed beyond opening it.

**Relationship to `CleanupStaleMappings`:** The existing `CleanupStaleMappings` method
compares `DrofusFieldName` against `AvailableFields`. When a configuration is active,
`AvailableFields` (via `GetFieldsForSelectedConfiguration`) returns only the fields in
that configuration — so a field removed from the configuration will be absent from
`AvailableFields` and will be caught by the existing cleanup logic. No new method is
needed; the existing mechanism handles this scenario correctly once `AvailableFields`
is properly scoped to the selected configuration.

**Startup vs Connect:** At startup, stale mappings are **flagged** (`DrofusFieldMissing
= true`) rather than removed — consistent with the existing startup validation
philosophy. At Connect, `CleanupStaleMappings` runs and removes them — consistent with
the existing Connect flow behaviour.

---

### Scenario 5 — User switches to a different configuration in the UI

**Detection:** `OnSelectedConfigurationChanged` fires in
`DrofusDataSourceControlViewModel` with a new `DrofusAttributeConfiguration` value
that differs from the previously selected one.

**Behaviour:**

If the new configuration contains all the same `DrofusAttributeId` values as the
current mappings' `DrofusFieldName` values — i.e. no mappings would be dropped —
the switch happens silently with no confirmation required.

If one or more existing mappings reference field ids not present in the new
configuration's elements, a confirmation dialog is shown before any change is made.
The dialog displays:
- The name of the configuration being switched to.
- The human-readable labels of the mappings that will be dropped (resolved via
  `GetFieldLabel` so the user sees names, not raw ids).
- The count of mappings that will be kept.

Example message: *"Switching to 'Rooms - Detailed' will remove 3 mapping(s): Programmed
Area, Ceiling Height, Room Data Status. 2 mapping(s) will be kept. Continue?"*

If the user confirms: `CleanupStaleMappings` runs against the new configuration's
fields, persists, and the UI refreshes.

If the user cancels: `SelectedConfiguration` is reverted to the previous value.
No mappings are changed. `DrofusDataSourceControlViewModel` holds a
`_previousConfigurationId` private field to enable this revert.

**Scope:** This confirmation applies only to user-initiated selection changes in
`DrofusDataSourceControlViewModel`. The `SettingsViewModel` load-settings path
constructs a fresh `DrofusPropertyMapper` from the loaded settings and does not
perform a mid-session switch, so no confirmation is needed there. `ValidateDrofusOnStartup`
runs pre-window with no UI interaction possible, so it also does not apply.

**Implementation touch points:** `DrofusDataSourceControlViewModel` —
`OnSelectedConfigurationChanged` partial method (or property setter); new
`_previousConfigurationId` field; new `ShowConfigurationChangeConfirmation` method
following the existing `ShowMappingDialog` pattern. `DrofusPropertyMapper` — no new
methods needed; `GetFieldsForSelectedConfiguration` and `CleanupStaleMappings` handle
the actual field filtering and removal after confirmation.

---

## Dependency Order

```
Step 1  — New models: DrofusRoomField, DrofusAttributeConfigurationElement
          (with Direction property), DrofusAttributeConfiguration

Step 2  — DrofusDataSourceSettings: add SelectedAttributeConfigurationId,
          StartupFieldCatalogue, StartupAttributeConfigurations;
          retire StartupAvailableFields (mark Obsolete)

Step 3  — DrofusDataSource:
          - add CreateRequest private helper (common HttpWebRequest setup)
          - refactor ExecuteGet to call CreateRequest (no signature change)
          - add ExecuteOptions private helper (OPTIONS verb)
          - stub ExecutePatch private helper (NotImplementedException, future)
          - fix FetchAllPages URL construction (& vs ? for $select coexistence)
          - add GetFieldCatalogue (calls ExecuteOptions, no paging; drop entries
            with null/empty id — Gap 6)
          - add GetAttributeConfigurations (calls FetchAllPages, client-side
            config_type == "room" filter)
          - update GetRoomsData ($select from active mappings; skip $select append
            when PropertyMappings empty — Gap 3)
          - mark GetAvailableFields Obsolete

Step 4  — DrofusPropertyMapper: change AvailableFields type, update all internal
          comparisons to use DrofusRoomField.Id, add configuration state,
          add GetFieldsForSelectedConfiguration, add GetElementForField (default
          unknown Direction to DrofusToRevit — Gap 4/8), add GetFieldLabel,
          add HandleDeletedConfiguration (NOT called on connection failure — Gap 9)

Step 5  — ValidateDrofusOnStartup: update Step 2 to call GetFieldCatalogue (Gap 1
          — fatal on failure, disable everything) and GetAttributeConfigurations
          (Gap 2 — fatal to mapping interface on failure); add Scenario 1 check
          (no configurations → warning + skip steps 3/4); add Scenario 3 check
          (deleted configuration → HandleDeletedConfiguration + warning; only when
          connection succeeds — Gap 9); update Step 3 field validation to use
          catalogue id lookup (Scenario 4 — flag only, no removal at startup)

Step 6  — DrofusDataSourceControlViewModel: update Connect flow (Gap 1 fatal,
          Gap 2 fatal to mapping interface); add Scenario 1 check (disable mapping
          interface when HasConfigurations == false); add Scenario 3 check (call
          HandleDeletedConfiguration only on successful connect — Gap 9); add
          Scenario 5 handling (OnSelectedConfigurationChanged: compute
          would-be-dropped list, show confirmation dialog if non-empty, revert via
          _previousConfigurationId on cancel, run CleanupStaleMappings on confirm);
          add configuration observable state; update OnStartupCompleted; add
          degraded-state handling for Gap 9 (grid disabled, push button disabled,
          error message)

Step 7  — DrofusPropertyMappingDialogViewModel: change field list type,
          update constructors, add direction pre-population from configuration
          element, update Ok command, update edit pre-population

Step 8  — DrofusPropertyMapViewModel: add fieldLabelResolver, add DrofusFieldLabel

Step 9  — Remove GetAvailableFields and StartupAvailableFields
          (all callers now gone)
```

---

## What Does Not Change

- `DrofusPropertyMap` model — no changes.
- `GetHeaderProperties` — no changes.
- `Validate` — no changes.
- `ExecuteGet` signature and all its call sites — unchanged. It is internally
  refactored to call `CreateRequest` but its public-facing behaviour is identical.
- `FetchAllPages` loop logic — only the URL construction (`?` vs `&`) changes.
- The Revit side of the mapping dialog — completely untouched.
- `CleanupStaleMappings` call sites — unchanged; internal logic updated in mapper.
- Settings serialisation infrastructure (`SettingsUtils`) — no changes.
- All other `IDataSource` implementations (`CsvDataSource`) — unaffected.

---

## Additional Unhappy Path Decisions

These decisions were made after the main implementation was specified. They cover
edge cases identified during review. Each is keyed to its gap number for traceability.

---

### Gap 1 — `GetFieldCatalogue` fails

**Decision:** Fatal to the Connect/startup sequence. Disable everything — mapping
interface, Add/Edit/Remove buttons, Load button. Settings are not changed.

**Error message:** *"Could not retrieve the room field catalogue from drofus. Check
your connection and reconnect."*

**Implementation:** `ValidateDrofusOnStartup` returns `Error` and skips Steps 3 and 4.
`DrofusDataSourceControlViewModel.Connect` catches the exception, sets `IsConnected =
false`, and surfaces the message. `HasAvailableFields` remains `false`, keeping the
mapping interface disabled.

---

### Gap 2 — `GetAttributeConfigurations` fails (catalogue succeeded)

**Decision:** Fatal to the mapping interface, treated identically to Scenario 1 (no
room configurations exist). The catalogue is retained in the mapper but the mapping UI
is disabled until a successful Connect returns at least one configuration.

**Error message:** *"No room attribute configurations are set up in drofus. At least
one is required to configure mappings. Please create a room attribute configuration in
drofus and reconnect."*

**Implementation:** Same path as Scenario 1 — `HasConfigurations == false` gates the
mapping interface. `ValidateDrofusOnStartup` returns `Warning` and skips Steps 3 and
4. The catalogue fetch is not undone.

---

### Gap 3 — `GetRoomsData` called with empty `PropertyMappings`

**Decision:** Already guarded. The existing `idMapping is null` check throws before
any HTTP call is made. The `$select` construction must additionally skip the
`?$select=` append when `PropertyMappings` is empty to avoid producing a malformed
URL. This is a defensive one-liner, not a new code path.

**Implementation note:** In `GetRoomsData`, build the `$select` string only when
`PropertyMappings.Count > 0`. If empty, pass the bare base URL to `FetchAllPages`
unchanged — the existing guard will throw before any room processing begins.

---

### Gap 4 — Unknown `Direction` value in `DrofusAttributeConfigurationElement`

**Decision:** Default to `MappingFlowDirection.DrofusToRevit`. This is the safe,
non-destructive fallback — data flows into Revit rather than overwriting drofus.

**Implementation note:** In `GetElementForField` / direction pre-population logic,
the `Direction` string switch should have an explicit `default` case that returns
`MappingFlowDirection.DrofusToRevit` and `IsUniqueId = false`. Add a code comment
noting this is intentional future-proofing against new API direction values.

---

### Gap 5 — Configuration has no `"Key"` element (no unique identifier)

**Decision:** Already handled. The existing `idCount != 1` guard in
`ValidateDrofusOnStartup` Step 4 catches this and aborts the room load with a clear
error message. No new code required. Documented here for completeness.

---

### Gap 6 — Null or empty field `id` in catalogue response

**Decision:** Defensive filter during parsing. Any `DrofusRoomField` entry whose `Id`
is null or whitespace is silently dropped during `GetFieldCatalogue` parsing.

**Implementation note:** In the `GetFieldCatalogue` JSON parsing loop, skip any object
whose `id` property is null, missing, or whitespace before constructing a
`DrofusRoomField`. No message needed — a null-id field is a malformed API response
and should not surface to the user.

---

### Gap 7 — `$select` query string length

**Decision:** Non-issue. No action required. Typical projects will have 10–40 mapped
fields, producing a `$select` string well within any reasonable URL length limit.
Documented here to prevent this being raised as a concern during code review.

---

### Gap 8 — Unknown `Direction` value (same as Gap 4, confirmed)

See Gap 4. Default to `MappingFlowDirection.DrofusToRevit`.

---

### Gap 9 — Network unavailable at startup with existing valid mappings

**Decision:** Degraded state. Existing mappings are preserved and not modified.
The grid is disabled. The Push button is disabled. An error message is shown.

**Error message:** *"Could not connect to drofus at startup. Existing mappings are
preserved. Reconnect to load room data."*

**Implementation:** `ValidateDrofusOnStartup` already returns `Error` when the
connection fails (Step 2 catch block). The additional requirements are:
- Grid disabled — driven by the existing `IsWaitingForRevitCommandToFinish` or a new
  `IsDrofusOffline` flag on `RoomsMainViewModel`, bound to the grid's `IsEnabled`.
- Push button disabled — same binding.
- Existing mappings untouched — `HandleDeletedConfiguration` is NOT called on
  connection failure; it is only called when the connection succeeds but the
  configuration id is missing from the returned list.

**Distinction from Scenario 3:** A connection failure means we have no information
about what exists in drofus — mappings must be preserved because the absence of data
is not evidence of deletion. Scenario 3 only fires when we have a successful connection
and positively confirm the configuration is gone.

