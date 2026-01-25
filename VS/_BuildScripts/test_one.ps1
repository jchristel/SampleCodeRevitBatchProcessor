param(
    [Parameter(Mandatory=$true)]
    [string]$NewVersion,
    [string]$OldVersion,
    [switch]$WhatIf,
    [int]$StartFromSolution = 1,
    [string]$BuildConfig = "Release"
)

Write-Host "Script started successfully!" -ForegroundColor Green
Write-Host "NewVersion: $NewVersion" -ForegroundColor Cyan