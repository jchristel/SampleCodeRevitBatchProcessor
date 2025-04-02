@echo off

IF [%5]==[] (
  echo ERROR : One or more arguments are missing.
  exit
)

set DeploymentDir=\\syd-file\Practice\InfoTech\Scripting\BvnRpmPlugins

set ConfigurationName=%~1
set ProjectDir=%~dp2
set TargetDir=%~dp3
set PluginName=%~4
set PluginVersion=%~5

echo.
echo ********************************************************************************



echo.
echo Copying plugin files to the plugin deployment folder...
echo   [from: %TargetDir%]
echo   [to: %PluginDeploymentDir%\]

xcopy /E /Q "%TargetDir%"* %PluginDeploymentDir%\

IF ERRORLEVEL 1 (
  echo ERROR: Could not copy all plugin files to the plugin deployment folder!
  exit
) ELSE (
  echo   Done.
)


echo.