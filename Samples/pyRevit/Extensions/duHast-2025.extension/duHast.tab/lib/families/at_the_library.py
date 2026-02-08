# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
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


from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.console_output import print_header, print_error
from duHast.pyRevit.net_dll_loader import load_net_dll_path, get_bin_path_from_script_path_within_extension

# import required dll names
from duHast.Revit.NetSupport.dll_names import (
    
    UTILITY,
    WPF_CUSTOM_CONTROLS,
    CSV_HELPER ,
    NEWTONSOFT, 
    REVIT_ASYCNC, 
    AT_THE_LIBRARY,
)


# .net dlls to load for this script, these need to be in the bin folder of the extension
# apparently load order is important here...start with dependencies first
DLL_LIST = [CSV_HELPER, NEWTONSOFT, REVIT_ASYCNC, UTILITY, WPF_CUSTOM_CONTROLS, AT_THE_LIBRARY]

def at_the_library_entry(doc, uiapp, output, forms):
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
        
        # trying not to show a pyRevit window....
        # get the bin directory for the extension, this is where the required dlls should be located
        bin_directory = get_bin_path_from_script_path_within_extension(__file__)   
        if bin_directory is None:
            print_header("Starting ...")
            message = "Failed to determine bin directory for dlls."
            print_error(message)
            return_value.update_sep(False, message)
            return return_value

        # load the required dlls for the UI
        load_result = load_net_dll_path(DLL_LIST, bin_directory=bin_directory, exact_match=False)
        if load_result.status is False:
            return_value.update_sep(False, "Failed to load required dlls for the UI.")
            print(load_result.message)
    
        # start at the library:
        # import the UI class from the AtTheLibrary namespace
        from duHastNet.AtTheLibrary import Main
       
        # create an instance of the Main class
        main = Main()
        
        # show the output window
        at_the_library_result = main.ExecuteInternal(uiapp)

        return return_value

    
    except Exception as e:
        # handle any exceptions that occur during the reload process
        message = "An error occurred while running at the library: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print(message)
        return return_value