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

from duHast.Utilities.Objects.result import Result

from System.Collections.Generic import List

def load_net_dll_path(dlls_to_load):
    """
    Loads dlls from the libs folder of the duHast extension.
    Useful if a dll is not loaded through the startup script of a pyRevit extension.

    :param dlls_to_load: List of dlls to load.
    :type dlls_to_load: list
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        # type checking
        if not isinstance(dlls_to_load, list):
            return_value.update_sep(
                False, "dlls_to_load must be a list, got {} instead.".format(type(dlls_to_load))
            )
            return return_value

        # the dll is located in the libs folder of the extension, which is one level up from the current file's directory
        current_directory = os.path.dirname(__file__)
        return_value.append_message("Current directory: {}".format(current_directory))
        parent_directory = os.path.dirname(current_directory)
        return_value.append_message("Parent directory: {}".format(parent_directory))

        # get all the lib paths from the sys.path
        lib_paths = [path for path in sys.path if path.endswith("lib")]

        if not lib_paths or len(lib_paths) == 0:
            return_value.update_sep(
                False, "No lib paths found in sys.path."
            )

            for p in sys.path:
                return_value.append_message("sys.path entry: {}".format(p))

            return return_value
        else:
            for p in lib_paths:
                duHast_path = os.path.join(p, "duHast")
                # check if path exists
                if os.path.exists(duHast_path):
                    return_value.append_message("Valid duHast path: {}".format(duHast_path))
                    # add the library path within the duHast folder to the sys.path
                    duHast_lib_path = os.path.join(duHast_path, "lib")
                    
                    # valid path check
                    if os.path.exists(duHast_lib_path):
                        return_value.append_message("Valid duHast//lib path: {}".format(duHast_lib_path))
                        
                        # load dlls
                        for dll in dlls_to_load:
                            # add the wrapper dll to the clr
                            dll_path = os.path.join(duHast_lib_path,dll)
                            
                            # valid path check
                            if os.path.exists( dll_path):
                                try:
                                    # add the dll to the clr
                                    clr.AddReferenceToFileAndPath(dll_path)
                                    return_value.append_message("Loaded dll: {}".format(dll_path))
                                except Exception as e:
                                    return_value.update_sep(
                                        False, "Failed to load dll: {}. Error: {}".format(dll_path, e)
                                    )
                            else:
                                return_value.update_sep(
                                    False, "DLL path does not exist: {}".format(dll_path)
                                )
                    else:
                        return_value.update_sep(
                            False, "Path to duHast//lib does not exist: {}".format(duHast_lib_path)
                        )
                        return return_value
                    break
                else:
                    return_value.update_sep(
                        False, "Path to duHast does not exist in : {}".format(p)
                    )
        return_value.append_message( "DLL path set successfully.")
    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while processing export settings: {}".format(e)
        return_value.update_sep(
            False, message
        )


    return return_value