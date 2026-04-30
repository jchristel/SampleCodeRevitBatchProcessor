# Transmittal View — Implementation Guidelines

---

## 1. Overview

The Transmittal view displays revision history per sheet. It is opened from `MergeView` via a dedicated button (position TBD). It is a standalone `Window` (not a `UserControl`) styled consistently with the rest of the application.

The view has two main sections — **Revisions** and **Documents** — each backed by a custom DataGrid base class defined in this project.

---

## 2. DataGrid Controls

Both the Revisions grid and the Documents grid use the existing `DynamicDataGrid` control from `duHastNet.UI.CustomControls.CustomDataGrid`. No new base classes are required.

### 2.1 Existing control summary

`DynamicDataGrid` derives from `DataGrid` and is driven by an `ObservableCollection<DynamicColumnDefinition>` bound to its `ColumnDefinitions` dependency property. It already sets `AutoGenerateColumns = false` and `CanUserAddRows = false` in its constructor. Columns are fully regenerated whenever the `ColumnDefinitions` collection changes or an individual definition's `IsReadOnly` property changes.

Row data uses `DynamicRowData`, which stores all cell values in a `Dictionary<string, object>` indexed by the column's `PropertyName`. Binding inside the generated columns uses the indexer syntax `[PropertyName]`.

### 2.2 Grid locking requirements

The following must be set on every `DynamicDataGrid` instance used in the Transmittal view in XAML:

| Property | Revisions grid | Documents grid | Action needed |
|---|---|---|---|
| `CanUserAddRows` | `False` | `False` | Already set in control constructor ✓ |
| `CanUserDeleteRows` | `False` | `False` | Already set in control constructor ✓ |
| `CanUserReorderColumns` | `False` | `False` | **Set in XAML per instance** |
| `CanUserSortColumns` | `False` | `False` | **Set in XAML per instance** |

> **Column-level `IsReadOnly`:** `DynamicDataGrid.CreateColumn` sets `column.IsReadOnly` and the binding mode directly from `DynamicColumnDefinition.IsReadOnly`. This is the only mechanism needed. The Documents grid sets all column definitions to `IsReadOnly = true`. The Revisions grid sets `IsReadOnly = false` on the `IsChecked` column and `IsReadOnly = true` on all others — no grid-level override is required in either case.

> **Note on `CanUserReorderColumns`:** The `DynamicDataGrid` constructor does not currently set this. It must be set explicitly in XAML for each instance.

### 2.3 Inactive row styling

The Documents grid must visually distinguish inactive documents (grey, italic). Since `DynamicDataGrid` uses generated columns and `DynamicRowData`, the inactive style is applied via a `DataGrid.RowStyle` in XAML, triggering on a well-known key in the row's data dictionary:

```xml
<DynamicDataGrid.RowStyle>
    <Style TargetType="DataGridRow">
        <Style.Triggers>
            <DataTrigger Binding="{Binding [IsInactive]}" Value="True">
                <Setter Property="Foreground" Value="#AAAAAA"/>
                <Setter Property="FontStyle" Value="Italic"/>
            </DataTrigger>
        </Style.Triggers>
    </Style>
</DynamicDataGrid.RowStyle>
```

The ViewModel sets `row["IsInactive"] = true/false` on each `DynamicRowData` row. The `IsInactive` key is never added as a `DynamicColumnDefinition`, so it does not appear as a visible column.

---

## 3. Transmittal Window

### 3.1 Class Names

| Artefact | Name |
|---|---|
| Window XAML | `TransmittalView.xaml` |
| Window code-behind | `TransmittalView.xaml.cs` |
| ViewModel | `TransmittalViewModel.cs` |

### 3.2 Namespace

Follow the existing pattern:
`duHastNet.DocManager.UI.Shared.Views.Transmittal`

### 3.3 Window Layout (rows, top to bottom)

```
Row 0  — Blue header banner (matches MergeView style: "Document Manager" / "Transmittal")
Row 1  — GlobalMessageView (bound to GlobalMessageViewModel — same pattern as MergeView)
Row 2  — Revisions section  (fixed height or proportional split — see §4)
Row 3  — Documents section  (fills remaining space — see §5)
Row 4  — Bottom action bar  (Export to CSV | Close)
```

`Row 2` and `Row 3` share the available space. Suggested split: `Row 2 = 2*`, `Row 3 = 3*`. Both sections are inside bordered panels matching the style of `DocumentMatchControl` in `MergeView` (`BorderBrush="Gray"`, `BorderThickness="1"`, `CornerRadius="3"`).

---

## 4. Revisions Section

### 4.1 Layout (within its bordered panel)

```
Row 0  — Section header: "Revisions"  (SemiBold label, left-aligned, padding 8,6)
Row 1  — Status message TextBlock      (see §7 for status message conventions)
Row 2  — DmDataGrid (revisions list)   (fills remaining height)
```

### 4.2 Control

Use `DynamicDataGrid` with `CanUserReorderColumns="False"` and `CanUserSortColumns="False"` set in XAML. Column interactivity is controlled entirely through `DynamicColumnDefinition.IsReadOnly` — no grid-level `IsReadOnly` is required or set. `CreateColumn` sets `column.IsReadOnly` and the binding mode (`TwoWay` / `OneWay`) directly from the column definition, so setting `IsReadOnly = false` on the checkbox column and `IsReadOnly = true` on the remaining columns is sufficient.

### 4.3 Column Definitions (`DynamicColumnDefinition`)

| `PropertyName` | `DisplayName` | `DataType` | Width | `IsReadOnly` |
|---|---|---|---|---|
| `IsChecked` | _(empty string)_ | `typeof(bool)` | `44` | `false` |
| `RevisionDate` | `Date` | `typeof(DateTime)` | `110` | `true` |
| `RevisionDescription` | `Description` | `typeof(string)` | `0` (star) | `true` |

### 4.4 Edge Cases

| Condition | Behaviour |
|---|---|
| No revisions in database | Show empty grid; status message row displays: _"No revisions in database."_ |

### 4.5 ViewModel — Revisions

Expose:

- `ObservableCollection<TransmittalRevisionRowViewModel> Revisions`
- `string RevisionsStatusMessage` — drives the status message row; empty string = row collapses (via `BoolToVisibilityConverter` on `string.IsNullOrEmpty`)
- `IEnumerable<TransmittalRevisionRowViewModel> CheckedRevisions` — derived from `Revisions` where `IsChecked == true`; used by Documents section

`TransmittalRevisionRowViewModel` properties:

- `bool IsChecked` — `[ObservableProperty]`, on change calls `RebuildDocumentColumns` on the parent ViewModel
- `DateTime RevisionDate`
- `string RevisionDescription`
- `int RevisionId` — internal, not displayed

---

## 5. Documents Section

### 5.1 Layout (within its bordered panel)

```
Row 0  — Section header + toggle control  (see §5.2)
Row 1  — Options row: "Show inactive documents" checkbox | "Include document history" checkbox
Row 2  — Status message TextBlock
Row 3  — DmDynamicDataGrid (documents list)  (fills remaining height)
```

### 5.2 Mode Toggle

Use a `ToggleButton` (or two `RadioButton`s styled as a segmented control) to switch between:

- **Show All Documents** (`DocumentDisplayMode.All`)
- **By Revisions Only** (`DocumentDisplayMode.ByRevision`)

Bind to `DocumentDisplayMode` property on the ViewModel (enum). Default: `All`.

### 5.3 Control

Use `DynamicDataGrid` bound to `ColumnDefinitions` and `ItemsSource` (both on the ViewModel). Set `IsReadOnly="True"`, `CanUserReorderColumns="False"`, and `CanUserSortColumns="False"` in XAML. Apply the inactive row style from §2.3.

### 5.4 Data loading strategy — pre-load all revision data into rows

All revision indicator data is loaded into `DynamicRowData` rows **once** when the Documents collection is first built (on load, on mode change, on filter change, or on `IncludeDocumentHistory` toggle). Each row carries indicator values for **every revision in the database**, stored in the `DynamicRowData` dictionary using the revision's `PropertyName` key (see §5.5).

When the user checks or unchecks a revision in the Revisions grid, **only `ColumnDefinitions` is updated** — rows are not rebuilt. This is efficient because `DynamicDataGrid` regenerates columns from `ColumnDefinitions` without touching `ItemsSource`.

**Rebuild triggers:**

| Trigger | Action |
|---|---|
| Initial load | Build rows + all `ColumnDefinitions` (static + all checked revisions) |
| Revision `IsChecked` toggled on | Add one `DynamicColumnDefinition` to `ColumnDefinitions` |
| Revision `IsChecked` toggled off | Remove one `DynamicColumnDefinition` from `ColumnDefinitions` |
| `DocumentDisplayMode` changed | Rebuild rows; rebuild `ColumnDefinitions` |
| `ShowInactiveDocuments` changed | Rebuild rows; rebuild `ColumnDefinitions` |
| `IncludeDocumentHistory` changed | Rebuild rows; rebuild `ColumnDefinitions` |

### 5.5 Column definitions

**Static columns** — always present, added first to `ColumnDefinitions`:

| `PropertyName` | `DisplayName` | `DataType` | Width | `IsReadOnly` |
|---|---|---|---|---|
| `DocumentNumber` | `Doc Number` | `string` | `160` | `true` |
| `DocumentName` | `Doc Name` | `string` | `*` (use `0` and set `Width` as star via `DataGridLength`) | `true` |
| `CurrentRevision` | `Current Rev.` | `string` | `90` | `true` |

**Dynamic revision columns** — one per checked revision in `CheckedRevisions`, appended after static columns:

| Field | Value |
|---|---|
| `PropertyName` | `"Rev_{RevisionId}"` — unique, stable key |
| `DisplayName` | `"{RevisionDate:d} — {RevisionDescription}"` (truncated to 40 chars if needed) |
| `DataType` | `string` |
| `Width` | `100` |
| `IsReadOnly` | `true` |

### 5.6 Row data — `DynamicRowData` population

For each document row, set the following keys in `DynamicRowData.Values`:

```csharp
row["DocumentNumber"]  = document.Number;           // or historical number
row["DocumentName"]    = document.Name;
row["CurrentRevision"] = document.Revision;
row["IsInactive"]      = !document.IsActive;        // used by row style, not shown as column

// For every revision in the database (not just checked ones):
foreach (var revision in allRevisions)
{
    string key = $"Rev_{revision.Id}";
    string indicator = document.GetRevisionIndicator(revision.Id) ?? string.Empty;
    row[key] = indicator;
}

// For history rows additionally:
row["IsHistoryRow"]    = true;
row["NumberActiveFrom"] = numberActiveFrom;         // DateOnly?, stored as string for display
row["NumberActiveTo"]   = numberActiveTo;           // DateOnly?, stored as string for display
```

`IsHistoryRow`, `NumberActiveFrom`, and `NumberActiveTo` are never added to `ColumnDefinitions` and are never visible in the grid. They are available for export logic and tooltip binding if needed.

### 5.7 Edge Cases

| Condition | Mode | Behaviour |
|---|---|---|
| No documents in database | Both | Empty grid; status: _"No documents in database."_ |
| No revisions checked | All | Static columns only; no dynamic columns; no status message |
| No revisions checked | By Revision | Empty grid; status: _"No revisions selected. Switch to 'Show All Documents' or select a revision above."_ |
| Checked revision(s) have no documents assigned | All | Dynamic column(s) shown; all revision indicator cells empty |
| Checked revision(s) have no documents assigned | By Revision | Empty grid; status: _"The selected revision(s) have no documents assigned."_ |
| No revisions in database | By Revision | Empty grid; status: _"No revisions available. Use 'Show All Documents' instead."_ |

### 5.8 "Show Inactive Documents" Checkbox

Bound to `bool ShowInactiveDocuments` on the ViewModel. When `false`, filter out rows where `IsInactive == true` before populating `Documents`. Default: `false`.

### 5.9 "Include Document History" Checkbox

Bound to `bool IncludeDocumentHistory` on the ViewModel. When `true`, include additional rows per document where the document number has changed — one row per historical number. These rows have `IsHistoryRow = true`.

#### Document History — Revision Inference Approach

The database does not store an explicit link between a historical document number and the revisions that were issued while that number was active. However, this can be inferred from the data that is available:

**Data available per `Document`:**
- `DocumentNumberHistory`: `Dictionary<string, DateOnly>` — key = old document number, value = date the number was changed away from it.
- `RevisionIndicatorHistory`: `Dictionary<int, string>` — key = `RevisionId`, value = revision indicator string issued for this document under that revision.

**Data available per `Revision`:**
- `RevisionDate`: `DateTime` — the date the revision was issued.

**Inference algorithm:**

1. Order all entries in `DocumentNumberHistory` by their change date ascending. This gives a chronological list of number changes.
2. Reconstruct the active date range for each historical number:
   - The first historical number was active from the beginning of time (or the document's creation) until its change date.
   - Each subsequent historical number was active from the previous change date until its own change date.
   - The current number is active from the last change date onward.
3. For each `RevisionId` in `RevisionIndicatorHistory`, look up the corresponding `Revision.RevisionDate`.
4. Assign each revision to the document number that was active on that revision date by comparing `RevisionDate` against the reconstructed date ranges.
5. Populate `RevisionIndicators` on the history row with only the indicators that fall within the active date range for that historical number. Cells outside the range are left empty.

**Assumptions and limitations:**
- Change dates are recorded as `DateOnly` using `DateTime.Now` at the time of import. If a document number was changed with a backdated revision, the inference may assign the revision to the wrong number. This is an edge case and is considered acceptable.
- If two number changes occurred on the same date, ordering is ambiguous. In this case, order by dictionary insertion order as a fallback and note the ambiguity in the row's tooltip.

**`TransmittalDocumentRowViewModel` additions for history rows:**

- `DateOnly? NumberActiveFrom` — inferred start date; `null` for the earliest known number
- `DateOnly? NumberActiveTo` — the change date from `DocumentNumberHistory`; `null` for the current number
- `string HistoryDateRangeLabel` — formatted display e.g. `"until 2023-06-15"` or `"2021-03-01 – 2023-06-15"`; shown as a suffix in the Doc Number cell or as a tooltip

---

## 6. Bottom Action Bar

Single `Border` row, `Background="#F5F5F5"`, `BorderThickness="0,1,0,0"`, `BorderBrush="#CCCCCC"`, `Padding="12,8"`.

Left side: status/hint text (e.g. export confirmation).
Right side: two buttons.

| Button | Content | Command | Notes |
|---|---|---|---|
| Export | `Export to CSV` | `ExportToCsvCommand` | Exports the Documents DataGrid only (all rows currently shown, respecting active mode and filters) |
| Close | `Close` | `CloseCommand` | Closes the window; no dialog result |

Button styling matches `MergeView` action buttons. Export button has `FontWeight="SemiBold"`, `Background="#2196F3"`, `Foreground="White"`, `BorderThickness="0"`.

---

## 7. Status Message Conventions

Each section has its own `TextBlock` for status messages. Follow this pattern consistently:

- Binding: `{Binding RevisionsStatusMessage}` / `{Binding DocumentsStatusMessage}`
- Visibility: collapse when empty via `BoolToVisibilityConverter` on a helper bool, or use a `StringToVisibilityConverter`
- Style: `FontSize="12"`, `Foreground="#CC0000"` for warnings/errors, `Foreground="#555555"` for neutral messages
- Margin: `"8,4,8,4"`
- Located directly above the DataGrid header in its section

---

## 8. GlobalMessageView

Placed at `Row 1` of the window grid, identical to `MergeView`:

```xml
<Grid Grid.Row="1">
    <utilsViews:GlobalMessageView DataContext="{Binding GlobalMessageViewModel}"/>
</Grid>
```

`GlobalMessageViewModel` is initialised in the constructor, wired to a `MessageStore` passed in from the caller.

---

## 9. ViewModel — `TransmittalViewModel`

Inherits `AppViewModelBase`.

### Constructor signature

```csharp
public TransmittalViewModel(
    IDocumentRepositorySync documentRepository,
    IRevisionRepositorySync revisionRepository,
    MessageStore messageStore)
```

All parameters validated against null per `ConstructorValidationBestPractices.md`.

### Key observable properties

| Property | Type | Notes |
|---|---|---|
| `Revisions` | `ObservableCollection<TransmittalRevisionRowViewModel>` | Loaded on construction |
| `DocumentColumnDefinitions` | `ObservableCollection<DynamicColumnDefinition>` | Static + dynamic columns; dynamic portion rebuilt on check/uncheck |
| `DocumentRows` | `ObservableCollection<DynamicRowData>` | All document rows with full revision data pre-loaded; rebuilt on mode/filter change only |
| `DocumentDisplayMode` | `DocumentDisplayMode` (enum) | `All` or `ByRevision`; change triggers full row rebuild |
| `ShowInactiveDocuments` | `bool` | Default `false`; change triggers full row rebuild |
| `IncludeDocumentHistory` | `bool` | Default `false`; change triggers full row rebuild |
| `RevisionsStatusMessage` | `string` | |
| `DocumentsStatusMessage` | `string` | |
| `GlobalMessageViewModel` | `GlobalMessageViewModel` | |

### Rebuild strategy

Two separate rebuild methods are used:

**`RebuildDocumentColumns()`** — called only when a revision `IsChecked` changes:
1. Preserve the three static `DynamicColumnDefinition` entries.
2. Remove all dynamic entries (`PropertyName` starts with `"Rev_"`).
3. For each revision in `Revisions` where `IsChecked == true`, append a new `DynamicColumnDefinition` using `PropertyName = "Rev_{RevisionId}"`.
4. Update `DocumentsStatusMessage`.

**`RebuildDocumentRows()`** — called on load, mode change, filter change, or history toggle:
1. Load all documents from the repository (respecting `ShowInactiveDocuments` and `DocumentDisplayMode`).
2. For each document, create a `DynamicRowData` and populate all keys including `Rev_{id}` for every revision in the database.
3. If `IncludeDocumentHistory` is on, apply the inference algorithm (see §5.9) and append history rows.
4. Replace `DocumentRows` with the new collection.
5. Call `RebuildDocumentColumns()` to ensure dynamic columns match current check state.
6. Update `DocumentsStatusMessage`.

---

## 10. Entry Point from MergeView

- Add a button to `MergeView.xaml` (position TBD by designer).
- Add `OpenTransmittalCommand` to `MergeViewModel`.
- The command instantiates `TransmittalViewModel` with the required repositories and opens `TransmittalView` as a non-modal window (or modal — TBD).
- The `TransmittalView` window receives the ViewModel via its constructor and sets `DataContext` in code-behind.

---

## 11. File Structure

```
duHastNet.DocManager.UI.Shared/
└── Views/
    └── Transmittal/
        ├── TransmittalView.xaml
        ├── TransmittalView.xaml.cs
        └── ViewModels/
            ├── TransmittalViewModel.cs
            ├── TransmittalRevisionRowViewModel.cs
            └── DocumentDisplayMode.cs          (enum)
```

> No new control classes are required. The existing `DynamicDataGrid` and `DynamicRowData` from `duHastNet.UI.CustomControls.CustomDataGrid` are used directly.

---

## 12. Build Order

1. `DocumentDisplayMode.cs` (enum)
2. `TransmittalRevisionRowViewModel.cs`
3. `TransmittalViewModel.cs`
4. `TransmittalView.xaml` + code-behind
5. `OpenTransmittalCommand` on `MergeViewModel`
6. Button on `MergeView.xaml`
