import os

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.file_picker import get_file_path_from_user

from duHast.Revit.Common import transaction as rTran
from duHast.pyRevit.console_output import print_header
from duHast.Utilities.files_csv import read_csv_file, write_report_data_as_csv
from duHast.Utilities.files_io import (
    get_file_name_without_ext,
    get_directory_path_from_file_path,
)
from duHast.Utilities.Objects.file_encoding_bom import BOMValue


# import Autodesk Revit DataBase namespace
from Autodesk.Revit.DB import  Transaction


def _print_parameters(parameters):
    """
    Print the parameter names to the pyRevit output.

    :param parameters: The list of parameters
    :type parameters: list
    """

    for p in parameters:
        print(p.Definition.Name)


def _print_clean_data(cleaned_csv_data, output):
    """
    Print the cleaned CSV data to the pyRevit output as a table.

    :param cleaned_csv_data: The cleaned CSV data
    :type cleaned_csv_data: list
    :param output: The pyRevit output module
    :type output: module
    """

    format_by_columns = [""] * len(cleaned_csv_data)

    output.print_table(
        table_data=cleaned_csv_data[1:],
        title="Cleaned CSV",
        columns=cleaned_csv_data[:1][
            0
        ],  # need index 0 since the first slice produces a list in a list
        formats=format_by_columns,
    )


def _get_family_type_parameters(doc):
    """
    Get the type parameters of the family.

    :param doc: The family document
    :type doc: Document

    :return:
        Result class instance.

        - result.status (bool) True if family type parameters where retrieved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be a list of the family type parameters [Autodesk.Revit.DB.Parameter]

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    type_parameters = []

    # Assume 'doc' is your current Document object
    family_manager = doc.FamilyManager

    # Get all family types
    family_types = family_manager.Types

    # set-up action to be executed in transaction
    def action():
        action_return_value = Result()
        try:
            # Iterate over each type in the family
            for family_type in family_types:
                action_return_value.append_message(
                    "Checking type: {}".format(family_type.Name)
                )
                # Set the current type
                family_manager.CurrentType = family_type

                # Iterate over all parameters of the family type
                for parameter in family_manager.Parameters:
                    # print("{} :: is instance: {} and storage type: {} ".format(parameter.Definition.Name, parameter.IsInstance, parameter.StorageType))
                    # Check if it's a type parameter and has a formula
                    if not parameter.IsInstance:
                        type_parameters.append(parameter)

                # no need to loop again...
                break
        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to get type parameters with exception: {}".format(e)
            )
        return action_return_value

    transaction = Transaction(doc, "Setting family type")
    return_value = rTran.in_transaction(transaction, action)
    if return_value.status:
        return_value.result = type_parameters
    return return_value


def _get_family_instance_parameters(doc):
    """
    Get the instance parameters of the family.

    :param doc: The family document
    :type doc: Document

    :return:
        Result class instance.

        - result.status (bool) True if family instance parameters where retrieved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be a list of the family instance parameters [Autodesk.Revit.DB.Parameter]

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
        - result.result will be an empty list.
        
    :rtype: :class:`.Result`
    """

    instance_parameters = []

    # Assume 'doc' is your current Document object
    family_manager = doc.FamilyManager

    # Get all family types
    family_types = family_manager.Types

    # set-up action to be executed in transaction
    def action():
        action_return_value = Result()
        try:
            # Iterate over each type in the family
            for family_type in family_types:
                action_return_value.append_message(
                    "Checking type: {}".format(family_type.Name)
                )
                # Set the current type
                family_manager.CurrentType = family_type

                # Iterate over all parameters of the family type
                for parameter in family_manager.Parameters:
                    # print("{} :: is instance: {} ".format(parameter.Definition.Name, parameter.IsInstance))
                    # Check if it's a type parameter and has a formula
                    if parameter.IsInstance:
                        instance_parameters.append(parameter)

                # no need to loop again...
                break
        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to get instance parameters with exception: {}".format(e)
            )
        return action_return_value

    transaction = Transaction(doc, "Setting family type")
    return_value = rTran.in_transaction(transaction, action)
    if return_value.status:
        return_value.result = instance_parameters
    return return_value


def _filter_parameters_by_formula_driven(parameters, keep_if_formulae_driven):
    """
    Filter the parameters by whether they are determined by a formula or not.

    :param parameters: The list of parameters
    :type parameters: list
    :param keep_if_formulae_driven: True to keep the parameters that are determined by a formula, False otherwise
    :type keep_if_formulae_driven: bool

    :return: The filtered list of parameters
    :rtype: [Autodesk.Revit.DB.Parameter]
    """

    return_list = []
    for parameter in parameters:
        if parameter.IsDeterminedByFormula and keep_if_formulae_driven:
            return_list.append(parameter)
        elif not parameter.IsDeterminedByFormula and not keep_if_formulae_driven:
            return_list.append(parameter)
    return return_list


def get_parameter_names(parameters):
    """
    Get the names of the parameters form Revit parameter elements.

    :param parameters: The list of parameters
    :type parameters: list
    :return: The names of the parameters
    :rtype: [str]
    """

    names = []
    for p in parameters:
        names.append(p.Definition.Name)
    return names


def get_column_indices_to_ignore(parameter_name_list, header_row):
    """
    Get the indices of the columns in the family type catalogue file to ignore based on the filter parameter name list and the type catalogue file header row.

    The shortened parameter name list is the list of parameter names containing only instance parameters and type parameters which are formula driven.
    This will return parameters which exists in the header row of the catalogue file and in the shortened parameter name list.

    :param parameter_name_list: The list of parameter names to ignore
    :type parameter_name_list: [str]
    :param header_row: The header row of the data
    :type header_row: [str]
    :return: The indices of the columns to ignore
    :rtype: [int]
    """

    column_matches = []
    for i in range(1, len(header_row)):

        column_header = header_row[i]
        # go with full length
        parameter_end_index = len(column_header)
        # parameter end is either indicated by an open square bracket or a double cross
        if "[" in column_header:
            parameter_end_index = column_header.index("[")
        else:
            # double cross is definitely in the header name
            parameter_end_index = column_header.index("#")

        parameter_name = column_header[:parameter_end_index]
        # print("parameter in header: {}".format(parameter_name))
        if parameter_name in parameter_name_list:
            column_matches.append(i)
    return column_matches


def filter_original_catalogue_data(catalogue_file_rows, ignore_column_indexes):
    """
    Filter the original catalogue data by removing columns based on the ignore column indexes

    :param catalogue_file_rows: The original catalogue data
    :type catalogue_file_rows: [[str]]
    :param ignore_column_indexes: The indexes of the columns to ignore
    :type ignore_column_indexes: list
    :return: The filtered catalogue data
    :rtype: [[str]]
    """

    new_catalogue_file_data = []
    for row in catalogue_file_rows:
        new_data_row = []
        for i in range(0, len(row)):
            if i not in ignore_column_indexes:
                new_data_row.append(row[i])
        new_catalogue_file_data.append(new_data_row)

    return new_catalogue_file_data


def extract_parameter_name(header):
    """
    Extract the parameter name from a header.
    Determine the parameter end index using the first occurrence of `[` or `#`

    :param header: The header to extract the parameter name from
    :type header: str
    :return: The parameter name part of the header
    :rtype: str
    """

    param_end_index = len(header)
    if "[" in header:
        param_end_index = header.index("[")
    elif "#" in header:
        param_end_index = header.index("#")
    # Return the parameter name part of the header
    return header[:param_end_index]


def reorder_columns(data, desired_order):
    """
    Reorder the columns in the data based on the desired order.

    :param data: The data to reorder
    :type data: [[str]]
    :param desired_order: The desired order of the columns, indicated by the column header names
    :type desired_order: list
    :return: The reordered data
    :rtype: [[str]]
    """

    # The first row contains the header
    headers = data[0]
    rows = data[1:]

    # Keep the first column header and data
    first_column = [row[0] for row in data]
    remaining_headers = headers[1:]

    # Create a mapping from header names to their parsed parameter names
    header_to_index = {
        header: index + 1 for index, header in enumerate(remaining_headers)
    }
    parameter_to_index = {
        extract_parameter_name(header): index
        for header, index in header_to_index.items()
    }

    # Determine the order of indices based on the desired order
    order_indices = []
    for param_name in desired_order:
        if param_name in parameter_to_index:
            order_indices.append(parameter_to_index[param_name])

    # Find any headers not in the desired order and sort them alphabetically by their extracted parameter name
    remaining_headers_unsorted = [
        header
        for header in remaining_headers
        if extract_parameter_name(header) not in desired_order
    ]
    remaining_indices = sorted(
        [header_to_index[header] for header in remaining_headers_unsorted],
        key=lambda i: extract_parameter_name(headers[i]),
    )

    # Append the remaining sorted indices to the order indices, with the first column remaining at index 0
    full_order = [0] + order_indices + remaining_indices

    # Reconstruct the sorted data
    sorted_data = []
    # Keep the first column header unchanged
    sorted_data.append([headers[i] for i in full_order])
    # Reorder the rows
    for row in rows:
        sorted_data.append([row[i] for i in full_order])

    return sorted_data


def check_utf16le_bom(file_path):
    """
    Check if a file has a UTF-16 LE BOM

    :param file_path: The path to the file
    :type file_path: str
    :return: True if the file has a UTF-16 LE BOM, False otherwise
    :rtype: bool
    """

    with open(file_path, "rb") as f:
        # Read the first two bytes
        bom = f.read(2)

        # print("{} vs {} vs {}".format(BOMValue.UTF_16_LITTLE_ENDIAN, b"\xff\xfe", bom))
        # Check if the bom matches the UTF-16 LE BOM
        return bom == BOMValue.UTF_16_LITTLE_ENDIAN


# Define the desired order of columns in the cleaned data file
# these columns will be the first columns in the cleaned data file
DESIRED_COLUMN_ORDER = [
    "Door_Panel_Width_Major",
    "Door_Panel_Width_Minor",
    "Door_Panel_Width",
    "Door_Height_Nominal",
    "Door_Panel_Thickness",
    "Clear_Opening_Width",
]


def clean_up_catalogue_file(doc, output, forms):
    """
    A function to clean up a catalogue file:

    - removes instance parameters
    - removes type parameters which are formula driven
    - sorts columns by header depending on desired order
    - sorts values in columns by header in ascending alphabetical order

    :param doc: A Revit family document
    :type doc: Document
    :param output: pyRevit console output
    :type output: module
    :param forms: pyRevit forms module
    :type forms: module

    :return:
        Result class instance.

        - result.status (bool) True if catalogue file was cleaned without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """
    # set up a status tracker
    return_value = Result()

    try:
        # check if the current doc is a family document
        # Assume 'doc' is your current Document object
        is_family_document = doc.IsFamilyDocument
        if not is_family_document:
            return_value.append_message("Document is not a family. Exiting.")
            print(return_value.message)
            return return_value

        # get user to select catalogue file
        file_selected = get_file_path_from_user(
            forms=forms, file_extension="txt", title="Select Catalogue File"
        )
        if file_selected is None:
            return_value.append_message("No valid catalogue file selected. Exiting.")
            print(return_value.message)
            return return_value

        # get type parameters from family manager and keep (name, id) those which are driven by a formula
        type_parameters_result = _get_family_type_parameters(doc=doc)
        if not type_parameters_result.status:
            return_value.append_message(
                "failed to get type parameters: {}. Exiting.".format(
                    type_parameters_result.message
                )
            )
            print(return_value.message)
            return return_value

        # get list of type paras which are formulae driven
        filtered_type_parameters = _filter_parameters_by_formula_driven(
            parameters=type_parameters_result.result, keep_if_formulae_driven=True
        )
        print_header("Type parameters which are formula driven:")
        _print_parameters(filtered_type_parameters)

        # get instance parameter and store names and ids
        instance_parameters_result = _get_family_instance_parameters(doc)
        if not instance_parameters_result.status:
            return_value.append_message(
                "failed to get instance parameters: {}. Exiting.".format(
                    instance_parameters_result.message
                )
            )
            print(return_value.message)
            return return_value
        print_header("Instance parameters:")
        _print_parameters(instance_parameters_result.result)

        print_header("Catalogue file processing:")

        print("reading: {}".format(file_selected))
        # open catalogue file and read data into rows
        row_data_result = read_csv_file(file_selected)
        if row_data_result.status is False:
            return_value.append_message(
                "Failed to read catalogue file: {}".format(row_data_result.message)
            )
            print(return_value.message)
            return return_value
        
        row_data = row_data_result.result
        
        print("Read {} rows.".format(len(row_data)))

        # build parameter names list:
        all_parameter_names_to_cull_names = get_parameter_names(
            parameters=instance_parameters_result.result + filtered_type_parameters
        )

        # get the header row and build a list of indices of which columns to ignore by row when building new data
        ignore_column_indices = get_column_indices_to_ignore(
            parameter_name_list=all_parameter_names_to_cull_names,
            header_row=row_data[0],
        )
        print("Removing columns: {}".format(ignore_column_indices))

        # loop over data and build new data based on ignore column index list
        filtered_catalogue_file_data = filter_original_catalogue_data(
            catalogue_file_rows=row_data, ignore_column_indexes=ignore_column_indices
        )
        # _print_clean_data (filtered_catalogue_file_data, output)

        # optional: sort columns by header in ascending alphabetical order
        sorted_data = reorder_columns(
            data=filtered_catalogue_file_data, desired_order=DESIRED_COLUMN_ORDER
        )
        _print_clean_data(sorted_data, output)

        # build new file name:
        new_file_name = get_file_name_without_ext(file_selected)
        target_dir = get_directory_path_from_file_path(file_selected)
        new_full_file_name = os.path.join(target_dir, new_file_name + "__.txt")
        # write new data to file
        write_report_data_as_csv(
            file_name=new_full_file_name,
            header=sorted_data[:1][0],
            data=sorted_data[1:],
            encoding="utf-16-le",
            bom=BOMValue.UTF_16_LITTLE_ENDIAN,
        )

        print("BOM is present: {}".format(check_utf16le_bom(new_full_file_name)))

    except Exception as e:
        return_value.update_sep(
            False, "Failed to clean up catalogue file: {}".format(e)
        )
        print(return_value.message)

    print("Finished.")
    return return_value
