"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family report data utility module containing functions to read the data from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

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
                    type(target_type)
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
            return_value.update_sep(True, "Successfully converted rows: {} into {}".format(len(data_rows)-1, type(target_type)))
        else:
            return_value.update_sep(False, "Failed to convert rows into {}: {} rows failed to convert".format(type(target_type), an_exception_occurred_counter))

    except Exception as e:
        return_value.update_sep(
            False, "Failed to convert rows into {}: {}".format(type(target_type), e)
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


def read_category_base_data(file_path):
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

    These are then added to a family container object and returned.

    Note: The content of multiple csv files of the same data type will be combined into a single list of objects.

    :param path_to_data: The path to the directory containing the csv files or fully qualified file path to a single data file.
    :type directory_path: str

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
            files = get_files_single_directory(path_to_data, file_extension=".csv")
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

        # add list of containers to return object
        for key, value in containers_grouped_by_family_data.items():
            return_value.result.append(value)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to read data with exception: {}".format(e)
        )
    return return_value
