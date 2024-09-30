"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class used to implement deleted element count for line styles when using purge by delete.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- checks whether the deleted element count is a list of 2 entries
- checks whether the first entry is a line style id
- checks whether the second entry is a graphics style id belonging to the line style id


This class is used to modify the deleted element count for line styles when using purge by delete because this modifier is called
after the elements are deleted from the model but a reference is required of them before they are deleted.
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
from System.Collections.Generic import (
    List,
)  # required since we are dealing with a c# List element

from duHast.Revit.Purge.Objects.ModifierBase import ModifierBase
from duHast.Revit.LinePattern.line_styles import (
    get_all_graphics_style_ids_by_line_style_id,
)

# required for isInstance check
from Autodesk.Revit.DB import (
    ElementId,
)


class LineStylePurgeModifier(ModifierBase):
    def __init__(self, doc):
        """
        Class constructor.

        """

        super(ModifierBase, self).__init__()

        # get dictionary of line styles
        self.graphic_style_id_by_line_style_id = (
            get_all_graphics_style_ids_by_line_style_id(doc)
        )
        self.debug_log = []

    def modify_deleted(self, doc, deleted):
        """
        Base implementation override to modify the deleted element count.

        Returns deleted element list unchanged if:
        - deleted is not a c# List[ElementId]
        - deleted is not exactly two ids
        - first deleted id is not in the dictionary of graphic style ids by line style ids
        - second deleted is not equal to the dictionary value of the first deleted id

        Returns:
        - deleted element list with the first id adjusted to 1 if the second id is equal to the dictionary value of the first id

        Args:
            deleted: The deleted element count

        """

        if isinstance(deleted, List[ElementId]) == False:
            self.debug_log.append(
                "deleted is not a List[ElementId]: {}".format(deleted)
            )
            raise TypeError("deleted must be a List[ElementId]:".format(deleted))

        # should be exactly two ids
        if len(deleted) != 2:
            self.debug_log.append("deleted count is not 2: {}".format(deleted))
            return deleted

        # sort ids ascending
        # first id should be the line style and second (higher value) the graphics style
        sorted_ids = sorted(deleted, key=lambda x: x.IntegerValue)
        if sorted_ids[0].IntegerValue in self.graphic_style_id_by_line_style_id:
            self.debug_log.append(
                "sorted_id: {} is in dictionary: {}".format(
                    sorted_ids[0], self.graphic_style_id_by_line_style_id
                )
            )
            if (
                sorted_ids[1].IntegerValue
                == self.graphic_style_id_by_line_style_id[sorted_ids[0].IntegerValue]
            ):
                self.debug_log.append(
                    "sorted_id: {} is equal to dictionary value: {}".format(
                        sorted_ids[1],
                        self.graphic_style_id_by_line_style_id[
                            sorted_ids[0].IntegerValue
                        ],
                    )
                )
                # adjusted the deleted id value to 1
                return [sorted_ids[0]]
            else:
                self.debug_log.append(
                    "sorted_id: {} is not equal to dictionary value: {}".format(
                        sorted_ids[1],
                        self.graphic_style_id_by_line_style_id[
                            sorted_ids[0].IntegerValue
                        ],
                    )
                )
                return deleted
        # leave the deleted id count value as is
        else:
            self.debug_log.append(
                "sorted_id: {} is not in dictionary: {}".format(
                    sorted_ids[0], self.graphic_style_id_by_line_style_id
                )
            )
        return deleted
