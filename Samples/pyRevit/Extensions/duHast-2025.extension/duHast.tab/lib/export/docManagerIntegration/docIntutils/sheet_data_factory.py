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

from duHast.pyRevit.console_output import print_header, print_error
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Views.sheets import get_all_sheets
from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.Revisions.revisions_from_sheet import get_revisions_from_sheet
DEBUG = True

def get_sheet_properties(doc, revit_sheet, revit_sheet_data):
    """
    Get the properties of the sheet and add them to the sheet data model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_sheet: The sheet to get the properties from.
    :type revit_sheet: Autodesk.Revit.DB.ViewSheet
    :param revit_sheet_data: The sheet data model to add the properties to.
    :type revit_sheet_data: RevitSheet

    :return: Result object with status, message, and the data model with properties.
    :rtype: Result
    """

    return_value = Result()
    
    try:
        # import the UI class from the DocManagerSettingsUI namespace
        from  duHastNet.UI.DocManagerUI.Utils.RevitData import RevitDocumentProperty

        # get all parameters attached to sheet
        paras = revit_sheet.GetOrderedParameters()
        for para in paras:
            # get values as utf-8 encoded strings
            # for some characters this still throws an exception...added ascii encoding
            value = rParaGet.get_parameter_value_utf8_string(para)

            # create a RevitDocumentProperty object and add it to the list in the data model
            data_property = RevitDocumentProperty(para.Definition.Name, value)

            # add property to sheet data
            revit_sheet_data.AddDocumentProperty(data_property)

        
        if DEBUG:
            props = revit_sheet_data.DocumentProperties
            items = [str(p) for p in props]  # calls .ToString() under the hood
            print("......{}: {}".format(revit_sheet_data.SheetNumber, ",\n".join(items)))
        
        return_value.result.append(revit_sheet_data)
        return return_value
    except Exception as e:
        message = "Error getting sheet data from file. Error: {}".format(e)
        if DEBUG:
            print_error(message)
        return_value.update_sep(False, message)
        return return_value
    

def get_sheet_revisions(doc, revit_sheet, revit_sheet_data, revit_data_model):
    """
    Get the revisions on the sheet and add them to the sheet data model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_sheet: The sheet to get the revisions from.
    :type revit_sheet: Autodesk.Revit.DB.ViewSheet
    :param revit_sheet_data: The sheet data model to add the revision data to.
    :type revit_sheet_data: RevitSheet
    :param revit_data_model: The data model to get the revision data from.
    :type revit_data_model: RevitDataModel

    :return: Result object with status, message, and the data model with revision data.
    :rtype: Result
    
    """
    return_value = Result()
    
    try:
        # import the UI class from the DocManagerSettingsUI namespace
        from  duHastNet.UI.DocManagerUI.Utils.RevitData import  RevitRevisionOnSheet

        # get revsions on sheet data
        revit_revisions = get_revisions_from_sheet(doc, revit_sheet)

        # check if sheet got any revisions, if not return the sheet data without any revisions
        if not revit_revisions:
            if DEBUG:
                print("......{}: No revisions on sheet".format(revit_sheet_data.SheetNumber))
            return_value.result.append(revit_sheet_data)
            return return_value
        
        if DEBUG:
            print("......{}: {} revisions on sheet".format(revit_sheet_data.SheetNumber, len(revit_revisions)))

        for rev in revit_revisions:
            
            revision_indicator = rev[0]
            revit_revision = rev[1]

            data_revision = revit_data_model. GetRevisionByRevitElementId(revit_revision.Id.Value)

            revision_on_sheet = RevitRevisionOnSheet(revision_indicator, data_revision)

            if DEBUG:
                print("......{}: {}".format(revit_sheet_data.SheetNumber, revision_on_sheet))

            revit_sheet_data.AddRevisionOnSheet(revision_on_sheet)

        return_value.result.append(revit_sheet_data)
        return return_value
    except Exception as e:
        message = "Error getting sheet data from file. Error: {}".format(e)
        if DEBUG:
            print_error(message)
        return_value.update_sep(False, message)
        return return_value


def get_sheet_data(doc,  revit_data_model):
    """
    Get the sheet data from the Revit model and add it to the data model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_data_model: The data model to add the sheet data to.
    :type revit_data_model: RevitDataModel
    :return: Result object with status, message, and the data model with sheet data.
    :rtype: Result
    """

    return_value = Result()
    
    try:
        
        # import the UI class from the DocManagerSettingsUI namespace
        # do this in this function to allow the caller to register the UI dll before this code is executed
        from  duHastNet.UI.DocManagerUI.Utils.RevitData import RevitSheet

        # get all sheets in the document
        sheets = get_all_sheets(doc)
        
        for sheet in sheets:
            
            # create a RevitSheet object to hold the data for this sheet, we will add the properties and revisions to this object as we get them
            revit_sheet_data = RevitSheet(sheet.SheetNumber, sheet.Name)

            if DEBUG:
                print("...{}".format(revit_sheet_data))

            # get the properties for this sheet and add them to the data model
            get_properties_result = get_sheet_properties(doc, sheet, revit_sheet_data)
            if not get_properties_result.status:
                return_value.update_sep(False, get_properties_result.message)
                # skip this sheet and continue with the next one
                continue

            revit_sheet_data = get_properties_result.result[0]

            # get the revisions for this sheet and add them to the data model
            get_revisions_result = get_sheet_revisions(doc, sheet, revit_sheet_data, revit_data_model)
            if not get_revisions_result.status:
                return_value.update_sep(False, get_revisions_result.message)
                # skip this sheet and continue with the next one
                continue

            revit_sheet_data = get_revisions_result.result[0]
            
            revit_data_model.AddSheet(revit_sheet_data)
            
            
        return_value.update_sep(True, "Successfully retrieved sheet data from document.")
        return_value.result.append(revit_data_model)
        return return_value
    
    except Exception as e:
        message = "Error getting sheet data from file. Error: {}".format(e)
        if DEBUG:
            print_error(message)
        return_value.update_sep(False, message)
        return return_value