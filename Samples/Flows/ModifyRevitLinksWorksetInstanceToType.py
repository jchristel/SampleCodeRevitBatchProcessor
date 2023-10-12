"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Link type workset updates - by instance.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to change revit link type workset to the same as the first revit link instance of the same type.

Notes:

- Revit Batch Processor settings:
    
    - open local copy of model
    - open all worksets

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
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

# this sample demonstrates how to move revit link types onto the same workset than the corresponding link instance

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r"C:\temp"
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r"C:\temp"
# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\temp\Test_Files.rvt"

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

clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = True

# Add batch processor scripting references
if not DEBUG:
    import revit_script_util
    import revit_file_util

    clr.AddReference("RevitAPI")
    clr.AddReference("RevitAPIUI")
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
def output(message=""):
    """
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    """

    if not DEBUG:
        revit_script_util.Output(str(message))
    else:
        print(message)


def _get_revit_instance_data_by_name(revitLinkName, doc):
    """
    returns Revit Link Instance data

    :param revitLinkName: The revit link name of which to return an instance Id
    :type revitLinkName: str
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A link instance Id if an instance of a given link was found, otherwise Invalid element Id (-1)
    :rtype: AutoDesk.Revit.DB.ElementId
    """

    match = False
    # default values
    instance_workset_name = "unknown"
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkInstance):
        # Output('['+str(Element.Name.GetValue(revitLinkName))+'][' + str(Element.Name.GetValue(p))+']')
        link_type_name_parts = rdb.Element.Name.GetValue(p).split(":")
        if len(link_type_name_parts) == 3:
            lN = link_type_name_parts[0]
            if lN[0:-1] == rdb.Element.Name.GetValue(revitLinkName):
                match = True
                wsparam = p.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
                instance_workset_name = wsparam.AsValueString()
                break
    if match == True:
        # Output(instanceWorksetName)
        return rWork.get_workset_id_by_name(doc, instance_workset_name)
    else:
        # Output('no match')
        return rdb.ElementId.InvalidElementId


def _modify_revit_link_type_data(revitLink, doc):
    """
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
    """

    return_value = res.Result()

    # get the workset Id of the link type
    wsparam = revitLink.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
    type_workset_name = wsparam.AsValueString()
    type_workset_id = rWork.get_workset_id_by_name(doc, type_workset_name)

    # get the workset id of a link instance belonging to same type
    instance_workset_id = _get_revit_instance_data_by_name(revitLink, doc)
    instance_workset_name = rWork.get_workset_name_by_id(
        doc, instance_workset_id.IntegerValue
    )

    # check if revit link type needs the workset changed?
    if (
        instance_workset_id != rdb.ElementId.InvalidElementId
        and instance_workset_id != type_workset_id
    ):
        output(
            "Moving: {} from: {} to: {}".format(
                rdb.Element.Name.GetValue(revitLink),
                type_workset_name,
                instance_workset_name,
            )
        )
        transaction = rdb.Transaction(
            doc, "Changing workset of {}".format(rdb.Element.Name.GetValue(revitLink))
        )
        return_value = rTran.in_transaction(
            transaction,
            rWork.get_action_change_element_workset(revitLink, instance_workset_id),
        )
        output(
            "{} [{}]".format(rdb.Element.Name.GetValue(revitLink), return_value.status)
        )
    else:
        return_value.append_message(
            "{} is already on default workset {}".format(
                rdb.Element.Name.GetValue(revitLink), instance_workset_name
            )
        )
    return return_value


#
def modify_revit_link_types(doc):
    """
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
    """

    return_value = res.Result()
    try:
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType):
            change_link = _modify_revit_link_type_data(p, doc)
            return_value.update(change_link)
    except Exception as e:
        return_value.update_sep(
            False, "Failed to modify revit link instances with exception: {}".format(e)
        )
    return return_value


# -------------
# main:
# -------------

# store output here:
rootPath_ = r"C:\temp"

# modify revit links
output("Modifying Revit Link(s).... start")
result_ = modify_revit_link_types(DOC)
output("{} [{}]".format(result_.message, result_.status))

# sync changes back to central
if DOC.IsWorkshared and DEBUG == False:
    output("Syncing to Central: start")
    syncing_ = rFileIO.sync_file(DOC)
    output("Syncing to Central: finished [{}]".format(syncing_.status))
output("Modifying Revit Link(s).... finished ")
