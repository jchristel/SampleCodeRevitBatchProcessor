#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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
from duHast.Revit.Views.schedules import  get_all_sheet_schedules
from duHast.pyRevit.ui_element_selection import get_element_selection_from_user


def schedule_name_builder(element):
    """
    Builds a key for the schedule element to be used in the user interface.

    Key consists of:

    - view template applied to schedule in square brackets
    - schedule name
    - schedule id in round brackets

    :param element: Schedule element.
    :type element: Autodesk.Revit.DB.ViewSchedule

    :return: Schedule key.
    :rtype: str
    """

    # get the id 
    schedule_id = element.Id

    # set a schedule name
    schedule_name = element.Name

    # build a key for the schedule
    key = "{} ({})".format(schedule_name, schedule_id)
    return key


def get_schedule_name_from_user(doc, forms):
    """
    Gets a schedule name from the user via a selection form.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module.
    :type forms: pyRevit.forms

    :return: Result object containing success status, messages and selected schedule name.
    :rtype: duHast.Utilities.Objects.result.Result
    """
    return_value = Result()

    schedule_ids = get_element_selection_from_user(
            doc=doc, 
            forms=forms, 
            element_getter=get_all_sheet_schedules, 
            element_selection_description= "Select Schedules", 
            multiselect=False, 
            ui_element_name_builder=schedule_name_builder
        )

    if schedule_ids is None or len(schedule_ids) == 0:
        message = "No valid schedules selected"
        print(message)
        return_value.update_sep(False, message)
        return return_value

    # get the schedule name from the first (and only selected id
    schedule_name = doc.GetElement(schedule_ids[0]).Name

    # update status and return
    return_value.update_sep(True, "Successfully selected schedule.")
    return_value.result.append(schedule_name)
    return return_value


def get_docs_folder_path_from_user(forms):
    """
    Gets a folder path from the user via a folder selection form.
    :param forms: pyRevit forms module.
    :type forms: pyRevit.forms
    :return: Result object containing success status, messages and selected folder path.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()

    # get the library directory path
    library_path = forms.pick_folder(title="select folder containing pdf's")
    if not library_path:
        message = "No directory selected."
        print(message)
        return_value.update_sep(False, message)
        return return_value
    
    return_value.update_sep(True, "Successfully selected directory.")
    return_value.result.append(library_path)
    return return_value