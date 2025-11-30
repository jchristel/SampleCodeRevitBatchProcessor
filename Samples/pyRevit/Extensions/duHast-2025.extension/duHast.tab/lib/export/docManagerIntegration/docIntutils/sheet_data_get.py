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
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value
from duHast.Revit.Views.sheets import get_all_sheets
from export.docManagerIntegration.Objects.DocManagerSheetData import DocManagerSheetData

from Autodesk.Revit.DB import BuiltInParameter




def get_sheet_data(doc):
    return_value = Result()
    
    try:
        
        # get all sheets in the document
        sheets = get_all_sheets(doc)
        
        sheet_data = []
        for sheet in sheets:
            
            sheet_number = sheet.SheetNumber
            # get the sheet name: BuiltInParameter.SHEET_NAME
            sheet_name = get_built_in_parameter_value(sheet, BuiltInParameter.SHEET_NAME)
            
            doc_manager_sheet = DocManagerSheetData(sheet_number, sheet_name)
            sheet_data.append(doc_manager_sheet)
            
        return_value.update_sep(True, "Successfully retrieved sheet data from document.")
        return_value.result.append(sheet_data)
        return return_value
    except Exception as e:
        message = "Error getting sheet data from file. Error: {}".format(e)
        return_value.update_sep(False, message)
        return return_value