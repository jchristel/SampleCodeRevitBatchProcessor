# -*- coding: utf-8 -*-


# pyrevit stuff
from pyrevit import revit, script, forms


import clr
import os
import sys

from System.Collections.Generic import List

# load the wrapper dll from the libs folder
# the dll is located in the libs folder of the extension, which is one level up from the current file's directory
current_directory = os.path.dirname(__file__)
parent_directory = os.path.dirname(current_directory)

# get all the lib paths from the sys.path
lib_paths = [path for path in sys.path if path.endswith(".lib")]

if not lib_paths or len(lib_paths) == 0:
    pass
else:
    for p in lib_paths:
        duHast_path = os.path.join(p, "duHast")
        # check if path exists
        if os.path.exists(duHast_path):
            # add the library path within the duHast folder to the sys.path
            duHast_lib_path = os.path.join(duHast_path, "libs")
            if os.path.exists(duHast_lib_path):
                #sys.path.append(duHast_lib_path)
                # add the wrapper dll to the clr
                pdf_dwg_exporter_ui_path = os.path.join(duHast_lib_path, r"PDFDWGExporterUI.dll")
                #print (pdf_dwg_exporter_ui_path)
                clr.AddReferenceToFileAndPath(pdf_dwg_exporter_ui_path)
                
                
            break

# import the WriteToFile class from the CSVHelperWrapper namespace
from duHastNet.UI.PDFDWGExporterUI import Main
parameter_names = List[str]()
parameter_names.Add("test")
parameter_names.Add("test2")
parameter_names.Add("test3")
main = Main(None, None, parameter_names)

main.Execute()