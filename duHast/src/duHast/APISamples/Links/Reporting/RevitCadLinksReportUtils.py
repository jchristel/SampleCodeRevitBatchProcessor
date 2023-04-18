'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for CAD link reports. 
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

from duHast.APISamples.Links.RevitCadLinks import get_all_cad_link_instances
from duHast.Utilities import FilesIO as util


def get_cad_link_type_data_by_name(cadLinkName, doc, revitFilePath):
    '''
    Extract the file path from CAD link type.
    :param cadLinkName: The cad link name
    :type cadLinkName: str
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The fully qualified file path to the model.
    :type revitFilePath: str
    :return: The fully qualified file path if the cad link type is a valid external reference.\
        Otherwise it will return 'unknown'.
    :rtype: str
    '''

    #default values
    modelPath = 'unknown'
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType):
        if (rdb.Element.Name.GetValue(p) == cadLinkName):
            try:
                exFileRef = p.GetExternalFileReference()
                if(exFileRef.IsValidExternalFileReference(exFileRef)):
                    modelPath = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(exFileRef.GetPath())
                    modelPath = util.convert_relative_path_to_full_path(modelPath, revitFilePath)
                break
            except Exception as e:
                modelPath = str(e)
    return modelPath


def get_cad_report_data(doc, revitFilePath):
    '''
    Gets CAD link data to be written to report file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The fully qualified file path to the model, which is added to data returned.
    :type revitFilePath: str
    :return: list of list of cad link properties.
    :rtype: list of list of str
    '''

    data = []
    collector = get_all_cad_link_instances(doc)
    for c in collector:
        # get the workset
        wsParam = c.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
        # get the design option
        doParam = c.get_Parameter(rdb.BuiltInParameter.DESIGN_OPTION_ID)
        # get the link name, link type name and shared coordinates (true or false)
        lNameParam = c.get_Parameter(rdb.BuiltInParameter.IMPORT_SYMBOL_NAME)
        # get the draw layer
        lDrawLayerParam = c.get_Parameter(rdb.BuiltInParameter.IMPORT_BACKGROUND)
        # get shared location?
        # lSharedParam = cadLink.get_Parameter(BuiltInParameter.GEO_LOCATION)
        isViewSpecific= c.ViewSpecific
        ownerViewId = c.OwnerViewId
        linkTypeData = get_cad_link_type_data_by_name(lNameParam.AsString(), doc, revitFilePath)
        data.append([
            revitFilePath,
            str(c.Id),
            str(lNameParam.AsString()),
            str(isViewSpecific),
            str(ownerViewId),
            str(wsParam.AsValueString()),
            str(doParam.AsString()),
            str(c.Pinned),
            str(lDrawLayerParam.AsValueString()),
            linkTypeData])
    return data