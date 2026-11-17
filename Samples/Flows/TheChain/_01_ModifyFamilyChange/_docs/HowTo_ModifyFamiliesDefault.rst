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

    - Removes any unused line patterns, taking nested families into account.

- Purge unused shared parameter definitions

    - Removes any shared parameter definitions, taking nested families into account.
    - Note: shared parameter definitions introduced to the family through a template can not be deleted.

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
        - Revit category:   the Revit family category


Inputs
~~~~~~~~~~

`Input_ModifyFamiliesDefault <Input_ModifyFamiliesDefault.rst>`_

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