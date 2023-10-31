"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing model health related functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Updates model health tracer family
- reports model health metrics to text files


"""

# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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
