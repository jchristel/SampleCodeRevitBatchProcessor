# DocManager - C# Multi-Platform Application Architecture

## Project Overview

DocManager is a document revision management system designed to run in two deployment scenarios:
1. **Standalone executable** - Independent WPF application
2. **Revit plugin** - Hosted within Revit to bypass certain restrictions

### Key Requirements
- .NET 8 target framework
- Separation of business logic and UI into separate DLLs
- No direct Revit API interaction (Revit used only as host)
- Shared UI components between both deployment modes
- Maximum code reuse and maintainability

## Solution Structure

```
DocManager/
├── docs/
│   ├── architecture/
│   │   ├── README.md                    # This architecture document
│   │   ├── database-design.md           # Document revision management database
│   │   ├── deployment-guide.md
│   │   └── security-considerations.md
│   │
│   ├── development/
│   │   ├── setup-guide.md               # Getting started for developers
│   │   ├── coding-standards.md
│   │   ├── testing-strategy.md
│   │   └── build-process.md
│   │
│   ├── user/
│   │   ├── user-manual.md
│   │   ├── installation-guide.md
│   │   └── troubleshooting.md
│   │
│   ├── api/
│   │   ├── core-services.md             # Business logic API documentation
│   │   └── ui-components.md             # Shared UI component documentation
│   │
│   └── project/
│       ├── requirements.md
│       ├── changelog.md
│       └── roadmap.md
│
├── src/
│   ├── DocManager.Core/                 # Business Logic DLL
│   │   ├── Interfaces/                  # Repository and service interfaces
│   │   ├── Models/                      # Domain entities and DTOs
│   │   │   ├── Config/                  # Configuration models
│   │   │   └── Results/                 # Operation result models
│   │   ├── Services/                    # Business services and implementations
│   │   │   ├── Api/                     # External integration APIs
│   │   │   └── Repositories/            # Data access layer
│   │   └── DocManager.Core.csproj       # .NET 8
│   │
│   ├── DocManager.UI.Shared/            # Shared UI Components DLL
│   │   ├── Views/
│   │   │   ├── MainView.xaml
│   │   │   ├── SettingsView.xaml
│   │   │   └── [Other UserControls]
│   │   ├── ViewModels/
│   │   │   ├── MainViewModel.cs
│   │   │   └── [Other ViewModels]
│   │   ├── Commands/
│   │   ├── Converters/
│   │   ├── Styles/
│   │   │   └── SharedStyles.xaml
│   │   └── DocManager.UI.Shared.csproj  # .NET 8, references Core
│   │
│   ├── DocManager.Standalone/           # Standalone EXE
│   │   ├── App.xaml                     # Application entry
│   │   ├── MainWindow.xaml              # Host window
│   │   ├── MainWindow.xaml.cs           # Hosts shared views
│   │   └── DocManager.Standalone.csproj # References UI.Shared
│   │
│   └── DocManager.Revit/                # Revit Plugin
│       ├── RevitCommand.cs              # IExternalCommand entry point
│       ├── RevitWindow.xaml             # Plugin window
│       ├── RevitWindow.xaml.cs          # Hosts same shared views
│       ├── manifest.addin               # Revit plugin manifest
│       └── DocManager.Revit.csproj      # References UI.Shared
│
├── tests/
│   ├── DocManager.Core.Tests/           # Business logic tests
│   │   ├── Models/                      # Entity model tests
│   │   ├── Services/                    # Service and repository tests
│   │   └── Integration/                 # End-to-end tests
│   └── DocManager.UI.Tests/             # UI component tests
│
└── DocManager.sln
```

## Current Implementation Status

### ✅ Completed Components

#### Core Domain Models
- **Revision** - Represents document release batches with dates and descriptions
- **Document** - Individual document versions with complete revision history
- **CustomProperty** - Flexible key-value properties for documents
- **ValidationResult** - Input validation results with error/warning collections
- **DatabaseStatistics** - Database metrics and reporting data

#### Configuration & Results Models
- **DatabaseSetupConfig** - Database initialization configuration
- **DocumentImportConfig** - Bulk import operation settings
- **DocumentImportData** - Individual document import data structure
- **ResultBase** - Base class for operation results with error/warning collections
- **SetupResult** - Database setup operation results
- **ValidationResult** - Document validation results
- **ImportResult** - Document import operation results

#### Data Access Layer (Repository Pattern)
- **IDatabaseService** - Database connection and schema management
- **DatabaseService** - SQLite database service implementation using sqlite-net-pcl
- **IRepository<T>** - Generic repository interface with CRUD operations
- **BaseRepository<T>** - Base repository implementation with sqlite-net-pcl ORM
- **IRevisionRepository** - Revision-specific queries (date ranges, latest revision)
- **RevisionRepository** - Revision data access implementation
- **IDocumentRepository** - Document-specific queries (by revision, search, existence checks)  
- **DocumentRepository** - Document data access implementation
- **ICustomPropertyRepository** - Custom property queries (by document, name, value)
- **CustomPropertyRepository** - Custom property data access implementation
- **IUnitOfWork** - Transaction management and repository coordination
- **UnitOfWork** - Unit of work implementation for sqlite-net-pcl

#### External Integration API
- **DocManagerApi** - Main API class for external integration (PyRevit, Revit Plugin, Standalone)
  - Database setup and initialization
  - Configuration validation
  - Health checks and diagnostics
  - Resource management and cleanup

#### Comprehensive Test Suite (200+ Tests)
- **Model Tests** - Entity behavior, validation, and business logic
- **Database Service Tests** - Connection management, schema creation, integrity checks
- **Repository Tests** - Data access operations, queries, and edge cases
- **Integration Tests** - Cross-component workflows and transactions
- **Special Cases** - Unicode handling, large datasets, concurrent operations

### 🚧 In Progress / Planned Components

#### High-Level Business Services
- **IDocumentService** - Document management business logic
- **DocumentService** - Implementation with validation, search, and statistics
- Document import/export workflows
- Revision management operations
- Custom property management

#### UI Components (Shared Library)
- WPF UserControls for document management
- ViewModels implementing MVVM pattern
- Commands and data binding infrastructure
- Shared styles and themes
- Validation UI components

#### Deployment Applications
- **Standalone Application** - Independent WPF executable
- **Revit Plugin** - Hosted within Revit environment
- Application configuration and settings
- Error handling and logging

## Architecture Principles

### 1. Business Logic (Core)
- **Target**: .NET 8
- **Purpose**: Contains all business logic, data models, and services
- **Dependencies**: Framework-agnostic, no UI dependencies
- **Database**: SQLite with sqlite-net-pcl ORM for type-safe operations
- **Key Features**:
  - Domain models with SQLite attributes for automatic schema creation
  - Repository pattern with generic base implementation
  - Unit of Work pattern for transaction management
  - External integration API for PyRevit and plugin scenarios
  - Comprehensive validation and error handling

### 2. Shared UI Components (UI.Shared)
- **Target**: .NET 8
- **Purpose**: Reusable UI components for both deployment modes
- **Dependencies**: References Core library
- **Key Features**:
  - UserControls (not Windows) for maximum reusability
  - ViewModels implementing MVVM pattern
  - Commands and converters
  - Shared styles and themes
  - Consistent user experience across platforms

### 3. Standalone Application
- **Target**: .NET 8
- **Purpose**: Independent executable application
- **Dependencies**: References UI.Shared
- **Key Features**:
  - Traditional WPF Application entry point
  - Main Window that hosts shared UserControls
  - Application-specific configuration

### 4. Revit Plugin
- **Target**: .NET 8
- **Purpose**: Plugin that runs within Revit process
- **Dependencies**: References UI.Shared
- **Key Features**:
  - Minimal wrapper around shared UI
  - Plugin manifest for Revit integration
  - Same UI components as standalone version

### MVVM Pattern Implementation
- ViewModels in shared library implement INotifyPropertyChanged
- Commands use RelayCommand or similar implementations
- Data binding for all UI interactions
- No code-behind logic in Views (UserControls)

### Shared UI Component Design

**Example MainWindow structures:**

**Standalone MainWindow.xaml:**
```xml
<Window x:Class="DocManager.Standalone.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:shared="clr-namespace:DocManager.UI.Shared.Views;assembly=DocManager.UI.Shared">
    <Grid>
        <shared:MainView DataContext="{Binding MainViewModel}" />
    </Grid>
</Window>
```

**Revit RevitWindow.xaml:**
```xml
<Window x:Class="DocManager.Revit.RevitWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:shared="clr-namespace:DocManager.UI.Shared.Views;assembly=DocManager.UI.Shared">
    <Grid>
        <shared:MainView DataContext="{Binding MainViewModel}" />
    </Grid>
</Window>
```

### External Integration API

The `DocManagerApi` class provides a clean interface for external systems:

```csharp
// Simple database setup
using var api = new DocManagerApi();
var result = await api.SetupDatabaseAsync(
    databasePath: @"C:\Projects\MyProject.db",
    customPropertyNames: new[] { "DisciplineCode", "ProjectPhase" },
    overwriteExisting: true
);

if (result.Success)
{
    Console.WriteLine($"Database ready at: {result.DatabasePath}");
}
```

## Key Benefits

### Code Reuse
- Single UI codebase shared between platforms
- Business logic completely separated and reusable
- Consistent user experience across deployment modes

### Maintainability
- Clear separation of concerns
- Testable business logic (200+ comprehensive tests)
- Modular architecture allows independent development

### Deployment Flexibility
- **Standalone**: Single executable deployment
- **Revit Plugin**: Install as Revit add-in
- **Future Platforms**: Easy to add new host applications

### Testing Strategy
- Unit tests for Core business logic using NUnit
- Repository tests with in-memory SQLite databases
- Integration tests for complete workflows
- ORM-first approach with sqlite-net-pcl testing patterns

## Development Setup

### Prerequisites
- Visual Studio 2022 or later
- .NET 8 SDK
- For Revit plugin development: Autodesk Revit 2024 or later

### Getting Started
1. Clone the repository
2. Open `DocManager.sln` in Visual Studio
3. Restore NuGet packages
4. Build the solution
5. Run tests to verify setup

### Testing
The project includes comprehensive test coverage:
- **200+ tests** covering all core functionality
- Tests use fluent NUnit syntax for readability
- Database tests use sqlite-net-pcl ORM patterns
- In-memory SQLite databases for fast test execution

```bash
# Run all tests
dotnet test

# Run specific test category
dotnet test --filter "Category=DatabaseService"
```

## Documentation Standards

### Documentation Structure
The `/docs` folder follows industry standards and is organized for different audiences:

- **Architecture**: Technical design documents for developers and architects
- **Development**: Guides and standards for contributing developers
- **User**: End-user documentation and support materials
- **API**: Technical reference for services and components
- **Project**: Project management and planning documents

### Documentation Benefits
- **Version Control**: Documentation stays in sync with code changes
- **Accessibility**: Easy for team members to find and contribute to docs
- **Automation**: Can set up automated documentation generation/deployment
- **Searchability**: IDEs and tools can index documentation alongside code

## Future Considerations

### Extensibility
- Plugin architecture for additional features
- Configuration management for different environments
- Logging and telemetry integration

### Performance
- Lazy loading of UI components
- Efficient data binding patterns
- Memory management best practices

### Security
- Input validation in Core layer
- Secure configuration management
- Error handling and logging

## Decision Rationale

### Why Separate UI.Shared Library?
- Maximizes code reuse between platforms
- Allows independent testing of UI components
- Enables consistent user experience
- Simplifies maintenance and updates

### Why .NET 8 for All Projects?
- Modern framework with latest features
- Consistent runtime across all components
- Better performance and security
- Long-term support and updates

### Why No Direct Revit API Integration?
- Simplifies architecture and reduces dependencies
- Allows business logic to remain platform-agnostic
- Easier testing and development
- Future-proofs for other hosting platforms

### Why sqlite-net-pcl?
- Provides full ORM capabilities with type safety
- Automatic schema generation from C# models
- LINQ-to-SQL query support
- Excellent performance for document management scenarios
- File-based databases enable project portability

## Contributing

Please read the development documentation in `/docs/development/` for coding standards, setup instructions, and contribution guidelines.