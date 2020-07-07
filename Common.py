#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import datetime
import System
from System.IO import Path
from Autodesk.Revit.DB import *
import os.path as path

#get a time stamp in format year_month_day
def GetFileDateStamp():
    d = datetime.datetime.now()
    return d.strftime('%y_%m_%d')

#returns an time stamped output file name based on the revit file name
#file extension needs to include '.', default is '.txt'
#file suffix will be appended after the name but before the file extension. Default is blank.
def GetOutPutFileName(revitFilePath, fileExtension = '.txt', fileSuffix = ''):
    #get date prefix for file name
    filePrefix = GetFileDateStamp()
    name = Path.GetFileNameWithoutExtension(revitFilePath)
    return filePrefix + '_' + name + fileSuffix + fileExtension

# returns the revit file name without the file extension
def GetRevitFileName(revitFilePath):
    name = Path.GetFileNameWithoutExtension(revitFilePath)
    return name

#removes '..\..' or '..\' from relative file path supplied by Revit and replaces it with full path derived from Revit document
def ConvertRelativePathToFullPath(relativeFilePath, fullFilePath):
    if( r'..\..' in relativeFilePath):
        two_up = path.abspath(path.join(fullFilePath ,r'..\..'))
        return two_up + relativeFilePath[5:]
    elif('..' in relativeFilePath):
        one_up = path.abspath(path.join(fullFilePath ,'..'))
        return one_up + relativeFilePath[2:]
    else:
        return relativeFilePath
    
#transaction wrapper
#returns:
#   - False if something went wrong
#   - None if the action has no return value specified 
#   - return the outcome of the action or None if that is the outcome...
def InTransaction(tranny, action):
    result = None
    tranny.Start()
    try:
        result = action()
        tranny.Commit()
    except Exception as e:
        tranny.RollBack()
        result = False
    return result

#synchronises a Revit central file
#returns:
#   - true if sync without exception been thrown
#   - false if an exception occured
def SyncFile (doc):
    result = True
    # set up sync settings
    ro = RelinquishOptions(True)
    transActOptions = TransactWithCentralOptions()
    sync = SynchronizeWithCentralOptions()
    sync.Comment = 'Synchronised by Revit Batch Processor'
    sync.SetRelinquishOptions(ro)
    #Synch it
    try:
        #save local first ( this seems to prevent intermittend crash on sync(?))
        doc.Save()
        doc.SynchronizeWithCentral(transActOptions, sync)
        #relinquish all
        WorksharingUtils.RelinquishOwnership(doc, ro, transActOptions)
    except Exception as e:
        result = False
    return result

#saves a new central file to given location
def SaveAsWorksharedFile(doc, fullFileName):
    result = True
    try:
        workSharingSaveAsOption = WorksharingSaveAsOptions()
        workSharingSaveAsOption.OpenWorksetsDefault = SimpleWorksetConfiguration.AskUserToSpecify
        workSharingSaveAsOption.SaveAsCentral = True
        saveOption = SaveAsOptions()
        saveOption.OverwriteExistingFile = True
        saveOption.SetWorksharingOptions(workSharingSaveAsOption)
        saveOption.MaximumBackups = 5
        saveOption.Compact = True
        doc.SaveAs(fullFileName, saveOption)
    except Exception:
        result = False
    return result
    
#encode string as ascii and replaces all non ascii characters
def EncodeAscii (string):
    return string.encode('ascii','replace')
