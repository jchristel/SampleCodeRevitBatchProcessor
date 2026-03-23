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
    â†"
Python Script (Entry Point)
    Reads database path from Revit extensible storage
    Collects sheets and revisions via Revit API
    â†"
Main.cs (ExecuteInternal)
    Connects to database (happy/unhappy path handled here)
    Reads existing documents and revisions from database
    Compares Revit data against database data
    Enqueues startup messages (errors/warnings)
    â†"
WPF Window Constructor
    Receives: revit sheets, revit revisions, database path,
              existing documents, existing revisions, message store
    â†"
WPF UI (MVVM Pattern)
    Presents filtered results (new/changed items)
    â†"
DocManagerApi (Sync Methods)
    â†"
SQLite Database
```

### Integration Layers

#### Layer 1: pyRevit Python Script
- **Purpose**: Entry point and Revit API data collection
- **Responsibilities**:
  - Initialize .NET runtime and load assemblies
  - Read database path from Revit extensible storage
  - Access Revit API to collect sheet and revision data
  - Invoke `Main.ExecuteInternal()` passing the Revit application context
  - Handle Revit threading context

#### Layer 2: Main.cs (ExecuteInternal)
- **Purpose**: Startup orchestration and pre-flight data loading
- **Responsibilities**:
  - Set up stores (`MessageStore`, etc.)
  - Connect to database using path from extensible storage
  - Read existing documents and revisions from database (synchronous)
  - Compare Revit data against database data to determine new/changed items
  - Enqueue startup errors or warnings to `MessageStore` (happy/unhappy path)
  - Pass all collected data into the WPF window constructor
  - Open the WPF window — window always opens, errors surface in the message banner

#### Layer 3: WPF User Interface
- **Purpose**: User interaction and data presentation
- **Responsibilities**:
  - Display pre-filtered Revit revisions and sheets (new or changed items only)
  - Provide import/update controls
  - Show startup messages, progress, and validation feedback
  - Handle user commands
  - Disable operations if database connection failed at startup

#### Layer 4: Document Manager API
- **Purpose**: Business logic and data persistence
- **Responsibilities**:
  - Database operations (CRUD)
  - Validation logic
  - Data transformation
  - Transaction management

---

## UI Design

### Main Window Layout

The WPF interface is divided into two distinct functional areas:

#### Area 1: Revisions Panel
- **Purpose**: Manage Revit revisions
- **Controls**:
  - DataGrid showing Revit revisions (Select, Date, Description)
  - "Import Revisions" button
  - Revision count display
  - Selection controls for filtering

#### Area 2: Sheets (Documents) Panel
- **Purpose**: Manage Revit sheets
- **Controls**:
  - Radio buttons for operation mode selection (Import / Update)
  - DataGrid showing Revit sheets (Select, Sheet Number, Sheet Name, Current Revision)
  - "Execute" button (performs selected operation)
  - Sheet count display
  - Filter and search controls

**Mode Selection Implementation:**
- Use enum `SheetOperationMode` with values: Import, Update
- Bind radio buttons to `SelectedSheetMode` property using `EnumToBooleanConverter`
- Mode change triggers sheet filtering (Import shows new sheets, Update shows existing)
- Single "Execute" button performs operation based on selected mode

### Startup Sequence

#### Happy Path
1. Python reads database path from Revit extensible storage
2. Python collects sheets and revisions from Revit API
3. `Main.ExecuteInternal()` connects to database successfully
4. Existing documents and revisions are read from database
5. Revit data is compared against database data — new/changed items identified
6. WPF window opens with filtered results ready for user action

#### Unhappy Path
The window always opens regardless of startup failures. Errors surface in the message banner.

| Failure | Behaviour |
|---|---|
| Database path not set | Error enqueued; window opens with all operations disabled |
| Database file not found at path | Error enqueued; window opens with all operations disabled |
| Database read fails | Error enqueued; window opens with all operations disabled |

### User Workflow

#### Import Revisions Workflow
1. Window opens with Revit revisions not already in the database pre-loaded
2. User reviews revision list and checks revisions to import
3. User clicks "Import Revisions"
4. System validates and imports selected revisions to database
5. User receives success/failure feedback

#### Import Sheets Workflow
1. Window opens with sheet data already collected
2. User navigates to Sheets panel and selects "Import" mode via radio button
3. System displays Revit sheets NOT already in the database
4. User reviews and checks sheets to import
5. User clicks "Execute"
6. System validates and imports selected sheets as documents
7. User receives success/failure feedback

#### Update Document Names Workflow
1. Window opens with sheet data already collected
2. User navigates to Sheets panel and selects "Update" mode via radio button
3. System displays only matched sheets where the name differs from the database
4. User reviews and checks sheets to update
5. User clicks "Execute"
6. System updates selected document names from Revit sheet names
7. User receives update summary (matched, updated, errors)

---

## Coding Guidelines

### 1. WPF MVVM Pattern with MVVM Community Toolkit

#### Required Pattern
All UI code MUST follow the MVVM (Model-View-ViewModel) pattern using the MVVM Community Toolkit.

#### ViewModel Structure
```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.ViewModels;

public partial class RevitIntegrationViewModel : ObservableObject
{
    private readonly DocManagerApi _docManagerApi;
    private readonly IMessageStore _messageStore;
    private readonly IList<RevisionData> _revitRevisions;
    private readonly IList<SheetData> _revitSheets;

    public RevitIntegrationViewModel(
        IMessageStore messageStore,
        IList<RevisionData> revitRevisions,
        IList<SheetData> revitSheets,
        IList<Revision> existingRevisions,
        IList<Document> existingDocuments,
        bool isDatabaseConnected)
    {
        _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
        _revitRevisions = revitRevisions ?? throw new ArgumentNullException(nameof(revitRevisions));
        _revitSheets = revitSheets ?? throw new ArgumentNullException(nameof(revitSheets));
        _docManagerApi = new DocManagerApi();
        IsDatabaseConnected = isDatabaseConnected;

        if (isDatabaseConnected)
        {
            LoadRevisions(existingRevisions);
            LoadSheets(existingDocuments);
        }
    }

    [ObservableProperty]
    private ObservableCollection<RevisionViewModel> _revisions = new();

    [ObservableProperty]
    private ObservableCollection<SheetViewModel> _sheets = new();

    [ObservableProperty]
    private SheetOperationMode _selectedSheetMode = SheetOperationMode.Import;

    [ObservableProperty]
    private bool _isLoading = false;

    [ObservableProperty]
    private bool _isDatabaseConnected = false;

    // Property changed handler for mode selection
    partial void OnSelectedSheetModeChanged(SheetOperationMode value)
    {
        FilterSheets();
        _messageStore.EnqueueMessage(
            value == SheetOperationMode.Import
                ? "Mode: Import new sheets"
                : "Mode: Update existing sheet names",
            MessageTypes.Information,
            dismissAfterSeconds: 3);
    }

    [RelayCommand]
    private void ImportRevisions() { /* Implementation */ }

    [RelayCommand]
    private void ExecuteSheetOperation()
    {
        if (SelectedSheetMode == SheetOperationMode.Import)
            ImportSheets();
        else
            UpdateDocumentNames();
    }

    private void LoadRevisions(IList<Revision> existingRevisions)
    {
        // Filter to revisions not already in the database
        foreach (var revit in _revitRevisions)
        {
            if (!existingRevisions.Any(r => r.Date == revit.Date && r.Description == revit.Description))
                Revisions.Add(new RevisionViewModel(revit));
        }
    }

    private void LoadSheets(IList<Document> existingDocuments)
    {
        FilterSheets(existingDocuments);
    }

    private void FilterSheets(IList<Document>? existingDocuments = null)
    {
        // Filtering logic depends on selected mode — Import shows new sheets,
        // Update shows matched sheets where name has changed
    }
}
```

**Key Points:**
- Constructor receives Revit data, existing database data, and connection state from `Main.cs`
- `IsDatabaseConnected` gates all operations — commands are disabled if startup failed
- Filtering of revisions and sheets happens at construction time, not lazily
- `IMessageStore` receives per-operation feedback; startup messages are enqueued before the window opens
- Single `ExecuteSheetOperation` command handles both Import and Update

### 2. Main.cs Startup Pattern

#### Startup Orchestration
`Main.ExecuteInternal()` runs all pre-flight work synchronously on the Revit API thread before the window opens. The window always opens — errors surface in the message banner rather than blocking launch.

```csharp
public Result ExecuteInternal(UIApplication uiapp)
{
    _messageStore = new MessageStore();

    // Read database path from extensible storage (handled elsewhere)
    string databasePath = ReadDatabasePathFromExtensibleStorage(uiapp.ActiveUIDocument.Document);

    // Collect Revit data on the API thread
    var revitSheets = CollectRevitSheets(uiapp.ActiveUIDocument.Document);
    var revitRevisions = CollectRevitRevisions(uiapp.ActiveUIDocument.Document);

    // Connect to database and read existing data
    bool isDatabaseConnected = false;
    IList<Revision> existingRevisions = new List<Revision>();
    IList<Document> existingDocuments = new List<Document>();

    if (string.IsNullOrEmpty(databasePath))
    {
        _messageStore.EnqueueMessage(
            "No database path configured. Use the setup utility to configure the database.",
            MessageTypes.Error);
    }
    else
    {
        (isDatabaseConnected, existingRevisions, existingDocuments) =
            LoadDatabaseData(databasePath);
    }

    // Open window — always opens regardless of startup failures
    var window = new RevitIntegrationWindow(
        _messageStore,
        revitRevisions,
        revitSheets,
        existingRevisions,
        existingDocuments,
        isDatabaseConnected);

    window.Show();
    return Result.Succeeded;
}

private (bool connected, IList<Revision> revisions, IList<Document> documents)
    LoadDatabaseData(string databasePath)
{
    var api = new DocManagerApi();
    try
    {
        var connectionResult = api.ConnectDatabase(databasePath);
        if (!connectionResult.Success)
        {
            _messageStore.EnqueueMessage(
                $"Could not connect to database: {connectionResult.Message}",
                MessageTypes.Error);
            return (false, new List<Revision>(), new List<Document>());
        }

        var revisions = api.GetAllRevisions();
        var documents = api.GetAllDocuments();

        return (true, revisions, documents);
    }
    catch (Exception ex)
    {
        _messageStore.EnqueueMessage(
            $"Failed to read database: {ex.Message}",
            MessageTypes.Error);
        return (false, new List<Revision>(), new List<Document>());
    }
}
```

**Key Points:**
- All database and Revit API calls happen before `window.Show()`
- Happy path: database connects and data reads → `isDatabaseConnected = true`, data passed in
- Unhappy path: any failure → error enqueued, `isDatabaseConnected = false`, empty lists passed in
- Window always opens; the ViewModel disables operations when `isDatabaseConnected` is false
- Database path comes from extensible storage — no file-based settings required
- User-specific settings are reserved for future use

#### View (XAML) Structure
```xml
<Window x:Class="duHastNet.DocManager.Revit.Views.RevitIntegrationView"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:vm="clr-namespace:duHastNet.DocManager.Revit.ViewModels"
        xmlns:converters="clr-namespace:duHastNet.DocManager.Revit.Converters">
    <Window.DataContext>
        <vm:RevitIntegrationViewModel/>
    </Window.DataContext>
    
    <Window.Resources>
        <converters:EnumToBooleanConverter x:Key="EnumToBooleanConverter"/>
    </Window.Resources>
    
    <Grid>
        <!-- Revisions Panel -->
        <!-- Sheets Panel with Mode Selection -->
        <GroupBox Header="Sheets (Documents)">
            <Grid>
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                    <RowDefinition Height="Auto"/>
                </Grid.RowDefinitions>
                
                <!-- Mode Selection -->
                <StackPanel Grid.Row="0" Orientation="Horizontal" Margin="5">
                    <TextBlock Text="Operation Mode:" Margin="0,0,10,0"/>
                    <RadioButton Content="Import New Sheets" 
                                 IsChecked="{Binding SelectedSheetMode, 
                                             Converter={StaticResource EnumToBooleanConverter}, 
                                             ConverterParameter={x:Static vm:SheetOperationMode.Import}}"
                                 Margin="0,0,20,0"/>
                    <RadioButton Content="Update Sheet Names" 
                                 IsChecked="{Binding SelectedSheetMode, 
                                             Converter={StaticResource EnumToBooleanConverter}, 
                                             ConverterParameter={x:Static vm:SheetOperationMode.Update}}"/>
                </StackPanel>
                
                <!-- DataGrid -->
                <DataGrid Grid.Row="1" ItemsSource="{Binding Sheets}" Margin="5"/>
                
                <!-- Execute Button -->
                <Button Grid.Row="2" Content="Execute" 
                        Command="{Binding ExecuteSheetOperationCommand}" 
                        HorizontalAlignment="Right" Margin="5"/>
            </Grid>
        </GroupBox>
    </Grid>
</Window>
```

**Required Converter:**
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

#### Use Sync API Methods
```csharp
// ✅ CORRECT - Use synchronous DocManagerApi methods
public class RevitIntegrationViewModel : ObservableObject
{
    private readonly DocManagerApi _docManagerApi;
    
    [RelayCommand]
    private void LoadDocuments()
    {
        try
        {
            IsLoading = true;
            StatusMessage = "Loading documents...";
            
            // Connect to database using synchronous method
            var connectionResult = _docManagerApi.ConnectDatabase(DatabasePath);
            
            if (!connectionResult.Success)
            {
                StatusMessage = $"Failed to connect: {connectionResult.Message}";
                return;
            }
            
            // Get documents using synchronous method
            var documents = _docManagerApi.GetActiveDocuments();
            
            // Update UI
            foreach (var doc in documents)
            {
                Documents.Add(new DocumentViewModel(doc));
            }
            
            StatusMessage = $"Loaded {documents.Count} documents successfully";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }
}
```

#### Do NOT Use Async Methods
```csharp
// ❌ WRONG - Async causes threading issues in Revit
[RelayCommand]
private async Task LoadDocumentsAsync()
{
    // This will cause threading exceptions in Revit!
    await _docManagerApi.ConnectDatabaseAsync(databasePath);
    var documents = await _docManagerApi.GetActiveDocumentsAsync();
}
```

#### DocManagerApi Synchronous Methods

The DocManagerApi provides synchronous methods that can be called directly without casting to sync interfaces:

```csharp
// Available synchronous methods on DocManagerApi
var docManagerApi = new DocManagerApi();

// Database operations
var connectionResult = docManagerApi.ConnectDatabase(databasePath);
var setupResult = docManagerApi.SetupDatabase(databasePath, customProperties, overwrite);
docManagerApi.Close();

// Document operations
var activeDocuments = docManagerApi.GetActiveDocuments();
var allDocuments = docManagerApi.GetAllDocuments();
var documentById = docManagerApi.GetDocumentById(documentId);

// Revision operations  
var allRevisions = docManagerApi.GetAllRevisions();
var revisionsByDate = docManagerApi.GetRevisionsByDate(date);
```

**Important Notes:**
- All methods shown above are synchronous and safe for Revit context
- No async/await keywords are used
- No threading issues will occur
- These are the methods demonstrated in the PyRevit proof of concept

### 4. Direct DocManagerApi Usage

#### Instantiation Pattern
For PyRevit/Revit integration, instantiate DocManagerApi directly in the ViewModel constructor:

```csharp
// ✅ CORRECT - Direct instantiation for Revit integration
public RevitIntegrationViewModel()
{
    _docManagerApi = new DocManagerApi();
    Documents = new ObservableCollection<DocumentViewModel>();
}
```

**Why this pattern for Revit integration:**
- Avoids complexity of dependency injection in PyRevit context
- Ensures synchronous operation throughout
- Matches the proof of concept implementation
- Simpler for Python to .NET interop

**Note:** For standalone WPF applications (non-Revit), continue using interface-based dependency injection as per project standards.

### 5. Constructor Validation

Apply constructor validation for any injected dependencies:

```csharp
public DocumentViewModel(Document document)
{
    // Validate constructor parameters
    _document = document ?? throw new ArgumentNullException(nameof(document));
}
```

**Note:** For ViewModels using parameterless constructors (like the PyRevit proof of concept), validation is applied when assigning properties or working with external data.

### 6. Line Endings

All code files MUST use Windows line endings (CRLF) for consistency with the Document Manager project.

### 7. Nullable Reference Types

The project MUST enable nullable reference types in the `.csproj` file:

```xml
<!-- Enable nullable reference types -->
<Nullable>enable</Nullable>
```

This means all code must correctly annotate nullability — use `?` for types that may be null and ensure non-nullable references are always initialised. Constructor validation (see section 5) is the primary mechanism for enforcing non-null guarantees on injected dependencies.

---

## Data Model

### Sheet Operation Mode Enum
```csharp
public enum SheetOperationMode
{
    Import,
    Update
}
```

### Revision Model
```csharp
public class RevisionViewModel : ObservableObject
{
    [ObservableProperty]
    private DateTime _date;
    
    [ObservableProperty]
    private string _description = string.Empty;
    
    [ObservableProperty]
    private bool _isSelected = false;
    
    public Revision ToRevision()
    {
        return new Revision
        {
            Date = Date,
            Description = Description
        };
    }
}
```

### Sheet Model
```csharp
public class SheetViewModel : ObservableObject
{
    [ObservableProperty]
    private string _sheetNumber = string.Empty;
    
    [ObservableProperty]
    private string _sheetName = string.Empty;
    
    [ObservableProperty]
    private string _currentRevision = string.Empty;
    
    [ObservableProperty]
    private bool _isSelected = false;
    
    public Document ToDocument()
    {
        return new Document
        {
            Number = SheetNumber,
            Name = SheetName,
            Revision = CurrentRevision
        };
    }
}
```

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
var allDocuments = _docManagerApi.GetAllDocuments();
var document = _docManagerApi.GetDocumentById(id);
var revisions = _docManagerApi.GetAllRevisions();
```

**Create/Update:**
```csharp
var result = _docManagerApi.CreateDocument(document);  // Returns affected rows
var result = _docManagerApi.CreateRevision(revision);
var result = _docManagerApi.UpdateDocument(document);
```

**Close:**
```csharp
_docManagerApi.Close();
```

### Implementation Pattern

**See the Complete Proof of Concept Example below for full implementation details.**

Key principles:
- Always check `IsDatabaseConnected` before operations
- Wrap operations in try-catch-finally with proper error handling
- Use `IsLoading` property to manage UI state
- Update `StatusMessage` for user feedback
- Validate data before database operations
- Filter items based on operation mode (Import/Update)

---

## Python Integration

### Loading .NET Assemblies
```python
import clr

# Add WPF references
clr.AddReference('PresentationFramework')
clr.AddReference('PresentationCore')
clr.AddReference('WindowsBase')

# Add DocManager DLLs
clr.AddReferenceToFileAndPath(r"C:\path\to\duHastNet.DocManager.Core.dll")
clr.AddReferenceToFileAndPath(r"C:\path\to\duHastNet.DocManager.Revit.dll")

from duHastNet.DocManager.Revit import DocManagerMain
```

### Launching via Main.cs
```python
from duHastNet.DocManager.Revit import DocManagerMain

def main(uiapp):
    try:
        entry = DocManagerMain()
        entry.ExecuteInternal(uiapp)
    except Exception as ex:
        print("Error: " + str(ex))

# pyRevit passes the UIApplication as __revit__
main(__revit__)
```

**Key Points:**
- Python invokes `DocManagerMain.ExecuteInternal()` directly, passing the Revit `UIApplication`
- All Revit data collection, database loading, and window construction happens inside `ExecuteInternal()`
- Python does not need to collect or pass any data itself — `Main.cs` handles the full startup sequence

---

## Complete Proof of Concept Example

The proof of concept demonstrates the full startup sequence: Revit data collected in Python, database loaded in `Main.cs`, everything passed into the window constructor.

### Main.cs (DocManagerMain.cs)
```csharp
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Revit.Views;
using duHastNet.DocManager.UI.Shared.Stores;

namespace duHastNet.DocManager.Revit
{
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class DocManagerMain : IExternalCommand
    {
        private MessageStore _messageStore;

        static DocManagerMain()
        {
            AppDomain.CurrentDomain.AssemblyResolve += AssemblyResolver.ResolveAssembly;
        }

        public Result ExecuteInternal(UIApplication uiapp)
        {
            _messageStore = new MessageStore();

            var doc = uiapp.ActiveUIDocument.Document;

            // Read database path from extensible storage (handled elsewhere)
            string databasePath = ReadDatabasePathFromExtensibleStorage(doc);

            // Collect Revit data on the API thread before window opens
            var revitSheets = CollectRevitSheets(doc);
            var revitRevisions = CollectRevitRevisions(doc);

            // Connect to database and read existing data
            bool isDatabaseConnected = false;
            IList<Revision> existingRevisions = new List<Revision>();
            IList<Document> existingDocuments = new List<Document>();

            if (string.IsNullOrEmpty(databasePath))
            {
                _messageStore.EnqueueMessage(
                    "No database path configured. Use the setup utility to configure the database.",
                    MessageTypes.Error);
            }
            else
            {
                (isDatabaseConnected, existingRevisions, existingDocuments) =
                    LoadDatabaseData(databasePath);
            }

            // Window always opens regardless of startup failures
            var window = new RevitIntegrationWindow(
                _messageStore,
                revitRevisions,
                revitSheets,
                existingRevisions,
                existingDocuments,
                isDatabaseConnected);

            window.Show();
            return Result.Succeeded;
        }

        private (bool connected, IList<Revision> revisions, IList<DocManagerDocument> documents)
            LoadDatabaseData(string databasePath)
        {
            var api = new DocManagerApi();
            try
            {
                var connectionResult = api.ConnectDatabase(databasePath);
                if (!connectionResult.Success)
                {
                    _messageStore.EnqueueMessage(
                        $"Could not connect to database: {connectionResult.Message}",
                        MessageTypes.Error);
                    return (false, new List<Revision>(), new List<DocManagerDocument>());
                }

                var revisions = api.GetAllRevisions();
                var documents = api.GetAllDocuments();

                return (true, revisions, documents);
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Failed to read database: {ex.Message}",
                    MessageTypes.Error);
                return (false, new List<Revision>(), new List<DocManagerDocument>());
            }
        }

        private string ReadDatabasePathFromExtensibleStorage(Autodesk.Revit.DB.Document doc)
        {
            // Implementation handled elsewhere
            return string.Empty;
        }

        private IList<SheetData> CollectRevitSheets(Autodesk.Revit.DB.Document doc)
        {
            // Collect sheets via Revit API
            return new List<SheetData>();
        }

        private IList<RevisionData> CollectRevitRevisions(Autodesk.Revit.DB.Document doc)
        {
            // Collect revisions via Revit API
            return new List<RevisionData>();
        }

        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            return ExecuteInternal(commandData.Application);
        }
    }
}
```

### ViewModel (RevitIntegrationViewModel.cs)
```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.ViewModels
{
    public partial class RevitIntegrationViewModel : ObservableObject
    {
        private readonly DocManagerApi _docManagerApi;
        private readonly IMessageStore _messageStore;
        private readonly IList<RevisionData> _revitRevisions;
        private readonly IList<SheetData> _revitSheets;

        public RevitIntegrationViewModel(
            IMessageStore messageStore,
            IList<RevisionData> revitRevisions,
            IList<SheetData> revitSheets,
            IList<Revision> existingRevisions,
            IList<DocManagerDocument> existingDocuments,
            bool isDatabaseConnected)
        {
            _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
            _revitRevisions = revitRevisions ?? throw new ArgumentNullException(nameof(revitRevisions));
            _revitSheets = revitSheets ?? throw new ArgumentNullException(nameof(revitSheets));
            _docManagerApi = new DocManagerApi();
            IsDatabaseConnected = isDatabaseConnected;

            if (isDatabaseConnected)
            {
                LoadRevisions(existingRevisions);
                LoadSheets(existingDocuments);
            }
        }

        [ObservableProperty]
        private ObservableCollection<RevisionViewModel> _revisions = new();

        [ObservableProperty]
        private ObservableCollection<SheetViewModel> _sheets = new();

        [ObservableProperty]
        private SheetOperationMode _selectedSheetMode = SheetOperationMode.Import;

        [ObservableProperty]
        private bool _isLoading = false;

        [ObservableProperty]
        private bool _isDatabaseConnected = false;

        partial void OnSelectedSheetModeChanged(SheetOperationMode value)
        {
            FilterSheets();
            _messageStore.EnqueueMessage(
                value == SheetOperationMode.Import
                    ? "Mode: Import new sheets"
                    : "Mode: Update existing sheet names",
                MessageTypes.Information,
                dismissAfterSeconds: 3);
        }

        [RelayCommand(CanExecute = nameof(CanImportRevisions))]
        private void ImportRevisions() { /* Implementation */ }

        private bool CanImportRevisions() => IsDatabaseConnected && !IsLoading;

        [RelayCommand(CanExecute = nameof(CanExecuteSheetOperation))]
        private void ExecuteSheetOperation()
        {
            if (SelectedSheetMode == SheetOperationMode.Import)
                ImportSheets();
            else
                UpdateDocumentNames();
        }

        private bool CanExecuteSheetOperation() => IsDatabaseConnected && !IsLoading;

        private void LoadRevisions(IList<Revision> existingRevisions)
        {
            foreach (var revit in _revitRevisions)
            {
                if (!existingRevisions.Any(r => r.Date == revit.Date && r.Description == revit.Description))
                    Revisions.Add(new RevisionViewModel(revit));
            }
        }

        private void LoadSheets(IList<DocManagerDocument> existingDocuments)
        {
            FilterSheets(existingDocuments);
        }

        private void FilterSheets(IList<DocManagerDocument>? existingDocuments = null)
        {
            // Import mode: show sheets not in database
            // Update mode: show matched sheets where name differs
        }

        private void ImportSheets() { /* Implementation */ }
        private void UpdateDocumentNames() { /* Implementation */ }
    }
}
```

### Window Host (RevitIntegrationWindow.cs)
```csharp
using System.Windows;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.Revit.ViewModels;
using duHastNet.DocManager.Revit.Views;

namespace duHastNet.DocManager.Revit
{
    public class RevitIntegrationWindow : Window
    {
        public RevitIntegrationWindow(
            IMessageStore messageStore,
            IList<RevisionData> revitRevisions,
            IList<SheetData> revitSheets,
            IList<Revision> existingRevisions,
            IList<DocManagerDocument> existingDocuments,
            bool isDatabaseConnected)
        {
            Title = "Document Manager - Revit Integration";
            Width = 1000;
            Height = 600;
            WindowStartupLocation = WindowStartupLocation.CenterScreen;

            var viewModel = new RevitIntegrationViewModel(
                messageStore,
                revitRevisions,
                revitSheets,
                existingRevisions,
                existingDocuments,
                isDatabaseConnected);

            Content = new RevitIntegrationView { DataContext = viewModel };
        }
    }
}
```

### Python Script (script.py)
```python
# -*- coding: utf-8 -*-
import clr
import sys

# Add WPF references
clr.AddReference('PresentationFramework')
clr.AddReference('PresentationCore')
clr.AddReference('WindowsBase')
clr.AddReference('System.Xaml')

# Add DocManager DLL references
doc_manager_core_path = r"C:\path\to\duHastNet.DocManager.Core.dll"
doc_manager_revit_path = r"C:\path\to\duHastNet.DocManager.Revit.dll"
clr.AddReferenceToFileAndPath(doc_manager_core_path)
clr.AddReferenceToFileAndPath(doc_manager_revit_path)

from Autodesk.Revit.UI import UIApplication
from duHastNet.DocManager.Revit import DocManagerMain

def main(uiapp):
    try:
        entry = DocManagerMain()
        entry.ExecuteInternal(uiapp)
    except Exception as ex:
        print("Error: " + str(ex))

# pyRevit passes the UIApplication as __revit__
main(__revit__)
```

**Key Patterns Demonstrated:**
1. ✅ Revit data collected in Python/Main.cs before window opens
2. ✅ Database path read from extensible storage (stub shown)
3. ✅ Database connection and read in `Main.cs`, not in the ViewModel
4. ✅ Happy path: data passed in, `isDatabaseConnected = true`
5. ✅ Unhappy path: errors enqueued, `isDatabaseConnected = false`, window still opens
6. ✅ ViewModel receives all data via constructor — no lazy loading
7. ✅ `CanExecute` guards on commands enforce `IsDatabaseConnected`
8. ✅ Constructor validation on all injected dependencies
9. ✅ All synchronous method calls throughout
10. ✅ IMessageStore.EnqueueMessage() for all user feedback

---

## Threading Considerations

### Revit API Threading Rules
1. **Main Thread Only**: All Revit API calls must be on the main UI thread
2. **No Async/Await**: Avoid async operations that might switch threads
3. **External Events**: Use Revit's External Event mechanism for asynchronous operations

### Implementation Strategy
```csharp
// Use synchronous operations throughout
[RelayCommand]
private void ImportRevisions()
{
    // All operations on UI thread
    // No await keywords
    // Direct synchronous calls to repositories
}
```

---

## Error Handling

### Standard Pattern
```csharp
[RelayCommand]
private void PerformOperation()
{
    if (!IsDatabaseConnected)
    {
        _messageStore.EnqueueMessage(
            "Database is not connected",
            MessageTypes.Error);
        return;
    }
    
    try
    {
        IsLoading = true;
        
        _messageStore.EnqueueMessage(
            "Processing...",
            MessageTypes.Information,
            dismissAfterSeconds: 3);
        
        // Operation logic here
        var result = _docManagerApi.ImportDocuments(documents);
        
        if (result.Success)
        {
            _messageStore.EnqueueMessage(
                $"Successfully imported {result.DocumentsCreated} documents",
                MessageTypes.Information,
                dismissAfterSeconds: 3);
        }
        else
        {
            _messageStore.EnqueueMessage(
                $"Import failed: {result.Message}",
                MessageTypes.Error);
        }
    }
    catch (Exception ex)
    {
        _messageStore.EnqueueMessage(
            $"Error: {ex.Message}",
            MessageTypes.Error);
    }
    finally
    {
        IsLoading = false;
    }
}
```

**Key Principles:**
- Always check preconditions (database connected, valid data)
- Use try-catch-finally pattern
- Use `IMessageStore.EnqueueMessage()` for user feedback
- Set `IsLoading` to manage UI state
- Check `result.Success` property for operation outcome
- Use `result.Message` for detailed feedback
- Handle specific exceptions when needed (SQLiteException, etc.)

---

## Testing

Follow the testing guidelines in `testStyles.md` with these considerations:

**ViewModel Tests:**
- Test logic, validation, and data transformation
- Focus on ViewModel behavior, not database operations
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
├── DocManagerMain.cs
├── Views/
│   └── RevitIntegrationView.xaml
│   └── RevitIntegrationView.xaml.cs
├── ViewModels/
│   └── RevitIntegrationViewModel.cs
│   └── RevisionViewModel.cs
│   └── SheetViewModel.cs
├── Models/
│   └── RevisionData.cs
│   └── SheetData.cs
├── Converters/
│   └── EnumToBooleanConverter.cs
├── Tests/
│   └── ViewModels/
│       └── RevitIntegrationViewModelTests.cs
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
4. Database path configured via setup utility and stored in Revit extensible storage

### Installation Steps
1. Copy .NET DLLs to pyRevit lib folder
2. Copy Python script to pyRevit extension folder
3. Reload pyRevit in Revit
4. Run setup utility to configure database path (stored in Revit extensible storage)

---

## Summary Checklist

When developing the Revit integration:

- ✅ Use WPF with MVVM pattern and MVVM Community Toolkit
- ✅ Use ONLY synchronous DocManagerApi methods (no async/await)
- ✅ Collect Revit sheets and revisions in `Main.cs` before window opens
- ✅ Read database path from Revit extensible storage in `Main.cs`
- ✅ Connect to database and read existing documents and revisions in `Main.cs`
- ✅ Pass all collected data (Revit data, database data, connection state) into window constructor
- ✅ Window always opens regardless of startup failures — errors surface in message banner
- ✅ ViewModel receives pre-loaded data via constructor — no lazy loading of Revit or database data
- ✅ Use `IsDatabaseConnected` to gate all commands via `CanExecute`
- ✅ Instantiate DocManagerApi directly in ViewModel constructor
- ✅ Validate all constructor parameters
- ✅ Use Windows line endings (CRLF)
- ✅ Enable nullable reference types (`<Nullable>enable</Nullable>` in .csproj) and annotate all types correctly
- ✅ Follow test style guide from testStyles.md
- ✅ Handle errors gracefully with user feedback via IMessageStore.EnqueueMessage()
- ✅ Keep all operations on UI thread
- ✅ Validate input data before database operations
- ✅ Provide clear status messages using MessageTypes (Information, Warning, Error)
- ✅ Include IsSelected property on ViewModels for user selection
- ✅ Filter items shown to users (new revisions only, new or changed sheets by mode)
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
| 1.1 | 2026-03-22 | Update | Revit data (sheets, revisions) collected by Python and passed via constructor; database connection and existing data read in Main.cs before window opens; happy/unhappy path startup sequence defined; ViewModel receives all data at construction time; IsDatabaseConnected gates all commands |
