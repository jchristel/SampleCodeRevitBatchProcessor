# Clean Up Catalogue File

## Overview
Cleans up family catalogue files by removing unnecessary parameters, sorting columns, and organizing data. This tool is specifically designed for Revit family documents and their associated catalogue files.

## Prerequisites
- Current document must be a Revit family document
- Existing catalogue file (.txt format)
- Read/write access to catalogue file location

## Functionality
This tool performs:
- Removal of instance parameters from catalogue
- Removal of type parameters that are formula-driven
- Column sorting based on predefined desired order
- Alphabetical sorting of values within columns
- File validation and cleanup

## Usage Steps
1. Open a Revit family document
2. Click the "Clean Up Catalogue File" button
3. Select the catalogue file (.txt) to clean
4. Tool automatically processes and cleans the file
5. Review results and any warning messages

## Document Requirements
- Must be executed within a Revit family document
- Non-family documents will be rejected with appropriate error message

## Catalogue File Processing
The tool removes:
- All instance parameters
- Type parameters driven by formulas
- Unnecessary or redundant data entries

## Column Organization
Applies predefined column order for door-related parameters:
- Door_Panel_Width_Major
- Door_Panel_Width_Minor  
- Door_Panel_Width
- Door_Height_Nominal
- Door_Panel_Thickness
- Clear_Opening_Width

## Data Sorting
- Columns arranged according to desired order
- Values sorted alphabetically within each column
- Maintains data integrity during reorganization

## Input Requirements
- Valid catalogue file in .txt format
- Proper parameter structure
- Compatible family document context

## Output
- Cleaned and organized catalogue file
- Improved parameter organization
- Removal of formula-driven redundancy
- Status messages confirming successful cleanup

## Error Handling
- Validates document type before execution
- Checks for valid catalogue file selection
- Handles file reading/writing errors
- Provides detailed error messages for troubleshooting

## Best Practices
- Always backup catalogue files before cleaning
- Verify family parameter structure before processing
- Review cleaned file to ensure expected results
- Use in family development workflow for optimization