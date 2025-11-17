# -*- coding: utf-8 -*-
"""
Open DocManager
Launches the DocManager WPF application from within Revit
"""
__title__ = "Open\nDocManager"
__author__ = "Jan Christel"
__doc__ = "Launch the DocManager document management application"

# Import Python standard library
import sys
import os

# Import .NET/CLR
import clr

# Add reference to the DocManager assemblies
# These should be in the lib folder of the extension
script_dir = os.path.dirname(__file__)
lib_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))), "lib")

# Add lib directory to system path
sys.path.append(lib_dir)

# Add references to required assemblies
clr.AddReference("duHastNet.DocManager.Core")
clr.AddReference("duHastNet.DocManager.UI.Shared")

# Import the bootstrapper from UI.Shared.Services
from duHastNet.DocManager.UI.Shared.Services import DocManagerBootstrapper

# Import WPF Window to check result type
from System.Windows import Window

def main():
    """
    Main entry point for the script
    Creates and shows the DocManager window
    """
    try:
        # Create the bootstrapper
        bootstrapper = DocManagerBootstrapper()
        
        # Initialize synchronously (IronPython has limited async support)
        # This returns a WPF Window
        window = bootstrapper.Initialize()
        
        # Show the window as a modeless dialog
        # User can interact with both Revit and DocManager
        window.Show()
        
        # Alternative: Use ShowDialog() for modal behavior
        # This will block Revit until DocManager is closed
        # window.ShowDialog()
        
        print("DocManager launched successfully")
        
    except Exception as ex:
        # Show error in pyRevit output window
        print("Error launching DocManager:")
        print(str(ex))
        import traceback
        traceback.print_exc()

# Run the script
if __name__ == "__main__":
    main()
