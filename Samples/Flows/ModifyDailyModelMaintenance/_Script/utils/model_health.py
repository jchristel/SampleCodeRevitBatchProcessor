"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing model health related functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Updates model health tracer family
- reports model health metrics to text files


"""
# import common library
import settings as settings  # sets up all commonly used variables and path locations!

import duHast.Utilities.Objects.result as res
from duHast.Revit.ModelHealth import model_health as rHealth


def update_model_health_tracer_fam(doc, revit_file_path, output):
    """
    Updates model health tracer family

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    """

    return_value = res.Result()
    output("Updating model health data family...start")
    task_value = rHealth.update_model_health_tracer_family(doc, revit_file_path)
    return_value.update(task_value)
    return return_value


def write_model_health_data(doc, revit_file_path, output):
    """
    Write model health data to file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    """

    return_value = res.Result()
    output("Exporting model health data...start")
    task_value = rHealth.write_model_health_report(
        doc, revit_file_path, settings.OUTPUT_FOLDER
    )
    return_value.update(task_value)
    return return_value
