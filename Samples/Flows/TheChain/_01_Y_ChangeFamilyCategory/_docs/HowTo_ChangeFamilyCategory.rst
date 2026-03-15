#############################################
Modify Families - Change Family Category
#############################################

Summary
=======

This flow changes the family existing category to a new category. Any existing custom sub-categories will be recreated under the new category and items reassigned to them.

Script flow diagram
--------------------------------


Outcomes
--------------------------------

- Processed families belong to a new category.
- A file containing the changed families has been created.

    - File name: ChangedFilesTaskList
    - File extension: '.csv'
    - File location: '\_Users\USERNAME\_Output'
    - File type: comma separated
    - Header row: yes
    - Columns (3):

        - file Name:    the family name
        - file Path:    the fully qualified file path
        - Revit category:   the Revit family category


Inputs
~~~~~~~~~~

`Input_ChangeFamilyCategory <Input_ChangeFamilyCategory.rst>`_

Setup
~~~~~~~~~~

Script
^^^^^^^^^^^^^

utilModify.py

- REVIT_LIBRARY_PATH : root directory of Revit family library to be processed

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