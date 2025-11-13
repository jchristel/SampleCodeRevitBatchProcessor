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
clr.AddReference('System')
from System.Collections.Generic import List

from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.pyRevit.file_picker import get_file_path_from_user

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Views.Import.read_filter_storage import read_filter_storage_from_file
from duHast.Revit.Views.Import.create_filter_from_storage import import_view_filters_from_data


DEBUG = False

def import_view_filters(doc, output, forms, debug=DEBUG):
    """

    Import selected view filters from file (.json)

    :param doc: The current revit document
    :type doc: Autodesk.Revit.DB.Document
    :param output: PyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms name space (module)
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status: Export status will be in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the file path of the .json file created.
        - result.result will be an empty list

        On exception

        - result.status (bool) will be False
        - result.message will contain the exception message

    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    
    try:

        # get the user to select the file to be imported
        file_path = get_file_path_from_user(
            forms=forms, title="Select view filters file", file_extension="json"
        )
        if file_path is None:
            print("No file selected. Exiting.")
            return_value.update_sep(False, "No file selected. Exiting.")
            return return_value
    
        # set up a pyrevit progress bar
        with forms.ProgressBar(
            title="Importing view filters: {value} of {max_value}", cancellable=True
        ) as pb:

            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)

            # get the document name
            doc_name = doc.Title
            # check file has a name (detached files this might be an empty string)
            if doc_name == "":
                # set a default value
                doc_name = "Detached file"

            read_result = read_filter_storage_from_file(
                file_path,
                "View Filters"
            )

            # update return value
            return_value.update(read_result)
            
            if(read_result.status):
                if debug:
                    print("Successfully read file: {}".format(file_path))
            else:
                print("Error reading file: {}".format(read_result.message))
                return return_value

            # everything went fine, get the json object
            data_objects = read_result.result

            # debug print
            if debug:
                print("Data to import:{}".format(len(data_objects)))
                for data_object in data_objects:
                    print("...{}".format(data_object.formatted_indented_str(1,".")))

            # import the view filters
            import_result = import_view_filters_from_data(doc, data_objects, progress_callback)

            if import_result.status:
                print("Successfully imported view filters from file: {}".format(file_path))
            else:
                print(import_result)
            # update return value
            return_value.update(import_result)
    
        return return_value

    except Exception as e:
        return_value.update_sep(
            status=False,
            message="Failed to import view filters: {}".format(e)
        )

    if debug:
        print(return_value)
    return return_value