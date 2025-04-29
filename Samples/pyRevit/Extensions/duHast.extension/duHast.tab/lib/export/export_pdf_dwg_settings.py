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

import clr
import os
import sys

from System.Collections.Generic import List

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.console_output import print_header, print_error

from duHast.pyRevit.net_dll_loader import load_net_dll_path

def settings_export_pdf_dwg_entry(doc, output, forms):
    """
    Exports sheets to pdf and dwg files.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:
        set_dll_path_result = load_net_dll_path(["Utils.23.0.0.3.dll", "PDFDWGExporterUI.dll"])

        if not set_dll_path_result.status:
            print_error(set_dll_path_result.message)

        # import the UI class from the PDFDWGExporterUI namespace
        from duHastNet.UI.PDFDWGExporterUI import Main
        parameter_names = List[str]()
        parameter_names.Add("test")
        parameter_names.Add("test2")
        parameter_names.Add("test3")
        main = Main(None, None, parameter_names)

        main.Execute()

    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while processing export settings: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    print("\nFinished pdf and dwg export settings.")

    return return_value