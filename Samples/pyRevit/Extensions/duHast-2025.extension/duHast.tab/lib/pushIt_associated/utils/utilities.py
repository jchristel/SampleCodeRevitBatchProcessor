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
#
import clr

import os

from duHast.Utilities.Objects.result import Result


from duHast.Utilities.files_json import read_json_data_from_file
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.utility import get_local_app_data_path
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

from duHast.Revit.Categories.categories_model import get_category_by_names, get_builtInCategory_from_category
from duHast.Revit.Common.design_set_options import get_design_set_option_info
from duHast.Revit.Common.Objects.design_set_property_names import DesignSetPropertyNames
from duHast.Revit.Family.family_utils import get_family_instances_of_built_in_category
from duHast.Revit.SharedParameters.shared_parameters import get_all_shared_parameters
from duHast.Revit.Common.parameter_get_utils import get_parameter_value
from duHast.Revit.Levels.levels import get_levels_list_ascending, get_nearest_level_absolute

from pushIt_associated.push_it_family_instance import PushItFamilyInstance
from pushIt_associated.push_it_family_property import PushItFamilyProperty


# family name prefix to identify the elements to be processed
PUSH_IT_COMMAND_NAME = "WLL"


def get_data_path_and_supported_categories():
    """
    Get the data path and supported categories from the settings file.

    :return: Path to local app data and list of supported Revit categories
    :rtype: str,[str]
    """

    # push it settings file path
    push_it_settings_file = os.path.join(
       get_local_app_data_path(),r"duHast/pushIt_settings.json")
    # read the settings file
    read_result = read_json_data_from_file(push_it_settings_file)
    
    # check if read was successful
    if not read_result.status:
        print(read_result.message)
        return None
    
    # get the json dictionary
    dic = read_result.result[0]

    data_path = None
    enabled_category_names = None
    # check if the dictionary has the field we are after
    if "DataPath" in dic:
        data_path = dic["DataPath"]
    else:
        print("DataPath not found in settings file")
        return None ,None
    
    if "EnabledCategoryNames" in dic:
        enabled_category_names = dic["EnabledCategoryNames"]  
    else:
        print("EnabledCategoryNames not found in settings file")
        return None,None
    
    return data_path, enabled_category_names


def get_unique_id_parameter_from_data_file(data_path):
    """
    Returns the unique ID parameter name and guid from the data file.

    :param data_path: Path to the data file
    :type data_path: str
    :return: Unique ID parameter name and guid
    :rtype: str,str
    """

    parameter_name = None
    parameter_guid = None
    
    read_result = read_csv_file(file_path=data_path, increase_max_field_size_limit=False)
    if not read_result.status:
        print(read_result.message)
        return None
    
    # get the first column of the first two rows
    # first row contains the name of the parameter
    # second row contains the guid of the parameter
    data = read_result.result[0:2]
    if len(data) < 2:
        print("Data file does not contain enough rows")
        return None
    
    if len(data[0]) < 1:
        print("Data file does not contain enough columns")
        return None
    
    # get the first column of the first two rows
    parameter_name = data[0][0]
    parameter_guid = data[1][0]

    return parameter_name, parameter_guid

def get_parameters_and_guids_from_data_file(data_path):
    """
    Returns the all parameter name and their guid from the data file.

    :param data_path: Path to the data file
    :type data_path: str
    :return: A dictionary of parameter name and guid
    :rtype: {str,str}
    """

   
    read_result = read_csv_file(file_path=data_path, increase_max_field_size_limit=False)
    if not read_result.status:
        print(read_result.message)
        return None
    
    # first row contains the name of the parameter
    # second row contains the guid of the parameter
    data = read_result.result[0:2]
    if len(data) < 2:
        print("Data file does not contain enough rows")
        return None
    
    if len(data[0]) < 1:
        print("Data file does not contain enough columns")
        return None
    
    parameter_data = {}

    # combine the first row and second row into a dictionary
    # first row contains the name of the parameter
    # second row contains the guid of the parameter

    for i in range(len(data[0])):
        # get the first column of the first two rows
        parameter_data[data[0][i]] = data[1][i]
       
    return parameter_data


def get_supported_revit_categories(doc, supported_category_names):
    
    # set up a status tracker
    return_value = Result()

    # get the supported categories
    supported_revit_categories =[]

    for supported_name in supported_category_names:
        # get the category by name
        category = get_category_by_names(doc, supported_name, supported_name)
        if category is None:
            return_value.update_sep(False, "Category not found: {}".format(supported_name))
            return return_value
        supported_revit_categories.append(category)


    return_value.result = supported_revit_categories
    return return_value

def get_supported_built_in_categories_from_categories(doc, supported_revit_categories):
    """
    Returns a list of built in categories from the supported Revit categories.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param supported_revit_categories: The supported Revit categories
    :type supported_revit_categories: list[Autodesk.Revit.DB.Category]
    :return: A list of built in categories
    :rtype: list[Autodesk.Revit.DB.BuiltInCategory]
    """

    # set up a status tracker
    return_value = Result()

    # get the supported categories
    supported_built_in_categories = []

    for category in supported_revit_categories:
        built_in = get_builtInCategory_from_category(doc, category)
        if built_in is None:
            return_value.update_sep(False, "Built in category not found: {}".format(category.Name))
            return return_value
        supported_built_in_categories.append(built_in)

    return_value.result = supported_built_in_categories
    return return_value


def get_family_instances_of_supported_categories(doc, supported_category_names):
    """
    Returns a list of family instances of push it supported categories.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param supported_category_names: The supported Revit categories
    :type supported_category_names: list[str]
    :return: Result class instance.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get supported revit categories
    get_supported_categories_result = get_supported_revit_categories(doc, supported_category_names)

    # check we got anything
    if not get_supported_categories_result.status:
        return_value.update_sep(False, "Failed to get supported categories: {}".format(get_supported_categories_result.message))
        return return_value
    elif len(get_supported_categories_result.result) == 0:
        return_value.update_sep(False, "No supported categories found")
        return return_value
    
    # get the supported categories
    supported_revit_categories = get_supported_categories_result.result

    # get the supported built in categories from revit categories
    supported_built_in_categories = []
    get_built_in_category_result = get_supported_built_in_categories_from_categories(doc, supported_revit_categories)

    # check if we got anything
    if not get_built_in_category_result.status:
        return_value.update_sep(False, "Failed to get supported built in categories: {}".format(get_built_in_category_result.message))
        return return_value
    elif len(get_built_in_category_result.result) == 0:
        return_value.update_sep(False, "No supported built in categories found.")
        return return_value
    
    supported_built_in_categories = get_built_in_category_result.result

    # get all family instances of supported categories
    family_instances = []
    for supported_built_in_category in supported_built_in_categories:
        family_instances.extend(get_family_instances_of_built_in_category(doc, supported_built_in_category))

    # check if we got any family instances
    if len(family_instances) == 0:
        return_value.update_sep(False, "No family instances found.")
        return return_value
    
    return_value.result = family_instances
    return return_value

def sort_families_by_design_set_and_option(doc, family_instances):

    """
    Sort family instances by design set and option.
    :param doc: The Revit document
    :param family_instances: The family instances to sort
    :return: A dictionary of family instances sorted by design set and option
    :rtype: dict
    """
    
    # sort family instances by design set and option
    # get the design set and option from the family instance

    # key is concatenated design set and option
    families_by_design_set_and_option = {}

    for fi in family_instances:
        # get the design set and option
        design_set_option_info = get_design_set_option_info(doc, fi)

        design_set_name = design_set_option_info[DesignSetPropertyNames.DESIGN_SET_NAME]
        design_option_name = design_set_option_info[DesignSetPropertyNames.DESIGN_OPTION_NAME]

        # create a key for the family instance
        key = "{}_{}".format(design_set_name, design_option_name)

        # add the family instance to the dictionary
        if key not in families_by_design_set_and_option:
            families_by_design_set_and_option[key] = []

        families_by_design_set_and_option[key].append(fi)
    
    return families_by_design_set_and_option


def sort_families_by_parameter_value(doc, family_instances,parameter_guid):
    """
    Sort family instances by parameter value.
    :param doc: The Revit document
    :param family_instances: The family instances to sort
    :param parameter_guid: The guid of the parameter to sort by
    :return: A dictionary of family instances sorted by parameter value
    :rtype: dict
    """
    
    # sort family instances by parameter value
    # get the parameter value from the family instance

    # key is concatenated design set and option
    families_by_parameter_value = {}

    # get the parameter name from the guid
    parameter_name = None
    # get the shared parameter definition
    shared_parameters = get_all_shared_parameters(doc)
    for p in shared_parameters:
        if p.GuidValue.ToString() ==parameter_guid:
            parameter_name = p.Name
            break

    if parameter_name is None:
        print("Parameter not found: {}".format(parameter_guid))
        return None


    for fi in family_instances:
        # get the parameter value
        para = fi.LookupParameter(parameter_name)
        param_value = get_parameter_value(para)

        # create a key for the family instance
        if param_value not in families_by_parameter_value:
            families_by_parameter_value[param_value] = []

        families_by_parameter_value[param_value].append(fi)
    
    return families_by_parameter_value


def sort_families_by_design_set(doc, family_instances_by_key):
    """
    Sort family instances by design set.
    :param doc: The Revit document
    :param family_instances: The family instances to sort as a dictionary where the key is a parameter value as string and the value is a list of family instances with the same key
    :return: A dictionary of family instances sorted by design set
    :rtype: dict
    """
    
    # sort family instances by design set
    # get the design set from the family instance

    # key is concatenated design set and option
    families_by_key = {}

    for parameter_value, family_instances in  family_instances_by_key.items():

        # ignore any entries where the family instances list is of length 1
        if len(family_instances) == 1:
            continue

        # get the design set and option from the family instance
        families_by_design_set= {}
        
        # loop over the family instances and sort them by design set
        for fi in family_instances:
            # get the design set
            design_set_option_info = get_design_set_option_info(doc, fi)
            design_set_name = design_set_option_info[DesignSetPropertyNames.DESIGN_SET_NAME]

            # add the family instance to the dictionary
            if design_set_name not in families_by_design_set:
                families_by_design_set[design_set_name] = []

            families_by_design_set[design_set_name].append(fi)
        
        # add the family instances to the dictionary
        families_by_key[parameter_value] = families_by_design_set
    
    # check if we got any key with more than one family instance
    problematic_keys = {}
    
    for key, value in families_by_key.items():
       
        if len(value) >1 :
            # check if the parameter value is empty
            if key == "None":
                continue

            problematic_keys[key] = value
           
    return problematic_keys


def get_family_instance_properties(family_instance, parameter_data, unique_id_parameter_guid):
    """
    Get the family instance properties.

    This assumes all properties to be extracted are based on shared parameters!

    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_instance: The family instance to get the properties from
    :type family_instance: Autodesk.Revit.DB.FamilyInstance
    :param parameter_data: The parameter data to use for the conversion
    :type parameter_data: dict
    :return: A list of family instance properties
    :rtype: list
    """

    family_instance_properties = []

    paras = family_instance.GetOrderedParameters()

    try:
        for para in paras:
            # check if this is a shared parameter
            if para.IsShared:
                # get the parameter name
                instance_parameter_name = para.Definition.Name
                instance_parameter_guid = para.GUID.ToString()
                instance_parameter_value = get_parameter_value(para)

                for parameter_name, parameter_guid in parameter_data.items():
                    # check if the unique id parameter value is empty, if so reject this family instance
                    if instance_parameter_guid == unique_id_parameter_guid:
                        if instance_parameter_value == "None" or instance_parameter_value == "":
                            raise ValueError("Unique Id Parameter value is None or empty for family instance: {}".format(family_instance.Id.Value))
                   
                    # check if the parameter is in the parameter data
                    if parameter_guid == instance_parameter_guid:
                        # create a family instance property
                        family_instance_property = PushItFamilyProperty()
                        family_instance_property.parameter_description = parameter_name
                        family_instance_property.parameter_name = instance_parameter_name
                        family_instance_property.parameter_guid = parameter_guid
                        family_instance_property.parameter_value =  instance_parameter_value

                        # add the property to the list
                        family_instance_properties.append(family_instance_property)
                        break
    except Exception as e:
        return None
            
    return family_instance_properties


def convert_family_instances_to_storage(doc, family_instances, parameter_data, unique_id_parameter_guid, forms, get_family_instance_data = True):
    """
    Convert family instances to storage.
    :param doc: The Revit document
    :param family_instances: The family instances to convert
    :type family_instances: list[Autodesk.Revit.DB.FamilyInstance]
    :param parameter_data: The parameter data to use for the conversion
    :type parameter_data: dict
    :return: A list of family instances converted to storage
    :rtype: list[Autodesk.Revit.DB.ElementId]
    """
    

    # set up a status tracker
    return_value = Result()

    # convert family instances to storage
    converted_family_instances = []

    levels_ascending = get_levels_list_ascending(doc)

    # set up a progress bar since this can take a moment
    counter = 1
    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Retrieving family data: {value} of {max_value}", cancellable=True
    ) as pb:

        # get the family instance from the family instance
        for fi in family_instances:

            # increase the progress bar
            pb.update_progress(counter, max_value=len(family_instances))
            
            # set up the family instance
            converted_family_instance = PushItFamilyInstance()

            # get the family instance id
            converted_family_instance.revit_element_id_integer_value = fi.Id.Value

            # get the family instance location point
            converted_family_instance.set_location_point(fi.Location.Point.X, fi.Location.Point.Y, fi.Location.Point.Z)

            # get the level name based on the placement Z coordinate
            # this is a more universal approach to getting the level name since different revit categories report levels differently
            # this also displays the level name as per the host model, not necessary as per the model where the push it instances are placed (if different)
            placement_level_and_offset = get_nearest_level_absolute(
                z=convert_imperial_feet_to_metric_mm(fi.Location.Point.Z),
                levels=levels_ascending, 
                ignore_level_names=[]
            )
            converted_family_instance.placement_level_name = placement_level_and_offset[0].Name

            # store design set and option info
            design_set_option_info = get_design_set_option_info(doc, fi)
            converted_family_instance.set_design_set_option_info_value(design_set_option_info)
            
            if (get_family_instance_data):

                # get the family instance properties
                family_instance_properties = get_family_instance_properties(fi, parameter_data, unique_id_parameter_guid)
            
                if family_instance_properties is None:
                    # ignore this family instance since the unique id parameter value is empty
                    counter += 1
                    continue
            
                for family_instance_property in family_instance_properties:
                    converted_family_instance.add_property(family_instance_property)

            # add the family instance to the list
            converted_family_instances.append(converted_family_instance)

            counter += 1

            # check for cancel
            if pb.cancelled:
                return_value.update_sep(False, "User cancelled.")
                print("User cancelled.")
                break
    
    # check if we got any family instances
    if len(converted_family_instances) == 0:
        return_value.update_sep(False, "No family instances with unique Id value set found.")
        return return_value

    # set up a status tracker
    return_value.result = converted_family_instances

    # return family instances
    return return_value