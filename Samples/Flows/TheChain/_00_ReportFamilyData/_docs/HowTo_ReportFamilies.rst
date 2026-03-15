#############################################
Reporting Families
#############################################

Summary
=======

The reporting flow will process all families in a given library and output the following reports:

- `FamilyBaseDataCombinedReport <FamilyBaseDataCombinedReport.rst>`_
- `FamilyCategoriesCombinedReport <FamilyCategoriesCombinedReport.rst>`_
- `FamilyLinePatternsCombinedReport <FamilyLinePatternsCombinedReport.rst>`_
- `FamilySharedParametersCombinedReport <FamilySharedParametersCombinedReport.rst>`_
- `FamilyWarningsCombinedReport <FamilyWarningsCombinedReport.rst>`_

After all families are processed, the flow will analyze some of the above reports and create the following additional reports:

- FamilyBaseDataCombined:

    - `CircularReferences <CircularReferencesReport.rst>`_
    - `MissingFamilies <MissingFamiliesReport.rst>`_
    - `MissingFamiliesHostsReport <MissingFamiliesHostsReport.rst>`_

- Batchprocessor log files:

    - ProcessExceptions
    - SecondProcessFamilies

All the above reports are located in:

- _Users\username\_Output
- _Users\username\_Analysis\currentDateFolder
- _Users\username\_Analysis\_Current


This flow can be used in 'follow-up mode'. In this mode all reports created from a sub set of families analysed, will be used to update a current set of reports.
Typical example would be to run two report flows sequentially: The first run will attempt to analyse all families in a given library. However, in large libraries (2k + families), more often then not, some process exceptions will occur
in the first run. The second run, in 'follow - up mode', will process only families in which the process exceptions occurred and will add that data to the overall data set from the first run.

Inputs
~~~~~~~~~~

`Input_ReportFamilies  <Input_ReportFamilies.rst>`_

Setup
~~~~~~~~~~

Script
^^^^^^^^^^^^^

utilData.py

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
