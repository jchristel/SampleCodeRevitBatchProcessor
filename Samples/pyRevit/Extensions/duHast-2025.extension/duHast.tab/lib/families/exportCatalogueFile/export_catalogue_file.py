# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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
import os

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Revit.Family.family_types_catalogue import export_catalogue_file


def export_catalogue_file(doc, output, forms):
    """
    Exports family type data to an xml file, reads that data back into custom objects and prints it to the pyRevit output as a table.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if files where processed without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get user to select a directory
    family_out_folder_path = None
    family_out_folder_path = forms.pick_folder(
        "Select the family data export directory"
    )
    if family_out_folder_path is None:
        message = "No folder selected. Exiting."
        print(message)
        return_value.update_sep(False, message=message)
        return return_value

    else:
        print("Saving family type data to directory: {}".format(family_out_folder_path))
    
    file_name = get_file_name_without_ext(doc.Title)
    output_file_name = os.path.join(family_out_folder_path, "{}.txt".format(file_name))

    export_result = export_catalogue_file(
        doc=doc,
        file_path = output_file_name, 
        filters = None, 
        parameter_order = None, 
        override_existing = True,
    )
    
    return_value.update(export_result)
    
    # give user some feedback
    if not export_result.status:
        message = "Family type data export failed. Exiting."
        print(message)
    else:
        message = "Family type data export successful."
        print(message)
    
    return return_value
