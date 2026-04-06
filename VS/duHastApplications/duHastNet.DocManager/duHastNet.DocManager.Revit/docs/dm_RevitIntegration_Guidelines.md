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
    Sets up stores (MessageStore, NavigationStore, StateStore)
    Sets up logging
    Loads UI settings
    Initialises Revit settings from RevitDataModel
    Processes document numbers
    Connects to database — happy/unhappy path resolved here
    Produces DatabaseDataModel
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
DocManagerApi (Sync Methods)
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
  - Set up stores (`MessageStore`, `NavigationStore`, `StateStore`)
  - Set up logging via `RevitDataModel`
  - Load UI settings (`UISettings`) and Revit settings (`Settings`)
  - Collect Revit data into `RevitDataModel` (sheets, revisions, document numbers)
  - Connect to database using path from `_revitSettings.DatabasePath`
  - Produce a `DatabaseDataModel` (connected with data, or disconnected with empty collections)
  - Enqueue startup errors or warnings to `MessageStore`
  - Create `RevitIntegrationViewModel` and set it as the navigation target
  - Open `MainWindow` — always opens regardless of startup failures

#### Layer 3: WPF User Interface
- **Purpose**: User interaction and data presentation
- **Responsibilities**:
  - `MainWindow` — shell window hosting `CurrentViewModel` via `MainViewModel` and `NavigationStore`
  - `RevitIntegrationView` — main UserControl with header strip, message banner, database status, navigation button, and panel content area
  - `SheetsPanelView` / `RevisionsPanelView` — panel UserControls (stub; to be built out)
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
- `Reload()` clears both collections, reconnects, repopulates in place, and updates `IsConnected`

```csharp
public partial class DatabaseDataModel : ObservableObject
{
    [ObservableProperty]
    private bool _isConnected;

    public ObservableCollection<Document> Documents { get; }
    public ObservableCollection<Revision> Revisions { get; }

    public DatabaseDataModel(bool isConnected, IList<Document> documents, IList<Revision> revisions) { ... }

    public static DatabaseDataModel CreateDisconnected() { ... }

    public void Reload(DocManagerApi docManagerApi, string databasePath, MessageStore messageStore) { ... }
}
```

**Key design decisions:**
- `DatabaseDataModel` is intentionally separate from `RevitDataModel` — clear delineation between Revit-sourced and database-sourced data
- The database path is NOT stored in `DatabaseDataModel` — it lives in `_revitSettings` and is passed at reload time
- On reload, collections are mutated in place rather than replacing the model object, so all existing bindings remain valid

### Separation of Concerns
| Data | Owner |
|---|---|
| Revit sheets, revisions, document numbers | `RevitDataModel` |
| Database documents, revisions, connection state | `DatabaseDataModel` |
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

#### Sheets Panel Controls (to be built out)
- Radio buttons for operation mode selection (Import / Update)
- DataGrid showing Revit sheets (Select, Sheet Number, Sheet Name, Current Revision, In Database, Needs Update)
- "Execute" button (performs selected operation)
- Sheet count display

#### Revisions Panel Controls (to be built out)
- DataGrid showing Revit revisions (Select, Date, Description, In Database)
- "Import Revisions" button
- Revision count display

**Mode Selection Implementation (Sheets panel):**
- Use enum `SheetOperationMode` with values: `Import`, `Update`
- Bind radio buttons to `SelectedSheetMode` property using `EnumToBooleanConverter`
- Mode change triggers sheet filtering (Import shows new sheets, Update shows matched sheets where name differs)
- Single "Execute" button performs operation based on selected mode

### Navigation Pattern

Panel switching is handled entirely within `RevitIntegrationViewModel` — the `NavigationStore` is NOT involved. `RevitIntegrationViewModel` holds both panel ViewModels as fields and exposes `CurrentPanelViewModel` as an `[ObservableProperty]`. A `NavigatePanelCommand` toggles between them. The navigation button label updates automatically via `[NotifyPropertyChangedFor(nameof(NavigationButtonLabel))]`.

Sheets panel is the default shown on startup.

### Database Refresh Pattern

After a successful write operation, a panel ViewModel raises its `RefreshRequested` event. `RevitIntegrationViewModel` handles this by calling `_databaseDataModel.Reload(...)`, which clears and repopulates the `ObservableCollection`s in place. All panel ViewModels bound to those collections update automatically. No new `DatabaseDataModel` object is created.

```
Panel command completes write
    ↓
Panel calls OnRefreshRequested()
    ↓
RevitIntegrationViewModel.OnPanelRefreshRequested()
    ↓
_databaseDataModel.Reload(_docManagerApi, databasePath, _messageStore)
    ↓
Collections cleared and repopulated in place
    ↓
ObservableCollection change notifications propagate to all bound views
```

### Startup Sequence

#### Happy Path
1. Python invokes `Main.ExecuteInternal()` passing `UIApplication`
2. `Main.cs` sets up stores, logging, UI settings, Revit settings
3. `RevitDataFactory` populates `RevitDataModel` with sheets and revisions
4. `RevitDataModel.AddFullDocumentNumber()` builds document numbers for all sheets
5. `Main.LoadDatabaseData()` connects to database, reads documents and revisions
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
2. Panel shows Revit revisions not already in the database
3. User reviews and selects revisions to import
4. User clicks "Import Revisions"
5. System validates and imports selected revisions to database
6. `RefreshRequested` raised — database collections reloaded in place
7. Panel re-evaluates which revisions are still new — list updates automatically

#### Import Sheets Workflow
1. Window opens showing Sheets panel in Import mode (default)
2. Panel shows Revit sheets NOT already in the database
3. User reviews and selects sheets to import
4. User clicks "Execute"
5. System validates and imports selected sheets as documents
6. `RefreshRequested` raised — database collections reloaded in place
7. Panel re-evaluates sheet status — imported sheets disappear from the list

#### Update Document Names Workflow
1. User selects "Update" mode via radio button in Sheets panel
2. Panel shows only matched sheets where the name differs from the database
3. User reviews and selects sheets to update
4. User clicks "Execute"
5. System updates selected document names from Revit sheet names
6. `RefreshRequested` raised — database collections reloaded in place
7. Panel re-evaluates — updated sheets disappear from the list

---

## Coding Guidelines

### 1. WPF MVVM Pattern with MVVM Community Toolkit

#### Required Pattern
All UI code MUST follow the MVVM pattern using the MVVM Community Toolkit.

All ViewModels in this project inherit from `AppViewModelBase` (not directly from `ObservableObject`):

```csharp
public partial class RevitIntegrationViewModel : AppViewModelBase { ... }
public partial class SheetsPanelViewModel : AppViewModelBase { ... }
public partial class RevisionsPanelViewModel : AppViewModelBase { ... }
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
    private readonly DocManagerApi _docManagerApi;

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

        _docManagerApi = new DocManagerApi();

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
        _databaseDataModel.Reload(_docManagerApi, _revitSettings.DatabasePath ?? string.Empty, _messageStore);
        OnPropertyChanged(nameof(IsDatabaseConnected));
    }
}
```

#### Panel ViewModel Structure
Panel ViewModels hold references to both models and the message store. They expose a `RefreshRequested` event raised after a successful write. They do NOT manage the database connection or reload — that is `RevitIntegrationViewModel`'s responsibility.

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
    }

    public event EventHandler? RefreshRequested;

    protected void OnRefreshRequested()
    {
        RefreshRequested?.Invoke(this, EventArgs.Empty);
    }
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
    _stateStore = new StateStore();

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
    _revitDataModel.AddFullDocumentNumber(_revitSettings.DocumentNumberString);

    // 8. Load database data — happy/unhappy path resolved here
    _databaseDataModel = LoadDatabaseData();

    // 9. Create ViewModel and open window
    _navigationStore.CurrentViewModel = CreateRevitIntegrationViewModel();

    var mainWindow = new MainWindow(_uiSettings)
    {
        DataContext = new MainViewModel(_navigationStore)
    };
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
        _messageStore.EnqueueMessage(
            "No database path configured. Use the setup utility to configure the database path.",
            MessageTypes.Error);
        _revitDataModel.LogMessages([("Database path is not configured.", MessageTypes.Error)]);
        return DatabaseDataModel.CreateDisconnected();
    }

    var api = new DocManagerApi();
    try
    {
        var connectionResult = api.ConnectDatabase(databasePath);
        if (!connectionResult.Success)
        {
            string errorMessage = $"Could not connect to database: {connectionResult.Message}";
            _messageStore.EnqueueMessage(errorMessage, MessageTypes.Error);
            _revitDataModel.LogMessages([(errorMessage, MessageTypes.Error)]);
            return DatabaseDataModel.CreateDisconnected();
        }

        var documents = api.GetActiveDocuments();
        var revisions = api.GetAllRevisions();

        _revitDataModel.LogMessages([
            ($"Loaded {documents.Count} document(s) from database.", MessageTypes.Information),
            ($"Loaded {revisions.Count} revision(s) from database.", MessageTypes.Information)
        ]);

        return new DatabaseDataModel(true, documents, revisions);
    }
    catch (Exception ex)
    {
        string errorMessage = $"Failed to read database: {ex.Message}";
        _messageStore.EnqueueMessage(errorMessage, MessageTypes.Error);
        _revitDataModel.LogMessages([(errorMessage, MessageTypes.Error)]);
        return DatabaseDataModel.CreateDisconnected();
    }
}
```

**Key Points:**
- All database calls happen before `mainWindow.Show()`
- Happy path: `DatabaseDataModel` created with `IsConnected = true` and populated collections
- Unhappy path: `DatabaseDataModel.CreateDisconnected()` returned with empty collections
- Window always opens; panel commands are disabled when `IsConnected` is false
- Database path comes from `_revitSettings.DatabasePath` — not from extensible storage directly
- `_databaseDataModel` is stored as a class-level field for use in `CreateRevitIntegrationViewModel()`

#### View (XAML) Structure
```xml
<!-- MainWindow.xaml — shell, registers DataTemplates -->
<Window ...>
    <Grid>
        <Grid.Resources>
            <DataTemplate DataType="{x:Type vms:RevitIntegrationViewModel}">
                <views:RevitIntegrationView/>
            </DataTemplate>
            <!-- POC kept for reference -->
            <DataTemplate DataType="{x:Type vms:PyRevitDocumentListViewModel}">
                <views:PyRevitDocumentListView/>
            </DataTemplate>
        </Grid.Resources>
        <ContentControl Content="{Binding CurrentViewModel}"/>
    </Grid>
</Window>

<!-- RevitIntegrationView.xaml — main integration UserControl -->
<UserControl ...>
    <UserControl.Resources>
        <!-- DataTemplates for panel switching — live here, not in MainWindow -->
        <DataTemplate DataType="{x:Type vms:SheetsPanelViewModel}">
            <views:SheetsPanelView/>
        </DataTemplate>
        <DataTemplate DataType="{x:Type vms:RevisionsPanelViewModel}">
            <views:RevisionsPanelView/>
        </DataTemplate>
    </UserControl.Resources>

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>  <!-- App name header -->
            <RowDefinition Height="Auto"/>  <!-- Global message banner -->
            <RowDefinition Height="Auto"/>  <!-- Database path + status -->
            <RowDefinition Height="Auto"/>  <!-- Navigation button -->
            <RowDefinition Height="*"/>     <!-- Panel content area -->
        </Grid.RowDefinitions>

        <Border Grid.Row="0" Background="#2196F3" Padding="15,10">
            <TextBlock Text="Document Manager — Revit Integration" .../>
        </Border>

        <ContentControl Grid.Row="1" Content="{Binding GlobalMessageViewModel}"/>

        <!-- Database path and connection badges (row 2) -->

        <Border Grid.Row="3" ...>
            <Button Content="{Binding NavigationButtonLabel}"
                    Command="{Binding NavigatePanelCommand}"/>
        </Border>

        <ContentControl Grid.Row="4" Content="{Binding CurrentPanelViewModel}"/>
    </Grid>
</UserControl>
```

**Required Converter (Sheets panel):**
```csharp
namespace duHastNet.DocManager.Revit.Converters
{
    public class EnumToBooleanConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            return value?.Equals(parameter) ?? false;
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            return (bool)value ? parameter : Binding.DoNothing;
        }
    }
}
```

### 3. Use Synchronous Core Functionality

#### Critical Requirement: Avoid Async in Revit Context

**IMPORTANT**: Due to Revit API threading constraints, all Document Manager API calls from the Revit integration MUST use synchronous methods.

```csharp
// ✅ CORRECT - Use synchronous DocManagerApi methods
var connectionResult = _docManagerApi.ConnectDatabase(databasePath);
var documents = _docManagerApi.GetActiveDocuments();
var revisions = _docManagerApi.GetAllRevisions();
_docManagerApi.Close();

// ❌ WRONG - Async causes threading issues in Revit
await _docManagerApi.ConnectDatabaseAsync(databasePath);
var documents = await _docManagerApi.GetActiveDocumentsAsync();
```

#### Available Synchronous Methods
```csharp
// Database operations
var connectionResult = docManagerApi.ConnectDatabase(databasePath);
var setupResult = docManagerApi.SetupDatabase(databasePath, customProperties, overwrite);
docManagerApi.Close();

// Document operations
var activeDocuments = docManagerApi.GetActiveDocuments();
var documentById = docManagerApi.GetDocumentById(documentId);
var rowsAffected = docManagerApi.UpdateDocument(document);

// Revision operations
var allRevisions = docManagerApi.GetAllRevisions();
var revisionsByDate = docManagerApi.GetRevisionsByDate(date);
var rowsAffected = docManagerApi.CreateRevision(revision);
```

### 4. Direct DocManagerApi Usage

Instantiate `DocManagerApi` directly in the ViewModel constructor — do not use dependency injection for Revit integration:

```csharp
// ✅ CORRECT
public RevitIntegrationViewModel(...)
{
    _docManagerApi = new DocManagerApi();
}
```

`RevitIntegrationViewModel` owns the single `DocManagerApi` instance used for reloads. Panel ViewModels do NOT own a `DocManagerApi` — they raise `RefreshRequested` and let `RevitIntegrationViewModel` handle the reload.

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

## Database Operations

### Key Synchronous Methods

**Connection:**
```csharp
var result = _docManagerApi.ConnectDatabase(databasePath);
if (!result.Success) { /* handle error */ }
```

**Retrieve Data:**
```csharp
var documents = _docManagerApi.GetActiveDocuments();
var document = _docManagerApi.GetDocumentById(id);
var revisions = _docManagerApi.GetAllRevisions();
```

**Create/Update:**
```csharp
var rowsAffected = _docManagerApi.CreateRevision(revision);
var rowsAffected = _docManagerApi.UpdateDocument(document);
```

**Close:**
```csharp
_docManagerApi.Close();
```

### Implementation Pattern

Key principles:
- Always check `IsDatabaseConnected` before operations (via `CanExecute` on commands)
- Wrap operations in try-catch-finally with proper error handling
- Use `MessageStore.EnqueueMessage()` for all user feedback
- Raise `RefreshRequested` after a successful write — do NOT reload inline
- Validate data before database operations

---

## Error Handling

### Standard Command Pattern
```csharp
[RelayCommand(CanExecute = nameof(CanImportRevisions))]
private void ImportRevisions()
{
    try
    {
        IsLoading = true;

        // Operation logic here
        var rowsAffected = _docManagerApi.CreateRevision(revision);

        _messageStore.EnqueueMessage(
            $"Successfully imported revision.",
            duHastNet.Utils.WPF.Stores.MessageTypes.Information);

        // Signal RevitIntegrationViewModel to reload database collections
        OnRefreshRequested();
    }
    catch (Exception ex)
    {
        _messageStore.EnqueueMessage(
            $"Error: {ex.Message}",
            duHastNet.Utils.WPF.Stores.MessageTypes.Error);
    }
    finally
    {
        IsLoading = false;
    }
}

private bool CanImportRevisions() => _databaseDataModel.IsConnected && !IsLoading;
```

---

## Python Integration

### Launching via Main.cs
```python
from duHastNet.DocManager.Revit import Main

def main(uiapp):
    try:
        entry = Main()
        entry.ExecuteInternal(uiapp, None)
    except Exception as ex:
        print("Error: " + str(ex))

# pyRevit passes the UIApplication as __revit__
main(__revit__)
```

**Key Points:**
- Python invokes `Main.ExecuteInternal()` directly, passing the Revit `UIApplication` and `None` for the data model (Main.cs creates it internally)
- All Revit data collection, database loading, and window construction happens inside `ExecuteInternal()`
- Python does not need to collect or pass any data

---

## Testing

Follow the testing guidelines in `testStyles.md` with these considerations:

**ViewModel Tests:**
- Test logic, validation, and data transformation
- Focus on ViewModel behaviour, not database operations
- Use real instances for simple tests

**Integration Tests:**
- Test database operations with real database
- Verify Create/Update/Read operations
- Test error handling with invalid data

**Example:**
```csharp
[TestFixture]
public class DocumentViewModelTests
{
    [Test]
    public void Constructor_WithValidDocument_CreatesViewModel()
    {
        var document = new Document { Id = 1, Number = "A-101", Name = "Plan" };
        var viewModel = new DocumentViewModel(document);

        Assert.That(viewModel.DisplayText, Is.EqualTo("A-101 - Plan"));
    }

    [Test]
    public void Constructor_WithNull_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => new DocumentViewModel(null));
    }
}
```

**See testStyles.md for complete testing patterns and guidelines.**

---

## File Structure

```
duHastNet.DocManager.Revit/
├── Main.cs
├── Views/
│   ├── MainWindow.xaml
│   ├── MainWindow.xaml.cs
│   ├── RevitIntegrationView.xaml          ← main integration UserControl
│   ├── RevitIntegrationView.xaml.cs
│   ├── SheetsPanelView.xaml               ← stub; to be built out
│   ├── SheetsPanelView.xaml.cs
│   ├── RevisionsPanelView.xaml            ← stub; to be built out
│   ├── RevisionsPanelView.xaml.cs
│   ├── PyRevitDocumentListView.xaml       ← POC; retained for reference
│   └── PyRevitDocumentListView.xaml.cs
├── ViewModels/
│   ├── MainViewModel.cs
│   ├── AppViewModelBase.cs
│   ├── RevitIntegrationViewModel.cs       ← main integration ViewModel
│   ├── SheetsPanelViewModel.cs            ← stub; to be built out
│   ├── RevisionsPanelViewModel.cs         ← stub; to be built out
│   └── PyRevitDocumentListViewModel.cs    ← POC; retained for reference
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
│   └── EnumToBooleanConverter.cs          ← to be added when Sheets panel is built
└── duHastNet.DocManager.Revit.csproj

pyRevit/
├── DocManager.extension/
│   └── DocManager.tab/
│       └── Revit Integration.panel/
│           └── Import Data.pushbutton/
│               └── script.py
└── lib/
    └── duHastNet.DocManager.Core.dll
    └── duHastNet.DocManager.Revit.dll
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
- ✅ All ViewModels inherit from `AppViewModelBase` (not directly from `ObservableObject`)
- ✅ Model classes needing change notification inherit from `ObservableObject` directly
- ✅ Do NOT use manual `INotifyPropertyChanged` implementations
- ✅ Use ONLY synchronous DocManagerApi methods (no async/await)
- ✅ Collect Revit data into `RevitDataModel` in `Main.cs` before window opens
- ✅ Read database path from `_revitSettings.DatabasePath` in `Main.cs`
- ✅ Connect to database and produce `DatabaseDataModel` in `Main.cs` before window opens
- ✅ `DatabaseDataModel` uses `ObservableCollection<T>` for Documents and Revisions
- ✅ On reload, clear and repopulate collections in place — do NOT replace the model object
- ✅ Panel ViewModels raise `RefreshRequested` event after successful write
- ✅ `RevitIntegrationViewModel` handles `RefreshRequested` by calling `DatabaseDataModel.Reload()`
- ✅ Window always opens regardless of startup failures — errors surface in message banner
- ✅ ViewModel receives pre-loaded data via constructor — no lazy loading
- ✅ `IsDatabaseConnected` derived from `DatabaseDataModel.IsConnected` gates all commands via `CanExecute`
- ✅ `DocManagerApi` instantiated directly in `RevitIntegrationViewModel` — panel ViewModels do NOT own one
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
- ✅ Filter items shown to users (new revisions only; new or changed sheets by mode)
- ✅ Write unit tests for ViewModels and integration tests for database operations
- ✅ Document public APIs and complex logic

---

## References

- **Test Style Guide**: testStyles.md
- **Database Tests**: databaseTests.md
- **Interface Best Practices**: InterfaceBestPractices.md
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
