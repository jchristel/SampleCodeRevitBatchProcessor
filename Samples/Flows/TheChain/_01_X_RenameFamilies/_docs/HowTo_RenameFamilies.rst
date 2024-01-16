#############################################
Rename Families
#############################################

Summary
=======

Families require renaming for a number of reasons: the initial name may not conform with a naming standard or the name does not adequately describe the family.
What makes the renaming of families complicated is the fact that families regularely contain other families nested into them. When renaming a family on a file server, these nested families do not know about the name change
and keep their old name.


Using the flow to rename nested families and family files
===============================================================

Flow: RenameFamilies

This flow will, as a pre- process, rename Revit family files and any catalogue files assoicated as per rename directives in the library folder in a drive location. It will then create a single task list file which will contain all the host family file path
of families containing the families to be renamed as nested families.
Next step is to process every family in the task file created and rename its directly nested families as required. No renaming pass the first level of nesting will occur.
Families will be saved to a temp location. Once all families have been processed the changed families will be copied back to the original family location therby overwriting the existing files.

Note:
To propagate those changes through the entire library the flow ModifyFamilyLibraryReloadAdvanced is required to be run after this flow.

Script flow diagram
--------------------------------


Outcomes
--------------------------------

Nested families and family files and catalogue files on a drive will have been renamed to match rename directives.

A file containing the changed families has been created.

    - File name: ChangedFilesTaskList
    - File extension: '.csv'
    - File location: _Users\userName\_Output
    - File type: comma separated
    - Header row: yes
    - Columns (3):

        - file Name:    the family name
        - file Path:    the fully qualified file path
        - revit category:   the revit family category

Inputs
~~~~~~~~~~

: Input_RenameFamilies.rst
