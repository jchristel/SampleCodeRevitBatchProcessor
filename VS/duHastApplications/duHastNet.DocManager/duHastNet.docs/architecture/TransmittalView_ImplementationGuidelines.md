# Transmittal View — Implementation Guidelines

> **Status: As-built.** This document reflects the implemented state of the Transmittal view as of the current codebase upload.

---

## 1. Overview

The Transmittal view displays revision history per document. It is opened from `MergeView` via the **Transmittal** button in the header toolbar. Navigation uses the existing `NavigationStore` pattern — the view is a `UserControl` hosted inside `NavigationHostView`, not a separate window.

The view has two main sections — **Revisions** and **Documents** — both backed by the existing `DynamicDataGrid` control.

---

## 2. DataGrid Controls

Both grids use `DynamicDataGrid` and `DynamicRowData` from `duHastNet.UI.CustomControls.CustomDataGrid`.

### 2.1 XAML namespace

```xml
xmlns:customGrid="clr-namespace:duHastNet.UI.CustomControls.CustomDataGrid;assembly=duHastUICustomControls.25.0.1.1"
```

### 2.2 Existing control summary

`DynamicDataGrid` derives from `DataGrid`. It is driven by an `ObservableCollection<DynamicColumnDefinition>` bound to its `ColumnDefinitions` dependency property. It already sets `AutoGenerateColumns = false` and `CanUserAddRows = false` in its constructor. Columns are fully regenerated whenever the `ColumnDefinitions` collection changes.

`DynamicRowData` stores all cell values in a `Dictionary<string, object>` indexed by the column's `PropertyName`. Binding inside generated columns uses the indexer syntax `[PropertyName]`. `DynamicRowData` implements `INotifyPropertyChanged` — the indexer setter fires `PropertyChanged` when a value changes.

### 2.3 Grid locking

| Property | Revisions grid | Documents grid | How |
|---|---|---|---|
| `CanUserAddRows` | `False` | `False` | Control constructor ✓ |
| `CanUserDeleteRows` | `False` | `False` | Control constructor ✓ |
| `CanUserReorderColumns` | `False` | `False` | Set in XAML |
| `CanUserSortColumns` | `False` | `False` | Set in XAML |
| `IsReadOnly` | Not set | `True` | Set in XAML — Documents grid only |

Column-level read-only is controlled via `DynamicColumnDefinition.IsReadOnly`. `CreateColumn` sets `column.IsReadOnly` and the binding mode (`TwoWay` / `OneWay`) directly from the definition. The Revisions grid relies entirely on per-column `IsReadOnly` — no grid-level `IsReadOnly` is set so the checkbox column remains interactive.

### 2.4 Inactive row styling (Documents grid)

Applied via `DataGrid.RowStyle` in XAML. The ViewModel writes `row[KeyIsInactive] = true/false` on each `DynamicRowData`. The key is never added to `DocumentColumnDefinitions` so it is invisible as a column.

```xml
<customGrid:DynamicDataGrid.RowStyle>
    <Style TargetType="DataGridRow">
        <Style.Triggers>
            <DataTrigger Binding="{Binding [IsInactive]}" Value="True">
                <Setter Property="Foreground" Value="#AAAAAA"/>
                <Setter Property="FontStyle" Value="Italic"/>
            </DataTrigger>
        </Style.Triggers>
    </Style>
</customGrid:DynamicDataGrid.RowStyle>
```

### 2.5 Two-way checkbox sync (Revisions grid)

`DynamicDataGrid` binds the `IsChecked` column `TwoWay` to `row["IsChecked"]` on `DynamicRowData`. The ViewModel maintains a parallel `TransmittalRevisionRowViewModel` per row. Two `PropertyChanged` handlers are wired in `LoadRevisionsAsync` to keep both in sync:

- `rowVm.PropertyChanged` → writes `row["IsChecked"]` (ViewModel → grid)
- `row.PropertyChanged` → writes `rowVm.IsChecked` (grid → ViewModel), guarded against infinite loops

`OnIsCheckedChanged` on `TransmittalRevisionRowViewModel` fires the `onCheckedChanged` callback, which calls `OnRevisionCheckedChanged` on the parent ViewModel.

---

## 3. View Layout

### 3.1 Class names

| Artefact | Name |
|---|---|
| View XAML | `TransmittalView.xaml` |
| View code-behind | `TransmittalView.xaml.cs` (standard, empty) |
| ViewModel | `TransmittalViewModel.cs` |
| Row ViewModel | `TransmittalRevisionRowViewModel.cs` |
| Enum | `DocumentDisplayMode.cs` |

### 3.2 Namespaces

```
duHastNet.DocManager.UI.Shared.Views.Transmittal
duHastNet.DocManager.UI.Shared.ViewModels.Transmittal
```

### 3.3 Layout (rows, top to bottom)

```
Row 0  — Blue header banner ("Document Manager" / "Transmittal — Revision History")
Row 1  — GlobalMessageView
Row 2  — Revisions section  (Height="2*")
Row 3  — Documents section  (Height="3*")
Row 4  — Action bar         (Export to CSV | Close)
```

Both sections are inside `Border` panels (`BorderBrush="Gray"`, `BorderThickness="1"`, `CornerRadius="3"`).

### 3.4 Navigation registration

`TransmittalView` is registered in `NavigationHostView.xaml` as a `DataTemplate` for `TransmittalViewModel`:

```xml
<DataTemplate DataType="{x:Type viewmodelstransmittal:TransmittalViewModel}">
    <localtransmittal:TransmittalView/>
</DataTemplate>
```

---

## 4. Revisions Section

### 4.1 Internal layout

```
Row 0  — Section header: "Revisions" (SemiBold, Margin 8,6,8,4)
Row 1  — Status message TextBlock (collapses when empty)
Row 2  — DynamicDataGrid (fills remaining height)
```

### 4.2 Column definitions

| `PropertyName` | `DisplayName` | `DataType` | `Width` | `IsReadOnly` |
|---|---|---|---|---|
| `IsChecked` | _(empty)_ | `typeof(bool)` | `44` | `false` |
| `RevisionDate` | `Date` | `typeof(DateTime)` | `110` | `true` |
| `RevisionDescription` | `Description` | `typeof(string)` | `400` | `true` |

Built once in `BuildRevisionColumnDefinitions()`, called from the constructor. Never rebuilt.

### 4.3 Data source

`ObservableCollection<DynamicRowData> RevisionRows` — loaded in `LoadRevisionsAsync()` on activation. Sorted newest-first by `RevisionDate` then `Id` descending.

### 4.4 Edge cases

| Condition | Behaviour |
|---|---|
| Database not ready | `RevisionsStatusMessage = "No database connected."` |
| No revisions | `RevisionsStatusMessage = "No revisions in database."` |
| Load exception | `RevisionsStatusMessage = "Error loading revisions: {message}"` |

### 4.5 `TransmittalRevisionRowViewModel`

| Property | Type | Notes |
|---|---|---|
| `RevisionId` | `int` | Internal — not displayed |
| `RevisionDate` | `DateTime` | Displayed in Date column |
| `RevisionDescription` | `string` | Displayed in Description column |
| `DocumentIds` | `IReadOnlyList<int>` | Used to filter documents in ByRevision mode |
| `IsChecked` | `bool` | `[ObservableProperty]` — fires `onCheckedChanged` callback on change |

Constructor: `(int revisionId, DateTime revisionDate, string revisionDescription, IReadOnlyList<int> documentIds, Action onCheckedChanged)`. `onCheckedChanged` validated against null.

---

## 5. Documents Section

### 5.1 Internal layout

```
Row 0  — Section header ("Documents") + mode toggle RadioButtons (right-aligned)
Row 1  — Options row: "Show inactive documents" checkbox | "Include document history" checkbox
Row 2  — Status message TextBlock (collapses when empty)
Row 3  — DynamicDataGrid (fills remaining height, IsReadOnly="True")
```

### 5.2 Mode toggle

Two `RadioButton`s bound to `IsShowAllMode` and `IsByRevisionMode` (both `Mode=TwoWay`). These are computed bool properties on the ViewModel backed by `DocumentDisplayMode` (enum). Setting either bool sets `DocumentDisplayMode`, which triggers `OnDocumentDisplayModeChanged`.

### 5.3 Static column definitions

Built once in `BuildDocumentColumnDefinitions()`, called from the constructor.

| `PropertyName` | `DisplayName` | `DataType` | `Width` | `IsReadOnly` |
|---|---|---|---|---|
| `DocumentNumber` | `Doc Number` | `string` | `160` | `true` |
| `DocumentName` | `Doc Name` | `string` | `0` (star) | `true` |
| `CurrentRevision` | `Current Rev.` | `string` | `90` | `true` |

### 5.4 Dynamic revision columns

One `DynamicColumnDefinition` per checked revision appended after the static columns:

| Field | Value |
|---|---|
| `PropertyName` | `"Rev_{RevisionId}"` |
| `DisplayName` | `"{RevisionDate:d} — {RevisionDescription}"` (truncated to 40 chars + "…") |
| `DataType` | `typeof(string)` |
| `Width` | `100` |
| `IsReadOnly` | `true` |

Managed by `RebuildDocumentColumns()` — called on every revision `IsChecked` change and after every `RebuildDocumentRows()`.

### 5.5 Data loading strategy

Documents are loaded once per activation into `_allDocuments` via `unitOfWork.Documents.GetAllAsync()`. All revision indicator data is pre-loaded into every `DynamicRowData` row at build time using `Rev_{id}` keys for every revision in `_allRevisions`. Checking/unchecking a revision only adds or removes a `DynamicColumnDefinition` — rows are never rebuilt solely for that action.

`RebuildDocumentRows()` is called on activation and whenever mode, filter, or history options change.

### 5.6 Hidden row keys

These keys are written into every `DynamicRowData` but never added to `DocumentColumnDefinitions`:

| Key constant | Purpose |
|---|---|
| `KeyIsInactive` | Drives inactive row style (grey/italic) |
| `KeyIsHistoryRow` | `true` for document history rows |
| `KeyNumberActiveFrom` | Inferred start date of historical number (string, may be empty) |
| `KeyNumberActiveTo` | Change date of historical number (string) |
| `KeyHistoryDateRangeLabel` | Formatted label e.g. `"until 2023-06-15"` |

### 5.7 Edge cases

| Condition | Mode | Behaviour |
|---|---|---|
| No documents | Both | `DocumentsStatusMessage = "No documents in database."` |
| No revisions checked | ByRevision | `"No revisions selected. Switch to 'Show All Documents' or select a revision above."` |
| No revisions exist | ByRevision | `"No revisions available. Use 'Show All Documents' instead."` |
| Checked revisions have no document IDs | ByRevision | `"The selected revision(s) have no documents assigned."` |
| Database not ready | Both | `DocumentsStatusMessage = "No database connected."` |
| Load exception | Both | `DocumentsStatusMessage = "Error loading documents: {message}"` |

### 5.8 Show Inactive Documents

`bool ShowInactiveDocuments` (default `false`). `OnShowInactiveDocumentsChanged` calls `RebuildDocumentRows()`. Filter: `ShowInactiveDocuments || d.IsActive`, applied in both Show All and ByRevision paths.

### 5.9 Include Document History

`bool IncludeDocumentHistory` (default `false`). `OnIncludeDocumentHistoryChanged` calls `RebuildDocumentRows()`. When on, `BuildHistoryRows(document)` is called after each primary document row and its results appended to `DocumentRows`.

#### Inference algorithm

The database stores `DocumentNumberHistory: Dictionary<string, DateOnly>` (key = old number, value = date number was changed away from it) and `RevisionIndicatorHistory: Dictionary<int, string>` (key = RevisionId, value = indicator). `_revisionDateLookup` maps RevisionId to RevisionDate.

1. Order `DocumentNumberHistory` entries by change date ascending. Same-date entries ordered by key as a stable fallback.
2. Reconstruct active date range: `activeFrom = previousChangedDate` (null for first entry), `activeTo = currentChangeDate`.
3. For each revision in `_allRevisions`, check if `DateOnly.FromDateTime(revision.RevisionDate)` falls within `[activeFrom, activeTo]`.
4. Populate `Rev_{id}` for matching revisions; empty string for non-matching.

History rows always have `IsInactive = true` and `IsHistoryRow = true`.

---

## 6. Action Bar

`Border` row, `Background="#F5F5F5"`, `BorderThickness="0,1,0,0"`, `BorderBrush="#CCCCCC"`, `Padding="12,8"`.

| Element | Details |
|---|---|
| Left `TextBlock` | `{Binding ExportStatusMessage}` — shows export result or empty |
| Export button | `ExportToCsvCommand`, `Background="#2196F3"`, `Foreground="White"`, `FontWeight="SemiBold"` |
| Close button | `CloseCommand` — navigates back to MergeView via `NavigationStore` |

---

## 7. Status Message Conventions

- `RevisionsStatusMessage` and `DocumentsStatusMessage` are `[ObservableProperty]` strings initialised to `string.Empty`.
- `TextBlock` visibility collapses via `Style.Trigger` when `Text == ""`.
- `Foreground="#555555"`, `FontSize="12"`, `TextWrapping="Wrap"`, `Margin="8,4,8,4"`.

---

## 8. GlobalMessageView

Row 1 of the main grid, identical to MergeView:

```xml
<Grid Grid.Row="1">
    <utilsViews:GlobalMessageView DataContext="{Binding GlobalMessageViewModel}"/>
</Grid>
```

---

## 9. ViewModel — `TransmittalViewModel`

Inherits `AppViewModelBase`, implements `IActivatable`.

### Constructor

```csharp
public TransmittalViewModel(
    NavigationStore navigationStore,
    IMessageStore messageStore,
    Func<Merge.MergeViewModel> createMergeViewModel,
    IDocManagerApi docManagerApi,
    IDialogService dialogService)
```

All five parameters validated with `ArgumentNullException.ThrowIfNull`. Column definitions built in constructor. Data loaded in `OnActivatedAsync()`.

### Observable properties

| Property | Type | Default | Notes |
|---|---|---|---|
| `RevisionRows` | `ObservableCollection<DynamicRowData>` | — | Revisions grid ItemsSource |
| `RevisionColumnDefinitions` | `ObservableCollection<DynamicColumnDefinition>` | — | Revisions grid ColumnDefinitions |
| `DocumentRows` | `ObservableCollection<DynamicRowData>` | — | Documents grid ItemsSource |
| `DocumentColumnDefinitions` | `ObservableCollection<DynamicColumnDefinition>` | — | Documents grid ColumnDefinitions |
| `DocumentDisplayMode` | `DocumentDisplayMode` | `All` | Triggers row + column rebuild |
| `IsShowAllMode` | `bool` (computed) | `true` | Bound to "Show All" RadioButton |
| `IsByRevisionMode` | `bool` (computed) | `false` | Bound to "By Revisions Only" RadioButton |
| `ShowInactiveDocuments` | `bool` | `false` | Triggers row rebuild |
| `IncludeDocumentHistory` | `bool` | `false` | Triggers row rebuild |
| `RevisionsStatusMessage` | `string` | `""` | |
| `DocumentsStatusMessage` | `string` | `""` | |
| `ExportStatusMessage` | `string` | `""` | |
| `IsBusy` | `bool` | `false` | Set during `OnActivatedAsync` |
| `GlobalMessageViewModel` | `GlobalMessageViewModel` | — | Registered child |

### Private fields

| Field | Type | Purpose |
|---|---|---|
| `_revisionViewModels` | `List<TransmittalRevisionRowViewModel>` | Tracks checked state; not bound to grid |
| `_allDocuments` | `List<Document>` | In-memory document cache |
| `_allRevisions` | `List<Revision>` | In-memory revision cache (newest-first) |
| `_revisionDateLookup` | `Dictionary<int, DateTime>` | RevisionId → RevisionDate for history inference |

### Rebuild triggers

| Trigger | Action |
|---|---|
| `OnActivatedAsync` | `LoadRevisionsAsync()` then `LoadDocumentsAsync()` (which calls `RebuildDocumentRows()`) |
| Revision `IsChecked` toggled | `RebuildDocumentRows()` (ByRevision only) + `RebuildDocumentColumns()` (always) |
| `DocumentDisplayMode` changed | `RebuildDocumentRows()` + `RebuildDocumentColumns()` |
| `ShowInactiveDocuments` changed | `RebuildDocumentRows()` |
| `IncludeDocumentHistory` changed | `RebuildDocumentRows()` |

### Commands

| Command | Action |
|---|---|
| `CloseCommand` | `_navigationStore.NavigateTo(_createMergeViewModel)` |
| `ExportToCsvCommand` | Save dialog → write `DocumentRows` to CSV via CsvHelper |

### CSV export details

Columns written: three static columns + one per visible dynamic revision column (those with `PropertyName` starting with `"Rev_"`). When `IncludeDocumentHistory` is on, three extra columns appended: `History` (Yes/blank), `Active From`, `Active To`. `ExportStatusMessage` updated on success or failure. Uses `CsvHelper` with `CsvConfiguration(CultureInfo.InvariantCulture)` and `StreamWriter`.

---

## 10. Entry Point from MergeView

`MergeViewModel` receives `Func<Transmittal.TransmittalViewModel>` as its eighth constructor parameter. `OpenTransmittalCommand` calls `_navigationStore.NavigateTo(() => _createTransmittalViewModel())`.

`NavigationHostViewModel.CreateTransmittalViewModel()` constructs the ViewModel with all five dependencies from its own fields.

---

## 11. File Structure

```
duHastNet.DocManager.UI.Shared/
├── Views/Transmittal/
│   ├── TransmittalView.xaml
│   └── TransmittalView.xaml.cs
└── ViewModels/Transmittal/
    ├── TransmittalViewModel.cs
    ├── TransmittalRevisionRowViewModel.cs
    └── DocumentDisplayMode.cs
```

**Modified files:**

- `MergeViewModel.cs` — added `createTransmittalViewModel` parameter + `OpenTransmittalCommand`
- `MergeView.xaml` — added Transmittal button to header toolbar
- `NavigationHostViewModel.cs` — added `CreateTransmittalViewModel()` factory
- `NavigationHostView.xaml` — added `TransmittalViewModel` DataTemplate
- `MergeViewModelTests.cs` / `_ExportMetData` / `_MergeFiles` / `_UpdateDataBase` — added `_mockCreateTransmittalViewModel` field and argument to all `MergeViewModel` constructor calls
