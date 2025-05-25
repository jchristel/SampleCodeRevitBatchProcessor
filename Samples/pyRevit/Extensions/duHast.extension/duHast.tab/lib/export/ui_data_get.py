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
from duHast.pyRevit.console_output import  print_error


from export.utility import get_sheet_parameter_data

from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet, ViewSheetSet

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

    print('here1')
    col = get_view_sets(doc)
    print('here2')

    for set in col:
        
        # check if the set has any views
        if set.OrderedViewList is None or set.OrderedViewList.Count == 0:
            continue
        
        print(set.Name)
        view_ids = []
        for sheet_in_set in set.OrderedViewList:
            if (isinstance(sheet_in_set, ViewSheet)):
                view_ids.append(sheet_in_set.Id.IntegerValue)
            
            print("...View in set: {} is of type: {}".format(sheet_in_set.Name, type(sheet_in_set)))
        
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

        # print the name of the set and the number of sheets in it
        print("Found print set: {} with {} sheets".format(set.Name, sheets_in_set.Count))

        # create a RevitPrintSet object with the set data
        revit_print_set = RevitPrintSet(
            name=set.Name,
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

    # return data as a tuple
    ui_data = (sheet_ui_data,print_set_ui_data)

    return ui_data