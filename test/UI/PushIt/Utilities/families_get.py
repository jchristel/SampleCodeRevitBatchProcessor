# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import Autodesk
from Autodesk.Revit.DB import BuiltInCategory
from System.Collections.Generic import List

from duHast.Revit.Common.parameter_get_utils import get_parameter_value_by_name
from duHast.Revit.Common.design_set_options import get_design_set_option_info
from duHast.Revit.Common.Objects.design_set_property_names import DesignSetPropertyNames
from duHast.Revit.Categories.categories_model import get_builtin_category_by_name,get_category_by_names, get_builtInCategory_from_category
from duHast.Revit.Family.family_utils import get_family_instances_by_built_in_categories

from PushIt.Models.RevitFamily import RFamily
from PushIt.Models.RoomProperty import RoomProperty
from PushIt.Utilities.shared_parameters import get_shared_parameter_data


def get_built_in_categories(doc, category_names):
    """
    Returns all built in categories in a model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param category_names: List of category names
    :type category_names: [str]

    :return: List of built in categories
    :rtype: [Autodesk.Revit.DB.BuiltInCategory]
    """

    # needs to be a c# list
    categories = List[BuiltInCategory]()

    for cat_name in category_names:
        cat = get_category_by_names(doc=doc, main_category_name=cat_name, sub_category_name=cat_name)
        cat_built_in = get_builtInCategory_from_category(doc, cat)
        
        if cat_built_in is None:
            continue

        categories.Add(cat_built_in)

    return categories

def extract_single_family_data(doc, family_instance, shared_parameter_data):
    """
    Extracts family data from a single family instance

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param family_instance: A family instance
    :type family_instance: Autodesk.Revit.DB.FamilyInstance
    :param shared_parameter_data: Shared parameter data
    :type shared_parameter_data: [dict]

    :return: A family instance
    :rtype: RFamily
    """

    # get the room_id value
    room_id = get_parameter_value_by_name(
        family_instance, shared_parameter_data[0].keys()[0]
    )
    if room_id is None or room_id == "":
        return None

    # strip any safety off information from the id
    room_id = room_id.split("::")[0]
    
    # get the area_briefed value
    area_briefed = get_parameter_value_by_name(
        family_instance, shared_parameter_data[1].keys()[0]
    )
    # check for spaces in the area_briefed value, indicating a unit string
    # if so, split the string and get the first value
    if " " in area_briefed:
        area_briefed = area_briefed.split(" ")[0]
        
    # get the area_design value
    area_design = get_parameter_value_by_name(
        family_instance, shared_parameter_data[2].keys()[0]
    )
    # check for spaces in the area_design value, indicating a unit string
    # if so, split the string and get the first value
    if " " in area_design:
        area_design = area_design.split(" ")[0]
    

    # get the other properties
    other_properties = []
    for prop in shared_parameter_data[3:]:
        prop_value = get_parameter_value_by_name(family_instance, prop.keys()[0])
        prop_instance = RoomProperty(name=prop.keys()[0], value=prop_value, parameter_guid=prop[prop.keys()[0]])
        other_properties.append(prop_instance)

    # get the design set and option values
    design_set_and_option_data = get_design_set_option_info(doc=doc, element=family_instance)

    # create a new family object
    family = RFamily(
        room_id=room_id,
        area_designed=area_design,
        area_briefed=area_briefed,
        properties=other_properties,
        design_set=design_set_and_option_data[
            DesignSetPropertyNames.DESIGN_SET_NAME
        ],
        design_option=design_set_and_option_data[
            DesignSetPropertyNames.DESIGN_OPTION_NAME
        ],
        design_option_is_primary=design_set_and_option_data[
            DesignSetPropertyNames.DESIGN_OPTION_IS_PRIMARY
        ],
        revit_element_id=family_instance.Id.IntegerValue,
    )

    return family

def extract_family_data(doc, family_instances, shared_parameter_data):
    """
    Extracts family data from family instances

    :param family_instances: List of family instances
    :type family_instances: [Autodesk.Revit.DB.FamilyInstance]
    :param shared_parameter_data: Shared parameter data
    :type shared_parameter_data: [dict]

    :return: List of family instances
    :rtype: [RFamily]
    """

    family_data = []
    # loop over family instances and extract properties matching room
    # ignore all families with no room_id value
    for family_instance in family_instances:
        
        # get a single family instance
        family_data_instance = extract_single_family_data(
            doc=doc,
            family_instance=family_instance, 
            shared_parameter_data=shared_parameter_data
        )

        # check if family data instance is not None (room_id value exists)
        if family_data_instance is not None:
            family_data.append(family_data_instance)

    return family_data


def get_families_in_model(doc, categories, room):
    """
    Returns all families in a model matching the categories provided and have an associated room_id value.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param categories: List of category names
    :type categories: [str]
    :param room: A sample room containing all properties and the shared parameters they are meant to be stored in.
    :type room: Room

    :return: List of family instances
    :rtype: [RFamily]
    """

    # list of family instances
    family_data = []

    # get shared parameter data
    # as a list of dictionaries (first entry is the unique room_id)
    shared_parameter_data = get_shared_parameter_data(doc, room)

    # families in the model of all categories required
    built_in_categories = get_built_in_categories(doc, categories)

    # get family instances in model
    family_instances = get_family_instances_by_built_in_categories(
        doc, built_in_categories
    )

    # loop over family instances and extract properties required
    # ignore all families with no room_id value
    family_data = extract_family_data(
        doc=doc,
        family_instances=family_instances, 
        shared_parameter_data=shared_parameter_data
    )

    return family_data
