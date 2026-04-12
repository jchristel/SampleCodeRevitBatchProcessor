# DocManager to Revit Integration Guidelines

## Overview
This document defines the scope, architecture, and coding standards for integrating Document Manager with Autodesk Revit through pyRevit. The integration enables bidirectional synchronization of revision and sheet data between Revit and the Document Manager database.

---

## Scope

### Integration Platform
- **Host**: pyRevit button/command
- **Entry Point**: Python script within pyRevit environment
- **UI Framework**: WPF (Windows Presentation Foundation)
- **Backend**: .NET DLLs from Document Manager Core

### Functional Requirements

The integration provides the following capabilities:

#### 1. Revit Revisions Management
- Import revisions (date, description) from Revit into Document Manager database
- View Revit revision sequences

#### 2. Revit Sheets (Documents) Management
- Import sheets from Revit into Document Manager database
- Update document names in Document Manager based on Revit sheet numbers

#### 3. Update Operations
- Update Document Manager document names from Revit sheets
- Match documents by sheet number
- Bulk update operations with validation

---

## Architecture

### Component Structure

```
pyRevit Button
    ↓
Python Script (Entry Point)
    Invokes Main.ExecuteInternal() passing UIApplication
    ↓
Main.cs (ExecuteInternal)
    Sets up stores (MessageStore, NavigationStore)
    Sets up logging
    Loads UI settings
    Initialises Revit settings from RevitDataModel
    Processes document numbers
    Connects to database — happy/unhappy path resolved here
    Produces DatabaseDataModel (including connected DocManagerApi)
    Creates RevitIntegrationViewModel
    Sets navigation store target
    Opens MainWindow
    ↓
MainWindow (shell)
    Hosts CurrentViewModel via NavigationStore/MainViewModel
    ↓
RevitIntegrationView (UserControl — navigation target)
    Header strip: app name, global message banner, database path + connection status
    Navigation button: toggles between Sheets and Revisions panels
    ContentControl: displays CurrentPanelViewModel
    ↓
SheetsPanelView / RevisionsPanelView (UserControl stubs)
    Full panel logic to be implemented in future steps
    ↓
DocManagerApi (Sync Methods) — accessed via DatabaseDataModel.Api
    ↓
SQLite Database
```

### Integration Layers

#### Layer 1: pyRevit Python Script
- **Purpose**: Entry point only — invokes Main.cs
- **Responsibilities**:
  - Initialize .NET runtime and load assemblies
  - Invoke `Main.ExecuteInternal()` passing the Revit `UIApplication`
  - Handle Revit threading context
  - Python does NOT collect or pass data — all data collection happens in `Main.cs`

#### Layer 2: Main.cs (ExecuteInternal)
- **Purpose**: Startup orchestration and pre-flight data loading
- **Responsibilities**:
  - Set up stores (`MessageStore`, `NavigationStore`)
  - Set up logging via `RevitDataModel`
  - Load UI settings (`UISettings`) and Revit settings (`Settings`)
  - Collect Revit data into `RevitDataModel` (sheets, revisions, document numbers)
  - Connect to database using path from `_revitSettings.DatabasePath`
  - Produce a `DatabaseDataModel` (connected with data, or disconnected with empty collections)
  - The connected `DocManagerApi` instance is stored inside `DatabaseDataModel` — do NOT discard it
  - Enqueue startup errors or warnings to `MessageStore`
  - Create `RevitIntegrationViewModel` and set it as the navigation target
  - Open `MainWindow` — always opens regardless of startup failures

#### Layer 3: WPF User Interface
- **Purpose**: User interaction and data presentation
- **Responsibilities**:
  - `MainWindow` — shell window hosting `CurrentViewModel` via `MainViewModel` and `NavigationStore`
  - `RevitIntegrationView` — main UserControl with header strip, message banner, database status, navigation button, and panel content area
  - `SheetsPanelView` / `RevisionsPanelView` — panel UserControls
  - Show startup messages, progress, and validation feedback
  - Disable operations when `DatabaseDataModel.IsConnected` is false

#### Layer 4: Document Manager API
- **Purpose**: Business logic and data persistence
- **Responsibilities**:
  - Database operations (CRUD) — synchronous methods only
  - Validation logic
  - Data transformation
  - Transaction management

---

## Data Models

### RevitDataModel
Carries all data sourced from the Revit model. Created in `Main.cs` before the window opens and passed into `RevitIntegrationViewModel` via constructor.

- Inherits `ObservableObject` (MVVM Community Toolkit)
- Holds `RevitSheetContainer` and `RevitRevisionContainer`
- Holds sheet number settings and logging infrastructure
- Holds startup messages generated during the startup sequence

```csharp
public partial class RevitDataModel : ObservableObject
{
    public string ModelName { get; private set; }
    public string SettingsAsJson { get; private set; }

    public void AddSheet(RevitSheet sheet) { ... }
    public void AddRevision(RevitRevision revision) { ... }
    public List<RevitSheet> GetSheets() { ... }
    public List<RevitRevision> GetRevisions() { ... }
    public void AddFullDocumentNumber(string documentNumberingJsonString) { ... }
}
```

### DatabaseDataModel
Carries all data sourced from the Document Manager database. Created in `Main.cs` via `LoadDatabaseData()` and passed into `RevitIntegrationViewModel` via constructor. The same instance is shared across all panel ViewModels for the lifetime of the window.

- Inherits `ObservableObject` (MVVM Community Toolkit)
- `Documents` and `Revisions` are `ObservableCollection<T>` so panel ViewModels bound to them update automatically when the collections change
- `IsConnected` is an `[ObservableProperty]` — flips on reload
- `CustomFieldDefinitions` is an `IReadOnlyList<CustomFieldDefinition>` — loaded once at startup, never changes while the app is running
- `Api` holds the connected `DocManagerApi` instance created in `LoadDatabaseData()`. This is the single instance used for all database reads and writes for the lifetime of the window
- `Reload()` clears both collections, reconnects, repopulates in place, updates `IsConnected`, and updates `Api`

```csharp
public partial class DatabaseDataModel : ObservableObject
{
    [ObservableProperty]
    private bool _isConnected;

    public ObservableCollection<Document> Documents { get; }
    public ObservableCollection<Revision> Revisions { get; }
    public IReadOnlyList<CustomFieldDefinition> CustomFieldDefinitions { get; }
    public DocManagerApi Api { get; private set; }

    public DatabaseDataModel(
        bool isConnected,
        IList<Document> documents,
        IList<Revision> revisions,
        IList<CustomFieldDefinition> customFieldDefinitions,
        DocManagerApi api) { ... }

    public static DatabaseDataModel CreateDisconnected() { ... }

    public void Reload(DocManagerApi docManagerApi, string databasePath, MessageStore messageStore) { ... }
}
```

**Key design decisions:**
- `DatabaseDataModel` is intentionally separate from `RevitDataModel` — clear delineation between Revit-sourced and database-sourced data
- The database path is NOT stored in `DatabaseDataModel` — it lives in `_revitSettings` and is passed at reload time
- On reload, collections are mutated in place rather than replacing the model object, so all existing bindings remain valid
- `DocManagerApi` is created in `Main.LoadDatabaseData()`, connected to the database, and stored in `DatabaseDataModel.Api`. It is NOT created in `RevitIntegrationViewModel`. Panel ViewModels access it via `_databaseDataModel.Api` — they do not own their own instance
- `CustomFieldDefinitions` are loaded once at startup alongside documents and revisions. They are not reloaded on `Reload()` because custom field schema does not change while the app is running

### Separation of Concerns
| Data | Owner |
|---|---|
| Revit sheets, revisions, document numbers | `RevitDataModel` |
| Database documents, revisions, connection state | `DatabaseDataModel` |
| Active custom field definitions | `DatabaseDataModel.CustomFieldDefinitions` |
| Connected DocManagerApi instance | `DatabaseDataModel.Api` |
| Database path | `_revitSettings.DatabasePath` (passed separately) |
| UI settings (window size, etc.) | `UISettings` |

---

## UI Design

### Main Window Layout

`MainWindow` is the shell window. It hosts `CurrentViewModel` via `MainViewModel` and `NavigationStore`. A `DataTemplate` registered in `MainWindow.xaml` maps `RevitIntegrationViewModel` to `RevitIntegrationView`.

`RevitIntegrationView` is a UserControl with five rows:

1. **App name header** — blue banner with application title
2. **Global message banner** — bound to `GlobalMessageViewModel` (sourced from `MessageStore`)
3. **Database path and connection status** — shows path from `_revitSettings`, green "Connected" or red "Not Connected" badge
4. **Navigation bar** — single button toggling between Sheets and Revisions panels
5. **Panel content area** — `ContentControl` bound to `CurrentPanelViewModel`

`DataTemplate`s for `SheetsPanelViewModel` and `RevisionsPanelViewModel` are declared in `RevitIntegrationView.xaml` resources so WPF automatically renders the correct panel view when `CurrentPanelViewModel` changes.

#### Sheets Panel Controls
- DataGrid showing ALL Revit sheets colour-coded by status (red = not in database, yellow = name differs, green = up to date)
- Checkbox column for row selection
- Count summary: Total, To import, To update, Selected
- Colour legend
- "Select All" / "Select None" buttons
- Single "Update" button (bottom right) — imports selected red rows and updates names of selected yellow rows in one pass
- When custom field definitions are present, importing red rows opens `SheetCustomPropertiesWindow` as a modal dialog first

#### Revisions Panel Controls
- DataGrid showing Revit revisions (Select, Date, Description, In Database)
- "Import Revisions" button
- Revision count display

### Navigation Pattern

Panel switching is handled entirely within `RevitIntegrationViewModel` — the `NavigationStore` is NOT involved. `RevitIntegrationViewModel` holds both panel ViewModels as fields and exposes `CurrentPanelViewModel` as an `[ObservableProperty]`. A `NavigatePanelCommand` toggles between them. The navigation button label updates automatically via `[NotifyPropertyChangedFor(nameof(NavigationButtonLabel))]`.

Sheets panel is the default shown on startup.

### Database Refresh Pattern

After a successful write operation, a panel ViewModel raises its `RefreshRequested` event. `RevitIntegrationViewModel` handles this by calling `_databaseDataModel.Reload(...)`, which clears and repopulates the `ObservableCollection`s in place. All panel ViewModels bound to those collections update automatically.

```
Panel command completes write
    ↓
Panel calls OnRefreshRequested()
    ↓
RevitIntegrationViewModel.OnPanelRefreshRequested()
    ↓
_databaseDataModel.Reload(_databaseDataModel.Api, databasePath, _messageStore)
    ↓
Collections cleared and repopulated in place
    ↓
ObservableCollection change notifications propagate to all bound views
    ↓
panelViewModel.OnDatabaseRefreshed() called to re-evaluate row statuses
```

Each panel ViewModel MUST implement a public `OnDatabaseRefreshed()` method.
`RevitIntegrationViewModel.OnPanelRefreshRequested` calls it after every reload so the
panel can re-evaluate its row-level database-status flags. Without this call, row colour
coding and command states would not update after an import or name update.

### Startup Sequence

#### Happy Path
1. Python invokes `Main.ExecuteInternal()` passing `UIApplication`
2. `Main.cs` sets up stores, logging, UI settings, Revit settings
3. `RevitDataFactory` populates `RevitDataModel` with sheets and revisions
4. `RevitDataModel.AddFullDocumentNumber()` builds document numbers for all sheets
5. `Main.LoadDatabaseData()` connects to database, reads documents, revisions, and custom field definitions; stores the connected `DocManagerApi` instance in `DatabaseDataModel`
6. `DatabaseDataModel` created with `IsConnected = true` and populated collections
7. `RevitIntegrationViewModel` created, `MainWindow` opens showing Sheets panel

#### Unhappy Path
The window always opens regardless of startup failures. Errors surface in the message banner. All operations are disabled when `DatabaseDataModel.IsConnected` is false.

| Failure | Behaviour |
|---|---|
| Database path not set in settings | Error enqueued; `DatabaseDataModel.CreateDisconnected()` returned |
| Database file not found at path | Error enqueued; `DatabaseDataModel.CreateDisconnected()` returned |
| Database read fails | Error enqueued; `DatabaseDataModel.CreateDisconnected()` returned |
| Revisions fail to load from Revit | `Result.Failed` returned; window does NOT open |
| Sheets fail to load from Revit | `Result.Failed` returned; window does NOT open |

### User Workflow

#### Import Revisions Workflow
1. Window opens showing Revisions panel (or user navigates to it)
2. Panel shows all Revit revisions colour-coded (new = actionable, already in database = greyed)
3. User reviews and selects revisions to import
4. User clicks "Import Revisions"
5. System validates and imports selected revisions to database
6. `RefreshRequested` raised — database collections reloaded in place
7. Panel re-evaluates which revisions are still new — list updates automatically

#### Import Sheets / Update Names Workflow
1. Window opens showing Sheets panel
2. Panel shows ALL Revit sheets: red (not in database), yellow (name differs), green (up to date)
3. User reviews, selects any combination of red and yellow rows
4. User clicks "Update"
5. If red rows are selected and custom field definitions exist, `SheetCustomPropertiesWindow` opens modally
6. User enters custom property values and confirms (or cancels, aborting the entire operation)
7. System imports selected red rows as new documents, then updates names of selected yellow rows
8. `RefreshRequested` raised — database collections reloaded in place; row statuses re-evaluated

---

## Coding Guidelines

### 1. WPF MVVM Pattern with MVVM Community Toolkit

#### Required Pattern
All UI code MUST follow the MVVM pattern using the MVVM Community Toolkit.

All ViewModels in this project inherit from `AppViewModelBase` (not directly from `ObservableObject`). This includes panel ViewModels, row ViewModels, and dialog ViewModels:

```csharp
public partial class RevitIntegrationViewModel : AppViewModelBase { ... }
public partial class SheetsPanelViewModel : AppViewModelBase { ... }
public partial class RevisionsPanelViewModel : AppViewModelBase { ... }
public partial class RevitSheetRowViewModel : AppViewModelBase { ... }
public partial class SheetCustomPropertiesViewModel : AppViewModelBase { ... }
```

`AppViewModelBase` is an empty abstract partial class that bridges the assembly boundary for source generators:

```csharp
public abstract partial class AppViewModelBase : ViewModelBase { }
```

Model classes that require change notification (e.g. `RevitDataModel`, `DatabaseDataModel`) inherit directly from `ObservableObject`:

```csharp
public partial class RevitDataModel : ObservableObject { ... }
public partial class DatabaseDataModel : ObservableObject { ... }
```

Do NOT use manual `INotifyPropertyChanged` implementations anywhere in this project.

#### RevitIntegrationViewModel Structure
```csharp
public partial class RevitIntegrationViewModel : AppViewModelBase
{
    private readonly RevitDataModel _revitDataModel;
    private readonly DatabaseDataModel _databaseDataModel;
    private readonly duHastNet.Utils.WPF.Stores.MessageStore _messageStore;
    private readonly duHastNet.UI.DocManagerSettingsUI.Utils.Settings _revitSettings;

    private readonly SheetsPanelViewModel _sheetsPanelViewModel;
    private readonly RevisionsPanelViewModel _revisionsPanelViewModel;

    public RevitIntegrationViewModel(
        RevitDataModel revitDataModel,
        DatabaseDataModel databaseDataModel,
        duHastNet.Utils.WPF.Stores.MessageStore messageStore,
        duHastNet.UI.DocManagerSettingsUI.Utils.Settings revitSettings)
    {
        _revitDataModel = revitDataModel ?? throw new ArgumentNullException(nameof(revitDataModel));
        _databaseDataModel = databaseDataModel ?? throw new ArgumentNullException(nameof(databaseDataModel));
        _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
        _revitSettings = revitSettings ?? throw new ArgumentNullException(nameof(revitSettings));

        // DocManagerApi is NOT created here — it lives in _databaseDataModel.Api
        _sheetsPanelViewModel = new SheetsPanelViewModel(_revitDataModel, _databaseDataModel, _messageStore);
        _revisionsPanelViewModel = new RevisionsPanelViewModel(_revitDataModel, _databaseDataModel, _messageStore);

        _sheetsPanelViewModel.RefreshRequested += OnPanelRefreshRequested;
        _revisionsPanelViewModel.RefreshRequested += OnPanelRefreshRequested;

        GlobalMessageViewModel = new GlobalMessageViewModel(_messageStore);
        _currentPanelViewModel = _sheetsPanelViewModel;
    }

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(NavigationButtonLabel))]
    private ObservableObject _currentPanelViewModel;

    public string NavigationButtonLabel =>
        CurrentPanelViewModel is SheetsPanelViewModel ? "Go to Revisions" : "Go to Sheets";

    public bool IsDatabaseConnected => _databaseDataModel.IsConnected;

    public GlobalMessageViewModel GlobalMessageViewModel { get; }

    [RelayCommand]
    private void NavigatePanel()
    {
        CurrentPanelViewModel = CurrentPanelViewModel is SheetsPanelViewModel
            ? _revisionsPanelViewModel
            : _sheetsPanelViewModel;
    }

    private void OnPanelRefreshRequested(object? sender, EventArgs e)
    {
        _databaseDataModel.Reload(
            _databaseDataModel.Api,
            _revitSettings.DatabasePath ?? string.Empty,
            _messageStore);
        OnPropertyChanged(nameof(IsDatabaseConnected));
        _sheetsPanelViewModel.OnDatabaseRefreshed();
        // Add equivalent call for RevisionsPanelViewModel when implemented.
    }

    /// <summary>
    /// Closes the database connection when the window closes so the SQLite file
    /// lock is released before the process exits.
    /// </summary>
    public override void OnClosing()
    {
        _databaseDataModel.Api.Close();
        base.OnClosing();
    }
}
```

#### Panel ViewModel Structure
Panel ViewModels hold references to both models and the message store. They expose a `RefreshRequested` event raised after a successful write. They do NOT manage the database connection or reload — that is `RevitIntegrationViewModel`'s responsibility. Database writes go through `_databaseDataModel.Api`.

Every panel ViewModel MUST implement the following pattern in full:

```csharp
public partial class SheetsPanelViewModel : AppViewModelBase
{
    private readonly RevitDataModel _revitDataModel;
    private readonly DatabaseDataModel _databaseDataModel;
    private readonly duHastNet.Utils.WPF.Stores.MessageStore _messageStore;

    public SheetsPanelViewModel(
        RevitDataModel revitDataModel,
        DatabaseDataModel databaseDataModel,
        duHastNet.Utils.WPF.Stores.MessageStore messageStore)
    {
        _revitDataModel = revitDataModel ?? throw new ArgumentNullException(nameof(revitDataModel));
        _databaseDataModel = databaseDataModel ?? throw new ArgumentNullException(nameof(databaseDataModel));
        _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));

        // Subscribe so command states re-evaluate when connection changes.
        _databaseDataModel.PropertyChanged += OnDatabaseDataModelPropertyChanged;
    }

    // ── RefreshRequested event (raised after every successful write) ──────────

    public event EventHandler? RefreshRequested;

    protected void OnRefreshRequested()
    {
        RefreshRequested?.Invoke(this, EventArgs.Empty);
    }

    // ── OnDatabaseRefreshed (called by RevitIntegrationViewModel after reload) ─

    /// <summary>
    /// Called by RevitIntegrationViewModel after DatabaseDataModel.Reload() completes.
    /// Re-evaluates every row's database-status flags and resets selections.
    /// </summary>
    public void OnDatabaseRefreshed()
    {
        // Re-evaluate each row against the refreshed collections, reset IsSelected.
        UpdateAllRowDatabaseStatus();
        UpdateCounts();
    }

    // ── IsDatabaseConnected (exposed for panel view bindings) ─────────────────

    /// <summary>
    /// Exposed on this ViewModel so the panel XAML can bind to it directly.
    /// Notified whenever DatabaseDataModel.IsConnected changes.
    /// </summary>
    public bool IsDatabaseConnected => _databaseDataModel.IsConnected;

    /// <summary>
    /// Hint text shown in the execute bar. Switches to a warning when disconnected.
    /// </summary>
    public string HintText => _databaseDataModel.IsConnected
        ? "Normal instruction text here."
        : "No database connection. Cannot perform any operations.";

    // ── PropertyChanged handler ───────────────────────────────────────────────

    private void OnDatabaseDataModelPropertyChanged(
        object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(DatabaseDataModel.IsConnected))
        {
            UpdateCounts();                             // re-evaluates all CanExecute
            OnPropertyChanged(nameof(IsDatabaseConnected));
            OnPropertyChanged(nameof(HintText));
        }
    }

    // ── CanExecute guards ─────────────────────────────────────────────────────

    private bool CanExecuteOperation()
    {
        if (!_databaseDataModel.IsConnected) return false;  // ALWAYS check this first
        if (IsBusy) return false;
        return /* at least one actionable row selected */ true;
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    public override void OnClosing()
    {
        _databaseDataModel.PropertyChanged -= OnDatabaseDataModelPropertyChanged;
        base.OnClosing();
    }

    public override void Dispose()
    {
        _databaseDataModel.PropertyChanged -= OnDatabaseDataModelPropertyChanged;
        base.Dispose();
    }

    // Database writes use _databaseDataModel.Api.GetUnitOfWorkSync()
    // Custom field definitions are read from _databaseDataModel.CustomFieldDefinitions
}
```

### 2. Main.cs Startup Pattern

#### Startup Orchestration
`Main.ExecuteInternal()` runs all pre-flight work synchronously before the window opens. The window always opens — errors surface in the message banner.

```csharp
public Result ExecuteInternal(UIApplication uiapp, Models.Revit.RevitDataModel revitDataModel)
{
    // 1. Set up stores
    _navigationStore = new NavigationStore();
    _messageStore = new MessageStore();

    // 2. Assign RevitDataModel
    _revitDataModel ??= revitDataModel;

    // 3. Set up logging
    SetupLog();

    // 4. Log startup info
    _revitDataModel.LogMessages([...]);

    // 5. Load UI settings
    _uiSettings = UISettingsUtils.LoadSettings();

    // 6. Initialise Revit settings
    _revitSettings = RevitSettingsUtils.InitialiseRevitSettings(_revitDataModel.SettingsAsJson);

    // 7. Process document numbers
    _revitDataModel.AddFullDocumentNumber(_revitSettings.DocumentNumberBuilderString);

    // 8. Load database data — happy/unhappy path resolved here
    //    The connected DocManagerApi instance is stored inside DatabaseDataModel
    _databaseDataModel = LoadDatabaseData();

    // 9. Create ViewModel and open window
    _navigationStore.CurrentViewModel = CreateRevitIntegrationViewModel();
    var mainWindow = new Views.MainWindow(_uiSettings) { DataContext = new ViewModels.MainViewModel(_navigationStore) };
    mainWindow.Show();
    return Result.Succeeded;
}
```

#### LoadDatabaseData Pattern
```csharp
private DatabaseDataModel LoadDatabaseData()
{
    string databasePath = _revitSettings?.DatabasePath ?? string.Empty;

    if (string.IsNullOrWhiteSpace(databasePath))
    {
        _messageStore.EnqueueMessage("No database path configured.", MessageTypes.Error);
        return DatabaseDataModel.CreateDisconnected();
    }

    var api = new DocManagerApi();
    try
    {
        var connectionResult = api.ConnectDatabase(databasePath);

        if (!connectionResult.Success)
        {
            _messageStore.EnqueueMessage($"Could not connect: {connectionResult.Message}", MessageTypes.Error);
            return DatabaseDataModel.CreateDisconnected();
        }

        var documents = api.GetActiveDocuments();
        var revisions = api.GetAllRevisions();
        var customFieldDefinitions = api.GetActiveCustomFieldDefinitions();

        _revitDataModel.LogMessages([
            ($"Loaded {documents.Count} document(s) from database.", MessageTypes.Information),
            ($"Loaded {revisions.Count} revision(s) from database.", MessageTypes.Information),
            ($"Loaded {customFieldDefinitions.Count} custom field definition(s) from database.", MessageTypes.Information)
        ]);

        // api is passed into DatabaseDataModel — it is NOT discarded
        return new DatabaseDataModel(true, documents, revisions, customFieldDefinitions, api);
    }
    catch (Exception ex)
    {
        _messageStore.EnqueueMessage($"Failed to read database: {ex.Message}", MessageTypes.Error);
        return DatabaseDataModel.CreateDisconnected();
    }
}
```

**Key Points:**
- All database calls happen before `mainWindow.Show()`
- The `DocManagerApi` instance (`api`) is connected and stored in `DatabaseDataModel.Api` — it is never discarded
- Happy path: `DatabaseDataModel` created with `IsConnected = true` and populated collections
- Unhappy path: `DatabaseDataModel.CreateDisconnected()` returned with empty collections and a new unconnected `DocManagerApi`
- Window always opens; panel commands are disabled when `IsConnected` is false

### 3. DocManagerApi Ownership

The single `DocManagerApi` instance is created in `Main.LoadDatabaseData()`, connected to the database, and stored in `DatabaseDataModel.Api`. It is the only instance used for all database operations for the lifetime of the window.

```
Main.LoadDatabaseData()
    Creates and connects: var api = new DocManagerApi()
    Passes to: new DatabaseDataModel(..., api)
    ↓
DatabaseDataModel.Api
    Used by: RevitIntegrationViewModel → _databaseDataModel.Reload(_databaseDataModel.Api, ...)
    Used by: SheetsPanelViewModel → _databaseDataModel.Api.GetUnitOfWorkSync()
    Used by: RevisionsPanelViewModel → _databaseDataModel.Api.GetUnitOfWorkSync()
```

- `RevitIntegrationViewModel` does NOT create a `DocManagerApi`
- Panel ViewModels do NOT own a `DocManagerApi` — they access `_databaseDataModel.Api`
- Do NOT create additional `DocManagerApi` instances anywhere in the UI layer

### 4. IsDatabaseConnected Gating

All commands that write to the database MUST check `_databaseDataModel.IsConnected` in their `CanExecute` method. This ensures the UI is fully disabled when the database is not connected (unhappy path).

```csharp
private bool CanUpdate()
{
    if (!_databaseDataModel.IsConnected) return false;  // ALWAYS first
    if (IsBusy) return false;
    return DisplayedItems != null && DisplayedItems.Any(r => r.IsSelected);
}
```

For the gating to be reactive (i.e. the button disables immediately when the connection drops rather than only on the next user interaction), the panel ViewModel MUST subscribe to `_databaseDataModel.PropertyChanged` in its constructor and call `UpdateCounts()` — which calls `NotifyCanExecuteChanged()` on all commands — whenever `IsConnected` changes:

```csharp
// In constructor:
_databaseDataModel.PropertyChanged += OnDatabaseDataModelPropertyChanged;

// Handler:
private void OnDatabaseDataModelPropertyChanged(
    object? sender, System.ComponentModel.PropertyChangedEventArgs e)
{
    if (e.PropertyName == nameof(DatabaseDataModel.IsConnected))
    {
        UpdateCounts();
        OnPropertyChanged(nameof(IsDatabaseConnected));
        OnPropertyChanged(nameof(HintText));
    }
}

// UpdateCounts must call NotifyCanExecuteChanged on all commands:
private void UpdateCounts()
{
    OnPropertyChanged(nameof(SelectedCount));
    // ... other count properties ...
    ImportCommand.NotifyCanExecuteChanged();
    SelectAllCommand.NotifyCanExecuteChanged();
    SelectNoneCommand.NotifyCanExecuteChanged();
}
```

Always unsubscribe in both `OnClosing()` and `Dispose()` to prevent memory leaks:

```csharp
public override void OnClosing()
{
    _databaseDataModel.PropertyChanged -= OnDatabaseDataModelPropertyChanged;
    base.OnClosing();
}

public override void Dispose()
{
    _databaseDataModel.PropertyChanged -= OnDatabaseDataModelPropertyChanged;
    base.Dispose();
}
```

### 4a. Row ViewModel Selection Callback Pattern

Each row ViewModel (e.g. `RevitSheetRowViewModel`, `RevitRevisionRowViewModel`) wraps one
Revit data item and exposes `IsSelected` for the checkbox column. When the user manually
ticks a checkbox, the parent panel ViewModel must re-evaluate its command can-execute states
immediately — without subscribing to `PropertyChanged` on every individual row.

The pattern is an `Action? onSelectionChanged` callback passed at construction time:

```csharp
public partial class RevitRevisionRowViewModel : AppViewModelBase
{
    private readonly Action? _onSelectionChanged;

    public RevitRevisionRowViewModel(RevitRevision revision, Action? onSelectionChanged = null)
    {
        _ = revision ?? throw new ArgumentNullException(nameof(revision));
        _onSelectionChanged = onSelectionChanged;
        // ... populate properties from revision ...
    }

    [ObservableProperty]
    private bool _isSelected;

    partial void OnIsSelectedChanged(bool value)
    {
        _onSelectionChanged?.Invoke();
    }
}
```

The panel ViewModel passes its own `UpdateCounts` method as the callback when building rows:

```csharp
var row = new RevitRevisionRowViewModel(revision, onSelectionChanged: UpdateCounts);
```

This means every manual checkbox tick immediately calls `UpdateCounts()`, which calls
`NotifyCanExecuteChanged()` on all commands — keeping the Import / Update button state
in sync without any event subscription overhead.

### 5. Domain Exceptions for Duplicate Detection

Use typed domain exceptions for duplicate detection — do NOT use `ArgumentException`:

```csharp
// ✅ CORRECT
throw new RevitRevisionDuplicateException(existingRevision, revision);
throw new RevisionOnSheetDuplicateException(existingRevisionOnSheet, revisionOnSheet);
throw new DocumentPropertyDuplicateException(existingProperty, documentProperty);

// ❌ WRONG
throw new ArgumentException($"A revision with the ID '{revision.RevitRevisionElementId}' already exists.");
```

Use the `Conflicts()` method on model objects for consistency:

```csharp
foreach (var existingRevision in _revisions)
{
    if (existingRevision.Conflicts(revision))
        throw new RevitRevisionDuplicateException(existingRevision, revision);
}
```

### 6. Constructor Validation

Apply null guards to all constructor parameters:

```csharp
public SheetsPanelViewModel(
    RevitDataModel revitDataModel,
    DatabaseDataModel databaseDataModel,
    MessageStore messageStore)
{
    _revitDataModel = revitDataModel ?? throw new ArgumentNullException(nameof(revitDataModel));
    _databaseDataModel = databaseDataModel ?? throw new ArgumentNullException(nameof(databaseDataModel));
    _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
}
```

Apply null guards and string guards to `Reload()` method parameters:

```csharp
public void Reload(DocManagerApi docManagerApi, string databasePath, MessageStore messageStore)
{
    _ = docManagerApi ?? throw new ArgumentNullException(nameof(docManagerApi));
    _ = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
    if (string.IsNullOrWhiteSpace(databasePath))
        throw new ArgumentException("Database path must not be null or whitespace.", nameof(databasePath));
    ...
}
```

### 7. Line Endings

All code files MUST use Windows line endings (CRLF).

### 8. Nullable Reference Types

Enable nullable reference types in the `.csproj`:

```xml
<Nullable>enable</Nullable>
```

Annotate all types correctly — use `?` for types that may be null. Constructor validation is the primary mechanism for enforcing non-null guarantees.

---

## File Structure

```
duHastNet.DocManager.Revit/
├── Main.cs
├── Views/
│   ├── MainWindow.xaml
│   ├── MainWindow.xaml.cs
│   ├── RevitIntegrationView.xaml
│   ├── RevitIntegrationView.xaml.cs
│   ├── SheetsPanelView.xaml
│   ├── SheetsPanelView.xaml.cs
│   ├── RevisionsPanelView.xaml
│   ├── RevisionsPanelView.xaml.cs
│   ├── SheetCustomPropertiesWindow.xaml
│   ├── SheetCustomPropertiesWindow.xaml.cs
│   ├── PyRevitDocumentListView.xaml        ← POC; retained for reference
│   └── PyRevitDocumentListView.xaml.cs
├── ViewModels/
│   ├── MainViewModel.cs
│   ├── AppViewModelBase.cs
│   ├── RevitIntegrationViewModel.cs
│   ├── SheetsPanelViewModel.cs
│   ├── RevisionsPanelViewModel.cs
│   ├── RevitSheetRowViewModel.cs
│   ├── SheetCustomPropertiesViewModel.cs
│   ├── SheetImportRowViewModel.cs
│   └── PyRevitDocumentListViewModel.cs     ← POC; retained for reference
├── Models/
│   ├── Revit/
│   │   ├── RevitDataModel.cs
│   │   ├── RevitSheetContainer.cs
│   │   └── RevitRevisionContainer.cs
│   └── Database/
│       └── DatabaseDataModel.cs
├── Utilities/
│   ├── RevitData/
│   │   ├── RevitSheet.cs
│   │   ├── RevitRevision.cs
│   │   ├── RevitRevisionOnSheet.cs
│   │   └── RevitDocumentProperty.cs
│   ├── RevitDataFactory.cs
│   ├── DocumentNumberBuilder.cs
│   ├── RevitSettings/
│   │   └── RevitSettingsUtils.cs
│   └── UISettings/
│       ├── UISettings.cs
│       └── UISettingsUtils.cs
├── Exceptions/
│   ├── RevitRevisionDuplicateException.cs
│   ├── RevisionOnSheetDuplicateException.cs
│   └── DocumentPropertyDuplicateException.cs
├── Converters/
│   └── EnumToBooleanConverter.cs
└── duHastNet.DocManager.Revit.csproj
```

---

## Deployment

### Requirements
1. pyRevit installed in Revit
2. .NET 8 or higher
3. Document Manager Core DLLs
4. Database path configured via setup utility and stored in Revit model settings (extensible storage)

### Installation Steps
1. Copy .NET DLLs to pyRevit lib folder
2. Copy Python script to pyRevit extension folder
3. Reload pyRevit in Revit
4. Run setup utility to configure database path

---

## Summary Checklist

When developing the Revit integration:

- ✅ Use WPF with MVVM pattern and MVVM Community Toolkit
- ✅ All ViewModels (including row and dialog ViewModels) inherit from `AppViewModelBase` — NOT directly from `ObservableObject`
- ✅ Model classes needing change notification inherit from `ObservableObject` directly
- ✅ Do NOT use manual `INotifyPropertyChanged` implementations
- ✅ Use ONLY synchronous DocManagerApi methods (no async/await)
- ✅ Collect Revit data into `RevitDataModel` in `Main.cs` before window opens
- ✅ Read database path from `_revitSettings.DatabasePath` in `Main.cs`
- ✅ Connect to database and produce `DatabaseDataModel` in `Main.cs` before window opens
- ✅ `DatabaseDataModel` uses `ObservableCollection<T>` for Documents and Revisions
- ✅ `DatabaseDataModel` stores the connected `DocManagerApi` instance in `Api` — do NOT discard it
- ✅ `DatabaseDataModel.CustomFieldDefinitions` is an `IReadOnlyList<CustomFieldDefinition>` loaded once at startup
- ✅ On reload, clear and repopulate collections in place — do NOT replace the model object
- ✅ Panel ViewModels raise `RefreshRequested` event after successful write
- ✅ `RevitIntegrationViewModel` handles `RefreshRequested` by calling `DatabaseDataModel.Reload()`
- ✅ Window always opens regardless of startup failures — errors surface in message banner
- ✅ ViewModel receives pre-loaded data via constructor — no lazy loading
- ✅ `IsDatabaseConnected` derived from `DatabaseDataModel.IsConnected` gates all write commands via `CanExecute`
- ✅ `DocManagerApi` owned by `DatabaseDataModel.Api` — created once in `Main.LoadDatabaseData()`, shared via `DatabaseDataModel`
- ✅ Panel ViewModels access the API via `_databaseDataModel.Api` — they do NOT own a `DocManagerApi`
- ✅ Panel switching handled within `RevitIntegrationViewModel` — `NavigationStore` not involved
- ✅ `DataTemplate`s for panel ViewModels declared in `RevitIntegrationView.xaml` resources
- ✅ Use domain exceptions for duplicate detection (not `ArgumentException`)
- ✅ Use `Conflicts()` method on model objects for duplicate checks
- ✅ Validate all constructor parameters
- ✅ Use Windows line endings (CRLF)
- ✅ Enable nullable reference types and annotate all types correctly
- ✅ Follow test style guide from testStyles.md
- ✅ Handle errors gracefully with user feedback via `MessageStore.EnqueueMessage()`
- ✅ Keep all operations on UI thread
- ✅ Validate input data before database operations
- ✅ Provide clear status messages using MessageTypes (Information, Warning, Error)
- ✅ Include `IsSelected` property on item ViewModels for user selection
- ✅ Row ViewModels accept an `Action? onSelectionChanged` callback and invoke it in `partial void OnIsSelectedChanged` so command states update on every manual tick
- ✅ Panel ViewModels subscribe to `_databaseDataModel.PropertyChanged` in constructor and unsubscribe in `OnClosing()` and `Dispose()`
- ✅ Panel ViewModels expose `IsDatabaseConnected` and `HintText` as derived properties so the panel XAML can bind directly without reaching up to `RevitIntegrationViewModel`
- ✅ Panel ViewModels implement `OnDatabaseRefreshed()` called by `RevitIntegrationViewModel` after every `Reload()` to re-evaluate row statuses
- ✅ `RevitIntegrationViewModel.OnClosing()` calls `_databaseDataModel.Api.Close()` to release the SQLite file lock when the window closes
- ✅ Write unit tests for ViewModels and integration tests for database operations
- ✅ Document public APIs and complex logic

---

## References

- **Constructor Validation**: ConstructorValidationBestPractices.md
- **MVVM Community Toolkit**: https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/
- **pyRevit Documentation**: https://pyrevitlabs.notion.site/
- **Revit API**: https://www.revitapidocs.com/

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-26 | Initial | Initial guideline document created |
| 1.1 | 2026-03-22 | Update | Revit data collected by Python and passed via constructor; database connection and existing data read in Main.cs before window opens; happy/unhappy path startup sequence defined; ViewModel receives all data at construction time; IsDatabaseConnected gates all commands |
| 1.2 | 2026-04-06 | Update | Architecture updated to reflect implemented design: RevitDataModel and DatabaseDataModel as separate data carriers; DatabaseDataModel uses ObservableCollections with in-place Reload(); RevitIntegrationViewModel owns panel switching and refresh cycle; MainWindow shell with NavigationStore; RevitIntegrationView UserControl with five-row layout; SheetsPanelViewModel and RevisionsPanelViewModel stubs with RefreshRequested event; AppViewModelBase required for all ViewModels; domain exceptions for duplicate detection; POC view retained for reference |
| 1.3 | 2026-04-12 | Update | DocManagerApi ownership moved to DatabaseDataModel.Api — created in Main.LoadDatabaseData() and passed into DatabaseDataModel constructor; RevitIntegrationViewModel no longer creates DocManagerApi; panel ViewModels access API via _databaseDataModel.Api; CustomFieldDefinitions added to DatabaseDataModel as IReadOnlyList loaded once at startup; AppViewModelBase requirement extended to all ViewModels including row and dialog ViewModels; IsDatabaseConnected gating requirement clarified; Sheets panel design updated to show all sheets with colour coding and single Update button; StateStore removed from Main.cs |
| 1.4 | 2026-04-12 | Update | Panel ViewModel pattern fully documented: PropertyChanged subscription for reactive IsDatabaseConnected gating, OnDatabaseRefreshed() public method required on all panel ViewModels, row ViewModel onSelectionChanged callback pattern, IsDatabaseConnected and HintText exposed as derived properties on panel ViewModels; RevitIntegrationViewModel.OnClosing() closes database connection via _databaseDataModel.Api.Close(); Section 4a added documenting row ViewModel callback pattern |
