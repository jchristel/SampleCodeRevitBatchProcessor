"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit room creation. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
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


from duHast.Revit.Common.transaction import in_transaction

from duHast.Utilities.Objects.result import Result


from Autodesk.Revit.DB import Transaction

def create_room (doc, level, location_point, modify_action, transaction_manager=in_transaction):
    """
    Create a room in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The level to create the room on.
    :type level: Autodesk.Revit.DB.Level
    :param location_point: The location point of the room.
    :type location_point: Autodesk.Revit.DB.XYZ
    :param  modify_action: An action executed on the room at the time of creation ( in same transaction).
    :type  modify_action: function taking the room as input
    :param transaction_manager: The transaction manager to use. Defaults to in_transaction.
    :type transaction_manager: TransactionManager, optional
    :return:
        Result class instance.

        - result.status. True if room was created successfully, otherwise  False.
        - Result.message. Generic success message.
        - Result.result. The created room if successful as first entry in list, otherwise None.

        On exception:

        - result.status (bool) will be False.
        - Result.message will contain the exception message.
        - Result.result will be an empty list.

    :rtype: Result
    """

    return_value = Result()

    try:
        
        def action():
            """
            Create the room and execute the modify action.
            """
            action_return_value = Result()
            try:
                # Create the room
                room = doc.Create.NewRoom(level, location_point)
                # Execute the modify action if provided
                if modify_action:
                    modify_action(room)
                action_return_value.result.append(room)
                action_return_value.append_message ("Room created successfully.")
            except Exception as e:
                action_return_value.update_sep (False,"{}".format(e))
            return action_return_value
        
        # execute inside transaction if a transaction manager is provided, otherwise run the action directly
        # assuming there is a transaction running already
        if transaction_manager:
            # Start the transaction
            tranny = Transaction(doc, "Create Room")
            return_value = transaction_manager(tranny, action)
        else:
            return_value = action()
        
        return return_value

    except Exception as e:
        return_value.update_sep (False,"{}".format(e))
    return return_value