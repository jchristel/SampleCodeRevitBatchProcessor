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

from duHast.Utilities.Objects.result import Result

from duHast.Revit.UI.custom_selection_user import get_user_selection
from duHast.Revit.Family.Data.Objects.family_directive_swap_instances_of_type import FamilyDirectiveSwap
from duHast.Revit.Family.family_swap_instances_of_types import _swap_loaded_family_instances
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict
from duHast.pyRevit.ui_element_selection import get_element_selection_from_user
from duHast.Revit.Family.Utility.family_swap_instances_by_type_utils import write_swap_directives_to_file


from families.util.swap_by import family_types_getter_target, ui_data_builder, get_target_category_name

from pyrevit.framework import Forms


from Autodesk.Revit.DB import (
    Element,
    FamilySymbol,
    FamilyInstance,
    FilteredElementCollector,
)

def selection_filter_family_instance(elem):
    """
    Returns True if the element is a family instance, otherwise False.

    :param elem: A revit element
    :type elem: Autodesk.Revit.DB.Element
    :return: True if the element is a family instance, otherwise False
    :rtype: bool
    """

    if isinstance(elem, FamilyInstance):
        return True
    else:
        return False


def get_user_selection_pick_instance(doc, uiapp):
    """
    Gets a user selection of family instances to swap out. ( if multiple families are selected only the first one will be used)

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The current Revit application.
    :type uiapp: Autodesk.Revit.UI.UIApplication

    :return: Result class instance containing the selected family instances.
        - result.status (bool) True if family instances were selected, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of with a single selected family instances.
        On exception:
        - result.status (bool) will be False.
        - result.message will contain exception message.


    :rtype: :class:`.Result`

    """
    # set up a status instance
    return_value = Result()
    # get user to select grids
    family_selected_result = get_user_selection(
        doc=doc,
        uidoc=uiapp.ActiveUIDocument,
        ui_text="Select family instances to swap out",
        selection_filter=selection_filter_family_instance,
    )

    # check if grids where selected
    if family_selected_result.status == False:
        return_value.update(family_selected_result)
        print("Failed to select a family instance: {}".format(family_selected_result.message))
        return return_value

    # get the actual grids selected
    family_selected = family_selected_result.result[0]
    if len(family_selected) == 0:
        print("No family instance was selected. Exiting.")
        return_value.status = False
        return
    elif len(family_selected) > 1:
        print("Multiple family instances selected. Only the first one will be used.")
        family_selected = family_selected[0]
    else:
        family_selected = family_selected[0]
    
    return_value.update_sep(True, "Family instances selected")
    return_value.result.append(family_selected)
    return return_value


def save_swap_directive_to_file(swap_directive):
    """
    Saves a swap directive to a file selected by the user.

    :param swap_directive: The swap directive to save.
    :type swap_directive: FamilyDirectiveSwap
    :return: Result class instance containing the result of the save operation.
        - result.status (bool) True if directive was saved successfully, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.
        On exception:
        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    # get file path from user
    file_name = None
    sf_dlg = Forms.SaveFileDialog()  # (file_ext="json", title="Save directive")
    sf_dlg.Filter = "Text files (*.csv)|*.csv|All files (*.*)|*.*"
    if sf_dlg.ShowDialog() == Forms.DialogResult.OK:
        file_name = sf_dlg.FileName

    if file_name is None:
        return_value.update_sep(
            False, "No file name for data file selected. Exiting."
        )
        return return_value
    
    # write data to file
    write_result = write_swap_directives_to_file([swap_directive], file_name)
    return write_result


def swap_instances_by_user_selection_pick_entry(doc, uiapp, output, forms):
    """
    Toggles the visibility of grid bubbles of selected grids at specified end.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The current Revit application.
    :type uiapp: Autodesk.Revit.UI.UIApplication
    :param output: pyRevit output
    :type output: Output
    :param forms: pyRevit forms
    :type forms: Forms


    :return:
        Result class instance.

        - result.status (bool) True if families where swapped out successfully, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status instance
    return_value = Result()

    try:
        # get the user selection
        user_selection_result = get_user_selection_pick_instance(doc, uiapp)

        # check if grids where selected
        if user_selection_result.status == False:
            return_value.update(user_selection_result)
            return return_value

        source_family_instance = user_selection_result.result[0]
        

        # get some source names
        source_type_id = source_family_instance.Symbol.Id
        source_type_name = Element.Name.GetValue(doc.GetElement(source_type_id))
        source_fam_name = Element.Name.GetValue(doc.GetElement(source_type_id).Family)

        # give some user feed back
        print("Selected family instance: \n...{} \nof type: \n...{} \nand family: \n...{}".format(Element.Name.GetValue(source_family_instance), source_type_name, source_fam_name))

        # separate the category name from the selection
        target_category_name = get_target_category_name(doc,source_type_id)

        # set up wrapper function to get the target family type filtered by category
        def getter_target_type (doc) :
            return family_types_getter_target(doc,  target_category_name)

        # get user to select the family target type
        selection_target_type = get_element_selection_from_user(
            doc=doc, 
            forms=forms, 
            element_getter=getter_target_type, 
            element_selection_description="Select the family type to swap to",
            multiselect=False,
            ui_element_name_builder=ui_data_builder,
        )

        # verify user selection
        if selection_target_type is None or len(selection_target_type) == 0:
            return_value.update_sep(False, "No target family type selected")
            print("No target family type selected. Exiting!")
            return return_value
        
        # get some target names
        target_type_id = selection_target_type[0]
        target_type_name = Element.Name.GetValue(doc.GetElement(target_type_id))
        target_fam_name = Element.Name.GetValue(doc.GetElement(target_type_id).Family)

        # create A swap directive from selection
        swap_directive = FamilyDirectiveSwap(
            name=source_fam_name,
            category=target_category_name,
            source_type_name = source_type_name,
            target_family_name=target_fam_name,
            target_family_type_name=target_type_name,
        )

        # get all family in file
        families = get_name_and_category_to_family_dict(doc)

        # swap the instances out
        swap_result = _swap_loaded_family_instances(doc, [swap_directive], families=families, progress_callback=None)
        # print logs
        print(swap_result.message)

        #If the swap was ok offer to save directive to file:
        save_result = save_swap_directive_to_file(swap_directive)
        print(save_result.message)

    
    except Exception as e:
        print("An exception occurred: {}".format(e))
        return_value.update_sep(
            False, "Failed to swap families with exception: {}".format(e)
        )
    
    return return_value