#############################################
The Chain
#############################################

Summary
=======

The chain consists of three workflows aimed at en mass family updates:

- Reporting - of family properties : HowTo_RenameFamilies.rst
- Changing - Specific families with specific actions : HowTo_RenameFamilies.rst
- Changing - All families with a default set of actions : HowTo_ModifyFamiliesDefault.rst
- Reloading - nested families into host families : HowTo_ReloadFamilies.rst

Putting it all together
=======================

The batch script 'theChain.bat' executes the 3 workflows in the following order:

#. Changing
#. Reloading
#. Reporting

In between executing flows it will copy the following files from the flow just finished to the one about to be executed:

#. Changing

    * Change list ChangedFilesTaskList.csv 
    
        * from folder:  __\_01_ModifyFamilyChange\_Output
        * to folder: __\_02_ModifyFamilyLibraryReloadAdvanced\_Input

#. Reloading

    * no files copied to next flow

#. Reporting

    * FamilyBaseDataCombinedReport.csv
    
        * from folder: __\_00_ReportFamilyData\_Output\userName
        * to folders:
            
            * __\_00_ReportFamilyData\_Analysis\YYMMDD
            * __\_00_ReportFamilyData\_Analysis\_Current
            * __\_01_ModifyFamilyChange\_Input
            * __\_02_ModifyFamilyLibraryReloadAdvanced\_Input