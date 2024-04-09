###############################################
Modify Families - Change Famnily Subcategories
###############################################

Summary
=======

This flow renames custom sub categories within a family.

Note: if a custom subcategory with the new name already exists, all elements assigned to the old subcategory will be moved to that subcategory and the old subcategory will be deleted only.

Script flow diagram
--------------------------------


Outcomes
--------------------------------

- Processed families with renamed subcategories.
- A file containing the changed families has been created.

    - File name: ChangedFilesTaskList
    - File extension: '.csv'
    - File location: '\_Users\USERNAME\_Output'
    - File type: comma separated
    - Header row: yes
    - Columns (3):

        - file Name:    the family name (without file extension)
        - file Path:    the fully qualified file path
        - revit category:   the revit family category


Inputs
~~~~~~~~~~

: Input_ChangeFamilySubCategroy.rst

Setup
~~~~~~~~~~

Script
^^^^^^^^^^^^^

utilModifyBVN.py

- REVIT_LIBRARY_PATH : root directory of revit family library to be processed

User
^^^^^^
User specific folder will be set up by SetupUser.bat script in the TheChain folder. Note: this flow will not execute if no user specific folder is present! After creation, it will require manual updates:

__\_Users\YOURUSERNAME\_Settings

    - In all settings files, these properties require updating:

        - "taskScriptFilePath" : update directory path
        - "revitFileListFilePath" : update directory path
        - "dataExportFolderPath" : update directory path
        - "preProcessingScriptFilePath" : update directory path
        - "PostProcessingScriptFilePath" : update directory path
        - "batchRevitTaskRevitVersion" : update Revit version