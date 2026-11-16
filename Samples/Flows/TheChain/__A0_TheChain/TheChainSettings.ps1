# Settings for The Chain: edit these to match your machine.
# Loaded by TheChainCommon.ps1, which every script of The Chain loads first.

# Shared PowerShell helpers: Samples\PowerShell\BatchProcessorUtils.ps1 in this repository.
# When The Chain is copied out of the repository, point this at a copy of that file.
$chain_utils_path = Join-Path $PSScriptRoot "..\..\..\PowerShell\BatchProcessorUtils.ps1"

# IronPython used to run the pre and post processing scripts of each flow
$iron_python_path = "C:\Program Files\IronPython 3.4\ipy.exe"

# Revit Batch Processor (default: the per user install location)
$batch_processor_path = Join-Path $env:LOCALAPPDATA "RevitBatchProcessor\BatchRvt.exe"

# Revit Batch Processor sessions started per flow, one per settings file: ...OneA... to ...OneD...
# (needs to match NUMBER_OF_TASK_FILES / TASK_FILE_NO in each flow's settings.py)
$chain_session_letters = @("A", "B", "C", "D")
