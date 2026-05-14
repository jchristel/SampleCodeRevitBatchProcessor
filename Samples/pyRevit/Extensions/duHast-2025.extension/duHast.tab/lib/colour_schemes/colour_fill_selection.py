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
from duHast.Utilities.files_csv import read_csv_file
from duHast.pyRevit.UI.ui_element_selection import get_element_selection_from_user
from duHast.pyRevit.file_picker import get_file_path_from_user
from duHast.Revit.ColourFillSchemes.Objects.colour_fill_storage import ColourFillStorage
from duHast.Revit.ColourFillSchemes.colour_fill_schemes import get_all_colour_schemes


from Autodesk.Revit.DB import ElementId

def colour_fill_scheme_name_builder_ui(doc, element):
    """
    Builds the colour fill scheme name using  the colour fill scheme name and the area scheme.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: The colour fill scheme element.
    :type element: Autodesk.Revit.DB.Element
    
    :return: The built colour fill scheme name.
    :rtype: str
    """

    colour_fill_name = element.Name
    area_scheme_name = ""

    # get the area scheme id
    area_scheme_id =  element.AreaSchemeId

    if area_scheme_id == ElementId.InvalidElementId:
        area_scheme_name= "Room Colour Fill Scheme"

    else:
        # get the area scheme name
        area_scheme = doc.GetElement(area_scheme_id)

        # get the area scheme name
        area_scheme_name = area_scheme.Name

    # Build the colour fill scheme name using the provided string
    return "{} <{}> ({})".format(colour_fill_name, area_scheme_name, element.Id.Value)


def colour_fill_scheme_getter(doc):
    """
    Gets all colour fill schemes in the model.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of all colour fill schemes in the document assigned to an area scheme.
    :rtype: list
    """

    colour_fill_scheme_filtered = []

    # Get all colour fill schemes in the document
    colour_fill_schemes = get_all_colour_schemes(doc=doc)

    for s in colour_fill_schemes:
       
        #  append the scheme
        colour_fill_scheme_filtered.append(s)

    return colour_fill_scheme_filtered


def user_select_colour_scheme(doc, forms, form_name, multiple_selection=True):
    """
    Prompts the user to select a colour fill scheme from the document.
    
    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: The forms object.
    :type forms: duHast.pyRevit.forms
    
    :return: A Result object containing the selected colour fill schemes.
    :rtype: Result
    """

    return_value = Result()

    # build action to get sheets from model
    def colour_fill_scheme_getter_in_line(doc):
        result_action =  colour_fill_scheme_getter(
            doc=doc
        )
        return result_action

    # build action for the sheet name to be displayed in UI
    def colour_fill_scheme_name_builder_ui_in_line(element):
        return colour_fill_scheme_name_builder_ui(
            doc=doc,
            element=element,
        )

    # get the user to select which sheet to export
    selected_colour_fill_scheme_ids=get_element_selection_from_user(
        doc=doc,
        forms=forms,
        element_getter=colour_fill_scheme_getter_in_line,
        element_selection_description=form_name,
        multiselect=multiple_selection,
        ui_element_name_builder= colour_fill_scheme_name_builder_ui_in_line,
    )

    # check if the user cancelled the selection
    if selected_colour_fill_scheme_ids is None or len(selected_colour_fill_scheme_ids) == 0:
        return return_value.update_sep(False, "User cancelled selection.")

   
    names_selected_colour_fill_scheme = []
    # get the selected colour fill schemes
    for selected_id in selected_colour_fill_scheme_ids:
        selected_colour_scheme = doc.GetElement(selected_id)
        return_value.result.append(selected_colour_scheme)
        names_selected_colour_fill_scheme.append(selected_colour_scheme.Name)
       
    return_value.append_message("Colour scheme(s) selected: {}".format(", ".join(names_selected_colour_fill_scheme)))
    
    return return_value


def import_colour_fill_scheme_from_file(forms):
    """
    Imports colour fill schemes data from a file.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A Result object containing the import status and message.
    :rtype: Result
    """

    return_value = Result()

    try:
        # get file selection from user and file content
        file_path = get_file_path_from_user(forms=forms, title = "Select a CSV file to import colour fill schemes from", file_extension = "csv")
        if file_path is None:
            return_value.update_sep(False, "User cancelled selection.")
            return return_value

        # read the file
        file_data_result = read_csv_file(file_path=file_path, increase_max_field_size_limit=False)

        # check if the file was read successfully
        if not file_data_result.status:
            return_value.update(file_data_result)
            return return_value

        data_entries = {}

        # convert data read into objects
        # data read has a header row ... ignore it
        colour_fill_scheme_data = file_data_result.result[1:]

        for colour_fill_scheme_row in colour_fill_scheme_data:
            colour_scheme_instance = ColourFillStorage()
            colour_scheme_instance.fill_scheme_name = colour_fill_scheme_row[0]
            colour_scheme_instance.area_scheme_name = colour_fill_scheme_row[1]
            colour_scheme_instance.parameter_value = colour_fill_scheme_row[2]
            colour_scheme_instance.storage_type = int(colour_fill_scheme_row[3])
            colour_scheme_instance.fill_pattern_id = int(colour_fill_scheme_row[4])
            colour_scheme_instance.is_in_use = bool(colour_fill_scheme_row[5])
            colour_scheme_instance.is_visible = bool(colour_fill_scheme_row[6])
            colour_scheme_instance.colour_red = int(colour_fill_scheme_row[7])
            colour_scheme_instance.colour_green = int(colour_fill_scheme_row[8])
            colour_scheme_instance.colour_blue = int(colour_fill_scheme_row[9])

            # build a key for the dictionary
            key = "{} <{}>".format(colour_scheme_instance.fill_scheme_name, colour_scheme_instance.area_scheme_name)
            # check if key is in dictionary, if not add it
            if  key not in data_entries:
                data_entries[key] = []
            # add the instance to the dictionary
            data_entries[key].append(colour_scheme_instance)

        # store the data in the result object
        return_value.result = [data_entries]
        return_value.append_message("Colour fill scheme data imported successfully.")
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Error importing colour scheme: {}".format(e))
        return return_value
    


def select_colour_scheme_to_import (forms, fill_scheme_data):


    # fill_scheme_data is a dictionary of name and data
    return_value = Result()

    try:

        if isinstance(fill_scheme_data, dict) == False:
            return_value.update_sep(False, "Data is not a dictionary. Got {}".format(type(fill_scheme_data)))
            return return_value

        # get the user to select the source ( returns a string)
        selection = forms.SelectFromList.show(sorted(list(fill_scheme_data.keys())), button_name='Select colour fill scheme to import', multiselect=False)

        if(selection == None):
            return_value.update_sep(False, "User cancelled selection.")
            return return_value
        
        return_value.result = fill_scheme_data[selection]

        return_value.append_message("Colour fill scheme data selected successfully.")
        return return_value
    
    except Exception as e:
        return_value.update_sep(False, "Error importing colour scheme: {}".format(e))
        return return_value
    


# set up some options for the user to select
UPDATE = "Update existing colours"
ADD_AND_UPDATE = "Add new values and update existing ones"


def get_user_options(forms):
    """
    Gets the user options for update or add and update.

    Options are: UPDATE or ADD_AND_UPDATE

    :param forms: the forms object
    :type forms: Forms
    :return: the user options
    :rtype: dict
    """

    # ask user if colours to be updated only
    # if new values are to be added and existing ones updated
    ops = [UPDATE,ADD_AND_UPDATE]
    configs = {
        UPDATE: {"background": "#00FF00"},
        ADD_AND_UPDATE : {"background": "#00FF00"},
    }
    ui_options = forms.CommandSwitchWindow.show(
        ops,  message="Do you want to update existing colours only or add new values and update existing ?", config=configs
    )

    return ui_options