@echo off
echo Running Incoming Clean...
call CleanOut_Incoming.bat

echo Running Current Folder(s) Clean...
call CleanOut_CurrentFolderSystem.bat

echo Running ArchiveClean...
call CleanOut_Archive.bat

echo All scripts completed!
pause