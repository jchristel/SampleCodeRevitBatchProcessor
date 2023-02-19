'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Link type workset updates - by instance.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to change revit link type workset to the same as the first revit link instance of the same type.

Notes:

- Revit Batch Processor settings:
    
    - open local copy of model
    - open all worksets

'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# this sample demonstrates how to move revit link types onto the same workset than the corresponding link instance

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
commonLibraryLocation_ = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
scriptLocation_ = r'C:\temp'
# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_Files.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import libraries
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitWorksets as rWork
from duHast.Utilities import Result as res

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name
    revitFilePath_ = debugRevitFileName_

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)
    
def _getRevitInstanceDataByName(revitLinkName, doc):
    '''
    returns Revit Link Instance data

    :param revitLinkName: The revit link name of which to return an instance Id
    :type revitLinkName: str
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A link instance Id if an instance of a given link was found, otherwise Invalid element Id (-1)
    :rtype: AutoDesk.Revit.DB.ElementId
    '''

    match = False
    # default values
    instanceWorksetName = 'unknown'
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkInstance):
        # Output('['+str(Element.Name.GetValue(revitLinkName))+'][' + str(Element.Name.GetValue(p))+']')
        linkTypeNameParts = rdb.Element.Name.GetValue(p).split(':')
        if(len(linkTypeNameParts) == 3):
            lN = linkTypeNameParts[0]
            if(lN[0:-1] == rdb.Element.Name.GetValue(revitLinkName)):
                match = True
                wsparam = p.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
                instanceWorksetName = wsparam.AsValueString()
                break
    if(match == True):
        # Output(instanceWorksetName)
        return rWork.GetWorksetIdByName(doc, instanceWorksetName)
    else:
        # Output('no match')
        return rdb.ElementId.InvalidElementId

def _modifyRevitLinkTypeData(revitLink, doc):
    '''
    Modifies the workset of an individual link type if not the same as an instance of that type.

    :param revitLink: A revit link type.
    :type revitLink: AutoDesk.Revit.DB.RevitLinkType
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - Result.status: True if link type was moved to a new worksets successfully or if it was on required workset already, otherwise False.
        - Result.message: A status message for each link type.
        - Result.result is empty list

        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()

    # get the workset Id of the link type
    wsparam = revitLink.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
    typeWorksetName = wsparam.AsValueString()
    typeWorksetId = rWork.GetWorksetIdByName(doc, typeWorksetName)

    # get the workset id of a link instance belonging to same type
    instanceWorksetId = _getRevitInstanceDataByName(revitLink, doc)
    instanceWorksetName = rWork.GetWorksetNameById(doc, instanceWorksetId.IntegerValue)

    # check if revit link type needs the workset changed?
    if(instanceWorksetId!= rdb.ElementId.InvalidElementId and instanceWorksetId != typeWorksetId):
        Output('Moving '+ str(rdb.Element.Name.GetValue(revitLink)) + ' from ' + str(typeWorksetName) + ' to ' + str(instanceWorksetName))
        transaction = rdb.Transaction(doc, "Changing workset of " + str(rdb.Element.Name.GetValue(revitLink)))
        returnValue = com.InTransaction(transaction, rWork.GetActionChangeElementWorkset(revitLink,instanceWorksetId))
        Output(str(rdb.Element.Name.GetValue(revitLink)) + ' ' + str(returnValue.status))
    else:
        returnValue.message = str(rdb.Element.Name.GetValue(revitLink)) + ' is already on default workset ' + str(instanceWorksetName)
    return returnValue

# 
def modifyRevitLinkTypes(doc):
    '''
    Method changing the workset of Revit link types if not on the same workset than the corresponding Revit link instance

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - Result.status: True if all link types where moved to the same workset as the link instance of the same type, otherwise False.
        - Result.message: A status message for each link type.
        - Result.result is empty list

        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType):
            changeLink = _modifyRevitLinkTypeData(p, doc)
            returnValue.Update(changeLink)
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to modify revit link instances with exception: ' + str(e))
    return returnValue

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# modify revit links
Output('Modifying Revit Link(s).... start')
result_ = modifyRevitLinkTypes(doc)
Output(str(result_.message) + ' ' + str(result_.status))

# sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))
Output('Modifying Revit Link(s).... finished ')