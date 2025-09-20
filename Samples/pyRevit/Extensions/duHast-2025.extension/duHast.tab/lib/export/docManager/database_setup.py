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



from System.Collections.Generic import List

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Views.sheets import get_all_sheets
from duHast.pyRevit.console_output import print_header, print_error
from duHast.pyRevit.net_dll_loader import load_net_dll_path
from duHast.Revit.NetSupport.dll_names import DOC_MANAGER_CORE 

DEBUG = True


def settings_database_entry(doc, output, forms):
    """
    Sets up a project specific database for document management.

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

        set_dll_path_result = load_net_dll_path([DOC_MANAGER_CORE])

        if not set_dll_path_result.status:
            print_error(set_dll_path_result.message)
            
        # setup the config class
        from duHastNet.DocManager.Core.Models.Config import DatabaseSetupConfig
        setup_config = DatabaseSetupConfig()
        
        # set up some hard coded test values
        setup_config.DatabasePath = r"C:\Temp\duHast\DocManager\TestProjectDatabase.db"
        
        # custom property names for documents
        setup_config.CustomPropertyNames = List[str]([
            "Discipline",
            "Status",
        ])
        
        # overwrite existing database (set to existing since we are debugging)
        if DEBUG:
            setup_config.OverwriteExisting = True
        else:
            setup_config.OverwriteExisting = False
        
        # setup the document manager api class
        from duHastNet.DocManager.Core.Services.Api import DocManagerApi
        api = DocManagerApi()
        
        setup_net_result = api.SetupDatabase(setup_config)
        print(setup_net_result)
        
        # Remember to clean up
        api.Close()

    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while setting up the data base: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    print("\nFinished database settings.")

    return return_value