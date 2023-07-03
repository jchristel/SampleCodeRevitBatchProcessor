"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing model health related functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Updates model health tracer family
- reports model health metrics to text files


"""

import os

# import common library
import settings as settings  # sets up all commonly used variables and path locations!

import duHast.Utilities.Objects.result as res
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Data.Utils.data_export import get_data_from_model
from duHast.Data.Utils.data_to_file import build_json_for_file
from duHast.Utilities.files_json import write_json_to_file


def write_out_geometry_data(doc, revit_file_path, output):
    """

    Geometry data exporter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: Fully qualified file of the model.
    :type revit_file_path: str

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Writing geometry data...start")
    file_name = os.path.join(
        settings.OUTPUT_FOLDER,
        get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_GEO_DATA
        + settings.REPORT_FILE_NAME_EXTENSION,
    )
    # get the data from the model
    data = get_data_from_model(doc)
    # prefix data with file name and date stamp node
    data_to_file = build_json_for_file(data, get_file_name_without_ext(revit_file_path))
    # write data to file
    task_value = write_json_to_file(data_to_file, file_name)
    return_value.update(task_value)
    return return_value
