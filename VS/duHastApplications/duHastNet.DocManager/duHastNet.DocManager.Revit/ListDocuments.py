# -*- coding: utf-8 -*-
"""
Document Manager - List Documents
Proof of Concept: Display documents from database in WPF grid
"""

# Import .NET assemblies
import clr
import sys

# Add reference to WPF assemblies
clr.AddReference('PresentationFramework')
clr.AddReference('PresentationCore')
clr.AddReference('WindowsBase')
clr.AddReference('System.Xaml')

# Add reference to DocManager assemblies
# NOTE: Update these paths to match your actual assembly locations
doc_manager_core_path = r"C:\Development\DocManager\bin\duHastNet.DocManager.Core.dll"
doc_manager_ui_path = r"C:\Development\DocManager\bin\duHastNet.DocManager.UI.PyRevit.dll"

clr.AddReferenceToFileAndPath(doc_manager_core_path)
clr.AddReferenceToFileAndPath(doc_manager_ui_path)

# Import .NET types
from System.Windows import Application
from duHastNet.DocManager.UI.PyRevit import PyRevitDocumentWindow

# Import PyRevit modules
from pyrevit import script

__title__ = "List Documents"
__author__ = "Jan Christel"
__doc__ = """Displays all documents from a hardcoded database path in a WPF grid.
This is a proof of concept demonstrating integration of DocManagerSync with PyRevit."""


def main():
    """
    Main entry point for the PyRevit script
    Creates and shows the WPF window
    """
    try:
        # Create the WPF window
        window = PyRevitDocumentWindow()
        
        # Show the window (modal)
        window.ShowDialog()
        
    except Exception as ex:
        # Display error in PyRevit output window
        output = script.get_output()
        output.print_md("## Error Loading Document Manager")
        output.print_md("**Error Message:**")
        output.print_md(str(ex))
        output.print_md("\n**Please check:**")
        output.print_md("- Database path is correct in PyRevitDocumentListViewModel.cs")
        output.print_md("- Assembly references are correct in this script")
        output.print_md("- All required DLLs are available")


if __name__ == "__main__":
    main()
