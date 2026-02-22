# PowerShell script to copy files from \Views and \ViewModels directories,
# plus .csproj files, from project folders to a temp folder

# Define your project paths here
$project1Path = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastUICustomControls"
$project2Path = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastUI"
$project3Path = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastRevitApplications"
$project4Path ="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\duHastNet.DocManager.UI.Shared.Tests"
$project5Path ="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\duHastNet.DocManager\duHastNet.docs"
$project6Path ="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastUI\DocManagerSettingsUI"

$project7Path ="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastUtils\Utils"
$project8Path ="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\duHastNet.DocManager"
$project9Path ="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastUICustomControls\duHastUICustomControls"

# Define the temp folder destination
$tempFolder = "$env:TEMP\ProjectFilesCopy"

# Clean out the temp folder if it already exists, then create it fresh
if (Test-Path -Path $tempFolder) {
    Write-Host "Cleaning existing temp folder: $tempFolder" -ForegroundColor Yellow
    Remove-Item -Path $tempFolder -Recurse -Force
}

New-Item -ItemType Directory -Path $tempFolder -Force | Out-Null
Write-Host "Created temp folder: $tempFolder" -ForegroundColor Green

# Function to copy files from a project
function Copy-ProjectFiles {
    param (
        [string]$sourcePath,
        [string]$projectName,
        [string]$destination
    )
    
    if (-not (Test-Path -Path $sourcePath)) {
        Write-Host "Warning: Source path not found: $sourcePath" -ForegroundColor Yellow
        return
    }

    $fileCount = 0

    # --- Copy .csproj files (from root and subdirectories) ---
    $csprojFiles = Get-ChildItem -Path $sourcePath -Include *.csproj -Recurse -File

    foreach ($file in $csprojFiles) {
        $destinationFile = Join-Path -Path $destination -ChildPath $file.Name
        $counter = 1
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
        $extension = $file.Extension

        while (Test-Path -Path $destinationFile) {
            $newName = "${baseName}_${counter}${extension}"
            $destinationFile = Join-Path -Path $destination -ChildPath $newName
            $counter++
        }

        Copy-Item -Path $file.FullName -Destination $destinationFile -Force
        $fileCount++
    }

    # --- Copy .cs and .xaml files only from \Views and \ViewModels directories ---
    $targetFolderNames = @("Views", "ViewModels")

    $allDirs = Get-ChildItem -Path $sourcePath -Recurse -Directory | Where-Object {
        $targetFolderNames -contains $_.Name
    }

    foreach ($dir in $allDirs) {
        $files = Get-ChildItem -Path $dir.FullName -Include *.cs, *.xaml -Recurse -File | Where-Object {
            $_.Name -notmatch '\.g\.cs$' -and
            $_.Name -notmatch '\.g\.i\.cs$' -and
            $_.Name -notmatch '\.g\.i_1\.cs$' -and
            $_.Name -notmatch 'AssemblyInfo' -and
            $_.Name -notmatch 'AssemblyAttributes'
        }

        foreach ($file in $files) {
            $destinationFile = Join-Path -Path $destination -ChildPath $file.Name
            $counter = 1
            $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
            $extension = $file.Extension

            while (Test-Path -Path $destinationFile) {
                $newName = "${baseName}_${counter}${extension}"
                $destinationFile = Join-Path -Path $destination -ChildPath $newName
                $counter++
            }

            Copy-Item -Path $file.FullName -Destination $destinationFile -Force
            $fileCount++
        }
    }

    Write-Host "Copied $fileCount files from $projectName" -ForegroundColor Cyan
}

# Copy files from both projects
Write-Host "`nCopying files from Project 1..." -ForegroundColor White
Copy-ProjectFiles -sourcePath $project1Path -projectName "Project1" -destination $tempFolder

Write-Host "`nCopying files from Project 2..." -ForegroundColor White
Copy-ProjectFiles -sourcePath $project2Path -projectName "Project2" -destination $tempFolder

Write-Host "`nCopying files from Project 3..." -ForegroundColor White
Copy-ProjectFiles -sourcePath $project3Path -projectName "Project3" -destination $tempFolder

# Write-Host "`nCopying files from Project 4..." -ForegroundColor White
# Copy-ProjectFiles -sourcePath $project4Path -projectName "Project4" -destination $tempFolder

# Write-Host "`nCopying files from Project 5..." -ForegroundColor White
# Copy-ProjectFiles -sourcePath $project5Path -projectName "Project5" -destination $tempFolder

# Write-Host "`nCopying files from Project 6..." -ForegroundColor White
# Copy-ProjectFiles -sourcePath $project6Path -projectName "Project6" -destination $tempFolder

Write-Host "`nCopying files from Project 7..." -ForegroundColor White
Copy-ProjectFiles -sourcePath $project7Path -projectName "Project7" -destination $tempFolder

#Write-Host "`nCopying files from Project 8..." -ForegroundColor White
#Copy-ProjectFiles -sourcePath $project8Path -projectName "Project8" -destination $tempFolder

#Write-Host "`nCopying files from Project 9..." -ForegroundColor White
#Copy-ProjectFiles -sourcePath $project9Path -projectName "Project9" -destination $tempFolder

Write-Host "`nAll files copied successfully to: $tempFolder" -ForegroundColor Green
Write-Host "Opening destination folder..." -ForegroundColor Gray

# Open the temp folder in Windows Explorer
explorer.exe $tempFolder