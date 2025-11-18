# DocManagerLauncher.py
import clr
import sys

# Add references to required assemblies
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
clr.AddReference("System.Xaml")

DLL_PATH = r"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\duHastNet.DocManager\duHastNet.DocManager.Revit\bin\x64\Debug\net8.0-windows\win-x64"
# Add path to your DLLs (adjust as needed)
sys.path.append(DLL_PATH)

clr.AddReference("duHastNet.DocManager.Core")
clr.AddReference("duHastNet.DocManager.UI.Shared")

from duHastNet.DocManager.UI.Shared.Services import DocManagerBootstrapper

# Create bootstrapper and initialize
bootstrapper = DocManagerBootstrapper()
window = bootstrapper.Initialize()  # Uses synchronous version
window.ShowDialog()  # Blocking call - script waits until window closes