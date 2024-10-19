"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit level export to DATA class functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from Autodesk.Revit.DB import (
    Element,
)


from duHast.Revit.Levels.levels import get_levels_list_ascending
from duHast.Data.Objects.data_level_building import DataLevelBuilding
from duHast.Revit.Exports.export_data import (
    get_model_data,
)
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

def populate_data_level_object(doc, revit_level):
    """
    Returns a custom level data objects populated with some data from the revit model level past in.

    - level id
    - level name
    - level elevation

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_level: A revit level instance.
    :type revit_level: Autodesk.Revit.DB.Level

    :return: A data level building object instance.
    :rtype: :class:`.DataLevelBuilding`
    """

    # set up data class object
    data_level_building = DataLevelBuilding()
    
    # id
    data_level_building.id = revit_level.Id.IntegerValue

    # name
    data_level_building.name = Element.Name.GetValue(revit_level)

    # elevation (converted to mm)
    data_level_building.elevation = convert_imperial_feet_to_metric_mm(revit_level.Elevation)

    # get the model name
    model = get_model_data(doc=doc)
    data_level_building.revit_model = model

    return data_level_building
   

def get_all_level_data(doc, filter_family_names=[]):
    """
    Gets a list of level data objects for each level element in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filter_family_names: filter list of level names to be ignored
    :type filter_family_names: [str]

    :return: A list of data level instances.
    :rtype: list of :class:`.DataLevelBuilding`
    """

    all_level_data = []
    revit_levels = get_levels_list_ascending(doc=doc)
    for revit_level in revit_levels:
        # check if level is in filter list and if so ignore it
        if len(filter_family_names) > 0:
            if Element.Name.GetValue(revit_level) in filter_family_names:
                continue
        level_data = populate_data_level_object(doc, revit_level)
        if level_data is not None:
            all_level_data.append(level_data)
    return all_level_data
