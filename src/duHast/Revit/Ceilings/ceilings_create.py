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
from duHast.Utilities.unit_conversion import convert_mm_to_imperial_feet
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import BuiltInParameter, Ceiling,ElementId, Transaction



def create_ceiling( doc, level_id, outline, elevation, ceiling_type_id, phase_created = None, transaction_manager=in_transaction):
    """
    Creates a ceiling in the given document at the specified level and elevation.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param level_id: The ElementId of the level where the ceiling should be created.
    :type level_id: Autodesk.Revit.DB.ElementId
    :param outline: The outline of the ceiling as a list of curve loops.
    :type outline: Autodesk.Revit.DB.CurveLoop
    :param elevation: The elevation in mmm of the ceiling above the level.
    :type elevation: float
    :param ceiling_type_id: The ElementId of the ceiling type to use.
    :type ceiling_type_id: Autodesk.Revit.DB.ElementId
    :param transaction_manager: Optional transaction manager to handle transactions.
    :type transaction_manager: function
    
    :return:
        Result class instance.

        - Ceiling creation status (bool) returned in result.status. False if an exception occurred, otherwise True.
        - Result.message property contains id of ceiling created.
        - Result.result will contain the created ceiling element if successful, otherwise an empty list.

        On exception:

        - .status (bool) will be False.
        - .message will contain the exception message.

    :rtype: :class:`.Result`
    """

    return_value = Result()
  
    def action ():
        action_return_value = Result()
        try:
            ceiling = Ceiling.Create(doc, outline, ElementId.InvalidElementId, level_id)

            if not ceiling:
                action_return_value.update_sep(False, "failed to create ceiling")
                return action_return_value
            
            # set the ceiling type
            ceiling.ChangeTypeId(ceiling_type_id)

            # set the elevation ( expectation is that the elevation is given in mm )
            param = ceiling.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM)
            param.Set(convert_mm_to_imperial_feet(elevation))

            # set the phase created if there is one provided
            if phase_created:
                # set the phase created if there is one provided
                ceiling.get_Parameter(BuiltInParameter.PHASE_CREATED).Set(phase_created.Id)
           
            # add the ceiling element to the return object
            action_return_value.result.append(ceiling)
            action_return_value.append_message("created ceiling: {}".format(ceiling.Id))
            return action_return_value
        except Exception as e:
            action_return_value.update_sep(False, "failed to create ceiling: {}".format(e))
            return action_return_value

    # check if a transaction manager is provided
    if transaction_manager:
        # run the action in a transaction
        tranny = Transaction(doc, "Adding ceiling")
        return_value = transaction_manager(tranny, action)
    else:
        return_value.update(action())
       

    return return_value
