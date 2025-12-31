@echo off
echo Running Incoming Clean...
call CleanOut_Incoming.bat

echo Running populate Incoming...
call CopyFiles_Incoming.bat

echo All scripts completed!
pause