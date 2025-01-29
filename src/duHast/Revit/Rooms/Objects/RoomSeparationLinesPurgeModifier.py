"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class used to implement deleted element and modified element count for room separation lines in warnings solver.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modify delete

- checks whether the deleted element count is a list of 2 entries
- checks whether any entry is a model line

Modified modifier

- check if any room in that collection has an area of zero after modification

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

import System
# required since we are dealing with a c# List element
from System.Collections.Generic import  List

from duHast.Revit.Purge.Objects.ModifierBase import ModifierBase

# required for isInstance check
from Autodesk.Revit.DB import (
    CurveElement, 
    ElementId,
    FilteredElementCollector
)

from Autodesk.Revit.DB.Architecture import Room

class RoomSeparationLinesPurgeModifier(ModifierBase):
    def __init__(self, doc):
        """
        Class constructor.

        """

        super(RoomSeparationLinesPurgeModifier, self).__init__()

        # get all model lines in the project before deletion in order to be able to check if the deleted element is a model line
        self.model_lines = FilteredElementCollector(doc).OfClass(CurveElement ).ToElementIds()

        self.debug_log = []

    def  modify_modified(self, doc, modified):
        """
        Base implementation override to modify the modified element count.

        Returns modified element list unchanged if:
        - modified is not a c# List[ElementId]
        

        Returns:
        - modified element list without any room objects

        Args:
            modified: The modified element count

        """

        if isinstance(modified, List[ElementId]) == False:
            self.debug_log.append(
                "modified is not a List[ElementId]: {}".format(modified)
            )
            raise TypeError("deleted must be a List[ElementId]:".format(modified))

        
        # remove any other modellines from modified list
        # check if room is in modified list and if so if it has an area???
        filtered_ids = []
        for id in modified:
            element = doc.GetElement(id)
            if type(element) is Room:
                # if the room has no area, the change of that room separation line is important and should not go ahead
                self.debug_log.append(
                    "...in rooms modified modifier: Room found with area: {}".format(element.Area)
                )
                if element.Area > 0 is False:
                    filtered_ids.append(id)
            
            else:
                # all the other elements:
                # ModelLines and other elements can be ignoerd
                pass
            
        return filtered_ids
    
    def  modify_deleted(self, doc, deleted):
        """
        Base implementation override to modify the deleted element count.

        Returns deleted element list unchanged if:
        - deleted is not a c# List[ElementId]
        - deleted is not a list of 2 elements

        Returns:
        - deleted element list without any model lines

        :param deleted: The deleted element id list
        :type deleted: List[ElementId]
        """

        if isinstance(deleted, List[ElementId]) == False:
            self.debug_log.append(
                "modified is not a List[ElementId]: {}".format(deleted)
            )
            raise TypeError("deleted must be a List[ElementId]:".format(deleted))
        
        # check if 2 elements got deleted..one is a model line and the other is <other> object
        # if so, remove the model line from the list

        if len(deleted) != 2:
            return deleted
        
        # check if the element is a model line
        filtered_ids = []
        for id in deleted:
            try:
                if id not in self.model_lines:
                    filtered_ids.append(id)
            except Exception as e:
                print("in deleted modifier: element not found: {} for : {}".format(e, id))
        
        return filtered_ids
        