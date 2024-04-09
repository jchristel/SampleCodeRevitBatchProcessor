#############################################
Reporting Families
#############################################

Summary
=======

The reporting flow will process all families in a given library and output the following reports:

- FamilyBaseDataCombinedReport : FamilyBaseDataCombinedReport.rst
- FamilyCategoriesCombinedReport : FamilyCategoriesCombinedReport.rst
- FamilyLinePatternsCombinedReport : FamilyLinePatternsCombinedReport.rst
- FamilySharedParametersCombinedReport : FamilySharedParametersCombinedReport.rst
- FamilyWarningsCombinedReport : FamilyWarningsCombinedReport.rst

After all families are processed, the flow will analyse some of the above reports and create the following additional reports:

- FamilyBaseDataCombined:

    - CircularReferences
    - MissingFamilies
    - HostsMissingFamilies

- Batchprocessor log files:

    - ProcessExceptions
    - SecondProcessFamilies

All the above reports are located in:

- _Users\username\_Output
- _Users\username\_Analysis\currentDateFolder
- _Users\jchristel\_Analysis\_Current


This flow can be used in 'follow-up mode'. In this mode all reports created from a sub set of families analysed, will be used to update a current set of reports.
Typical example would be to run two report flows sequentially: The first run will attempt to analyse all families in a given library. However, in large libraries (2k + families), more often then not, some process exceptions will occur
in the first run. The second run, in 'follow - up mode', will process only families in which the process exceptions ocurred and will add that data to the overall data set from the first run.

Inputs
~~~~~~~~~~

: Input_ReportFamilies.rst

Setup
~~~~~~~~~~

Script
^^^^^^^^^^^^^

utilDataBVN.py

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
