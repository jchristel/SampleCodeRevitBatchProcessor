import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import Autodesk
from Autodesk.Revit.DB import BuiltInCategory
from System.Collections.Generic import List

from duHast.Revit.Common.parameter_get_utils import get_parameter_value_by_name
from duHast.Revit.SharedParameters.shared_parameters import get_all_shared_parameters
from duHast.Revit.Common.design_set_options import get_design_set_option_info
from duHast.Revit.Common.Objects.design_set_property_names import DesignSetPropertyNames
from duHast.Revit.Categories.categories_model import get_builtin_category_by_name
from duHast.Revit.Family.family_utils import get_family_instances_by_built_in_categories

from PushIt.Models.RevitFamily import RFamily


def get_built_in_categories(category_names):
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
        cat = get_builtin_category_by_name(cat_name)
        if cat is None:
            continue
        
        categories.Add(cat)

    return categories


def get_parameter_name_by_guid(parameters, guid):
    """
    Returns the parameter name by guid

    :param parameters: The parameters.
    :type parameters: Autodesk.Revit.DB.ParameterSet
    :param guid: The guid of the parameter.
    :type guid: str

    :return: The parameter name.
    :rtype: str
    """

    for parameter in parameters:
        if parameter.GuidValue.ToString() == guid:
            return parameter.Definition.Name

    return None


def get_shared_parameter_data(doc, room):
    """
    Returns shared parameter data for a room
    
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param room: The room.
    :type room: Room
    
    :return: Shared parameter data.
    :rtype: [dict]
    """
    
    data = []
    
    # get shared parameters from revit document
    shared_parameters = get_all_shared_parameters(doc)
    
    id_parameter_name = get_parameter_name_by_guid(shared_parameters, room.id.parameter_guid)
    data.append({id_parameter_name: room.id.parameter_guid})
    
    area_briefed_parameter_name = get_parameter_name_by_guid(shared_parameters, room.area_briefed.parameter_guid)
    data.append({area_briefed_parameter_name: room.area_briefed.parameter_guid})
    
    area_design_parameter_name = get_parameter_name_by_guid(shared_parameters, room.area_designed.parameter_guid)
    data.append({area_design_parameter_name: room.area_designed.parameter_guid})
    
    for prop in room.other_properties:
        prop_name = get_parameter_name_by_guid(shared_parameters, prop.parameter_guid)
        data.append({prop_name: prop.parameter_guid})
        
    return data
    

def extract_family_data(family_instances, shared_parameter_data):
    """
    Extracts family data from family instances

    :param family_instances: List of family instances
    :type family_instances: [Autodesk.Revit.DB.FamilyInstance]
    :param shared_parameter_data: Shared parameter data
    :type shared_parameter_data: [dict]

    :return: List of family instances
    :rtype: [RFamily]
    """
    
    family_data=[]
    # loop over family instances and extract properties matching room
    # ignore all families with no room_id value
    for family_instance in family_instances:
        # get the room_id value
        room_id = get_parameter_value_by_name(family_instance, shared_parameter_data[0].keys()[0])
        if room_id is None or room_id == "":
            continue
        
        # get the area_briefed value
        area_briefed = get_parameter_value_by_name(family_instance, shared_parameter_data[1].keys()[0])
        
        # get the area_design value
        area_design = get_parameter_value_by_name(family_instance, shared_parameter_data[2].keys()[0])
        
        # get the other properties
        other_properties = []
        for prop in shared_parameter_data[3:]:
            prop_value = get_parameter_value_by_name(family_instance, prop.keys()[0])
            other_properties.append(prop_value)
        
        # get the design set and option values
        design_set_and_option_data = get_design_set_option_info(family_instance)
        
        # create a new family object
        family = RFamily(
            room_id=room_id,
            area_designed=area_design,
            area_briefed=area_briefed,
            properties=other_properties,
            design_set=design_set_and_option_data[DesignSetPropertyNames.DESIGN_SET_NAME],
            design_option=design_set_and_option_data[DesignSetPropertyNames.DESIGN_OPTION_NAME],
            design_option_is_primary=design_set_and_option_data[DesignSetPropertyNames.DESIGN_OPTION_IS_PRIMARY]
        )
        
        family_data.append(family)
    
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
    built_in_categories = get_built_in_categories(categories)
    
    # get family instances in model
    family_instances = get_family_instances_by_built_in_categories(doc, built_in_categories)
    
    # loop over family instances and extract properties required
    # ignore all families with no room_id value
    family_data = extract_family_data(family_instances, shared_parameter_data)
    
    return family_data

