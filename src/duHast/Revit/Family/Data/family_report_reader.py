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
from duHast.Utilities.Objects.result import Result


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
            raise TypeError("Invalid file path type. Expected str.")

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read the data from the file
        data = read_csv_file(file_path)

        # Check if the data is empty
        if not data or len(data) <= 1:
            raise ValueError(f"Empty data in the file: {file_path}")

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
                if len(row) != len(FamilyBaseDataStorage.number_of_properties):
                    raise ValueError(
                        "Invalid data in the file: {}.\nrow{}".format(file_path, row)
                    )
                # initialise the storage object without the data type
                dummy = FamilyBaseDataStorage(*row[1:])
                return_value.result(dummy)
            except Exception as e:
                return_value.append_message("Failed to read data row with exception: {}".format(e))

    except Exception as e:
        return_value.update_sep(False, "Failed to read data file with exception: {}".format(e))
    
    return return_value
        