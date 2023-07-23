'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Link instance workset updates - by type.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to change revit link instances worksets to the same as the corresponding revit link type workset.

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
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

# this sample demonstrates how to move revit link instances onto the same workset than the corresponding link type

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
from duHast.Utilities import utility as util
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common import transaction as rTran

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = True

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
    #get default revit file name
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

def _getRevitLinkTypeDataByName(revitLinkName, doc):
    '''
    Returns the Revit link type workset Id.

    :param revitLinkName: The revit link name
    :type revitLinkName: str
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Revit link type workset Id, or Invalid Element Id
    :rtype: AutoDesk.Revit.DB.ElementId
    '''

    # default values
    typeWorksetName = 'unknown'
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType):
        # Output('['+str(revitLinkName)+'][' + str(Element.Name.GetValue(p))+']')
        if (rdb.Element.Name.GetValue(p) == revitLinkName):
            wsparam = p.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
            typeWorksetName = wsparam.AsValueString()
            break
    return rWork.get_workset_id_by_name(doc, typeWorksetName)

def _modifyRevitLinkInstanceData(revitLink, doc):
    '''
    Changes the workset of a revit link instance belonging to a particular type to the same workset as the revit link type it belongs to.

    :param revitLink: The revit link instance
    :type revitLink: AutoDesk.Revit.DB.RevitLinkInstance
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - Result.status: True if a link instance was successfully moved to a new workset, otherwise False.
        - Result.message: A status message for the link instance.
        - Result.result is empty list

        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    #get the workset ot the revit link instance
    wsparam = revitLink.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
    instanceWorksetName = wsparam.AsValueString()
    instanceWorksetId = rWork.get_workset_id_by_name(doc, instanceWorksetName)

    lN = "unknown"
    #split revit link name at colon
    linkTypeNameParts = revitLink.Name.split(':')
    if(len(linkTypeNameParts) == 3):
        lN = linkTypeNameParts[0]
        #get the link type data before extension is stripped from the name,
        # strip space of end of name too
        typeWorksetId = _getRevitLinkTypeDataByName(lN[0:-1], doc)
        typeWorksetName = rWork.get_workset_name_by_id(doc, typeWorksetId)
        #revit will return a -1 if link is not loaded...
        if(typeWorksetId != rdb.ElementId.InvalidElementId):
            linkInstanceNameEncoded = util.encode_ascii(lN[0:-1])
            if(instanceWorksetId != typeWorksetId):
                output('Moving '+ str(linkInstanceNameEncoded) + ' from ' + str(instanceWorksetName) + ' to ' + str(typeWorksetName))
                transaction = rdb.Transaction(doc, "Changing workset of " + linkInstanceNameEncoded)
                returnValue = rTran.in_transaction(transaction,  rWork.get_action_change_element_workset(revitLink, typeWorksetId))
                output(linkInstanceNameEncoded + ' ' + str(returnValue.status))
            else:
               returnValue.message = str(linkInstanceNameEncoded + ' is already on default workset ' + str(typeWorksetName))
        else:
          returnValue.message = str('Link is not loaded' + str(util.encode_ascii(lN[0:-1])))
    else:
        returnValue.update_sep(False, 'Failed to split link name into 3 parts')
    return returnValue

def modifyRevitLinkInstance(doc):
    '''
    Method moving all revit link instances to the same workset as their corresponding types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - Result.status: True if all link instance where moved to the same workset as the corresponding link type, otherwise False.
        - Result.message: A status message for each link instance.
        - Result.result is empty list

        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.

    :rtype: :class:`.Result`
    '''
    
    returnValue = res.Result()
    try:
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkInstance):
            changeLink = _modifyRevitLinkInstanceData(p, doc)
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
result_ = modifyRevitLinkInstance(DOC)
output('{} [{}]'.format(result_.message, result_.status))

#sync changes back to central
if (DOC.IsWorkshared and DEBUG == False):
    output('Syncing to Central: start')
    syncing_ = rFileIO.sync_file (DOC)
    output('Syncing to Central: finished [{}]'.format(syncing_.status))

output('Modifying Revit Link(s).... finished ')
