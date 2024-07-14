"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family report data utility module containing functions to read the data from file.
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

import os
from duHast.Utilities.files_csv import read_csv_file
from duHast.Revit.Family.Data.Objects.ifamily_data_storage import IFamilyDataStorage
from duHast.Revit.Family.Data.Objects.family_base_data_storage import (
    FamilyBaseDataStorage,
)
from duHast.Revit.Categories.Data.Objects.category_data_storage import (
    FamilyCategoryDataStorage,
)
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_storage import (
    FamilyLinePatternDataStorage,
)
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_storage import (
    FamilySharedParameterDataStorage,
)
from duHast.Revit.Warnings.Data.Objects.warnings_data_storage import (
    FamilyWarningsDataStorage,
)
from duHast.Revit.Family.Data.Objects.family_data_container import FamilyDataContainer
from duHast.Revit.Family.Data.Objects.family_data_family import FamilyDataFamily
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import file_exist
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.directory_io import is_directory


DATA_CONVERSION = {
    FamilyBaseDataStorage.data_type: FamilyBaseDataStorage,
    FamilyCategoryDataStorage.data_type: FamilyCategoryDataStorage,
    FamilyLinePatternDataStorage.data_type: FamilyLinePatternDataStorage,
    FamilySharedParameterDataStorage.data_type: FamilySharedParameterDataStorage,
    FamilyWarningsDataStorage.data_type: FamilyWarningsDataStorage,
}


def convert_data_rows_to_data_storage(data_rows, target_type):
    """
    Convert the data rows into the target type of data storage object.

    :param data_rows: The data rows to be converted into the target type of data storage object.
    :type data_rows: list
    :param target_type: The target type of data storage object to convert the data rows into.
    :type target_type: IFamilyDataStorage
    :return: A Result object containing the list of IFamilyDataStorage objects if successful.
    :rtype: Result

    """

    return_value = Result()
    # flag checking whether an exception occurred when converting the data rows
    an_exception_occurred_counter = 0
    try:
        if not issubclass(target_type, IFamilyDataStorage):
            raise TypeError(
                "Invalid target type. Expected IFamilyDataStorage, got {}".format(
                    target_type.__name__
                )
            )
        # check if the data rows is a list
        if not isinstance(data_rows, list):
            raise TypeError(
                "Invalid data rows type. Expected list, got {}".format(type(data_rows))
            )

        # loop over all rows but the first (header row) extracted and set up objects
        for row in data_rows[1:]:
            try:
                # check if the row has the correct number of columns
                if len(row) != target_type.number_of_properties:
                    raise ValueError("Invalid data row{}".format(row))
                # initialise the storage object without the data type
                dummy = target_type(*row[1:])
                return_value.result.append(dummy)
            except Exception as e:
                return_value.append_message(
                    "Failed to convert data row with exception: {}".format(e)
                )
                an_exception_occurred_counter = an_exception_occurred_counter + 1

        # check if an exception occurred
        if an_exception_occurred_counter == 0:
            return_value.update_sep(
                True,
                "Successfully converted rows: {} into {}".format(
                    len(data_rows) - 1, target_type.__name__
                ),
            )
        else:
            return_value.update_sep(
                False,
                "Failed to convert rows into {}: {} rows failed to convert".format(
                    target_type.__name__, an_exception_occurred_counter
                ),
            )

    except Exception as e:
        return_value.update_sep(
            False, "Failed to convert rows into {}: {}".format(target_type.__name__, e)
        )
    return return_value


def read_base_data(file_path, data_type):
    """
    Read the base data from the file and return a list of IFamilyDataStorage objects.

    :param file_path: The path to the file to read the data from.
    :type file_path: str
    :param data_type: The type of data storage the file data is to be converted to.
    :type data_type: IFamilyDataStorage
    :return: A Result object containing the list of IFamilyDataStorage objects if successful.
    :rtype: Result

    """

    return_value = Result()
    try:
        # check what was past in
        if not isinstance(file_path, str):
            raise TypeError(
                "Invalid file path type. Expected str, got {}".format(type(file_path))
            )

        if not issubclass(data_type, IFamilyDataStorage):
            raise TypeError(
                "Invalid data type. Expected IFamilyDataStorage, got {}".format(
                    type(data_type)
                )
            )

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))

        # Read the data from the file
        data = read_csv_file(file_path)

        # Check if the data is empty
        if not data or len(data) <= 1:
            raise ValueError("Empty data in the file: {}".format(file_path))

        # check data type is what we expect
        # first column in second row contains the report data type
        if len(data[1]) == 0:
            raise ValueError("Data type missing in the file.")
        else:
            if not (data[1][0] == data_type.data_type):
                raise TypeError(
                    "Invalid data type.Got: {}, expected {}.".format(
                        data[1][0], data_type.data_type
                    )
                )

        # convert rows read into data storage objects
        data_storage_conversion_result = convert_data_rows_to_data_storage(
            data_rows=data, target_type=data_type
        )
        # check what came back before adding to converted data
        if data_storage_conversion_result.status:
            return_value.result = data_storage_conversion_result.result

        # just append the log message
        return_value.append_message(data_storage_conversion_result.message)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to read data file with exception: {}".format(e)
        )

    return return_value


def read_family_base_data(file_path):
    """
    Read the family base data from the file and return a list of FamilyBaseDataStorage objects.

    :param file_path: The path to the file to read the data from.
    :type file_path: str
    :return: A Result object containing the list of FamilyBaseDataStorage objects if successful.
    :rtype: Result

    """

    return_value = Result()
    try:

        return_value = read_base_data(
            file_path=file_path, data_type=FamilyBaseDataStorage
        )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to read data file with exception: {}".format(e)
        )

    return return_value


def read_family_category_base_data(file_path):
    """
    Read the family category data from the file and return a list of FamilyCategoryDataStorage objects as part of a result object

    :param file_path: The path to the file to read the data from.
    :type file_path: str
    :return: A Result object containing the list of FamilyCategoryDataStorage objects if successful.
    :rtype: Result

    """
    return_value = Result()
    try:

        return_value = read_base_data(
            file_path=file_path, data_type=FamilyCategoryDataStorage
        )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to read data file with exception: {}".format(e)
        )

    return return_value


def read_family_line_pattern_base_data(file_path):
    """
    Read the family line pattern data from the file and return a list of FamilyLinePatternDataStorage objects as part of a result object

    :param file_path: The path to the file to read the data from.
    :type file_path: str
    :return: A Result object containing the list of FamilyLinePatternDataStorage objects if successful.
    :rtype: Result

    """
    return_value = Result()
    try:

        return_value = read_base_data(
            file_path=file_path, data_type=FamilyLinePatternDataStorage
        )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to read data file with exception: {}".format(e)
        )

    return return_value


def read_family_shared_parameter_data(file_path):
    """
    Read the family shared parameter data from the file and return a list of FamilySharedParameterDataStorage objects as part of a result object

    :param file_path: The path to the file to read the data from.
    :type file_path: str
    :return: A Result object containing the list of FamilySharedParameterDataStorage objects if successful.
    :rtype: Result

    """
    return_value = Result()
    try:

        return_value = read_base_data(
            file_path=file_path, data_type=FamilySharedParameterDataStorage
        )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to read data file with exception: {}".format(e)
        )

    return return_value


def read_family_warnings_data(file_path):
    """
    Read the family warnings data from the file and return a list of FamilyWarningsDataStorage objects as part of a result object

    :param file_path: The path to the file to read the data from.
    :type file_path: str
    :return: A Result object containing the list of FamilyWarningsDataStorage objects if successful.
    :rtype: Result

    """
    return_value = Result()
    try:

        return_value = read_base_data(
            file_path=file_path, data_type=FamilyWarningsDataStorage
        )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to read data file with exception: {}".format(e)
        )

    return return_value


def read_data_into_family_containers(path_to_data):
    """
    Get all csv files in directory provided and attempts to read them into varies lists of data storage objects:

    - FamilyBaseDataStorage
    - FamilyCategoryDataStorage
    - FamilyLinePatternDataStorage
    - FamilySharedParameterDataStorage
    - FamilyWarningsDataStorage

    These are then added to a family container object and returned. The family container object contains all storage instances of a specific root or nested family
    identified by a unique family name nesting path + family category nesting path

    Note: The content of multiple csv files of the same data type will be combined into a single list of objects.

    :param path_to_data: The path to the directory containing the csv files or fully qualified file path to a single data file.
    :type directory_path: str

    :return: A Result object containing the list of Family Containers objects if successful.
    :rtype: Result
    """

    files = []
    return_value = Result()
    try:
        # check if path_to_data is a string
        if isinstance(path_to_data, str) == False:
            raise TypeError(
                "Invalid path type. Expected str, got {}".format(type(path_to_data))
            )

        # check if past in path is a directory or file
        # if it is a directory, get all csv files in the directory
        if is_directory(path_to_data):
            # get all csv files in the directory
            files = get_files_single_directory(
                folder_path=path_to_data,
                file_prefix="",
                file_suffix="",
                file_extension=".csv",
            )
        else:
            # if it is a file, check if it is a csv file
            if path_to_data.endswith(".csv"):
                # check if file exists
                if file_exist(path_to_data) == False:
                    raise FileNotFoundError("File not found: {}".format(path_to_data))
                else:
                    files.append(path_to_data)

        # read the data from each file into rows
        data_read = []
        for data_file in files:
            try:
                # read the data from the file
                data = read_csv_file(data_file)
                if not data or len(data) <= 1:
                    raise ValueError("Empty data in the file: {}".format(data_file))
                else:
                    data_read.append(data)
            except Exception as e:
                return_value.append_message(
                    "Failed to read data file with exception: {}".format(e)
                )
        return_value.append_message("Read {} files".format(len(data_read)))

        # convert the data rows into storage objects depending on the data type
        # this will end up containing lists of storage objects, one list per file read
        data_converted = []
        for data in data_read:
            # check the first entry in the second row, since it contains the storage data type
            if len(data[1]) == 0:
                raise ValueError("Data type missing in the file.")
            else:
                if not (data[1][0] in DATA_CONVERSION.keys()):
                    raise TypeError("Invalid data type.Got: {}.".format(data[1][0]))
                else:
                    # convert row into storage object depending on the data type
                    data_type_name = data[1][0]
                    data_conversion_type = DATA_CONVERSION[data_type_name]
                    data_storage_conversion_result = convert_data_rows_to_data_storage(
                        data_rows=data, target_type=data_conversion_type
                    )
                    # check what came back before adding to converted data
                    if data_storage_conversion_result.status:
                        data_converted.append(data_storage_conversion_result.result)
                    # just append the log message
                    return_value.append_message(data_storage_conversion_result.message)

        return_value.append_message(
            "Converted {} data entries".format(len(data_converted))
        )
        # group storage containers by family root path and category root path identifying unique families
        containers_grouped_by_family_data = {}
        # loop over all storage lists and assign data to container
        for storage_list in data_converted:
            for storage_instance in storage_list:
                if (
                    storage_instance.root_name_path
                    + storage_instance.root_category_path
                    not in containers_grouped_by_family_data
                ):
                    # set up a new container for this family
                    container_instance = FamilyDataContainer()
                    # add the storage
                    container_instance.add_data_storage(storage_instance)
                    containers_grouped_by_family_data[
                        storage_instance.root_name_path
                        + storage_instance.root_category_path
                    ] = container_instance
                else:
                    # add the storage to the existing container
                    containers_grouped_by_family_data[
                        storage_instance.root_name_path
                        + storage_instance.root_category_path
                    ].add_data_storage(storage_instance)

        # add list of containers to return object
        for key, value in containers_grouped_by_family_data.items():
            return_value.result.append(value)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to read data with exception: {}".format(e)
        )
    return return_value


def _get_root_families(families):
    """
    Returns all families which root families from past in list

    :param families: _description_
    :type families: _type_
    :return: _description_
    :rtype: _type_
    """
    root_families = []

    # do a type check
    if isinstance(families, list) == False:
        raise TypeError(
            "families needs to be of type list. Got: {} instead".format(type(families))
        )

    for family in families:
        # do a type check
        if isinstance(family, FamilyDataFamily) == False:
            raise TypeError(
                "All instances in families needs to be of type FamilyDataFamily. Got: {} instead".format(
                    type(family)
                )
            )

        if family.is_root_family:
            root_families.append(family)
    return root_families


def _assign_nested_families_to_root_families(root_families, families):
    """
    Adds nested families to their respective root families ( root family here is the top most family in the nesting tree)

    :param root_families: List of roo
    :type root_families: _type_
    :param families: _description_
    :type families: _type_
    :raises ValueError: _description_
    :return: _description_
    :rtype: _type_
    """
    for family in families:
        # check if this is a nested family ( not a root family )
        if family.is_root_family == False:
            # get the root family name and category
            root_name_path_chunks = family.family_nesting_path.split(NESTING_SEPARATOR)
            compare_family_name = root_name_path_chunks[0]
            category_name_path_chunks = family.family_category_nesting_path.split(
                NESTING_SEPARATOR
            )
            compare_family_category = category_name_path_chunks[0]

            # loop over root families and find the host
            found_root_family = False
            for root_family in root_families:
                if (
                    root_family.family_name == compare_family_name
                    and root_family.family_category == compare_family_category
                ):
                    root_family.add_nested_family_instance(family)
                    found_root_family = True
                    break

            # do a sanity check
            if found_root_family == False:
                raise ValueError(
                    "Cant find root family for {} {}".format(
                        compare_family_name, compare_family_category
                    )
                )
    return root_families


def read_data_into_families(path_to_data):
    """
    Read the data from the csv files in the directory and return a list of FamilyDataFamily objects.

    :param path_to_data: The path to the directory containing the csv files or fully qualified file path to single report csv file.
    :type path_to_data: str
    :return: A Result object containing the list of FamilyDataFamily objects if successful.
    :rtype: Result

    """

    return_value = Result()
    families = []

    try:
        # first read reports into containers
        container_read_result = read_data_into_family_containers(path_to_data)
        return_value.update(container_read_result)

        # check if the read was successful
        if container_read_result.status == False:
            raise ValueError(
                "Failed to read data from: {} into family containers: {} ".format(
                    path_to_data, container_read_result.message
                )
            )

        # cycle over all containers and assign the data to the family objects
        # unique root families are identified by the following container properties
        # - the family name
        # - the family category

        containers = container_read_result.result
        # loop over containers and assign to families
        for container in containers:

            # check if the family is already in the list
            # compare_family_name = container.family_nesting_path
            # compare_family_category = container.family_category_nesting_path

            # if container.is_root_family:
            # if family is a root family use directly the containers family name and family category
            #    compare_family_name = container.family_nesting_path
            #    compare_family_category = container.family_category_nesting_path
            # else:
            # if a nested family get, need to get to the root family at the top of the nesting tree
            #    root_name_path_chunks = container.family_nesting_path.split(
            #        NESTING_SEPARATOR
            #    )
            #    compare_family_name = root_name_path_chunks[0]
            #    category_name_path_chunks = (
            #        container.family_category_nesting_path.split(NESTING_SEPARATOR)
            #    )
            #    compare_family_category = category_name_path_chunks[0]

            # check if the family is already in the list
            family_found = False
            for family in families:
                if (
                    family.family_name == container.family_name
                    and family.family_category == container.family_category
                    and family.family_nesting_path == container.family_nesting_path
                    and family.family_category_nesting_path
                    == container.family_category_nesting_path
                    and family.is_root_family == container.is_root_family
                ):
                    family_found = True
                    family.add_data_container(container)
                    return_value.append_message(
                        "Added container to family: {} - {} {} - {}".format(
                            container.family_name,
                            container.family_category,
                            container.family_nesting_path,
                            container.family_category_nesting_path,
                        )
                    )
                    break
            # if the family is not in the list, add it
            if family_found == False:
                new_family = FamilyDataFamily(
                    family_name=container.family_name,
                    family_category=container.family_category,
                    family_file_path=container.family_file_path,
                    family_nesting_path=container.family_nesting_path,
                    family_category_nesting_path=container.family_category_nesting_path,
                    is_root_family=container.is_root_family,
                )
                new_family.add_data_container(container)
                families.append(new_family)
                return_value.append_message(
                    "Added new family: {} - {} {} - {}".format(
                        container.family_name,
                        container.family_category,
                        container.family_nesting_path,
                        container.family_category_nesting_path,
                    )
                )

        # need to add nested families to root families
        # filter out root families
        root_families = _get_root_families(families=families)
        # assign nested families to root families
        families = _assign_nested_families_to_root_families(root_families, families)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to convert containers into families: {}".format(e)
        )

    return_value.result = families
    return return_value
