#############################################
Modify Families - Default Actions
#############################################

Summary
=======

This flow purges family files from the following objects if not in use in the root family or any nested family therein.

- General purge unused using Autodesk eTransmit.

    - This mimics the UI command purge unused. Note: this step will be omitted if any nested family instance placed uses a label to change its type. 

- Purge unused sub-categories
    
    - Removes any unused sub categories, taking nested families into account.

- Purge unused line patterns

    - Removes any unsed line patterns, taking nested families into account.

- Purge unused shared parameter definitions

    - Removes any shared parameter definitions, taking nested families into account.
    - Note: shared parameter defintions introduced to the family through a template can not be deleted.

Script flow diagram
--------------------------------


Outcomes
--------------------------------

- Processed families have unused objects removed.
- A file containing the changed families has been created.

    - File name: ChangedFilesTaskList
    - File extension: '.csv'
    - File location: '\_Users\USERNAME\_Output'
    - File type: comma separated
    - Header row: yes
    - Columns (3):

        - file Name:    the family name
        - file Path:    the fully qualified file path
        - revit category:   the revit family category


Inputs
~~~~~~~~~~

: Input_SaveOutMissingFamilies.rst

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