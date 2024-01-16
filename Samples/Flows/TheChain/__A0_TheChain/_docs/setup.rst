#############################################
Setting Up - The Chain
#############################################

- copy folder structure from:
    \\bvn\Data\studio\infotech\standards\Scripts\Revit Python\RBP\Workflows\TheChain
    to your project folder location

- change file path in all settings files in all _default folders per work flow: (use visual studio code: find and replace in files)

    - "taskScriptFilePath": "\\\\bvn\\data\\studio\\SharedAssets\\Revit\\RevitContent\\CentralHealthLibrary\\04 BatchP\\_00_ReportFamilyData\\_Script\\ReportFamilyData.py",
    - "revitFileListFilePath": "\\\\bvn\\data\\studio\\SharedAssets\\Revit\\RevitContent\\CentralHealthLibrary\\04 BatchP\\_00_ReportFamilyData\\_Users\\jchristel\\_TaskList\\Tasklist_1.txt",
    - "dataExportFolderPath": "\\\\bvn\\data\\studio\\SharedAssets\\Revit\\RevitContent\\CentralHealthLibrary\\04 BatchP\\_00_ReportFamilyData\\_Users\\jchristel\\_Users\\jchristel\\SessionData",
    - "preProcessingScriptFilePath": "\\\\bvn\\data\\studio\\SharedAssets\\Revit\\RevitContent\\CentralHealthLibrary\\04 BatchP\\_00_ReportFamilyData\\_Script\\Pre_FirstTask.py",
    - "PostProcessingScriptFilePath": "\\\\bvn\\data\\studio\\SharedAssets\\Revit\\RevitContent\\CentralHealthLibrary\\04 BatchP\\_00_ReportFamilyData\\_Script\\Post_BVNRevitFileSaveAsWSMKillOnly.py",

- check revit version in _default settings to match your required version

    - "singleRevitTaskRevitVersion": "Revit2020"
    - "batchRevitTaskRevitVersion": "Revit2020"

- change file path to revit library in python util files:
    
    - Report (utilModifyBVN.py), Modify (utilModifyBVN.py) & Reload (utilReloadBVN.py):

        - REVIT_LIBRARY_PATH = r'\\bvn\data\studio\SharedAssets\Revit\RevitContent\CentralHealthLibrary\_Kinship'

- run setupUser.bat located in ___A0_TheChain to create a user specific folder in each flow. Note: without a user specific folder the flow will not work.