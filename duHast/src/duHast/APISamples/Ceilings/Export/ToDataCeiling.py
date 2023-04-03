'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit ceilings export to DATA class functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

from duHast.APISamples.Common import RevitDesignSetOptions as rDesignO, RevitElementParameterGetUtils as rParaGet, RevitPhases as rPhase
from duHast.APISamples.Ceilings.Geometry import Geometry
from duHast.APISamples.Ceilings import RevitCeilings as rCeiling
from duHast.DataSamples.Objects import DataCeiling as dCeiling
from duHast.DataSamples.Objects.Properties.Geometry import FromRevitConversion as rCon


def PopulateDataCeilingObject(doc, revitCeiling):
    '''
    Returns a custom ceiling data objects populated with some data from the revit model ceiling past in.

    - ceiling id
    - ceiling type name
    - ceiling mark
    - ceiling type mark
    - ceiling level name
    - ceiling level id
    - ceiling offset from level

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitCeiling: A revit ceiling instance.
    :type revitCeiling: Autodesk.Revit.DB.Ceiling
    
    :return: A data ceiling object instance.
    :rtype: :class:`.DataCeiling`
    '''

    # set up data class object
    dataC = dCeiling.DataCeiling()
    # get ceiling geometry (boundary points)
    revitGeometryPointGroups = Geometry.Get2DPointsFromRevitCeiling(revitCeiling)
    if(len(revitGeometryPointGroups) > 0):
        ceilingPointGroupsAsDoubles = []
        for allCeilingPointGroups in revitGeometryPointGroups:
            dataGeoConverted = rCon.convert_xyz_in_data_geometry_polygons(doc, allCeilingPointGroups)
            ceilingPointGroupsAsDoubles.append(dataGeoConverted)
        dataC.geometryPolygon = ceilingPointGroupsAsDoubles
        # get design set data
        design_set_data = rDesignO.GetDesignSetOptionInfo(doc, revitCeiling)
        dataC.designSetAndOption.designOptionName = design_set_data['designOptionName']
        dataC.designSetAndOption.designSetName = design_set_data['designSetName']
        dataC.designSetAndOption.isPrimary = design_set_data['isPrimary']

        # get type properties
        dataC.typeProperties.typeId = revitCeiling.GetTypeId().IntegerValue
        dataC.typeProperties.typeName = rdb.Element.Name.GetValue(revitCeiling).encode('utf-8')
        ceilingType = doc.GetElement(revitCeiling.GetTypeId())

        # custom parameter value getters
        value_getter = {
            rdb.StorageType.Double : rParaGet.getter_double_as_double_converted_to_millimeter,
            rdb.StorageType.Integer : rParaGet.getter_int_as_int,
            rdb.StorageType.String : rParaGet.getter_string_as_UTF8_string, # encode ass utf 8 just in case
            rdb.StorageType.ElementId : rParaGet.getter_element_id_as_element_int, # needs to be an integer for JSON encoding
            str(None) : rParaGet.getter_none
        }
        dataC.typeProperties.properties = rParaGet.get_all_parameters_and_values_wit_custom_getters(ceilingType, value_getter)

        # get instance properties
        dataC.instanceProperties.instanceId = revitCeiling.Id.IntegerValue
        dataC.instanceProperties.properties = rParaGet.get_all_parameters_and_values_wit_custom_getters(revitCeiling, value_getter)

        # get level properties
        dataC.level.levelName = rdb.Element.Name.GetValue(doc.GetElement(revitCeiling.LevelId)).encode('utf-8')
        dataC.level.levelId = revitCeiling.LevelId.IntegerValue
        dataC.level.offsetFromLevel = rParaGet.get_built_in_parameter_value(revitCeiling, rdb.BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM)   # offset from level

        # get the model name
        if(doc.IsDetached):
            dataC.revitModel.modelName = 'Detached Model'
        else:
            dataC.revitModel.modelName = doc.Title

        # get phasing information
        dataC.phasing.phaseCreated = rPhase.GetPhaseNameById(doc, rParaGet.get_built_in_parameter_value(revitCeiling, rdb.BuiltInParameter.PHASE_CREATED, rParaGet.get_parameter_value_as_element_id)).encode('utf-8')
        dataC.phasing.phaseDemolished = rPhase.GetPhaseNameById(doc, rParaGet.get_built_in_parameter_value(revitCeiling, rdb.BuiltInParameter.PHASE_DEMOLISHED, rParaGet.get_parameter_value_as_element_id)).encode('utf-8')

        return dataC
    else:
        return None


def GetAllCeilingData(doc):
    '''
    Gets a list of ceiling data objects for each ceiling element in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of data ceiling instances.
    :rtype: list of :class:`.DataCeiling`
    '''

    allCeilingData = []
    ceilings = rCeiling.GetAllCeilingInstancesInModelByCategory(doc)
    for ceiling in ceilings:
        cd = PopulateDataCeilingObject(doc, ceiling)
        if(cd is not None):
            allCeilingData.append(cd)
    return allCeilingData