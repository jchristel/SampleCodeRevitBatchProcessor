@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build

REM Root of the repository (one level up from docsource/)
set REPOROOT=%~dp0..

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help

REM Custom target: copy Revit app UI docs then run a full html build
if "%1" == "ui-html" goto ui-html

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

REM ---------------------------------------------------------------------------
:ui-html
echo.
echo.Copying Revit app UI documentation into docsource...
echo.

REM Revit add-ins
if not exist "%SOURCEDIR%\revit_apps\pushit" mkdir "%SOURCEDIR%\revit_apps\pushit"
xcopy /Y "%REPOROOT%\VS\duHastRevitApplications\PushIt\docs\*.md" "%SOURCEDIR%\revit_apps\pushit\"

if not exist "%SOURCEDIR%\revit_apps\athelibrary" mkdir "%SOURCEDIR%\revit_apps\athelibrary"
xcopy /Y "%REPOROOT%\VS\duHastRevitApplications\AtTheLibrary\docs\*.md" "%SOURCEDIR%\revit_apps\athelibrary\"

REM WPF UI libraries
if not exist "%SOURCEDIR%\revit_apps\docmanagersettingsui" mkdir "%SOURCEDIR%\revit_apps\docmanagersettingsui"
xcopy /Y "%REPOROOT%\VS\duHastUI\DocManagerSettingsUI\docs\*.md" "%SOURCEDIR%\revit_apps\docmanagersettingsui\"

if not exist "%SOURCEDIR%\revit_apps\docmanagerui" mkdir "%SOURCEDIR%\revit_apps\docmanagerui"
xcopy /Y "%REPOROOT%\VS\duHastUI\DocManagerUI\docs\*.md" "%SOURCEDIR%\revit_apps\docmanagerui\"

if not exist "%SOURCEDIR%\revit_apps\familyreloaderui" mkdir "%SOURCEDIR%\revit_apps\familyreloaderui"
xcopy /Y "%REPOROOT%\VS\duHastUI\FamilyReloaderUI\docs\*.md" "%SOURCEDIR%\revit_apps\familyreloaderui\"

if not exist "%SOURCEDIR%\revit_apps\pdfdwgexporterui" mkdir "%SOURCEDIR%\revit_apps\pdfdwgexporterui"
xcopy /Y "%REPOROOT%\VS\duHastUI\PDFDWGExporterUI\docs\*.md" "%SOURCEDIR%\revit_apps\pdfdwgexporterui\"

if not exist "%SOURCEDIR%\revit_apps\pdfdwgexporterselectionui" mkdir "%SOURCEDIR%\revit_apps\pdfdwgexporterselectionui"
xcopy /Y "%REPOROOT%\VS\duHastUI\PDFDWGExporterSelectionUI\docs\*.md" "%SOURCEDIR%\revit_apps\pdfdwgexporterselectionui\"

if not exist "%SOURCEDIR%\revit_apps\selectfiles" mkdir "%SOURCEDIR%\revit_apps\selectfiles"
xcopy /Y "%REPOROOT%\VS\duHastUI\SelectFiles\docs\*.md" "%SOURCEDIR%\revit_apps\selectfiles\"

echo.
echo.Running sphinx-apidoc...
sphinx-apidoc -f -o "%SOURCEDIR%\duHast" "%REPOROOT%\src\duHast\"

echo.
echo.Building HTML...
%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

REM ---------------------------------------------------------------------------
:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
