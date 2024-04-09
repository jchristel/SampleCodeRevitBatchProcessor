#############################################
Report Families - Save out missing families
#############################################

Summary
=======

This flow saves out any family processed which is not in a provided base data combined report file. Families are saved into separate folders per their Revit category.


Script flow diagram
--------------------------------



Outcomes
--------------------------------

Missing families have been saved out into nominated folder.

Report file listing all saved out families:

    - file location: '\_Users\USERNAME\_Output'
    - File name: SecondProcessFamilies.csv
    - file type: comma separated
    - header row: no
    - columns
        - Fully qualified file path to family saved out

Inputs
~~~~~~~~~~

: Input_SaveOutMissingFamilies.rst

Setup
~~~~~~~~~~

Script
^^^^^^^^^^^^^

utilDataBVN.py

- REVIT_FILES_DIRECTORY : root directory of revit family library to be processed

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