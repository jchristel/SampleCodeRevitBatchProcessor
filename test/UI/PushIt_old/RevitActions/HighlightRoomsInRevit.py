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

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class highlighting family instances representing rooms.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
# required for .net list object
import clr

clr.AddReference("System.Core")
from System import Linq # required for .net list object
clr.ImportExtensions(Linq)
# end required for .net list object


from PushIt_old.RevitActions.RevitActionBase import RevitActionBase
from Autodesk.Revit.DB import (ElementId)

class HighlightRoomsInRevit(RevitActionBase):

    def __init__(self, revit_model):
        """
        Constructor for the Revit Action class.
        """

        super(HighlightRoomsInRevit, self).__init__(revit_model=revit_model)
    
    
    def execute(self, doc, ui_app):
        """
        Execute the action.
        """
        
        # check if the room of interest is set
        if self.revit_model._room_of_interest is None:
            print("Room of interest is not set.")
            return
        
        # build a list of element ids
        element_ids = []
        for fam_placed in self.revit_model._room_of_interest.get_revit_matches():
            element_ids.append(ElementId(fam_placed.revit_element_id))
        
        # get the active ui document
        ui_doc = ui_app.ActiveUIDocument
        
        #wrap in try catch in case the elements are not found
        try:
            # highlight the elements
            ui_doc.Selection.SetElementIds(element_ids.ToList[ElementId]())
            
            # zoom to the elements
            ui_doc.ShowElements(element_ids.ToList[ElementId]())
            
            # regenerate the view
            ui_doc.RefreshActiveView()
        except Exception as e:
            print("Failed to highlight rooms with exception: {}".format(e))
            return False
        
        