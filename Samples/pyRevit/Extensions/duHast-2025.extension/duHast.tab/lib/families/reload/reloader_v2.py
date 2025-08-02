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
import settings

from duHast.Utilities.Objects.result import Result

from duHast.pyRevit.console_output import print_header, print_error
from duHast.pyRevit.net_dll_loader import load_net_dll_path

from families.reload.get_families import get_families_in_model_net

DEBUG = False

def reloaded_families_entry(doc, output, forms):
    """
    Reports on loaded families in a project file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return: Result class instance.
        - `result` (bool): True if warnings where reported without an exception, otherwise False.
        - `message` (str): details how many warnings where retrieved.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    try:
        
        print_header("Reloading families in the model...")
        # load .net interface dlls
        set_dll_path_result = load_net_dll_path(["FamilyReloaderUI.dll"])

        # check if the dlls were loaded successfully
        if not set_dll_path_result.status:
            print_error(set_dll_path_result.message)
            return_value.update_sep(False, set_dll_path_result.message)
            return return_value
        
        # get all families in file as a list of .net RevitFamily objects
        families_net = get_families_in_model_net(doc=doc)
        
        # check if families were found
        if not families_net or families_net.Count == 0:
            print_header("No families found in the model.")
            return_value.update_sep(True, "No families found in the model.")
            return return_value
        
        # import the UI class from the PDFDWGExporterUI namespace
        from duHastNet.UI.FamilyReloaderUI import Main
       
        # create an instance of the Main class
        main = Main(families_net)
        
        # show the output window
        families_reload = main.Execute()
        
        print(families_reload)

    
    except Exception as e:
        # handle any exceptions that occur during the reload process
        message = "An error occurred while reloading families: {}".format(e)
        return_value.update_sep(
            False, "Failed to reload families with exception: {}".format(e)
        )
        print(message)
