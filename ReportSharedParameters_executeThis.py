#!/usr/bin/python
# -*- coding: utf-8 -*-
import clr
import System
import datetime

# flag whether this runs in debug or not
debug = False

# --------------------------
#default file path locations
# --------------------------
#store output here:
rootPath = r'C:\temp'
#path to Common.py
commonlibraryDebugLocation = r'C:\temp'
#debug mode revit project file name
debugRevitFileName = r'C:\temp\Test.rvt'

# Add batch processor scripting references
if not debug:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
     # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath = revit_script_util.GetRevitFilePath()
else:
    #set path to common library
    import sys
    sys.path.append(commonlibraryDebugLocation)
    #get default revit file name
    revitFilePath = debugRevitFileName

#import common library
import Common
from Common import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

from Autodesk.Revit.DB import *
from System.IO import Path, Directory

# -------------
# my code here:
# -------------

#get date prefix for file name
d = datetime.datetime.now()
filePrefix = d.strftime("%y_%m_%d")

#build output file name
fileName = rootPath + '\\'+ filePrefix + '_' + Path.GetFileName(revitFilePath) + '.txt'

#method writing out shared parameter information
def writeSharedData(doc, fileName):
    status = True
    try:
        f = open(fileName, "w")
        f.write("\t".join(["GUID", "ID", "NAME", "\n"]))
        for p in FilteredElementCollector(doc).OfClass(SharedParameterElement):
            f.write("\t".join([p.GuidValue.ToString(), str(p.Id.IntegerValue), Element.Name.GetValue(p), "\n"]))
        f.close()
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName, debug)
        Output (str(e), debug)
    return status

# -------------
# main:
# -------------

Output('Writing Shared Parameter Data.... start', debug)

#write out shared parameter data
result = writeSharedData(doc, fileName)

Output('Writing Shared Parameter Data.... status: ' + str(result), debug)
Output('Writing Shared Parameter Data.... finished ' + fileName, debug)