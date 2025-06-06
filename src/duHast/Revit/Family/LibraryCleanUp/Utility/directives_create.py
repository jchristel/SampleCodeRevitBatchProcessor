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



from duHast.Utilities.Objects.result import Result



from duHast.Revit.Family.LibraryCleanUp.Utility.defaults import GROUPING_CODE_PARAMETER_NAME
from duHast.Revit.Family.LibraryCleanUp.Utility.grouping_code import clean_code, convert_to_file_name_code, load_group_code_description
from duHast.Revit.Family.LibraryCleanUp.Utility.family_file_name import clean_up_family_name, build_family_name_from_descriptor


from duHast.Revit.Family.Data.Objects.family_type_data_storage_manager import FamilyTypeDataStorageManager
from duHast.Revit.Family.Data.Objects.family_type_data_storage import FamilyTypeDataStorage
from duHast.Revit.Family.Data.Objects.family_directive_copy import FamilyDirectiveCopy
from duHast.Revit.Family.Data.Objects.family_directive_swap_instances_of_type import FamilyDirectiveSwap


def get_unique_group_codes(family_storage_data):
    """
    Get unique group codes from the family storage data.

    if codes are ITSE-001.2 and ITSE-002.1 it will return ITSE-001 and ITSE-002 as unique group codes.

    :param family_storage_data: The family storage data from which to get the unique group codes.
    :type family_storage_data: :class:`.FamilyTypeDataStorageManager`
    :return: A list of unique group codes.
    :rtype: list[str]
    """


    unique_group_codes = []

    if (isinstance(family_storage_data, FamilyTypeDataStorageManager)==False):
        raise TypeError("family_storage_data must be an instance of FamilyTypeDataStorageManager. Got instead: {}".format(type(family_storage_data)))
    
    if (family_storage_data.family_has_types == False):
        # return an empty list if the family has no types
        return unique_group_codes
    
    # loop over types and try to get the grouping code
    for family_type_storage in family_storage_data.family_type_data_storage:
        if (isinstance(family_type_storage, FamilyTypeDataStorage)==False):
            raise TypeError("family_type_storage must be an instance of FamilyTypeDataStorage. Got instead: {}".format(type(family_type_storage)))
        
        grouping_code_parameter = family_type_storage.get_parameter_by_name(GROUPING_CODE_PARAMETER_NAME)

        #check if successful
        if (grouping_code_parameter is None):
            raise ValueError("Grouping code parameter '{}' not found in family type data storage.".format(GROUPING_CODE_PARAMETER_NAME))
        
        # remove any sub codes 
        group_code_cleaned = clean_code(grouping_code_parameter.value)
        if group_code_cleaned not in unique_group_codes:
            unique_group_codes.append(group_code_cleaned)
    
    return unique_group_codes


def create_copy_directives(family_storage_data, unique_group_codes, output_directory,  code_to_descriptor_map):
    """
    Create copy directives for each unique group code in the family storage data.

    :param family_storage_data: The family storage data from which to create copy directives. (takes the family name, category and file path from this data)
    :type family_storage_data: :class:`.FamilyTypeDataStorageManager`
    :param unique_group_codes: A list of unique group codes to create copy directives for.
    :type unique_group_codes: list[str]
    :param output_directory: The directory where the copied families will be saved.
    :type output_directory: str
    
    :return: A list of copy directives.
    :rtype: list[:class:`.FamilyDirectiveCopy`]
    """

    # set up a list containing all copy directives to be created
    copy_directives = []

    for each_group_code in unique_group_codes:

        # get the description for the group code
        group_code_description = code_to_descriptor_map.get(each_group_code, None)
        # this should not happen....
        if group_code_description is None:
            raise ValueError("Grouping code '{}' not found in code description mapping.".format(each_group_code))
        
        # build family name from the group code description
        fam_name_part = build_family_name_from_descriptor(group_code_description)

        # build new family name
        new_file_name = "{}_{}.rfa".format(fam_name_part,  convert_to_file_name_code( each_group_code))

        print("Creating copy directive for group code: {} with new file name: {}".format(each_group_code, new_file_name))
        # create a copy directive for each unique group code
        #name, category, source_file_path, target_directory, new_name
        copy_directive = FamilyDirectiveCopy(
            name = family_storage_data.family_name, 
            category = family_storage_data.family_category, 
            source_file_path = family_storage_data.family_file_path, 
            target_directory =  output_directory, 
            new_name = new_file_name,
        )
        
        # add to over all list
        copy_directives.append(copy_directive)

    # return the list of copy directives
    return copy_directives


def create_type_maintained_lists(family_storage_data, unique_group_codes, copy_directives):

    """
    Create lists of family types to be maintained in the new family based on unique group codes.

    :param family_storage_data: The family storage data from which to create type maintained lists.
    :type family_storage_data: :class:`.FamilyTypeDataStorageManager`
    :param unique_group_codes: A list of unique group codes to create type maintained lists for.
    :type unique_group_codes: list[str]
    :param copy_directives: A list of copy directives to be used for creating type maintained lists.
    :type copy_directives: list[:class:`.FamilyDirectiveCopy`]
    
    :return: A list of nested type maintained lists with two entries each: new family name, family type name to be maintained. ( a family with multiple times to be maintained will have multiple entries in the list )
    :rtype: list[ list[str] ]
    """
    
    #loop over unique group codes and
    # find associated copy directive
    # all types with matching group code

    type_keep_lists = []

    for each_group_code in unique_group_codes:

        # amend the group code to the copy directive file name
        group_code_in_file_name = "{}.rfa".format(convert_to_file_name_code(each_group_code))
        # find the copy directive for this group code
        copy_directive = next((cd for cd in copy_directives if cd.new_name.endswith(group_code_in_file_name)), None)

        if copy_directive is not None:
            # loop over family types and add to type keep list
            for family_type_storage in family_storage_data.family_type_data_storage:
                grouping_code_parameter = family_type_storage.get_parameter_by_name(GROUPING_CODE_PARAMETER_NAME)
                if grouping_code_parameter and clean_code(grouping_code_parameter.value) == each_group_code:
                    type_keep_lists.append([copy_directive.new_name, family_type_storage.family_type_name])
        else:
            print("Le impossibele: No copy directive found for group code: {}".format(group_code_in_file_name))
            for cp in copy_directives:
                print("Copy Directive: {}".format(cp.new_name))

    
    return type_keep_lists


def create_swap_directives(family_storage_data, unique_group_codes, copy_directives):
    """
    Create swap directives for each unique group code in the family storage data.

    :param family_storage_data: The family storage data from which to create swap directives.
    :type family_storage_data: :class:`.FamilyTypeDataStorageManager`
    :param unique_group_codes: A list of unique group codes to create swap directives for.
    :type unique_group_codes: list[str]
    :param copy_directives: A list of copy directives to be used for creating swap directives.
    :type copy_directives: list[:class:`.FamilyDirectiveCopy`]
    
    :return: A list of swap directives.
    :rtype: list[:class:`.FamilyDirectiveSwap`]
    """
    
    #loop over unique group codes and
    # find associated copy directive
    # build swap directive from old family name , new family name nad same family type name

    swap_directives = []

    for each_group_code in unique_group_codes:
        # amend the group code to the copy directive file name
        group_code_in_file_name = "{}.rfa".format(convert_to_file_name_code(each_group_code))
        # find the copy directive for this group code
        copy_directive = next((cd for cd in copy_directives if cd.new_name.endswith(group_code_in_file_name)), None)

        if copy_directive is not None:
            # loop over family types and create swap directives
            for family_type_storage in family_storage_data.family_type_data_storage:
                grouping_code_parameter = family_type_storage.get_parameter_by_name(GROUPING_CODE_PARAMETER_NAME)
                if grouping_code_parameter and clean_code(grouping_code_parameter.value) == each_group_code:
                    swap_directive = FamilyDirectiveSwap(
                        name = family_storage_data.family_name,
                        category= family_storage_data.family_category,
                        source_type_name= family_type_storage.family_type_name,
                        target_family_name = copy_directive.new_name[:-4]   , # remove the '.rfa' !!
                        target_family_type_name = family_type_storage.family_type_name
                    )
                    swap_directives.append(swap_directive)
        else:
            print("Le impossibele: No copy directive found for group code: {}".format(group_code_in_file_name))
            for cp in copy_directives:
                print("Copy Directive: {}".format(cp.new_name))


    return swap_directives


def create_directives(family_storage_data_list, output_directory, code_descriptor_path):
    """
    Create directives based on family storage data.

    :param family_storage_data: The family storage data from which to create directives.
    :type family_storage_data: a list of :class:`.FamilyTypeDataStorageManager`
    
    :return:
        Result class instance.

        - result.status: Directive creation status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message will be a log of conversion steps.
        - result.result will be [tbc]

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list

    :rtype: :class:`.Result`
    """
    return_value = Result()
    
    try:
       # analyse each family:
       # set up a copy directive for each unique group code
       # set up a sap directive for each family type from old family to new family
       # create a list of types to keep per new family ( text file with same name as the new family name )

        overall_copy_directives = []
        overall_swap_directives = []
        overall_type_keep_lists = []

        print("loading code description mapping from file: {}".format(code_descriptor_path))
        # load code  to descriptor mapper
        code_to_descriptor_map = load_group_code_description(code_descriptor_path)
        print("Loaded code to descriptor with {} entries from mapping from file.".format(len(code_to_descriptor_map)))
        if code_to_descriptor_map is None:
            return_value.update_sep(
                False,
                "Failed to load code description mapping from file: {}".format(code_descriptor_path),
            )
            return return_value

        # loop over all family storage instances and build directives
        for family_data_storage_instance in family_storage_data_list:

            # get the uniq group codes from the family storage data
            unique_group_codes = get_unique_group_codes(family_data_storage_instance)

            # if no codes found move on to the next family
            if len(unique_group_codes) == 0:
                return_value.update_sep(
                    False,
                    "No unique group codes found in family storage data. {}".format(family_data_storage_instance.family_name),
                )
                continue

            # check all group codes exist in descriptor mapper
            for group_code in unique_group_codes:
                if group_code not in code_to_descriptor_map:
                    return_value.update_sep(
                        False,
                        "Grouping code '{}' not found in code description mapping.".format(group_code),
                    )
                    continue

            # create directives for each unique group code
            copy_directives = create_copy_directives(family_data_storage_instance, unique_group_codes, output_directory,  code_to_descriptor_map)
            # add directives to be returned
            overall_copy_directives = overall_copy_directives + copy_directives

            # create lists of types to be maintained in the new family
            type_keep_lists = create_type_maintained_lists(family_data_storage_instance, unique_group_codes, copy_directives)
            overall_type_keep_lists = overall_type_keep_lists + type_keep_lists
            
            # create swap directives
            swap_directives = create_swap_directives(family_data_storage_instance, unique_group_codes, copy_directives)
            overall_swap_directives = overall_swap_directives + swap_directives

        # return the overall copy directives, keep lists, swap directives
        return_value.result.append(overall_copy_directives)
        return_value.result.append(overall_type_keep_lists)
        return_value.result.append(overall_swap_directives)
            
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to create directives with exception: {}".format(e),
        )
    
    return return_value