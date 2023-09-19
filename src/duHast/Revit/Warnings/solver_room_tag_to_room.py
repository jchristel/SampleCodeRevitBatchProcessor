"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Room tag not in room warnings solver class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Utilities.Objects import result as res
from duHast.Revit.Rooms.room_tags import move_tag_to_room
from duHast.Revit.Common.transaction import in_transaction

# import Autodesk
# import Autodesk.Revit.DB as rdb
from duHast.Utilities.Objects import base


class RevitWarningsSolverRoomTagToRoom(base.Base):
    def __init__(
        self,
        transaction_manager=in_transaction,
        callback=None,
    ):
        """
        Empty constructor this solver does not take any further arguments.
        """

        # ini super class to allow multi inheritance in children!
        super(RevitWarningsSolverRoomTagToRoom, self).__init__()
        self.filter_name = "Room tag outside of room."
        self.transaction_manager = transaction_manager
        self.callback = callback

    # --------------------------- room tag not in room ---------------------------
    #: guid identifying this specific warning
    GUID = "4f0bba25-e17f-480a-a763-d97d184be18a"

    def solve_warnings(self, doc, warnings):
        """
        Solver moving room tags to room location point.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param warnings: List of warnings to be solved.
        :type warnings: Autodesk.Revit.DB.FailureMessage

        :return:
            Result class instance.

            - .result = True if all room tags within warnings could be moved to room location point. Otherwise False.
            - .message will be 'moved tag to room xyz'

        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        if len(warnings) > 0:
            # report progress to call back if required
            counter = 0
            if self.callback:
                self.callback(counter, len(warnings))
            for warning in warnings:
                element_ids = warning.GetFailingElements()
                for el_id in element_ids:
                    result = move_tag_to_room(
                        doc=doc,
                        tag_id=el_id,
                        transaction_manager=self.transaction_manager,
                    )
                    return_value.update(result)
                counter = counter + 1
        else:
            return_value.update_sep(
                True, "No warnings of type: room tag outside of room in model."
            )
        return return_value
