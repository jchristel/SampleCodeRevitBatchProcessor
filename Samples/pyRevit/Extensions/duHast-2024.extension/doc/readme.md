# PyRevit Extension Library

A comprehensive collection of Revit automation tools built with pyRevit, designed to streamline common BIM workflows, family management, view operations, and model maintenance tasks.

## 📁 Extension Categories

### 🏗️ Family and Library Management
Tools for managing Revit families, libraries, and catalogue files.

- **[Compare Library Reports](compare_library_reports.md)** - Compare reports across different family libraries to identify differences and duplicates
- **[Report Families in Library XML](report_families_library_xml.md)** - Generate comprehensive CSV reports from XML part atom exports
- **[Create Part Atom Library](create_part_atom_library.md)** - Create XML part atom exports for family files in library locations
- **[Bulk Load Families](bulk_load_families.md)** - Load multiple families into the current document with batch selection
- **[Clean Up Catalogue File](clean_catalogue_file.md)** - Clean and organize family catalogue files by removing redundant parameters

### 📄 Export and Documentation
Advanced export tools for creating PDFs, DWGs, and documentation.

- **[Export PDF/DWG v2](export_pdf_dwg_v2.md)** - Advanced sheet export tool with comprehensive configuration options
- **[Export PDF/DWG Settings](export_pdf_dwg_settings.md)** - Configure export parameters, naming schemes, and file organization

### 👁️ View Management
Tools for managing views, templates, and display settings.

- **[Purge Views](purge_views.md)** - Remove unused views to improve model performance and reduce file size
- **[Propagate Grids](propagate_grids.md)** - Copy grid visibility settings from active view to multiple target views
- **[View Template Overrides I/O](view_template_overrides_io.md)** - Import/export view template override settings via JSON files

### 📏 Level Management
Control level annotation display and visibility.

- **[Switch Level Headers On (Start)](switch_level_headers_start.md)** - Show level bubble headers at the start (0 end) of levels
- **[Switch Level Headers On (End)](switch_level_headers_end.md)** - Show level bubble headers at the end (1 end) of levels

### ⚠️ Warning Resolution
Automated tools for resolving common Revit warnings and model issues.

- **[Solve Room Tag Warnings](solve_room_tag_warnings.md)** - Automatically fix room tags that are outside their associated rooms
- **Solve Room Separation Line Warnings** - Resolve overlapping room separation line warnings (long/short options)
- **Solve Area Separation Line Warnings** - Fix overlapping area separation line warnings (long/short options)

### 🏠 PushIt Room System
Specialized tools for the PushIt room management workflow.

- **Get PushIt Room Data by Selection** - Retrieve data for selected PushIt room elements
- **Update PushIt Rooms** - Update PushIt room areas based on Revit room calculations  
- **Get A Room** - Main room generation system using filled regions
- **Get A Room Settings** - Configuration settings for the room generation system

### 🎨 Color Fill Management
Tools for managing and organizing color fill schemes.

- **Color Fill Selection** - Import and update color fill schemes with various options

## 🚀 Getting Started

1. **Installation**: Copy the extension to your pyRevit extensions directory
2. **Dependencies**: Ensure all required .NET DLLs and duHast libraries are available
3. **Configuration**: Run settings tools before using export functions
4. **Usage**: Access tools through the pyRevit ribbon interface

## 📋 Common Workflows

### Library Management Workflow
1. Use **Create Part Atom Library** to generate XML exports
2. Run **Report Families in Library XML** to create documentation
3. Use **Compare Library Reports** to analyze differences between libraries
4. Load families with **Bulk Load Families** as needed

### Export Workflow  
1. Configure settings with **Export PDF/DWG Settings**
2. Use **Export PDF/DWG v2** for batch sheet export
3. Manage view templates with **View Template Overrides I/O**

### Model Maintenance Workflow
1. Use warning resolution tools to clean up model issues
2. Apply **Purge Views** to optimize model performance
3. Standardize level display with level header tools
4. Propagate consistent settings with grid and template tools

## 🔧 Technical Requirements

- **pyRevit**: Latest version recommended
- **Revit**: Compatible with supported Revit versions
- **duHast Library**: Required for core functionality
- **.NET Framework**: For advanced UI components
- **File Permissions**: Read/write access for import/export operations

## 📚 Documentation
Each tool includes comprehensive documentation covering:
- Prerequisites and requirements
- Step-by-step usage instructions
- Input/output specifications
- Error handling and troubleshooting
- Best practices and workflows
