#############################################
FamilyWarningsCombinedReport Report
#############################################

Summary
=======

This report list all warnings occuring in families and their nested families.

- File name: FamilyWarningsCombinedReport.csv
- File type: comma separated
- Header row: yes

Properties listed
=====================

One row per warning per family processed.

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

- warningText

    - The warning text (message).

- warningGUID

    - The warning GUID.

- warningRelatedIds

    - The element ids relating to this warning directly.

- warningOtherIds

    - TBC

Notes
=====================

Nill
