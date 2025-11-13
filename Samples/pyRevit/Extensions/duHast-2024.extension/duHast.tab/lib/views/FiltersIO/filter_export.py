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

from duHast.Data.Utils.data_to_file import build_json_for_file
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_json import write_json_to_file

from duHast.Revit.Views.filters import get_all_filters
from duHast.Revit.Views.Export.filters_to_storage import analyze_filters

from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit

from pyrevit.framework import Forms

DEBUG = False



def _get_view_filters_for_ui(doc):
    """
    Returns all view filters in the model

    - 0 is view filter names ( list of strings)
    - 1 is a dictionary where the key is the view filter name and value is the actual view filter

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: view_filter_names, view_filters_by_name
    :rtype: [str], {str: Autodesk.Revit.DB.View}
    """

    # set up return values
    view_filter_names = []
    view_filters_by_name = {}

    # get all view templates
    view_filters = get_all_filters(doc=doc)
    for vt in view_filters:
        key = vt.Name
        view_filter_names.append(key)
        view_filters_by_name[key] = vt

    return view_filter_names, view_filters_by_name


def _get_source_view_filters(doc, forms, button_name="Select View Filter To Export"):
    """
    returns the source view filters by user selection

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module
    :param source_view_template_name: The name of the source view template to exclude from the list of target view templates.
    :type source_view_template_name: str

    :return: target_view_templates
    :rtype: [Autodesk.Revit.DB.View]
    """

    source_view_filters = []

    # get view filter in the model
    view_filter_names, view_filters_by_name = _get_view_filters_for_ui(doc)

    # check if we got any?
    if len(view_filter_names) == 0:
        return source_view_filters

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(view_filter_names),
        button_name=button_name,
        multiselect=True,
    )

    # print (selection, type(selection))

    if selection is None or len(selection) == 0:
        return source_view_filters
    else:
        for source_view_filter_name in selection:
            source_view_filters.append(
                view_filters_by_name[source_view_filter_name]
            )
        return source_view_filters


def export_view_filters(doc, output, forms, debug=DEBUG):
    """

    Exports selected view filters to file (.json)

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

        all_filters = _get_source_view_filters(doc, forms, button_name="Select View Filter To Export")

        if len(all_filters) == 0:
            return_value.update_sep(
                status=False,
                message="No view filters selected for export.",
            )
            return return_value

        #set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Exporting filter: {value} of {max_value}",
            cancellable=True,
        ) as pb:

            # set up a progress call back
            progress_callback = ProgressPyRevit(form=pb)

            # analyze filters
            data_result = analyze_filters(doc, all_filters, progress_callback, debug)

            # check what came back
            if data_result.status is False or len(data_result.result) == 0:
                return_value.update_sep(
                    status=False,
                    message="No view filters found in model.",
                )
                return_value.update(data_result)
                print(data_result)
                return return_value
            
            # get the data from the result
            data = data_result.result[0]
            print ("Found {} view filters in model.".format(len(data)))

            for d in data:
                if debug:
                    print("...{}".format(d.formatted_indented_str(1,".")))
                else:
                    print("...{}".format(d.name))
            
            # build a json structure
            data_json = build_json_for_file({"View Filters":data}, doc.Title)

            # get the file path from the user
            file_name = None
            sf_dlg = Forms.SaveFileDialog()  # (file_ext="json", title="Save template data")
            sf_dlg.Filter = "Text files (*.json)|*.json|All files (*.*)|*.*"
            if sf_dlg.ShowDialog() == Forms.DialogResult.OK:
                file_name = sf_dlg.FileName

            if file_name is None:
                print("No file name for data file selected. Exiting.")
                return_value.update_sep(
                    False, "No file name for data file selected. Exiting."
                )
                return return_value

            write_result = write_json_to_file(
                data_json,
                file_name
            )

            # update return value
            return_value.update(write_result)
            
            if(write_result.status):
                print("Exported {} view filters to file: {}".format(len(data), file_name))
                print("Finished.")
            else:
                print("Error writing file: {}".format(write_result.message))
            return return_value

        
        return return_value
    
    except Exception as e:
        return_value.update_sep(
            status=False,
            message="Failed to export view filters: {}".format(e)
        )
        

        print("Error: {}".format(e))

        return return_value