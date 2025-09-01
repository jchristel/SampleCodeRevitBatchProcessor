# C# Multi-Platform Application Architecture

## Project Overview

This project is designed to run in two deployment scenarios:
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
YourSolution/
├── src/
│   ├── YourProject.Core/              # Business Logic DLL
│   │   ├── Models/
│   │   ├── Services/
│   │   ├── Interfaces/
│   │   ├── Configuration/
│   │   ├── Utilities/
│   │   └── YourProject.Core.csproj    # .NET 8
│   │
│   ├── YourProject.UI.Shared/         # Shared UI Components DLL
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
│   │   └── YourProject.UI.Shared.csproj # .NET 8, references Core
│   │
│   ├── YourProject.Standalone/        # Standalone EXE
│   │   ├── App.xaml                   # Application entry
│   │   ├── MainWindow.xaml            # Host window
│   │   ├── MainWindow.xaml.cs         # Hosts shared views
│   │   └── YourProject.Standalone.csproj # References UI.Shared
│   │
│   └── YourProject.Revit/             # Revit Plugin
│       ├── RevitCommand.cs            # IExternalCommand entry point
│       ├── RevitWindow.xaml           # Plugin window
│       ├── RevitWindow.xaml.cs        # Hosts same shared views
│       ├── manifest.addin             # Revit plugin manifest
│       └── YourProject.Revit.csproj   # References UI.Shared
│
├── tests/
│   ├── YourProject.Core.Tests/        # Business logic tests
│   └── YourProject.UI.Tests/          # UI component tests
│
└── YourSolution.sln
```

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
<Window x:Class="YourProject.Standalone.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:shared="clr-namespace:YourProject.UI.Shared.Views;assembly=YourProject.UI.Shared">
    <Grid>
        <shared:MainView DataContext="{Binding MainViewModel}" />
    </Grid>
</Window>
```

**Revit RevitWindow.xaml:**
```xml
<Window x:Class="YourProject.Revit.RevitWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:shared="clr-namespace:YourProject.UI.Shared.Views;assembly=YourProject.UI.Shared">
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
    services.AddScoped<IYourService, YourService>();
    
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

### YourProject.Core.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
</Project>
```

### YourProject.UI.Shared.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
  </PropertyGroup>
  
  <ItemGroup>
    <ProjectReference Include="../YourProject.Core/YourProject.Core.csproj" />
  </ItemGroup>
</Project>
```

### YourProject.Standalone.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
    <OutputType>WinExe</OutputType>
  </PropertyGroup>
  
  <ItemGroup>
    <ProjectReference Include="../YourProject.UI.Shared/YourProject.UI.Shared.csproj" />
  </ItemGroup>
</Project>
```

### YourProject.Revit.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
  </PropertyGroup>
  
  <ItemGroup>
    <ProjectReference Include="../YourProject.UI.Shared/YourProject.UI.Shared.csproj" />
  </ItemGroup>
  
  <ItemGroup>
    <Reference Include="RevitAPI">
      <HintPath>[Path to Revit API DLL]</HintPath>
      <Private>false</Private>
    </Reference>
  </ItemGroup>
</Project>
```

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