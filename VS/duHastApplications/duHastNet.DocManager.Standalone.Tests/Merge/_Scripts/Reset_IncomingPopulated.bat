@echo off
echo Running Incoming Clean...
call CleanOut_Incoming.bat

echo Running Current Folder(s) Clean...
call CleanOut_CurrentFolderSystem.bat

echo Running populate Incoming...
call CopyFiles_Incoming.bat

echo All scripts completed!
pause