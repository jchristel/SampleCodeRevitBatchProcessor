#############################################
FamilySharedParametersCombinedReport Report
#############################################

Summary
=======

This report list all shared parameters of families and their nested families.

- File name: FamilySharedParametersCombinedReport.csv
- File type: comma separated
- Header row: yes

Properties listed
=====================

One row per shared parameter per family processed.

- root

    - Describes the location of the family within the (tree like) nesting structure of the root (top most) family.
    - Each nesting level is indicated by a ' :: '
    - Always contains, as a last entry, the actual family name

- rootCategory

    - Similar to root, this describes the category nesting structure.
    - Always contains, as a last entry, the actual family category

- familyName

    - The family name (without file extension)

- familyFilePath

    - The fully qualified file path of the family file.

- parameterName

    - The shared parameter name.

- parameterGUID

    - The shared parameter GUID.

- parameterId

    - The shared parameter Element Id.

- usageCounter

    - Default is 0: this shared parameter definition is not used in a family parameter, otherwise 1 (is used)

- usedBy

    - List of 

        - Family parameters using the shared parameter definition in format:

            - {'parameterGUID': '16c78725-1525-4efa-b88d-cb6b211d1fc0', 'parameterName': 'The parameter name', 'root': 'The family Name'}
        
        - Nested families where this shared parameter occurs (This is only shown in root families!):

            - {'parameterGUID': '16c78725-1525-4efa-b88d-cb6b211d1fc0', 'parameterName': 'The parameter name', 'root': 'The family Name :: The nested family name'}


Notes
=====================

Nill
