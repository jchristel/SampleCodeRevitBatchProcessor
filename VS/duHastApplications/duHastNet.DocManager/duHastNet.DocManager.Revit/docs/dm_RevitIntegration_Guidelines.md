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
- Import revisions from Revit into Document Manager database
- View and manage Revit revision sequences
- Synchronize revision metadata (number, date, description, issued status)

#### 2. Revit Sheets (Documents) Management
- Import sheets from Revit into Document Manager database
- View and manage Revit sheet properties
- Update document names in Document Manager based on Revit sheet numbers
- Synchronize sheet metadata (number, name, revision, sheet properties)

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
  - DataGrid showing Revit revisions (Number, Date, Description, Issued)
  - "Import Revisions" button
  - Revision count display
  - Selection controls for filtering

#### Area 2: Sheets (Documents) Panel
- **Purpose**: Manage Revit sheets
- **Controls**:
  - DataGrid showing Revit sheets (Sheet Number, Sheet Name, Current Revision)
  - "Import Sheets" button
  - "Update Document Names" button
  - Sheet count display
  - Filter and search controls

### User Workflow

#### Import Revisions Workflow
1. User clicks pyRevit button
2. WPF UI loads and displays Revit revisions
3. User reviews revision list
4. User clicks "Import Revisions"
5. System validates and imports revisions to database
6. User receives success/failure feedback

#### Import Sheets Workflow
1. User navigates to Sheets panel
2. System displays Revit sheets from current document
3. User reviews sheet list
4. User clicks "Import Sheets"
5. System validates and imports sheets as documents
6. User receives success/failure feedback

#### Update Document Names Workflow
1. User navigates to Sheets panel
2. User clicks "Update Document Names"
3. System matches Revit sheets with database documents by sheet number
4. System updates document names from Revit sheet names
5. User receives update summary (matched, updated, errors)

---

## Coding Guidelines

### 1. WPF MVVM Pattern with MVVM Community Toolkit

#### Required Pattern
All UI code MUST follow the MVVM (Model-View-ViewModel) pattern using the MVVM Community Toolkit.

#### ViewModel Structure
```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace duHastNet.DocManager.Revit.ViewModels;

public partial class RevitIntegrationViewModel : ObservableObject
{
    private readonly IDocManagerApi _api;
    
    public RevitIntegrationViewModel(IDocManagerApi api)
    {
        _api = api ?? throw new ArgumentNullException(nameof(api));
    }
    
    [ObservableProperty]
    private ObservableCollection<RevisionViewModel> _revisions = new();
    
    [ObservableProperty]
    private ObservableCollection<SheetViewModel> _sheets = new();
    
    [RelayCommand]
    private async Task ImportRevisionsAsync()
    {
        // Implementation
    }
    
    [RelayCommand]
    private async Task ImportSheetsAsync()
    {
        // Implementation
    }
    
    [RelayCommand]
    private async Task UpdateDocumentNamesAsync()
    {
        // Implementation
    }
}
```

#### View (XAML) Structure
```xml
<Window x:Class="duHastNet.DocManager.Revit.Views.RevitIntegrationView"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:vm="clr-namespace:duHastNet.DocManager.Revit.ViewModels">
    <Window.DataContext>
        <vm:RevitIntegrationViewModel/>
    </Window.DataContext>
    
    <Grid>
        <!-- UI Controls bound to ViewModel properties and commands -->
    </Grid>
</Window>
```

### 2. Use Synchronous Core Functionality

#### Critical Requirement: Avoid Async in Revit Context

**IMPORTANT**: Due to Revit API threading constraints, all Document Manager API calls from the Revit integration MUST use synchronous methods.

#### Use Sync API Methods
```csharp
// âœ… CORRECT - Use synchronous IDocManagerApi methods
public class RevitIntegrationViewModel : ObservableObject
{
    private readonly IDocManagerApi _api;
    
    [RelayCommand]
    private void ImportRevisions()
    {
        var unitOfWork = _api.GetUnitOfWork();
        if (unitOfWork == null)
        {
            // Handle error
            return;
        }
        
        // Use synchronous repository methods
        var revisionRepo = unitOfWork.Revisions as IRevisionRepositorySync;
        foreach (var revision in Revisions)
        {
            revisionRepo.CreateSync(revision.ToRevision());
        }
        
        unitOfWork.SaveChanges();
    }
}
```

#### Do NOT Use Async Methods
```csharp
// âŒ WRONG - Async causes threading issues in Revit
[RelayCommand]
private async Task ImportRevisionsAsync()
{
    // This will cause threading exceptions in Revit!
    await _api.CreateRevisionAsync(revision);
}
```

#### Accessing Sync Repositories
```csharp
// All repositories implement both async and sync interfaces
var unitOfWork = _api.GetUnitOfWork();

// Cast to sync interface for Revit context
var revisionRepo = unitOfWork.Revisions as IRevisionRepositorySync;
var documentRepo = unitOfWork.Documents as IDocumentRepositorySync;
var customPropRepo = unitOfWork.CustomProperties as ICustomPropertyRepositorySync;

// Use sync methods
revisionRepo.CreateSync(revision);
documentRepo.UpdateSync(document);
customPropRepo.GetByDocumentIdSync(documentId);
```

### 3. Interface-Based Design

#### Dependency Injection
All dependencies MUST be injected as interfaces, not concrete classes.

```csharp
// âœ… CORRECT
public RevitIntegrationViewModel(
    IDocManagerApi api,
    IDialogService dialogService,
    IMessageStore messageStore)
{
    _api = api ?? throw new ArgumentNullException(nameof(api));
    _dialogService = dialogService ?? throw new ArgumentNullException(nameof(dialogService));
    _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
}

// âŒ WRONG
public RevitIntegrationViewModel(
    DocManagerApi api,        // Concrete class - not testable
    DialogService dialogService)  // Concrete class - not mockable
{
    _api = api;
    _dialogService = dialogService;
}
```

### 4. Constructor Validation

Apply constructor validation as per `ConstructorValidationBestPractices.md`:

```csharp
public RevitIntegrationViewModel(IDocManagerApi api)
{
    // Validate all constructor parameters
    _api = api ?? throw new ArgumentNullException(nameof(api));
}
```

### 5. Line Endings

All code files MUST use Windows line endings (CRLF) for consistency with the Document Manager project.

---

## Data Model

### Revision Model
```csharp
public class RevisionViewModel : ObservableObject
{
    [ObservableProperty]
    private string _number = string.Empty;
    
    [ObservableProperty]
    private DateTime _date;
    
    [ObservableProperty]
    private string _description = string.Empty;
    
    [ObservableProperty]
    private bool _issued;
    
    public Revision ToRevision()
    {
        return new Revision
        {
            Number = Number,
            Date = Date,
            Description = Description,
            Issued = Issued
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

### Database Setup
```csharp
// Initialize or connect to database
public async Task InitializeDatabaseAsync(string databasePath)
{
    var result = await _api.ConnectDatabaseAsync(databasePath);
    
    if (!result.IsSuccessful)
    {
        // Handle connection error
        ShowError(result.Errors);
        return;
    }
    
    // Load existing data
    await LoadDataAsync();
}
```

### Revision Import
```csharp
[RelayCommand]
private void ImportRevisions()
{
    if (!_api.IsDatabaseReady())
    {
        ShowError("Database is not connected");
        return;
    }
    
    var unitOfWork = _api.GetUnitOfWork();
    var revisionRepo = unitOfWork.Revisions as IRevisionRepositorySync;
    
    try
    {
        foreach (var revisionVm in Revisions)
        {
            var revision = revisionVm.ToRevision();
            revisionRepo.CreateSync(revision);
        }
        
        unitOfWork.SaveChanges();
        ShowSuccess($"Imported {Revisions.Count} revisions");
    }
    catch (Exception ex)
    {
        ShowError($"Import failed: {ex.Message}");
    }
}
```

### Document Import
```csharp
[RelayCommand]
private void ImportSheets()
{
    if (!_api.IsDatabaseReady())
    {
        ShowError("Database is not connected");
        return;
    }
    
    var unitOfWork = _api.GetUnitOfWork();
    var documentRepo = unitOfWork.Documents as IDocumentRepositorySync;
    
    try
    {
        foreach (var sheetVm in Sheets)
        {
            var document = sheetVm.ToDocument();
            documentRepo.CreateSync(document);
        }
        
        unitOfWork.SaveChanges();
        ShowSuccess($"Imported {Sheets.Count} sheets");
    }
    catch (Exception ex)
    {
        ShowError($"Import failed: {ex.Message}");
    }
}
```

### Document Name Update
```csharp
[RelayCommand]
private void UpdateDocumentNames()
{
    if (!_api.IsDatabaseReady())
    {
        ShowError("Database is not connected");
        return;
    }
    
    var unitOfWork = _api.GetUnitOfWork();
    var documentRepo = unitOfWork.Documents as IDocumentRepositorySync;
    
    try
    {
        int updatedCount = 0;
        
        foreach (var sheetVm in Sheets)
        {
            // Find document by sheet number
            var documents = documentRepo.GetAllSync();
            var document = documents.FirstOrDefault(d => d.Number == sheetVm.SheetNumber);
            
            if (document != null)
            {
                // Update name from Revit sheet
                document.Name = sheetVm.SheetName;
                documentRepo.UpdateSync(document);
                updatedCount++;
            }
        }
        
        unitOfWork.SaveChanges();
        ShowSuccess($"Updated {updatedCount} document names");
    }
    catch (Exception ex)
    {
        ShowError($"Update failed: {ex.Message}");
    }
}
```

---

## Python Integration

### Loading .NET Assemblies
```python
import clr
import sys
from System.Windows import Window

# Add reference to Document Manager DLLs
clr.AddReference('duHastNet.DocManager.Core')
clr.AddReference('duHastNet.DocManager.Revit')

from duHastNet.DocManager.Core.Interfaces import IDocManagerApi
from duHastNet.DocManager.Revit.Views import RevitIntegrationView
from duHastNet.DocManager.Revit.ViewModels import RevitIntegrationViewModel
```

### Passing Revit Data to .NET
```python
from System.Collections.Generic import List
from duHastNet.DocManager.Revit.Models import RevisionData, SheetData

def get_revit_revisions(doc):
    """Extract revisions from Revit document"""
    revisions = List[RevisionData]()
    
    for rev in doc.GetElement(DB.RevisionId):
        revision_data = RevisionData()
        revision_data.Number = rev.SequenceNumber
        revision_data.Date = rev.RevisionDate
        revision_data.Description = rev.Description
        revision_data.Issued = rev.Issued
        revisions.Add(revision_data)
    
    return revisions

def get_revit_sheets(doc):
    """Extract sheets from Revit document"""
    sheets = List[SheetData]()
    
    collector = DB.FilteredElementCollector(doc)
    sheet_elements = collector.OfClass(DB.ViewSheet).ToElements()
    
    for sheet in sheet_elements:
        sheet_data = SheetData()
        sheet_data.SheetNumber = sheet.SheetNumber
        sheet_data.SheetName = sheet.Name
        sheet_data.CurrentRevision = sheet.get_Parameter(
            DB.BuiltInParameter.SHEET_CURRENT_REVISION).AsString()
        sheets.Add(sheet_data)
    
    return sheets
```

### Launching WPF UI
```python
def show_revit_integration_ui():
    """Show the Revit integration WPF dialog"""
    
    # Get current Revit document
    doc = __revit__.ActiveUIDocument.Document
    
    # Extract data from Revit
    revisions = get_revit_revisions(doc)
    sheets = get_revit_sheets(doc)
    
    # Create and show WPF window
    view = RevitIntegrationView()
    viewModel = view.DataContext
    
    # Pass Revit data to ViewModel
    viewModel.LoadRevitData(revisions, sheets)
    
    # Show dialog
    view.ShowDialog()
```

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

### Validation Errors
```csharp
private bool ValidateRevision(Revision revision)
{
    if (string.IsNullOrWhiteSpace(revision.Number))
    {
        ShowError("Revision number is required");
        return false;
    }
    
    if (revision.Date == default)
    {
        ShowError("Revision date is required");
        return false;
    }
    
    return true;
}
```

### Database Errors
```csharp
private void HandleDatabaseError(Exception ex)
{
    if (ex is SQLiteException sqlEx)
    {
        ShowError($"Database error: {sqlEx.Message}");
    }
    else if (ex is InvalidOperationException)
    {
        ShowError("Database is not initialized");
    }
    else
    {
        ShowError($"Unexpected error: {ex.Message}");
    }
}
```

### User Feedback
```csharp
[ObservableProperty]
private string _statusMessage = string.Empty;

[ObservableProperty]
private bool _isOperationInProgress;

private void ShowSuccess(string message)
{
    StatusMessage = message;
    // Update UI to show success state
}

private void ShowError(string message)
{
    StatusMessage = $"Error: {message}";
    // Update UI to show error state
}
```

---

## Testing

### Unit Tests
Follow the testing guidelines in `testStyles.md`:

```csharp
using NUnit.Framework;
using Moq;
using duHastNet.DocManager.Core.Interfaces;

namespace duHastNet.DocManager.Revit.Tests.ViewModels;

[TestFixture]
public class RevitIntegrationViewModelTests
{
    private Mock<IDocManagerApi> _mockApi;
    private RevitIntegrationViewModel _viewModel;
    
    [SetUp]
    public void Setup()
    {
        _mockApi = new Mock<IDocManagerApi>();
        _viewModel = new RevitIntegrationViewModel(_mockApi.Object);
    }
    
    [Test]
    public void ImportRevisions_WithValidData_CallsApi()
    {
        // Arrange
        var mockUnitOfWork = new Mock<IUnitOfWork>();
        var mockRevisionRepo = new Mock<IRevisionRepositorySync>();
        
        _mockApi.Setup(x => x.GetUnitOfWork()).Returns(mockUnitOfWork.Object);
        mockUnitOfWork.Setup(x => x.Revisions).Returns(mockRevisionRepo.Object);
        
        // Act
        _viewModel.ImportRevisionsCommand.Execute(null);
        
        // Assert
        mockRevisionRepo.Verify(x => x.CreateSync(It.IsAny<Revision>()), Times.AtLeastOnce);
    }
}
```

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
2. .NET Framework 4.8 or higher
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

- âœ… Use WPF with MVVM pattern and MVVM Community Toolkit
- âœ… Use ONLY synchronous Document Manager API methods (no async/await)
- âœ… Inject dependencies as interfaces (IDocManagerApi, not DocManagerApi)
- âœ… Validate all constructor parameters
- âœ… Use Windows line endings (CRLF)
- âœ… Follow test style guide from testStyles.md
- âœ… Cast repositories to sync interfaces (IRevisionRepositorySync)
- âœ… Handle errors gracefully with user feedback
- âœ… Keep UI responsive (all operations on UI thread)
- âœ… Validate input data before database operations
- âœ… Provide clear status messages to users
- âœ… Write unit tests for all ViewModels
- âœ… Document public APIs and complex logic

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
