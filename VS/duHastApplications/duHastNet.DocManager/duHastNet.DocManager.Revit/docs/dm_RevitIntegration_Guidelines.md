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
    â†"
.NET DLLs (Document Manager Core)
    â†"
WPF UI (MVVM Pattern)
    â†"
DocManagerApi (Sync Methods)
    â†"
SQLite Database
```

### Integration Layers

#### Layer 1: pyRevit Python Script
- **Purpose**: Entry point and Revit API interaction
- **Responsibilities**:
  - Initialize .NET runtime and load assemblies
  - Access Revit API for document, sheet, and revision data
  - Launch WPF UI
  - Handle Revit threading context

#### Layer 2: WPF User Interface
- **Purpose**: User interaction and data presentation
- **Responsibilities**:
  - Display Revit revisions and sheets
  - Provide import/update controls
  - Show progress and validation feedback
  - Handle user commands

#### Layer 3: Document Manager API
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

### User Workflow

#### Import Revisions Workflow
1. User clicks pyRevit button
2. WPF UI loads and displays Revit revisions not in database
3. User reviews revision list and checks revisions to import
4. User clicks "Import Revisions"
5. System validates and imports selected revisions to database
6. User receives success/failure feedback

#### Import Sheets Workflow
1. User navigates to Sheets panel
2. User selects "Import" mode via radio button
3. System displays Revit sheets NOT in database
4. User reviews and checks sheets to import
5. User clicks "Execute"
6. System validates and imports selected sheets as documents
7. User receives success/failure feedback

#### Update Document Names Workflow
1. User navigates to Sheets panel
2. User selects "Update" mode via radio button
3. System matches Revit sheets with database documents by sheet number
4. System displays only matched sheets that require updating
5. User reviews and checks sheets to update
6. User clicks "Execute"
7. System updates selected document names from Revit sheet names
8. User receives update summary (matched, updated, errors)

---

## Coding Guidelines

### 1. WPF MVVM Pattern with MVVM Community Toolkit

#### Required Pattern
All UI code MUST follow the MVVM (Model-View-ViewModel) pattern using the MVVM Community Toolkit.

#### ViewModel Structure
```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.ViewModels;

public partial class RevitIntegrationViewModel : ObservableObject
{
    private readonly DocManagerApi _docManagerApi;
    private readonly IMessageStore _messageStore;
    
    public RevitIntegrationViewModel(IMessageStore messageStore)
    {
        _docManagerApi = new DocManagerApi();
        _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
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
}
```

**Key Points:**
- Include `IMessageStore` field for user feedback
- Use `partial void OnSelectedSheetModeChanged()` to react to mode changes
- Single `ExecuteSheetOperation` command handles both Import and Update
- Filter sheets display based on selected mode

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

### 2. Use Synchronous Core Functionality

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

### 3. Direct DocManagerApi Usage

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

### 4. Constructor Validation

Apply constructor validation for any injected dependencies:

```csharp
public DocumentViewModel(Document document)
{
    // Validate constructor parameters
    _document = document ?? throw new ArgumentNullException(nameof(document));
}
```

**Note:** For ViewModels using parameterless constructors (like the PyRevit proof of concept), validation is applied when assigning properties or working with external data.

### 5. Line Endings

All code files MUST use Windows line endings (CRLF) for consistency with the Document Manager project.

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

from duHastNet.DocManager.Revit import PyRevitDocumentWindow
```

### Launching WPF UI
```python
def main():
    try:
        window = PyRevitDocumentWindow()
        window.ShowDialog()
    except Exception as ex:
        print("Error: " + str(ex))

if __name__ == "__main__":
    main()
```

**Note:** See Complete Proof of Concept Example for passing Revit data to .NET if needed.

---

## Complete Proof of Concept Example

Based on the PyRevit proof of concept, here's a complete working example:

### ViewModel (PyRevitDocumentListViewModel.cs)
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
    public partial class PyRevitDocumentListViewModel : ObservableObject
    {
        private readonly DocManagerApi _docManagerApi;
        private readonly IMessageStore _messageStore;
        private const string DATABASE_PATH = @"C:\path\to\your\database.db";

        public PyRevitDocumentListViewModel(IMessageStore messageStore)
        {
            _docManagerApi = new DocManagerApi();
            _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
            Documents = new ObservableCollection<DocumentViewModel>();
        }

        [ObservableProperty]
        private ObservableCollection<DocumentViewModel> _documents;

        [ObservableProperty]
        private bool _isLoading = false;

        [ObservableProperty]
        private int _totalDocuments = 0;

        [ObservableProperty]
        private string _databasePath = DATABASE_PATH;

        [ObservableProperty]
        private bool _isDatabaseConnected = false;

        [RelayCommand]
        private void LoadDocuments()
        {
            try
            {
                IsLoading = true;
                _messageStore.EnqueueMessage(
                    $"Connecting to database: {DatabasePath}",
                    MessageTypes.Information,
                    dismissAfterSeconds: 3);
                Documents.Clear();

                // Connect using synchronous method
                var connectionResult = _docManagerApi.ConnectDatabase(DatabasePath);

                if (!connectionResult.Success)
                {
                    _messageStore.EnqueueMessage(
                        $"Failed to connect: {connectionResult.Message}",
                        MessageTypes.Error);
                    IsDatabaseConnected = false;
                    return;
                }

                IsDatabaseConnected = true;
                _messageStore.EnqueueMessage(
                    "Database connected. Loading documents...",
                    MessageTypes.Information,
                    dismissAfterSeconds: 3);

                // Get documents using synchronous method
                var documents = _docManagerApi.GetActiveDocuments();

                // Convert to ViewModels
                foreach (var doc in documents)
                {
                    Documents.Add(new DocumentViewModel(doc));
                }

                TotalDocuments = Documents.Count;
                _messageStore.EnqueueMessage(
                    $"Loaded {TotalDocuments} documents successfully",
                    MessageTypes.Information,
                    dismissAfterSeconds: 3);
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error: {ex.Message}",
                    MessageTypes.Error);
                IsDatabaseConnected = false;
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand(CanExecute = nameof(CanRefresh))]
        private void Refresh()
        {
            LoadDocuments();
        }

        private bool CanRefresh() => IsDatabaseConnected && !IsLoading;

        [RelayCommand]
        private void Close()
        {
            try
            {
                if (IsDatabaseConnected)
                {
                    _docManagerApi.Close();
                    IsDatabaseConnected = false;
                    Documents.Clear();
                    TotalDocuments = 0;
                    _messageStore.EnqueueMessage(
                        "Database connection closed",
                        MessageTypes.Information,
                        dismissAfterSeconds: 3);
                }
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error closing database: {ex.Message}",
                    MessageTypes.Error);
            }
        }
    }

    public partial class DocumentViewModel : ObservableObject
    {
        private readonly Document _document;

        public DocumentViewModel(Document document)
        {
            _document = document ?? throw new ArgumentNullException(nameof(document));
        }

        public int Id => _document.Id;
        public string Number => _document.Number;
        public string Name => _document.Name;
        public string Revision => _document.Revision;
        public int RevisionId => _document.RevisionId;
        public bool IsActive => _document.IsActive;
        public string DisplayText => $"{Number} - {Name}";
        public string Status => IsActive ? "Active" : "Inactive";
    }
}
```

### View Code-Behind (PyRevitDocumentListView.xaml.cs)
```csharp
using System.Windows.Controls;
using duHastNet.DocManager.Revit.ViewModels;

namespace duHastNet.DocManager.Revit.Views
{
    public partial class PyRevitDocumentListView : UserControl
    {
        public PyRevitDocumentListView()
        {
            InitializeComponent();
            DataContext = new PyRevitDocumentListViewModel();
        }
    }
}
```

### Window Host (PyRevitDocumentWindow.cs)
```csharp
using System.Windows;
using duHastNet.DocManager.Revit.Views;

namespace duHastNet.DocManager.Revit
{
    public class PyRevitDocumentWindow : Window
    {
        public PyRevitDocumentWindow()
        {
            Title = "Document Manager - PyRevit";
            Width = 1000;
            Height = 600;
            WindowStartupLocation = WindowStartupLocation.CenterScreen;
            
            Content = new PyRevitDocumentListView();
        }
    }
}
```

### Python Script (ListDocuments.py)
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

from duHastNet.DocManager.Revit import PyRevitDocumentWindow

def main():
    try:
        window = PyRevitDocumentWindow()
        window.ShowDialog()
    except Exception as ex:
        print("Error: " + str(ex))

if __name__ == "__main__":
    main()
```

**Key Patterns Demonstrated:**
1. ✅ Direct DocManagerApi instantiation in constructor
2. ✅ IMessageStore injection for user feedback
3. ✅ All synchronous method calls (ConnectDatabase, GetActiveDocuments, Close)
4. ✅ ObservableProperty for UI binding
5. ✅ RelayCommand for button actions
6. ✅ IMessageStore.EnqueueMessage() for user feedback with MessageTypes
7. ✅ IsLoading for UI state management
8. ✅ Try-catch-finally error handling
9. ✅ Constructor validation in DocumentViewModel
10. ✅ Python script loads WPF window with .NET DLLs

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
â"œâ"€â"€ Views/
â"‚   â""â"€â"€ RevitIntegrationView.xaml
â"‚   â""â"€â"€ RevitIntegrationView.xaml.cs
â"œâ"€â"€ ViewModels/
â"‚   â""â"€â"€ RevitIntegrationViewModel.cs
â"‚   â""â"€â"€ RevisionViewModel.cs
â"‚   â""â"€â"€ SheetViewModel.cs
â"œâ"€â"€ Models/
â"‚   â""â"€â"€ RevisionData.cs
â"‚   â""â"€â"€ SheetData.cs
â"œâ"€â"€ Services/
â"‚   â""â"€â"€ RevitDataService.cs
â"œâ"€â"€ Tests/
â"‚   â""â"€â"€ ViewModels/
â"‚       â""â"€â"€ RevitIntegrationViewModelTests.cs
â""â"€â"€ duHastNet.DocManager.Revit.csproj

pyRevit/
â"œâ"€â"€ DocManager.extension/
â"‚   â""â"€â"€ DocManager.tab/
â"‚       â""â"€â"€ Revit Integration.panel/
â"‚           â""â"€â"€ Import Data.pushbutton/
â"‚               â""â"€â"€ script.py
â""â"€â"€ lib/
    â""â"€â"€ duHastNet.DocManager.Core.dll
    â""â"€â"€ duHastNet.DocManager.Revit.dll
```

---

## Deployment

### Requirements
1. pyRevit installed in Revit
2. .NET 8 or higher
3. Document Manager Core DLLs
4. SQLite database file (or path to create one)

### Installation Steps
1. Copy .NET DLLs to pyRevit lib folder
2. Copy Python script to pyRevit extension folder
3. Reload pyRevit in Revit
4. Configure database path in settings

---

## Summary Checklist

When developing the Revit integration:

- ✅ Use WPF with MVVM pattern and MVVM Community Toolkit
- ✅ Use ONLY synchronous DocManagerApi methods (no async/await)
- ✅ Instantiate DocManagerApi directly in ViewModel constructor
- ✅ Use synchronous methods: ConnectDatabase(), GetActiveDocuments(), CreateDocument(), etc.
- ✅ Validate constructor parameters for wrapper ViewModels (DocumentViewModel, etc.)
- ✅ Use Windows line endings (CRLF)
- ✅ Follow test style guide from testStyles.md
- ✅ Handle errors gracefully with user feedback via IMessageStore.EnqueueMessage()
- ✅ Keep UI responsive (all operations on UI thread)
- ✅ Validate input data before database operations
- ✅ Provide clear status messages to users using MessageTypes (Information, Warning, Error)
- ✅ Include IsSelected property on ViewModels for user selection
- ✅ Filter items shown to users (e.g., only revisions not in database)
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
