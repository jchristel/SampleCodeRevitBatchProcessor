#############################################
Report Families - Save out missing families
#############################################

Summary
=======

This flow saves out any nested family during processing, which does not have a matching root family entry in a provided base data combined report file. Families are saved into separate folders per their Revit category.


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

`Input_SaveOutMissingFamilies <Input_SaveOutMissingFamilies.rst>`_

Setup
~~~~~~~~~~

Script
^^^^^^^^^^^^^

utilData.py

- REVIT_FILES_DIRECTORY : root directory of Revit family library to be processed

User
^^^^^^
User specific folder will be set up by the setupUsers.ps1 script in the __A0_TheChain folder (see the set up notes of The Chain). Note: this flow will not execute if no user specific folder is present!

setupUsers.ps1 points the directory paths in the settings files in __\_Users\YOURUSERNAME\_Settings at your user folder. If needed, update by hand:

        - "singleRevitTaskRevitVersion" and "batchRevitTaskRevitVersion" : update Revit version