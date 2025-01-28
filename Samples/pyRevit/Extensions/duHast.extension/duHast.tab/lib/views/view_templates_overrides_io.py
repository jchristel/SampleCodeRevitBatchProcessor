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

import sys

duHast_git = r"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\src"

sys.path.insert(0, duHast_git)

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Views.Utility.convert_revit_override_to_data import (
    get_views_graphic_settings_data,
)
from duHast.Revit.Views.visibility_graphics import apply_overrides_from_file
from duHast.Revit.Views.Reporting.views_data_report import (
    write_graphics_settings_report,
)
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit

from views.view_templates_ui import _get_target_view_templates
from pyrevit.framework import Forms

# get the user to select a file to open
from duHast.pyRevit.file_picker import get_file_path_from_user


def export_overrides_of_selected_viewtemplates(doc, output, forms):
    """

    Exports category graphics overrides and filter overrides from selected templates to file (.json)

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

    # get templates to export
    view_templates_to_export = _get_target_view_templates(
        doc=doc, forms=forms, source_view_template_name=None
    )

    if view_templates_to_export is None or len(view_templates_to_export) == 0:
        print(
            "No view template selected or no suitable view templates in file. Exiting."
        )
        return_value.update_sep(
            False, "No view template selected or no suitable view templates in file."
        )
        return return_value

    # set up a pyrevit progress bar
    with forms.ProgressBar(
        title="Reporting view templates: {value} of {max_value}", cancellable=True
    ) as pb:

        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # get export data
        data_json = get_views_graphic_settings_data(
            doc=doc, views=view_templates_to_export, progress_callback=progress_callback
        )

        # get file path from user
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

        # get the document name
        doc_name = doc.Title
        # check file has a name (detached files this might be an empty string)
        if doc_name == "":
            # set a default value
            doc_name = "Detached file"

        # write json data to file
        write_result = write_graphics_settings_report(
            revit_file_name=doc_name, file_path=file_name, data=data_json
        )

        # update return value
        return_value.update(write_result)
        print(write_result.message)

        return return_value


def import_overrides_from_file(doc, output, forms):
    """
    Imports overides saved to file in json format and applies to matching templates (by template name)

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

    # get the user to select the file to be imported
    file_path = get_file_path_from_user(
        forms=forms, title="Select overrides file", file_extension="json"
    )
    if file_path is None:
        print("No file selected. Exiting.")
        return_value.update_sep(False, "No file selected. Exiting.")
        return return_value

    print("Reading file: {}".format(file_path))
    apply_status = apply_overrides_from_file(doc=doc, file_path=file_path)

    print(
        "Applied imported overrides  with status: {}\n{}".format(
            apply_status.status, apply_status.message
        )
    )
    print("Finished.")
    return return_value
