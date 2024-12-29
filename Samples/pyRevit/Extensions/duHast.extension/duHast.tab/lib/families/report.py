# required for .ToList() on FilteredElementCollector
import clr, os

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

from collections import Counter

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit

from duHast.Revit.Family.Reporting.report import report_loaded_families
from duHast.Utilities.files_csv import write_report_data_as_csv

from pyrevit.framework import Forms


# default list of parameters to report on
FAMILY_PARAMETERS_TO_REPORT = [
    "Sample Parameter One",
    "Sample Parameter Two",
    "Sample Parameter Three",
]


def _convert_data_to_list_string(data):

    # convert data to string values
    data_converted = []
    for fam in data:
        row = fam.get_properties_as_list_str()
        data_converted.append(row)
    return data_converted


def _print_family_table(data, data_header, output):
    """
    Print a table of family data to the pyRevit output.

    :param data: List of family data.
    :type data: [[str]]
    :param data_header: List of data headers.
    :type data_header: [str]
    :param output: pyRevit output
    :type output: pyRevit output module
    """

    format_by_columns = [""] * len(data_header)

    # convert data to string values
    data_converted = _convert_data_to_list_string(data)

    output.print_table(
        table_data=data_converted,
        title="Families in Model",
        columns=data_header,
        formats=format_by_columns,
    )

    # try a chart

    # refer to  https://pyrevit1.readthedocs.io/en/latest/outputfeatures.html
    # first time in a revit session this will throw an error about scripts being run...

    # show number of families, types, categories and instances placed

    # Extract the relevant fields from the headers row
    fields_to_count = [1, 2, 3, len(data_header) - 1]

    # Initialize counters for each field
    counters = {field: Counter() for field in fields_to_count}

    # Count unique values in each field
    for row in data_converted:
        for field in fields_to_count:
            counters[field][row[field]] += 1

    # count each unique key
    data_set_a_values = []
    for field, counter in counters.items():
        value = 0
        for item_name in counter:
            # count unique keys only
            value += 1
        data_set_a_values.append(value)

    # get labels from headers
    labels = [data_header[i] for i in fields_to_count]

    # get pie chart object
    chart = output.make_pie_chart()

    # add data labels
    chart.data.labels = labels

    # Let's add the first dataset to the chart object
    # we'll give it a name: set_a
    set_a = chart.data.new_dataset("families")

    # And let's add data to it.
    # These are the data for the Y axis of the graph
    # The data length should match the length of data for the X axis
    set_a.data = data_set_a_values

    # You can set a different color for each pie of the chart
    set_a.backgroundColor = ["#560764", "#1F6CB0", "#F98B60", "#913175"]

    # Finally let's draw the chart
    chart.draw()


def _save_data(data_header, data):
    """
    Save data to a file.

    :param data_header: List of data headers.
    :type data_header: [str]
    :param data: List of data.
    :type data: [[str]]

    :return:
        Result class instance.

        - result.status (bool) True if families where reported without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()
    # get file path from user
    file_name = None
    sf_dlg = Forms.SaveFileDialog()  # (file_ext="json", title="Save template data")
    sf_dlg.Filter = "Text files (*.csv)|*.csv|All files (*.*)|*.*"
    if sf_dlg.ShowDialog() == Forms.DialogResult.OK:
        file_name = sf_dlg.FileName

    if file_name is None:
        print("No file name for data file selected. Exiting.")
        return_value.update_sep(False, "No file name for data file selected. Exiting.")
        return return_value

    try:
        # convert data to string values
        data_converted = _convert_data_to_list_string(data)

        # write data to file
        write_result = write_report_data_as_csv(
            file_name=file_name, header=data_header, data=data_converted
        )
        if write_result.status == False:
            raise ValueError(write_result.message)
        
        return_value.append_message("Wrote file to: {}".format(file_name))
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write data file with exception: {}".format(e)
        )

    return return_value


def report_loaded_families_entry(doc, output, forms):
    """
    Reports on loaded families in a project file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if families where reported without an exception, otherwise False.
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

        # set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Reporting families: {value} of {max_value}", cancellable=True
        ) as pb:

            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)

            # get family data
            report_status = report_loaded_families(
                doc=doc,
                parameter_names_filter=FAMILY_PARAMETERS_TO_REPORT,
                progress_callback=progress_callback,
            )
            print(report_status.message)

            # check what came back before proceeding
            if report_status.status == False:
                return_value.update(report_status)
                return return_value

            # sort family data by family name type name
            family_data = sorted(
                report_status.result,
                key=lambda x: ((x.family_name, x.family_type_name)),
            )

            if len(family_data) == 0:
                return_value.append_message("No families in file. Exiting")
                print(return_value.message)
                return return_value

            # report headers:
            report_headers = family_data[0].get_property_headers()

            # print out  table
            _print_family_table(
                data=family_data, data_header=report_headers, output=output
            )

            # save data
            save_status = _save_data(data_header=report_headers, data=family_data)
            return_value.update(save_status)

            # check for cancel
            if pb.cancelled:
                return_value.update_sep(False, "User cancelled.")

    except Exception as e:
        return_value.update_sep(
            False, "Failed to report families with exception: {}".format(e)
        )

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value
