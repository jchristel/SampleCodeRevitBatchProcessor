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

from System.Collections.Generic import List

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Views.sheets import get_all_sheets
from duHast.Revit.Views.schedules import  get_all_sheet_schedules
from duHast.Revit.Views.schedules_fields import get_field_names_to_parameters, get_field_values_from_schedule_by_parameter_id
from duHast.Revit.Views.schedules_sheets_export import  export_all_sheet_schedules_and_read_data_back
from duHast.pyRevit.console_output import  print_error


from export.utility import get_sheet_parameter_data

from Autodesk.Revit.DB import ElementId, FilteredElementCollector, ViewSheet, ViewSheetSet

def schedule_contains_sheet_number_field(schedule):
    """
    Checks if the given schedule contains the sheet number field.

    :param schedule: The schedule to check.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :return: True if the schedule contains the sheet number field, False otherwise.
    :rtype: bool
    """

    # get the field names in the schedule
    field_names = get_field_names_to_parameters(schedule)

    # check if the sheet number field is in the field parameter ids
    for field_names,parameter_id in field_names.items():
        # SHEET_NUMBER	-1,007,401	"Sheet Number" ( revit api docs)
        if parameter_id.IntegerValue == -1007401:
            # sheet number field found, return True
            return True
    
    return false


def get_sheet_numbers_in_schedule(schedule):
    """
    Gets all sheet numbers listed in the given schedule.

    :param schedule: The schedule to extract sheet numbers from.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :return: A list of sheet numbers found in the schedule.
    :rtype: list of str
    """

    sheet_numbers = []

    sheet_number_element_id = ElementId(-1007401)  # SHEET_NUMBER parameter id
    try:
        sheet_numbers = get_field_values_from_schedule_by_parameter_id(schedule, sheet_number_element_id)
        return sheet_numbers
    except Exception as e:
        print_error("Error getting sheet numbers from schedule '{}': {}".format(schedule.Name, e))
        return sheet_numbers

    

def get_ui_schedule_data (doc, sheets):

    """
    Gets the print set data for the export process.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Tuple containing the print set data.
    :rtype: tuple
    """
    
    # import the Schedule class from the PDFDWGExporterUI namespace
    from duHastNet.UI.PDFDWGExporterSelectionUI.Models import RevitSchedule
    from duHastNet.UI.PDFDWGExporterSelectionUI.Models import RevitSheet

    # create a .net list to hold the schedule objects
    schedule_data = List[RevitSchedule]()


    # export all sheet schedules and read the data back
    schedule_export_result = export_all_sheet_schedules_and_read_data_back(doc)
    print("Exported all sheet schedules with status: {}".format(schedule_export_result.status))
    print("Message: {}".format(schedule_export_result.message))
    print("Result: {}".format(schedule_export_result.result))


    if schedule_export_result.status:
        
        # if the export was successful, get the data from the result
        schedule_data = schedule_export_result.result
        print("Found {} schedules in the model.".format(len(schedule_data)))
    else:
        # if the export failed, print the error message and return an empty list
        print_error("Error exporting sheet schedules: {}".format(schedule_export_result.message))
        return schedule_data


    # get all sheet schedules in the model'
    sheet_schedules = get_all_sheet_schedules(doc)

    print( "Found {} sheet schedules in the model.".format(sheet_schedules.Count))
    for schedule in sheet_schedules:
        
        # check if the schedule contains the sheet number field
        if not schedule_contains_sheet_number_field(schedule):
            continue

        # get all sheet numbers listed in schedule
        sheet_numbers_in_schedule = get_sheet_numbers_in_schedule(schedule)
        if len(sheet_numbers_in_schedule) == 0:
            # no sheet numbers found in the schedule, skip this schedule
            continue

        sheets_in_schedule = List[RevitSheet]() 

        for number_found in sheet_numbers_in_schedule:
            for sheet in sheets:
                if sheet.SheetNumber == number_found:
                    sheets_in_schedule.Add(sheet)

        # populate a RevitSchedule object with the schedule data
        revit_sheet_schedule =  RevitSchedule(
            name=schedule.Name,
        )

        # iterate over the sheets in the set and add them to the RevitPrintSet object
        for sheet in sheets_in_schedule:
            revit_sheet_schedule.AddRevitSheet(sheet)

        # add the RevitPrintSet object to the list of print sets
        schedule_data.Add(revit_sheet_schedule)

    # currently no schedule data is available, so return an empty list
    return schedule_data



def get_view_sets(doc):

    # set up a filtered element collector to get all view sets in the document
    view_set_collector = FilteredElementCollector(doc).OfClass(ViewSheetSet)
    return view_set_collector



def get_ui_print_set_data(doc, sheets):
    """
    Gets the print set data for the export process.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Tuple containing the print set data.
    :rtype: tuple
    """
    
    # import the PrintSet class from the PDFDWGExporterUI namespace
    from duHastNet.UI.PDFDWGExporterSelectionUI.Models import RevitPrintSet
    from duHastNet.UI.PDFDWGExporterSelectionUI.Models import RevitSheet

    # create a .net list to hold the print set objects
    print_set_data = List[RevitPrintSet]()

    # get the view sets in the model
    col = get_view_sets(doc)
    
    for set in col:
        
        # check if the set has any views
        if set.OrderedViewList is None or set.OrderedViewList.Count == 0:
            continue
        
        view_ids = []
        for sheet_in_set in set.OrderedViewList:
            if (isinstance(sheet_in_set, ViewSheet)):
                view_ids.append(sheet_in_set.Id.IntegerValue)
            
        
        # check if any sheet ids where found in the set
        if len(view_ids) == 0:
            continue
        
        sheets_in_set = List[RevitSheet]() 

        for id_found in view_ids:
            for sheet in sheets:
                if sheet.RevitElementId.Value == str(id_found):
                    sheets_in_set.Add(sheet)
        

        # check if any sheets were found in the set
        if sheets_in_set.Count == 0:
            # no sheets found in the set, skip this set
            continue

        # create a RevitPrintSet object with the set data
        revit_print_set = RevitPrintSet(
            name=set.Name
        )

        # iterate over the sheets in the set and add them to the RevitPrintSet object
        for sheet in sheets_in_set:
            revit_print_set.AddRevitSheet(sheet)
       
        # add the RevitPrintSet object to the list of print sets
        print_set_data.Add(revit_print_set)

    # currently no print set data is available, so return an empty list
    return print_set_data



def get_ui_sheet_data(doc):
    # get all sheets in the document
    all_sheets = get_all_sheets(doc)

    # import the UI class from the PDFDWGExporterUI namespace
    from duHastNet.UI.PDFDWGExporterSelectionUI.Models import RevitSheet
    from duHastNet.UI.PDFDWGExporterSelectionUI.Models import SheetProperty


    # create a .net list to hold the RevitSheet objects
    sheet_ui_data = List[RevitSheet]() 

    try:
        # iterate over all sheets in the document and create RevitSheet objects
        for sheet in all_sheets:
            # get the sheet parameter data
            sheet_parameter_data = get_sheet_parameter_data(sheet)
            

            # create a RevitSheet object with the sheet data
            revit_sheet = RevitSheet(
                revitElementId=str(sheet.Id.IntegerValue),
                sheetName=sheet.Name,
                sheetNumber=sheet.SheetNumber
            )
            
            # add the parameter data to the RevitSheet object
            for para_name, para_value in sheet_parameter_data.items():
            
                # create a SheetProperty object
                sheet_property = SheetProperty(
                    name=para_name,
                    value=para_value
                )
                try:
                    # add the property to the RevitSheet object
                    revit_sheet.AddSheetProperty(sheet_property)
                except Exception as e:
                    # handle any exceptions that occur while adding the property
                    print_error("Error adding property '{}' to sheet '{}': {}".format(para_name, sheet.Name, e))
                    continue

            # add the sheet to the list of sheets
            sheet_ui_data.Add(revit_sheet)


    except Exception as e:
        # handle any exceptions that occur while getting sheet data
        print_error("Error getting sheet data: {}".format(e))
        
    
    return sheet_ui_data

def get_ui_data(doc):
    """
    Gets the UI data for the export process.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Tuple containing the output directory, export sheets flag, and selected sheet ids.
    :rtype: tuple
    """
    
    
    # get all .net sheet data
    sheet_ui_data = get_ui_sheet_data(doc)

    # get print set data
    print_set_ui_data = get_ui_print_set_data(doc, sheet_ui_data)

    # get schedule data
    schedule_ui_data = get_ui_schedule_data(doc, sheet_ui_data)
    print ("Schedule UI Data: {}".format(schedule_ui_data))

    # return data as a tuple
    ui_data = (sheet_ui_data,print_set_ui_data)

    return ui_data