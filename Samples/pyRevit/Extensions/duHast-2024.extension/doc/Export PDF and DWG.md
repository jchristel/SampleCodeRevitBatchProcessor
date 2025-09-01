# Export PDF/DWG v2

## Overview
Advanced sheet export tool that exports Revit sheets to PDF and DWG formats with comprehensive configuration options and batch processing capabilities.

## Prerequisites
- Export settings must be configured using "Export PDF/DWG Settings" first
- .NET interface DLLs must be available
- Valid sheet content in the Revit model
- Extensible schema with export settings

## Functionality
This tool provides:
- Batch export of selected sheets to PDF and/or DWG
- Advanced file naming based on sheet parameters
- Print set management and updates
- User-friendly selection interface
- Progress tracking for large export jobs

## Usage Steps
1. Configure export settings using the settings tool first
2. Click the "Export PDF/DWG v2" button
3. Select export options (PDF only or PDF + DWG)
4. Choose sheets to export from the selection interface
5. Configure print sets if needed
6. Monitor export progress
7. Review export results and file locations

## Export Options
- **PDF Only**: Exports sheets as PDF files only
- **PDF and DWG**: Exports sheets in both PDF and DWG formats

## Selection Interface Features
- Sheet selection with preview information
- Print set configuration and updates
- Parameter-based file naming options
- Schedule export capabilities
- Real-time parameter validation

## File Naming
Uses configurable naming schemes based on:
- Sheet parameters (number, name, etc.)
- Custom naming rules
- Project-specific conventions
- Delimiter-based string splitting

## Input Requirements
- Configured export settings in extensible schema
- Valid sheets in the model
- Write access to export directory
- Compatible .NET interface libraries

## Output
- PDF files in specified export directory
- DWG files (if selected) in specified format
- Export log with success/failure status
- Updated print sets in the model

## Progress Tracking
- Real-time progress bar during export
- Cancellable export process
- Detailed status messages
- Performance timing information

## Error Handling
- Validates extensible schema existence
- Checks for required .NET DLL availability
- Handles sheet export failures gracefully
- Provides detailed error diagnostics
- Validates export settings before processing

## Performance Features
- Optimized batch processing
- Memory-efficient export handling
- Background processing capabilities
- Configurable export quality settings

## Integration
- Works with Export PDF/DWG Settings tool
- Integrates with Revit print sets
- Supports custom parameter schemes
- Compatible with automated workflows