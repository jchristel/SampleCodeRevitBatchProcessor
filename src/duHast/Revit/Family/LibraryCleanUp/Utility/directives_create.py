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



from duHast.Revit.Family.LibraryCleanUp.Utility.defaults import GROUPING_CODE_PARAMETER_NAME, CATEGORY_FILE_NAME_PREFIX_MAPPER
from duHast.Revit.Family.LibraryCleanUp.Utility.grouping_code import clean_code, convert_to_file_name_code, load_group_code_description
from duHast.Revit.Family.LibraryCleanUp.Utility.family_file_name import build_family_name_from_descriptor


from duHast.Revit.Family.Data.Objects.family_type_data_storage_manager import FamilyTypeDataStorageManager
from duHast.Revit.Family.Data.Objects.family_type_data_storage import FamilyTypeDataStorage
from duHast.Revit.Family.Data.Objects.family_directive_copy import FamilyDirectiveCopy
from duHast.Revit.Family.Data.Objects.family_directive_swap_instances_of_type import FamilyDirectiveSwap

from duHast.Utilities.files_io import file_exist



def get_code_to_use(full_code, group_code, code_to_descriptor_map):

    # get the description for the group code
    code_description = code_to_descriptor_map.get(full_code, None)

    # this should not happen....
    if code_description is None:
        # try to get the group code description from the group code
        code_description = code_to_descriptor_map.get(group_code, None)
        if code_description is None:
            # if the group code is not in the mapping, raise an error
            raise ValueError("Grouping code '{}' and full code: {} not found in code description mapping.".format(group_code, full_code))
    
    # use the first part of the description as the code to use for the file name
    code_to_use  = code_description[0]
    return code_to_use, code_description

def get_unique_group_codes_from_family(family_storage_data):
    """
    Get unique group codes from the family storage data.

    will return a dictioanry where key is the full code and value is the group code without any sub codes.
    ITSE-002.01 will return {'ITSE-002.01': 'ITSE-002'}
    ITSE-001 will return {'ITSE-001': 'ITSE-001'}

    :param family_storage_data: The family storage data from which to get the unique group codes.
    :type family_storage_data: :class:`.FamilyTypeDataStorageManager`
    :return: A dictionary of unique  codes and their cleaned versions.
    :rtype: {str:str}
    """

    unique_group_codes = {}
   
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

        # check if successful
        if (grouping_code_parameter is None):
            raise ValueError("Grouping code parameter '{}' not found in family type data storage.".format(GROUPING_CODE_PARAMETER_NAME))
        
        # remove any sub codes 
        group_code_cleaned = clean_code(grouping_code_parameter.value)
        if grouping_code_parameter.value not in unique_group_codes:
            unique_group_codes[grouping_code_parameter.value] = group_code_cleaned  # store the cleaned code as the value in the dictionary
           
    
    return unique_group_codes


def create_copy_directive_catalogue_file(name, category, source_file_path, target_directory, new_name ):
    """
    Create a copy directive for the catalogue file.

    :param name: The name of the catalogue file.
    :type name: str
    :param category: The category of the family.
    :type category: str
    :param source_file_path: The path to the source catalogue file.
    :type source_file_path: str
    :param target_directory: The directory where the catalogue file will be copied to.
    :type target_directory: str
    :param new_name: The new name for the catalogue file.
    :type new_name: str
    :return: A copy directive for the catalogue file.
    :rtype: :class:`.FamilyDirectiveCopy` or None if the source file does not exist.
    """

    # check if the source file path exists and is a file
    if (file_exist(source_file_path)):
        # create a copy directive for the catalogue file
        return FamilyDirectiveCopy(
            name=name, 
            category=category, 
            source_file_path=source_file_path, 
            target_directory=target_directory, 
            new_name=new_name,
        )
    return None

def create_copy_directives(family_storage_data, unique_group_codes, output_directory, code_to_descriptor_map, output):
    """
    Create copy directives for each unique group code in the family storage data.

    :param family_storage_data: The family storage data from which to create copy directives. (takes the family name, category and file path from this data)
    :type family_storage_data: :class:`.FamilyTypeDataStorageManager`
    :param unique_group_codes: A dictionary where key is the full code and value is the group code without any sub codes.
    :type unique_group_codes: dictionary {str:str}
    :param output_directory: The directory where the copied families will be saved.
    :type output_directory: str
    :param code_to_descriptor_map: A mapping of grouping codes to their descriptions.
    :type code_to_descriptor_map: dict[str, (str, str)]
    
    :return: A list of copy directives.
    :rtype: list[:class:`.FamilyDirectiveCopy`]
    """

    # set up a list containing all copy directives to be created
    copy_directives = []
    unique_new_file_name_list = []  # to keep track of unique new file names

    for full_code, group_code in unique_group_codes.items():
        output("...Processing full code: {} and group code: {}".format(full_code, group_code))
        
        # get the code to use to identify the family in the copy directive
        code_to_use, code_description = get_code_to_use(full_code, group_code, code_to_descriptor_map)

        # build family name from the group code and description
        fam_name_part = build_family_name_from_descriptor(code_description, code_to_use, output=output)

        output("...Family name part for group code {}: {} derived from: {}".format( code_to_use, fam_name_part, code_description))


        # set a default indicating that category does not exist in the mapper
        category_prefix = "WTF"
        # get the category prefix
        if family_storage_data.family_category in CATEGORY_FILE_NAME_PREFIX_MAPPER:
            # if the family category is in the mapper, use the prefix from the mapper
            category_prefix = CATEGORY_FILE_NAME_PREFIX_MAPPER[family_storage_data.family_category]

        # build new family name
        new_file_name_base ="{}_{}".format(category_prefix, fam_name_part)
        new_file_name_revit = "{}.rfa".format(new_file_name_base)
        new_family_name_catalogue = "{}.txt".format(new_file_name_base)

        # only add copy directive if the new file name is unique in the list of unique new file names
        # since we are combining multiple codes into one family there is a possibility that the new file name is not unique
        if new_file_name_revit in unique_new_file_name_list:
            continue  # skip if the new file name is not unique

        # add the new file name to the list of unique new file names
        unique_new_file_name_list.append(new_file_name_revit)

        output("Creating copy directive for group code: {} with new file name: {}".format(code_to_use, new_file_name_revit))
        # create a copy directive for each unique group code
        #name, category, source_file_path, target_directory, new_name
        copy_directive = FamilyDirectiveCopy(
            name = family_storage_data.family_name, 
            category = family_storage_data.family_category, 
            source_file_path = family_storage_data.family_file_path, 
            target_directory =  output_directory, 
            new_name = new_file_name_revit,
        )

        #output("...Created copy directive, new name: {}".format(copy_directive.new_name))
        
        # add to over all list
        copy_directives.append(copy_directive)

        # original catalogue file name
        original_catalogue_file_name = "{}.txt".format(family_storage_data.family_name[:-4])  # remove the '.rfa' from the family name

        # get the source file path
        original_catalogue_file_path = family_storage_data.family_file_path.replace(".rfa", ".txt")  # replace the '.rfa' with '.txt'

        # get catalogue file copy directive
        copy_directive_catalogue_file = create_copy_directive_catalogue_file( 
            original_catalogue_file_name,
            family_storage_data.family_category,  
            original_catalogue_file_path, 
            output_directory, 
            new_family_name_catalogue,
        )
        
        # check if the catalogue file copy directive is not None ( there is no catalogue file for this family )
        if copy_directive_catalogue_file is not None:
            #output("...Created copy directive, new name: {}".format(copy_directive_catalogue_file.new_name))
            # add to the copy directives list
            copy_directives.append(copy_directive_catalogue_file)

    # return the list of copy directives
    return copy_directives


def create_type_maintained_lists(family_storage_data, unique_group_codes, copy_directives, code_to_descriptor_map):

    """
    Create lists of family types to be maintained in the new family based on unique group codes.

    :param family_storage_data: The family storage data from which to create type maintained lists.
    :type family_storage_data: :class:`.FamilyTypeDataStorageManager`
    :param unique_group_codes: A dictionary where key is the full code and value is the group code without any sub codes.
    :type unique_group_codes: dictionary {str:str}
    :param copy_directives: A list of copy directives to be used for creating type maintained lists.
    :type copy_directives: list[:class:`.FamilyDirectiveCopy`]
    :param code_to_descriptor_map: A mapping of grouping codes to their descriptions.
    :type code_to_descriptor_map: dict[str, (str, str)]
    
    :return: A list of nested type maintained lists with two entries each: new family name, family type name to be maintained. ( a family with multiple times to be maintained will have multiple entries in the list )
    :rtype: list[ list[str] ]
    """
    
    #loop over unique group codes and
    # find associated copy directive
    # all types with matching group code

    type_keep_lists = []

    type_keep_list_unique = []

    for full_code, group_code in unique_group_codes.items():

        # get the code to use to identify the family in the copy directive
        code_to_use, code_description = get_code_to_use(full_code, group_code, code_to_descriptor_map)
        
        # get the code used on the family
        #group_code_descriptor_family = code_to_descriptor_map.get(group_code, None)
        # if group_code_descriptor_family is None:
        #    raise ValueError("Grouping code '{}' not found in code description mapping.".format(group_code))
        

        # amend the group code to the copy directive file name
        group_code_in_file_name = "{}.rfa".format(convert_to_file_name_code(code_to_use))

        # find the copy directive for this group code
        copy_directive = next((cd for cd in copy_directives if cd.new_name.endswith(group_code_in_file_name)), None)

        if copy_directive is not None:
            # loop over family types and add to type keep list
            for family_type_storage in family_storage_data.family_type_data_storage:

                # get the grouping code parameter from the family type storage
                grouping_code_parameter = family_type_storage.get_parameter_by_name(GROUPING_CODE_PARAMETER_NAME)
                
                # check if we have a grouping code parameter and if it matches the group code 
                if grouping_code_parameter :
                    if clean_code(grouping_code_parameter.value) == group_code or clean_code(grouping_code_parameter.value) == full_code:
                        key = "{}{}".format(copy_directive.new_name, family_type_storage.family_type_name)
                        # make sure we only add unique type keep lists
                        if key not in type_keep_list_unique:
                            type_keep_lists.append([copy_directive.new_name, family_type_storage.family_type_name])
                            type_keep_list_unique.append(key)  # add the key to the set of unique type keep lists

        else:
            print("Le impossibele: No copy directive found for group code: {}".format(group_code_in_file_name))
            for cp in copy_directives:
                print("Copy Directive: {}".format(cp.new_name))

    
    return type_keep_lists


def create_swap_directives(family_storage_data, unique_group_codes, copy_directives, code_to_descriptor_map, output=None):
    """
    Create swap directives for each unique group code in the family storage data.

    :param family_storage_data: The family storage data from which to create swap directives.
    :type family_storage_data: :class:`.FamilyTypeDataStorageManager`
    :param unique_group_codes: A dictionary of full code to group code mappings.(i.e ITSE-002.01: ITSE-002 or ITSE-001: ITSE-001)
    :type unique_group_codes: {str:str}
    :param copy_directives: A list of copy directives to be used for creating swap directives.
    :type copy_directives: list[:class:`.FamilyDirectiveCopy`]
    :param code_to_descriptor_map: A mapping of grouping codes to their descriptions.
    :type code_to_descriptor_map: dict[str, (str, str)]
    
    :return: A list of swap directives.
    :rtype: list[:class:`.FamilyDirectiveSwap`]
    """
    
    #loop over unique group codes and
    # find associated copy directive
    # build swap directive from old family name , new family name nad same family type name

    swap_directives = []
    swap_directives_unique = set()  # to keep track of unique swap directives

    for full_code, group_code in unique_group_codes.items():

        # get the code to use to identify the family in the copy directive
        code_to_use, code_description = get_code_to_use(full_code, group_code, code_to_descriptor_map)
        
        # amend the group code to the copy directive file name
        group_code_in_file_name = "{}.rfa".format(convert_to_file_name_code(code_to_use))
        # find the copy directive for this group code
        copy_directive = next((cd for cd in copy_directives if cd.new_name.endswith(group_code_in_file_name)), None)

        if copy_directive is not None:
            # loop over family types and create swap directives
            for family_type_storage in family_storage_data.family_type_data_storage:
                grouping_code_parameter = family_type_storage.get_parameter_by_name(GROUPING_CODE_PARAMETER_NAME)
                
                
                if grouping_code_parameter:
                    if clean_code(grouping_code_parameter.value) == group_code or clean_code(grouping_code_parameter.value) == full_code:
                        # check by family name, category and family type name if the swap directive is unique
                        key = "{}{}{}".format(family_storage_data.family_name, family_storage_data.family_category, family_type_storage.family_type_name)
                        if key not in swap_directives_unique:
                            swap_directive = FamilyDirectiveSwap(
                                name = family_storage_data.family_name,
                                category= family_storage_data.family_category,
                                source_type_name= family_type_storage.family_type_name,
                                target_family_name = copy_directive.new_name[:-4]   , # remove the '.rfa' !!
                                target_family_type_name = family_type_storage.family_type_name
                            )
                            swap_directives.append(swap_directive)
                            swap_directives_unique.add(key)  # add the key to the set of unique swap directives
                            if output is not None:
                                #output("Created swap directive for family'{}'.".format(key))
                                pass
                        else:
                            if output is not None:
                                #output("Swap directive for family type '{}' already exists, skipping...".format(key))
                                pass
                            #print("Swap directive for family type '{}' already exists, skipping...".format(family_type_storage.family_type_name))
        else:
            print("Le impossibele: No copy directive found for group code: {}".format(group_code_in_file_name))
            for cp in copy_directives:
                print("Copy Directive: {}".format(cp.new_name))


    return swap_directives


def create_directives(family_storage_data_list, output_directory, code_descriptor_path, output):
    """
    Create directives based on family storage data.

    :param family_storage_data: The family storage data from which to create directives.
    :type family_storage_data: a list of :class:`.FamilyTypeDataStorageManager`
    
    :return:
        Result class instance.

        - result.status: Directive creation status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message will be a log of conversion steps.
        - result.result will be a list containing the following items:
            - A list of :class:`.FamilyDirectiveCopy` directives for copying families.
            - A list of lists containing family type names to be maintained in the new family.
            - A list of :class:`.FamilyDirectiveSwap` directives for swapping family instances of types.
            - A list of family storage instances that had missing group codes in the code description mapping.

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
       # set up a swap directive for each family type from old family to new family
       # create a list of types to keep per new family ( text file with same name as the new family name )

        overall_copy_directives = []
        overall_swap_directives = []
        overall_type_keep_lists = []
        families_with_missing_group_codes = []

        output("loading code description mapping from file: {}".format(code_descriptor_path))
        # load code  to descriptor mapper
        code_to_descriptor_map = load_group_code_description(code_descriptor_path)
        
        if code_to_descriptor_map is None:
            return_value.update_sep(
                False,
                "Failed to load code description mapping from file: {}".format(code_descriptor_path),
            )
            return return_value
        
        output("Loaded code to descriptor with {} entries from mapping from file.".format(len(code_to_descriptor_map)))

        # loop over all family storage instances and build directives
        for family_data_storage_instance in family_storage_data_list:

            return_value.append_message("Processing family storage data for family: {}".format(family_data_storage_instance.family_name))
            output("Processing family storage data for family: {}".format(family_data_storage_instance.family_name))
            unique_group_codes_in_family = {}
            
            # wrap into try catch since this may raise an exception if the family storage data is not valid or does not contain types
            try:
                # get the unique group codes from the family storage data
                # this function will raise an exception if the family storage data is not valid or does not contain types
                unique_group_codes_in_family = get_unique_group_codes_from_family(family_data_storage_instance)

                # if no codes found move on to the next family
                if len(unique_group_codes_in_family) == 0:
                    return_value.append_message(
                        "No unique group codes found in family storage data. {}".format(family_data_storage_instance.family_name),
                    )
                    families_with_missing_group_codes.append(family_data_storage_instance)
                    continue
            except Exception as e:
                return_value.append_message(
                    "Failed to get unique group codes from family storage data for family {}: {}. Skipping...".format(family_data_storage_instance.family_name, e),
                )
                output("Failed to get unique group codes from family storage data for family {}: {}. Skipping...".format(family_data_storage_instance.family_name, e))
                families_with_missing_group_codes.append(family_data_storage_instance)
                # skip to next family
                continue

            return_value.append_message("Found {} unique group codes in family storage data for family: {}".format(len(unique_group_codes_in_family), family_data_storage_instance.family_name))
            output("Found {} unique group codes in family storage data for family: {}".format(len(unique_group_codes_in_family), family_data_storage_instance.family_name))
            found_all_group_codes = True
            
            missing_group_codes = {}
            # check all group codes exist in descriptor mapper
            for code_full, group_code in unique_group_codes_in_family.items():
                if code_full not in code_to_descriptor_map and group_code not in code_to_descriptor_map:
                    return_value.append_message(
                        "Full code '{}' and group code: {} not found in code description mapping.".format(code_full,group_code),
                    )
                    output("......Full code '{}' and group code: {} not found in code description mapping.".format(group_code,group_code))
                    found_all_group_codes = False
                    missing_group_codes[code_full] = group_code # add the full code and group code to the list of codes
                    #break

            if not found_all_group_codes:
                # remove the missing codes from the unique group codes in family
                for code_full, group_code in missing_group_codes.items():
                    unique_group_codes_in_family.pop(code_full, None)  # remove the full code from the dictionary
                    return_value.append_message(
                        "......Full code '{}' and group code: {} removed due to missing mapping mapping.".format(code_full,group_code),
                    )
                    output("......Full code '{}' and group code: {} removed due to missing mapping mapping.".format(code_full,group_code))
                
            copy_directives = []
            try:
                # create directives for each unique group code
                copy_directives = create_copy_directives(family_data_storage_instance, unique_group_codes_in_family, output_directory, code_to_descriptor_map, output=output)
            except Exception as e:
                return_value.append_message(
                    "Failed to create copy directives for family {}: {}. Skipping...".format(family_data_storage_instance.family_name, e),
                )
                output("Failed to create copy directives for family {}: {}. Skipping...".format(family_data_storage_instance.family_name, e))
                # skip to next family
                continue
            
            return_value.append_message("Created {} copy directives for family: {}".format(len(copy_directives), family_data_storage_instance.family_name))
            output("Created {} copy directives for family: {}".format(len(copy_directives), family_data_storage_instance.family_name))
            
            # add directives to be returned
            overall_copy_directives = overall_copy_directives + copy_directives

            type_keep_lists = []

            try:
                # create lists of types to be maintained in the new family
                type_keep_lists = create_type_maintained_lists(
                    family_data_storage_instance, 
                    unique_group_codes_in_family, 
                    copy_directives, 
                    code_to_descriptor_map
                )
            except Exception as e:
                return_value.append_message(
                    "Failed to create type maintain lists for family {}: {}. Skipping...".format(family_data_storage_instance.family_name, e),
                )
                output("Failed to create type maintain lists for family {}: {}. Skipping...".format(family_data_storage_instance.family_name, e))
                # skip to next family
                continue

            return_value.append_message("Created {} type keep lists for family: {}".format(len(type_keep_lists), family_data_storage_instance.family_name))
            output("Created {} type keep lists for family: {}".format(len(type_keep_lists), family_data_storage_instance.family_name))

            overall_type_keep_lists = overall_type_keep_lists + type_keep_lists
            
            swap_directives = []

            try:
                # create swap directives
                swap_directives = create_swap_directives(
                    family_data_storage_instance, 
                    unique_group_codes_in_family, 
                    copy_directives, 
                    code_to_descriptor_map,
                    output=output,
                )
            except Exception as e:
                return_value.append_message(
                    "Failed to create swap directives for family {}: {}. Skipping...".format(family_data_storage_instance.family_name, e),
                )
                output("Failed to create swap directives for family {}: {}. Skipping...".format(family_data_storage_instance.family_name, e))
                # skip to next family
                continue

            return_value.append_message("Created {} swap directives for family: {}".format(len(swap_directives), family_data_storage_instance.family_name))
            output("Created {} swap directives for family: {}".format(len(swap_directives), family_data_storage_instance.family_name))

            overall_swap_directives = overall_swap_directives + swap_directives

        # return the overall copy directives, keep lists, swap directives, and list of instances with missing group codes
        return_value.result = []    
        return_value.result.append(overall_copy_directives)
        return_value.result.append(overall_type_keep_lists)
        return_value.result.append(overall_swap_directives)
        return_value.result.append(families_with_missing_group_codes)
        
    except Exception as e:
        output(e)
        return_value.update_sep(
            False,
            "Failed to create directives with exception: {}".format(e),
        )
    
    output("Directive creation completed successfully {}".format(return_value.status))
    return return_value