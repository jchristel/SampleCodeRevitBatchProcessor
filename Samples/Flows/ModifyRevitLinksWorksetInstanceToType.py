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
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'
# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_Files.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import libraries
from duHast.Revit.Common import file_io as rFileIO
from duHast.Revit.Common import worksets as rWork
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common import transaction as rTran

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = False

# Add batch processor scripting references
if not DEBUG:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    # NOTE: these only make sense for batch Revit file processing mode.
    DOC = revit_script_util.GetScriptDocument()
    REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name
    REVIT_FILE_PATH = DEBUG_REVIT_FILE_NAME
    # get document from python shell
    DOC = doc

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not DEBUG:
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
        return rWork.get_workset_id_by_name(doc, instanceWorksetName)
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
    typeWorksetId = rWork.get_workset_id_by_name(doc, typeWorksetName)

    # get the workset id of a link instance belonging to same type
    instanceWorksetId = _getRevitInstanceDataByName(revitLink, doc)
    instanceWorksetName = rWork.get_workset_name_by_id(doc, instanceWorksetId.IntegerValue)

    # check if revit link type needs the workset changed?
    if(instanceWorksetId!= rdb.ElementId.InvalidElementId and instanceWorksetId != typeWorksetId):
        output('Moving '+ str(rdb.Element.Name.GetValue(revitLink)) + ' from ' + str(typeWorksetName) + ' to ' + str(instanceWorksetName))
        transaction = rdb.Transaction(doc, "Changing workset of " + str(rdb.Element.Name.GetValue(revitLink)))
        returnValue = rTran.in_transaction(transaction, rWork.get_action_change_element_workset(revitLink,instanceWorksetId))
        output(str(rdb.Element.Name.GetValue(revitLink)) + ' ' + str(returnValue.status))
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
            returnValue.update(changeLink)
    except Exception as e:
        returnValue.update_sep(False, 'Failed to modify revit link instances with exception: ' + str(e))
    return returnValue

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# modify revit links
output('Modifying Revit Link(s).... start')
result_ = modifyRevitLinkTypes(DOC)
output('{} [{}]'.format(result_.message, result_.status))

# sync changes back to central
if (DOC.IsWorkshared and DEBUG == False):
    output('Syncing to Central: start')
    syncing_ = rFileIO.sync_file (DOC)
    output('Syncing to Central: finished [{}]'.format(syncing_.status))
output('Modifying Revit Link(s).... finished ')