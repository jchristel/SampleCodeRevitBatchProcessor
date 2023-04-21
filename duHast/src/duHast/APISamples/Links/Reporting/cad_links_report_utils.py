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

from duHast.APISamples.Links.cad_links import get_all_cad_link_instances
from duHast.Utilities import FilesIO as util


def get_cad_link_type_data_by_name(cad_link_name, doc, revit_file_path):
    '''
    Extract the file path from CAD link type.
    :param cad_link_name: The cad link name
    :type cad_link_name: str
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The fully qualified file path to the model.
    :type revit_file_path: str
    :return: The fully qualified file path if the cad link type is a valid external reference.\
        Otherwise it will return 'unknown'.
    :rtype: str
    '''

    #default values
    model_path = 'unknown'
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType):
        if (rdb.Element.Name.GetValue(p) == cad_link_name):
            try:
                ex_file_ref = p.GetExternalFileReference()
                if(ex_file_ref.IsValidExternalFileReference(ex_file_ref)):
                    model_path = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(ex_file_ref.GetPath())
                    model_path = util.convert_relative_path_to_full_path(model_path, revit_file_path)
                break
            except Exception as e:
                model_path = str(e)
    return model_path


def get_cad_report_data(doc, revit_file_path):
    '''
    Gets CAD link data to be written to report file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The fully qualified file path to the model, which is added to data returned.
    :type revit_file_path: str
    :return: list of list of cad link properties.
    :rtype: list of list of str
    '''

    data = []
    collector = get_all_cad_link_instances(doc)
    for c in collector:
        # get the workset
        ws_param = c.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
        # get the design option
        do_param = c.get_Parameter(rdb.BuiltInParameter.DESIGN_OPTION_ID)
        # get the link name, link type name and shared coordinates (true or false)
        l_name_param = c.get_Parameter(rdb.BuiltInParameter.IMPORT_SYMBOL_NAME)
        # get the draw layer
        l_draw_layer_param = c.get_Parameter(rdb.BuiltInParameter.IMPORT_BACKGROUND)
        # get shared location?
        # lSharedParam = cadLink.get_Parameter(BuiltInParameter.GEO_LOCATION)
        is_view_specific= c.ViewSpecific
        owner_view_id = c.OwnerViewId
        link_type_data = get_cad_link_type_data_by_name(l_name_param.AsString(), doc, revit_file_path)
        data.append([
            revit_file_path,
            str(c.Id),
            str(l_name_param.AsString()),
            str(is_view_specific),
            str(owner_view_id),
            str(ws_param.AsValueString()),
            str(do_param.AsString()),
            str(c.Pinned),
            str(l_draw_layer_param.AsValueString()),
            link_type_data])
    return data