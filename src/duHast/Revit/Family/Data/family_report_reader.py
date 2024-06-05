"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family report data utility module containing functions to read the data from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
from duHast.Utilities.files_csv import read_csv_file
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

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import is_directory, file_exist
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_csv import read_csv_file


def convert_data_rows_to_family_base_data_storage(data_rows):
    pass


def convert_data_rows_to_family_category_data_storage(data_rows):
    pass


def convert_data_rows_to_family_line_pattern_data_storage(data_rows):
    pass


def convert_data_rows_to_family_shared_parameter_data_storage(data_rows):
    pass


def convert_data_rows_to_family_warnings_data_storage(data_rows):
    pass


DATA_CONVERSION = {
    FamilyBaseDataStorage.data_type: convert_data_rows_to_family_base_data_storage,
    FamilyCategoryDataStorage.data_type: convert_data_rows_to_family_category_data_storage,
    FamilyLinePatternDataStorage.data_type: convert_data_rows_to_family_line_pattern_data_storage,
    FamilySharedParameterDataStorage.data_type: convert_data_rows_to_family_shared_parameter_data_storage,
    FamilyWarningsDataStorage.data_type: convert_data_rows_to_family_warnings_data_storage,
}


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

        # check what was past in
        if not isinstance(file_path, str):
            raise TypeError(
                "Invalid file path type. Expected str, got {}".format(type(file_path))
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
            if not (data[1][0] == FamilyBaseDataStorage.data_type):
                raise TypeError(
                    "Invalid data type.Got: {}, expected {}.".format(
                        data[1][0], FamilyBaseDataStorage.data_type
                    )
                )

        # loop over all rows but the first (header row) extracted and set up objects
        for row in data[1:]:
            try:
                # check if the row has the correct number of columns
                if len(row) != FamilyBaseDataStorage.number_of_properties:
                    raise ValueError(
                        "Invalid data in the file: {}.\nrow{}".format(file_path, row)
                    )
                # initialise the storage object without the data type
                dummy = FamilyBaseDataStorage(*row[1:])
                return_value.result.append(dummy)
            except Exception as e:
                return_value.append_message(
                    "Failed to read data row with exception: {}".format(e)
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
    pass


def read_family_line_pattern_base_data(file_path):
    """
    Read the family line pattern data from the file and return a list of FamilyLinePatternDataStorage objects as part of a result object

    :param file_path: The path to the file to read the data from.
    :type file_path: str
    :return: A Result object containing the list of FamilyLinePatternDataStorage objects if successful.
    :rtype: Result

    """
    pass


def read_family_shared_parameter_data(file_path):
    """
    Read the family shared parameter data from the file and return a list of FamilySharedParameterDataStorage objects as part of a result object

    :param file_path: The path to the file to read the data from.
    :type file_path: str
    :return: A Result object containing the list of FamilySharedParameterDataStorage objects if successful.
    :rtype: Result

    """
    pass


def read_family_warnings_data(file_path):
    """
    Read the family warnings data from the file and return a list of FamilyWarningsDataStorage objects as part of a result object

    :param file_path: The path to the file to read the data from.
    :type file_path: str
    :return: A Result object containing the list of FamilyWarningsDataStorage objects if successful.
    :rtype: Result

    """
    pass


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
                    data_type = data[1][0]
                    # call the conversion function for the data type
                    data_conversion = DATA_CONVERSION[data_type]
                    data_storage = data_conversion(data[1:])
                    data_converted.append(data_storage)

        # group storage containers by family root path and category root path identifying unique families
        # set up a family container file for each grouping
        # populate the family container with the storage objects
        # return the family containers

    except Exception as e:
        return_value.update_sep(
            False, "Failed to read data with exception: {}".format(e)
        )
    return return_value
