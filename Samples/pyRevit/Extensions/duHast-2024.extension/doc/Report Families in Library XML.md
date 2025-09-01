# Report Families in Library XML

## Overview
Creates comprehensive reports on families in library locations based on XML part atom exports. This function analyzes family data from XML files and generates detailed CSV reports.

## Prerequisites
- XML part atom files must exist in the library directories
- Read access to library directories
- Valid family library structure

## Functionality
This tool provides:
- Analysis of family type data from XML part atom exports
- Generation of detailed CSV reports
- Progress tracking for large library collections
- Tabular display of family information in pyRevit output

## Usage Steps
1. Click the "Report Families in Library XML" button
2. Select library directories to process
3. Monitor progress through the pyRevit progress bar
4. Review the family data table in the pyRevit output
5. Save the report as a CSV file when prompted

## Input Requirements
- Library directories containing XML part atom files
- Valid XML structure from family exports
- Sufficient disk space for CSV output files

## Output
- Detailed family report table in pyRevit console
- CSV file with comprehensive family data
- Progress indicators during processing
- Status messages for large datasets (>10,000 rows)

## Report Contents
The generated report includes:
- Family names and types
- Parameter information
- Library location data
- Family metadata from XML exports

## Performance Notes
- Processing time depends on library size
- Large libraries (>10,000 families) will show performance warnings
- Progress bar provides real-time status updates

## Error Handling
- Validates XML file structure
- Handles missing or corrupted XML files
- Provides detailed error messages for troubleshooting