# Export PDF/DWG Settings

## Overview
Configuration tool for setting up PDF and DWG export parameters, file naming schemes, and export options. This tool must be run before using the Export PDF/DWG v2 function.

## Prerequisites
- Sheet parameters must be assigned in the Revit model
- Write access to project file for storing settings
- Compatible .NET interface libraries

## Functionality
This tool configures:
- PDF export file naming schemes
- DWG export file naming schemes  
- DWG export scheme selection
- Parameter-based naming rules
- Export directory preferences

## Usage Steps
1. Ensure sheets have assigned parameters
2. Click the "Export PDF/DWG Settings" button
3. Configure PDF naming scheme using available parameters
4. Set up DWG naming scheme and export format
5. Select appropriate DWG export scheme
6. Save settings to the project file

## Configuration Options

### PDF Settings
- Custom file naming using sheet parameters
- Parameter-based string construction
- Delimiter and separator configuration
- File path organization rules

### DWG Settings  
- DWG-specific naming schemes
- Export format selection
- Layer mapping preferences
- Scale and unit configurations

### Parameter Integration
- Utilizes assigned sheet parameters
- Supports custom parameter schemes
- Validates parameter availability
- Provides parameter selection interface

## Settings Storage
- Settings saved in extensible schema
- Project-specific configuration
- Persistent across sessions
- Verification of stored settings

## Input Requirements
- Valid sheet parameters in model
- Available parameter names
- Write permissions for settings storage
- Compatible export scheme definitions

## Output
- Configured export settings stored in project
- Verification messages for successful configuration
- Parameter validation results
- Ready-to-use export configuration

## Validation Features
- Verifies parameter assignments
- Checks for required export schemes
- Validates naming string construction
- Confirms settings storage integrity

## Error Handling
- Handles missing parameter assignments
- Validates export scheme availability
- Provides clear configuration error messages
- Guides user through setup requirements

## Integration
- Required prerequisite for Export PDF/DWG v2
- Works with Revit's native export schemes
- Supports custom parameter workflows
- Integrates with project information storage

## Best Practices
- Configure settings before first export
- Verify parameter assignments are correct
- Test naming schemes with sample data
- Review settings periodically for accuracy