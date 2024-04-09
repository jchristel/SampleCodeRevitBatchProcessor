#############################################
FamilyBaseDataCombined Report
#############################################

Summary
=======

This report list some base properties of families and their nested families.

- File name: FamilyBaseDataCombinedReport.csv
- File type: comma separated
- Header row: yes

Properties listed
=====================

One row per family processed.

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

- categoryName

    - The family Revit category.

Notes
=====================

This report is used to create the following reports:

- Missing families report
- Missing families host report
- Circular references report

In addition this report is used to:

- Determine the re-load order of changed families in the Modify Family Library Advaced flow.