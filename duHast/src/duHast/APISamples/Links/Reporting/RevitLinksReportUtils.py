'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for Revit link reports. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples.Links.RevitLinks import GetAllRevitLinkInstances, GetRevitLinkTypeFromInstance


def GetRevitLinkTypeData(doc, revitLinkType):
    '''
    Gets Revit Link Type data for reporting.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitLinkType: The link type of which to get the data from.
    :type revitLinkType: Autodesk.Revit.DB.RevitLinkType
    :return: A list of string 
    :rtype: list str
    '''

    # default values
    modelPath = 'unknown'
    isLoaded = False
    isFromLocalPath = False
    pathType = 'unknown'
    isLoaded = revitLinkType.IsLoaded(doc, revitLinkType.Id)
    isFromLocalPath = revitLinkType.IsFromLocalPath()
    exFileRef = revitLinkType.GetExternalFileReference()
    # get the workset of the link type (this can bew different to the workset of the link instance)
    wsParameter = revitLinkType.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
    if(exFileRef.IsValidExternalFileReference(exFileRef)):
        modelPath = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(exFileRef.GetPath())
        pathType = exFileRef.PathType.ToString()

    data=[
        rdb.Element.Name.GetValue(revitLinkType),
        str(isLoaded),
        str(wsParameter.AsValueString()),
        str(isFromLocalPath),
        pathType,
        modelPath]

    return data

def GetRevitLinkReportData(doc, revitFilePath):
    '''
    Gets link data ready for being printed to file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str
    :return: list of list of revit link properties.
    :rtype: list of list of str
    '''

    data = []
    collector = GetAllRevitLinkInstances(doc)
    for c in collector:
        # get the workset
        wsParameter = c.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
        # get the design option
        doParameter = c.get_Parameter(rdb.BuiltInParameter.DESIGN_OPTION_ID)
        # get whether link is shared or not (only works when link is loaded)
        if ('<Not Shared>' in c.Name):
            lS = False
        else:
            lS = True
        # get shared location name ( needs to be in try catch in case file is unloaded)
        linkLocationName = 'unknown'
        try:
            linkLocationName = c.GetLinkDocument().ActiveProjectLocation.Name
        except Exception:
            pass
        linkType = GetRevitLinkTypeFromInstance(doc, c)
        linkTypeData = GetRevitLinkTypeData(doc, linkType)
        # add other data
        linkTypeData = [revitFilePath] + [str(c.Id)] + linkTypeData + [str(lS)] +[linkLocationName] + [rParaGet.get_parameter_value (wsParameter)] + [rParaGet.get_parameter_value(doParameter)]
        data.append(linkTypeData)
    return data