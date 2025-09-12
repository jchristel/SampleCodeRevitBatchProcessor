# DocManager - C# Multi-Platform Application Architecture

## Project Overview

DocManager is designed to run in two deployment scenarios:
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
│   │   ├── Models/
│   │   ├── Services/
│   │   ├── Interfaces/
│   │   ├── Configuration/
│   │   ├── Utilities/
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
│   └── DocManager.UI.Tests/             # UI component tests
│
└── DocManager.sln
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

## Architecture Principles

### 1. Business Logic (Core)
- **Target**: .NET 8
- **Purpose**: Contains all business logic, data models, and services
- **Dependencies**: Framework-agnostic, no UI dependencies
- **Key Features**:
  - Domain models and entities
  - Business services and interfaces
  - Configuration management
  - Utility functions
  - Dependency injection support

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

## Implementation Guidelines

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

### MVVM Pattern Implementation
- ViewModels in shared library implement INotifyPropertyChanged
- Commands use RelayCommand or similar implementations
- Data binding for all UI interactions
- No code-behind logic in Views (UserControls)

### Dependency Injection Setup
```csharp
// In both Standalone and Revit projects
public void ConfigureServices(IServiceCollection services)
{
    // Core services
    services.AddScoped<IDocumentService, DocumentService>();
    
    // ViewModels
    services.AddTransient<MainViewModel>();
    services.AddTransient<SettingsViewModel>();
}
```

## Key Benefits

### Code Reuse
- Single UI codebase shared between platforms
- Business logic completely separated and reusable
- Consistent user experience across deployment modes

### Maintainability
- Clear separation of concerns
- Testable business logic
- Modular architecture allows independent development

### Deployment Flexibility
- **Standalone**: Single executable deployment
- **Revit Plugin**: Install as Revit add-in
- **Future Platforms**: Easy to add new host applications

### Testing Strategy
- Unit tests for Core business logic
- UI tests for shared components
- Integration tests for complete workflows

## Project Dependencies

### DocManager.Core.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
</Project>
```

### DocManager.UI.Shared.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
  </PropertyGroup>
  
  <ItemGroup>
    <ProjectReference Include="../DocManager.Core/DocManager.Core.csproj" />
  </ItemGroup>
</Project>
```

### DocManager.Standalone.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
    <OutputType>WinExe</OutputType>
  </PropertyGroup>
  
  <ItemGroup>
    <ProjectReference Include="../DocManager.UI.Shared/DocManager.UI.Shared.csproj" />
  </ItemGroup>
</Project>
```

### DocManager.Revit.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
  </PropertyGroup>
  
  <ItemGroup>
    <ProjectReference Include="../DocManager.UI.Shared/DocManager.UI.Shared.csproj" />
  </ItemGroup>
  
  <ItemGroup>
    <Reference Include="RevitAPI">
      <HintPath>[Path to Revit API DLL]</HintPath>
      <Private>false</Private>
    </Reference>
  </ItemGroup>
</Project>
```

## Getting Started

### Prerequisites
- Visual Studio 2022 or later
- .NET 8 SDK
- For Revit plugin development: Autodesk Revit 2024 or later

### Setup Instructions
1. Clone the repository
2. Open `DocManager.sln` in Visual Studio
3. Restore NuGet packages
4. Build the solution
5. For detailed setup instructions, see `/docs/development/setup-guide.md`

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

## Contributing

Please read `/docs/development/coding-standards.md` and `/docs/development/setup-guide.md` before contributing to this project.