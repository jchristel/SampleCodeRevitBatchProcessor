#############################################
Setting Up - The Chain
#############################################

Requirements
============

- Windows PowerShell 5.1 (part of Windows) or PowerShell 7
- `Revit Batch Processor <https://github.com/bvn-architecture/RevitBatchProcessor>`_
- IronPython 3.4, used to run the pre and post processing scripts of each flow
- the duHast library

Set up
======

- copy the TheChain folder to your project folder location

- edit __A0_TheChain\\TheChainSettings.ps1:

    - chain_utils_path : the shared PowerShell helpers, Samples\\PowerShell\\BatchProcessorUtils.ps1 in this repository.
      The default works while The Chain is inside the repository. When The Chain is copied elsewhere, point this at a copy of that file.
    - iron_python_path : IronPython (default: C:\\Program Files\\IronPython 3.4\\ipy.exe)
    - batch_processor_path : Revit Batch Processor (default: the per user install location, %LOCALAPPDATA%\\RevitBatchProcessor\\BatchRvt.exe)

- in each flow's _Script\\settings.py:

    - DU_HAST_PATH : where the duHast library is installed
    - REVIT_LIBRARY_PATH : the root directory of your Revit family library (also in _01_X_RenameFamilies\\_Script\\utilModify.py
      and _02_ModifyFamilyLibraryReloadAdvanced\\_Script\\utilReload.py)

- check the Revit version in the settings files in each flow's _Users\\_default\\_Settings folder matches your required version:

    - "singleRevitTaskRevitVersion": "Revit2024"
    - "batchRevitTaskRevitVersion": "Revit2024"

- run setupUsers.ps1 located in __A0_TheChain to create a user specific folder in each flow:

    .. code-block:: powershell

        powershell -ExecutionPolicy Bypass -File setupUsers.ps1

  It copies each flow's _Users\\_default folder to _Users\\YOURUSERNAME and points the paths in the settings files in it at your
  user folder, wherever The Chain is located. Note: without a user specific folder the flows will not run.

  After moving or copying The Chain to another location, run it again with -RefreshSettings to update the paths in the settings
  files of user folders that exist already:

    .. code-block:: powershell

        powershell -ExecutionPolicy Bypass -File setupUsers.ps1 -RefreshSettings
