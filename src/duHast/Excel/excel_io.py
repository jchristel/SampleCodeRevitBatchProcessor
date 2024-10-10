"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions Excel file operations.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#

import clr

clr.AddReference("Microsoft.Office.Interop.Excel")
import Microsoft.Office.Interop.Excel as Excel

import os

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import (
    get_directory_path_from_file_path,
    file_delete,
    get_file_name_without_ext,
)
from duHast.Utilities.files_csv import read_csv_file


def get_excel_tab_names(file_path):
    """
    Returns a list of tab names (work sheet names) in the Excel file.

    :param file_path: The path to the Excel file.
    :type file_path: str
    :return: A result object with the result set to a list of tab names if successful, otherwise an error message.
    :rtype: Result
    """

    return_value = Result()
    excel = None
    wb = None
    try:
        excel = Excel.ApplicationClass()
        excel.Visible = False
        excel.DisplayAlerts = False
        # refer to this website for arg docs:https://learn.microsoft.com/en-us/office/vba/api/Excel.Workbooks.Open
        wb = excel.Workbooks.Open(
            file_path,  # excel doc file path
            0,  # update links ( 0 No )
            True,  # read only
            5,  # format delimeter ( 5 = nothing )
            "",  # password to open  a file (not required)
            "",  # password to write to a write protected  file (not required)
            True,  # ignore read only recommended (False = don't ignore, True = ignore)
            Excel.XlPlatform.xlWindows,  # file origin (xlWindows = Microsoft Windows)
            "\t",  # delimiter (tab) optional
            False,  # editable (False = read only, True = editable)
            False,  # notify (False = don't notify, True = notify)
            0,  # converter (0 = don't convert, 1 = convert)
            False,  # add to MRU (False = don't add, True = add)
            True,  # local (False = don't local, True = local)
            False,  # corrupt load (False = don't load, True = load)
        )
        tab_names = [ws.Name for ws in wb.Worksheets]
        return_value.update_sep(True, "Successfully read Excel file.")
        return_value.result = tab_names
    except Exception as e:
        return_value.update_sep(False, "Failed to read Excel file. Error: {}".format(e))
    finally:
        if wb:
            wb.Close(False)
        if excel:
            excel.Quit()

    return return_value


def save_excel_file_as_csv(file_path_excel, file_path_csv, tab_name=None):
    """
    Saves an Excel file as a CSV file.

    :param file_path_excel: The path to the Excel file.
    :type file_path_excel: str
    :param file_path_csv: The path to the CSV file.
    :type file_path_csv: str
    :param tab_name: The name of the tab ( work sheet ) in the Excel file to save as CSV. If None, the first tab is saved.
    :type tab_name: str
    :return: A result object with the result set to True if successful, otherwise an error message.
    :rtype: Result
    """

    return_value = Result()
    excel = None
    wb = None
    try:
        excel = Excel.ApplicationClass()
        excel.Visible = False
        excel.DisplayAlerts = False
        # refer to this website for arg docs:https://learn.microsoft.com/en-us/office/vba/api/Excel.Workbooks.Open
        wb = excel.Workbooks.Open(
            file_path_excel,  # excel doc file path
            0,  # update links ( 0 No )
            True,  # read only
            5,  # format delimeter ( 5 = nothing )
            "",  # password to open  a file (not required)
            "",  # password to write to a write protected  file (not required)
            True,  # ignore read only recommended (False = don't ignore, True = ignore)
            Excel.XlPlatform.xlWindows,  # file origin (xlWindows = Microsoft Windows)
            "\t",  # delimiter (tab) optional
            False,  # editable (False = read only, True = editable)
            False,  # notify (False = don't notify, True = notify)
            0,  # converter (0 = don't convert, 1 = convert)
            False,  # add to MRU (False = don't add, True = add)
            True,  # local (False = don't local, True = local)
            False,  # corrupt load (False = don't load, True = load)
        )
        if tab_name:
            ws = wb.Worksheets[tab_name]
            ws.Activate()
        else:
            ws = wb.Worksheets[1]
            ws.Activate()

        wb.SaveAs(file_path_csv, Excel.XlFileFormat.xlCSV)
        return_value.update_sep(True, "Successfully saved Excel file as CSV.")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to save Excel file as CSV. Error: {}".format(e)
        )
    finally:
        if wb:
            wb.Close(False)
        if excel:
            excel.Quit()
    return return_value


def read_excel_file(file_path, excel_tab_name=None):
    """
    Reads the content of an Excel file into a 2D array.

    Note: this function is rather slow, so use it with caution.

    :param file_path: The path to the Excel file.
    :type file_path: str
    :param excel_tab_name: The name of the tab ( work sheet ) in the Excel file to read from. If None, the first tab is read.
    :type excel_tab_name: str
    :return: A result object with the result set to a 2D array if successful, otherwise an error message.
    :rtype: Result
    """

    return_value = Result()
    excel = None
    wb = None
    try:
        excel = Excel.ApplicationClass()
        excel.Visible = False
        excel.DisplayAlerts = False
        # refer to this website for arg docs:https://learn.microsoft.com/en-us/office/vba/api/Excel.Workbooks.Open
        wb = excel.Workbooks.Open(
            file_path,  # excel doc file path
            0,  # update links ( 0 No )
            True,  # read only
            5,  # format delimeter ( 5 = nothing )
            "",  # password to open  a file (not required)
            "",  # password to write to a write protected  file (not required)
            True,  # ignore read only recommended (False = don't ignore, True = ignore)
            Excel.XlPlatform.xlWindows,  # file origin (xlWindows = Microsoft Windows)
            "\t",  # delimiter (tab) optional
            False,  # editable (False = read only, True = editable)
            False,  # notify (False = don't notify, True = notify)
            0,  # converter (0 = don't convert, 1 = convert)
            False,  # add to MRU (False = don't add, True = add)
            True,  # local (False = don't local, True = local)
            False,  # corrupt load (False = don't load, True = load)
        )
        if excel_tab_name:
            ws = wb.Worksheets[excel_tab_name]
        else:
            ws = wb.Worksheets[1]

        # get the used range of the worksheet
        used_range = ws.UsedRange
        rows_count = used_range.Rows.Count
        cols_count = used_range.Columns.Count

        # read the data into a 2D array
        used_data = []

        try:
            for row in range(1, rows_count + 1):
                row_data = []
                for col in range(1, cols_count + 1):
                    # get the cell value, just in case it's empty or contains a formula with an error wrap in try/except
                    try:
                        cell_value = used_range.Cells[row, col].Value2
                    except Exception as e:
                        cell_value = None
                    row_data.append(cell_value)
                used_data.append(row_data)
        except Exception as e:
            return_value.update_sep(
                False, "Failed to read Excel file. Error: {}".format(e)
            )

        wb.Close(False)
        excel.Quit()
        return_value.update_sep(True, "Successfully read Excel file.")
        return_value.result = used_data
    except Exception as e:
        return_value.update_sep(False, "Failed to read Excel file. Error: {}".format(e))
    finally:
        if wb:
            wb.Close(False)
        if excel:
            excel.Quit()

    return return_value


def read_excel_file_fast(file_path, excel_tab_name=None):
    """
    Reads the content of an Excel file into a 2D array.

    Note: this function is faster than read_excel_file
    It will save the excel file as a csv file first and then read its content.

    :param file_path: The path to the Excel file.
    :type file_path: str
    :param excel_tab_name: The name of the tab ( work sheet ) in the Excel file to read from. If None, the first tab is read.
    :type excel_tab_name: str
    :return: A result object with the result set to a 2D array if successful, otherwise an error message.
    :rtype: Result
    """

    return_value = Result()
    temp_csv_path = None
    try:
        temp_csv_path = os.path.join(
            get_directory_path_from_file_path(file_path), "temp.csv"
        )

        conversion_result = save_excel_file_as_csv(
            file_path, temp_csv_path, excel_tab_name
        )
        if not conversion_result.status:
            raise ValueError(conversion_result.message)
        return_value.update(conversion_result)

        # read the csv file
        data = read_csv_file(temp_csv_path)
        return_value.append_message(
            "Successfully read temp csv file. Number of rows read: {}".format(len(data))
        )
        return_value.result = data

    except Exception as e:
        return_value.update_sep(False, "Failed to read Excel file. Error: {}".format(e))

    finally:
        if temp_csv_path:
            delete_flag = file_delete(temp_csv_path)
            return_value.append_message(
                "Deleted temp csv file with status [{}]".format(delete_flag)
            )

    return return_value


def save_csv_as_excel(file_path):
    """
    Convertes as csv to .xslx in the same directory.

    :param file_path: The path to the csv file.
    :type file_path: str

    :return: A result object with the result status set to true if successful, otherwise an error message.
    :rtype: Result
    """

    return_value = Result()
    excel = None
    file_name_new = ""
    try:
        excel = Excel.ApplicationClass()
        excel.Visible = False
        excel.DisplayAlerts = False
        # refer to this website for arg docs:https://learn.microsoft.com/en-us/office/vba/api/Excel.Workbooks.Open
        # open excel and the csv
        wb = excel.Workbooks.Open(
            file_path,  # excel doc file path
            0,  # update links ( 0 No )
            True,  # read only
            6,  # format delimeter ( 6 = CSV)
            "",  # password to open a file (not required)
            "",  # password to write to a write protected file (not required)
            True,  # ignore read only recommended (False = don't ignore, True = ignore)
            Excel.XlPlatform.xlWindows,  # file origin (xlWindows = Microsoft Windows)
            ",",  # delimiter (comma) optional
            False,  # editable (False = read only, True = editable)
            False,  # notify (False = don't notify, True = notify)
            0,  # converter (0 = don't convert, 1 = convert)
            False,  # add to MRU (False = don't add, True = add)
            True,  # local (False = don't local, True = local)
            False,  # corrupt load (False = don't load, True = load)
        )
        # build new file name:
        output_dir = get_directory_path_from_file_path(file_path)
        file_name_part = get_file_name_without_ext(file_path=file_path)
        file_name_new = os.path.join(output_dir, file_name_part + ".xlsx")

        # save:
        save_status = wb.SaveAs(file_name_new, Excel.XlFileFormat.xlWorkbookDefault)

        # save the file
        wb.Close(False)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to save csv with exception: {}".format(e)
        )

    if excel is not None:
        excel.Quit()

    return_value.update_sep(
        True, "Successfully saved Excel file: {}.".format(file_name_new)
    )
    return return_value
