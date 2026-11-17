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
        - Revit category:   the Revit family category


Inputs
~~~~~~~~~~

`Input_ChangeFamilySubCategory <Input_ChangeFamilySubCategory.rst>`_

Setup
~~~~~~~~~~

Script
^^^^^^^^^^^^^

utilModify.py

- REVIT_LIBRARY_PATH : root directory of Revit family library to be processed

User
^^^^^^
User specific folder will be set up by the setupUsers.ps1 script in the __A0_TheChain folder (see the set up notes of The Chain). Note: this flow will not execute if no user specific folder is present!

setupUsers.ps1 points the directory paths in the settings files in __\_Users\YOURUSERNAME\_Settings at your user folder. If needed, update by hand:

        - "singleRevitTaskRevitVersion" and "batchRevitTaskRevitVersion" : update Revit version