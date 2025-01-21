Intro
=====

The Reporting section covers classes and utilities functions used to report on families within project files.


Standard Reporting
------------------



Reporting based on XML data
----------------------------

report_fam_types_differences_from_XML module contains a script which reports on family type differences between a project file and a library of families. 

The script reads in xml files created through the PartAtomExport function of the Revit API and compares the family types in the project file to those in the library.
The output can be filtered by an ignore list in form of a .csv file. 

Ignore list format:

- columns
 
   - Family name
   - Family category

Output:

Creates a .csv file with the following columns:

- Family name
- Family category
- Family exists in library
- Family type name
- Family type exists in Library
- Parameter name
- Parameter exists in library
- Parameter difference (Project -> Library)

Output content:

- if family does or does not exist in library
- if type does not exist in library
- if a parameter value for a given type is different to the parameter value for that type in the library


This report assumes that:

- there is a library of families (.rfa) located in a project directory or multiple directories.
- there is an xml files for each family located in the library created through the PartAtomExport function of the Revit API. These are considered the source of truth and the families in the project file are compared to those xml files.



