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

from System.Collections.Generic import List

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Ceilings.ceilings import  get_all_ceiling_types_by_category
from duHast.Revit.Ceilings.ceilings_create import create_ceiling
from duHast.Revit.Rooms.Geometry.geometry import get_room_boundary_loops,convert_boundary_segments_to_curve_loops
from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Common.parameter_get_utils import get_parameter_value, get_built_in_parameter_value

from duHast.pyRevit.console_output import print_error
from duHast.Revit.Common.phases import get_name_to_phase_dict

from Autodesk.Revit.DB import BuiltInParameter,  CurveLoop, Element, SpatialElementBoundaryLocation


# where is the ceiling type code located in the room?
ROOM_CEILING_TYPE_PARAMETER_NAME = "Ceiling Finish"
PHASE_NAME = "Project Scope"


def get_ceiling_type_from_room(doc, room):

    # get the ceiling type from a room property or a default type
    all_ceiling_types = get_all_ceiling_types_by_category(doc)

    parameter_value = None

    for p in room.GetOrderedParameters():
        if p.Definition.Name == ROOM_CEILING_TYPE_PARAMETER_NAME:
            #print(p)
            parameter_value = get_parameter_value(p)
            #print("p value: {}".format(parameter_value))
    

    # get the second type as default
    ceiling_type_match = None
    counter = 0
    for ceiling_type in all_ceiling_types:
        counter = counter + 1
        # check if the ceiling type is suitable for the room
        if counter == 2:
            ceiling_type_match = ceiling_type
            
    if parameter_value is None:
        #print("No value for room ceiling code. Using default type")
        # return the default
        return ceiling_type_match
    else:
        # loop over ceilings and match mark with value
        for ceiling_type in all_ceiling_types:
            # get the type mark value
            type_mark_value = get_built_in_parameter_value(
                element=ceiling_type,
                built_in_parameter_def=BuiltInParameter.WINDOW_TYPE_ID
            )
            if type_mark_value == parameter_value:
                return ceiling_type
            else:
                pass
                #print("no match for ceiling type: {} and room ceiling code: {}".format(Element.Name.GetValue(ceiling_type),type_mark_value))
        
        #print("no match found using default ceiling type for room ceiling code: {}".format(parameter_value))
        # if no ceiling type is found, return the default type
        return ceiling_type_match


def create_ceiling_by_room(doc, room):
    """
    Creates a ceiling by room.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param room: The room element.
    :type room: Autodesk.Revit.DB.Element
    :return: Result object containing the created ceiling element.
    :rtype: Result
    """
    
    return_value = Result()

    try:
        # get the created in phase by name
        phases = get_name_to_phase_dict(doc)
        ceiling_phase = phases.get(PHASE_NAME, None)

        # get the ceiling type from a room property or a default type
        ceiling_type = get_ceiling_type_from_room(doc, room)

        if not ceiling_type:
            return_value.update_sep(False, "no ceiling type found for room: {}".format(room.Id))
            return return_value
        
        # update result
        return_value.append_message("using ceiling type: {}".format(Element.Name.GetValue(ceiling_type)))

        # get the room outlines
        # these are nested ... skip the first level
        all_boundary_loops = get_room_boundary_loops(revit_room = room,  boundary_location=SpatialElementBoundaryLocation.Finish)[0]

        # set up curve loops for ceiling creation
        curve_loops = List[CurveLoop]()

        # boundary loops are nested and contain the outlines of the room
        for boundary_loop in all_boundary_loops:
            # change boundary loop to curve loop
            curve_loop_result = convert_boundary_segments_to_curve_loops(boundary_loop)
            if curve_loop_result.status == False:
                print_error (curve_loop_result.message)
            else:
                curve_loop = curve_loop_result.result[0]
                if curve_loop is None:
                    print_error("none found for boundary loop: {}".format(boundary_loop))
                    return_value.update_sep(False, "failed to convert boundary loop to curve loop for room: {}".format(room.Id))
                    return return_value
            curve_loops.Add(curve_loop)
        
        create_ceiling_result = create_ceiling(
            doc=doc, 
            level_id = room.LevelId,  
            outline = curve_loops,
            elevation=2700.0,
            ceiling_type_id=ceiling_type.Id,
            phase_created = ceiling_phase,
            transaction_manager=in_transaction
        )
        print("create_ceiling_result: {}".format(create_ceiling_result.message))

        return_value.append_message("created ceiling by room: {}".format(room.Id))
        return return_value
    except Exception as e:
        print_error("failed to create ceiling by room: {}".format(e))
        return_value.update_sep(False, "failed to create ceiling by room: {}".format(e))
        return return_value
    