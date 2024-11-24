"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of utility functions which create views usually found on a Room Layout Sheet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Views created for a room are:

- plan
- elevations
- 3D view
- schedule



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

from duHast.Utilities.Objects.result import Result
from duHast.Data.Objects.Collectors.Properties.data_view_port_type_names import DataViewPortTypeNames
from duHast.Revit.Views.plan_view_create import create_view_plan
from duHast.Revit.Views.elevation_view_create import create_elevation_views
from duHast.Revit.Rooms.Objects.RoomSpatialObject import RoomSpatialObj
from duHast.Utilities.date_stamps import get_date_stamp, TIME_STAMP_HHMMSEC_UNDERSCORE


from duHast.Revit.Common.transaction import in_transaction_with_failure_handling
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)
from duHast.Revit.Common.parameter_set_utils import set_builtin_parameter_without_transaction_wrapper_by_name


from Autodesk.Revit.DB import  BuiltInParameter,Transaction

def create_plan_view_from_room (doc, room, view_plan_type):
    return_value = Result()

    # in order to create the view plan I need:
    # - level ( same as room)
    # - view plan type
    # - phase of the view ( same as the room created)
    # - bounding box: same as the rooms
    # - view name : room number + room name

    try:

        # test if room is placed in model ...just in case
        if room.Location is None:
            raise ValueError ("Room is not placed in model.")
        
        # get the room information
        room_spatial = RoomSpatialObj(rvt_doc=doc, room=room)

        # create a plan view
        create_view_status = create_view_plan(
            doc=doc, 
            level=room_spatial.level, 
            view_type=view_plan_type, 
            view_name="{} {}".format(room_spatial.number_name_comb, get_date_stamp(TIME_STAMP_HHMMSEC_UNDERSCORE)),
            phasing = room_spatial.phase_object, 
            view_crop=room_spatial.bbox,
            view_crop_visible=False,
        )

        return_value.update(create_view_status)

    except Exception as e:
        return_value.update_sep(False, "An exception occured: {}".format(e))

    return return_value


def create_elevation_views_in_room (doc, room, view_plan, view_elevation_type, scale):

    """
    Creates elevations in a room

    based on: # https://forums.autodesk.com/t5/revit-api-forum/automate-room-elevations-using-revit-api/td-p/3504490
    
    :return: _description_
    :rtype: _type_
    """
    
    return_value = Result()

    try:
        # test if room is placed in model ...just in case
        if room.Location is None:
            raise ValueError ("Room is not placed in model.")
        
        # get the room information
        room_spatial = RoomSpatialObj(rvt_doc=doc, room=room)


        # to speed things up I will manage the transaction here

        def action():
            action_return_value = Result()
            try:
                
                # create an elevation marker first with a single elevation
                result_marker = create_elevation_views(
                    doc=doc,
                    view_type=view_elevation_type,
                    view_marker_location=room_spatial.bbox_centre,
                    scale=scale,
                    view_index_list=[3],
                    view_names=[],
                    view_plan=view_plan,
                    phasing=room_spatial.phase_object,
                    view_crop=None,
                    view_crop_visible=False,
                    transaction_manager=None
                )

                action_return_value.update(result_marker)

                if result_marker.status == False:
                    raise ValueError("Creating elevation marker failed.")
                
                # get the elevation marker
                elevation_marker = result_marker.result[0]

                # get the single elevation view
                view_three = result_marker.result[1]

                   

                # rotate the marker so it faced the X axis ( from min_x, min_y to max_x, min_y)
                # I eventually worked out that I needed to create one of the elevations (index 3), rotate the marker, create elevation indexes 0, 1, & 2, and then delete 3, and then recreate 3.
                # What? Why? By using this approach the extents of the elevations are set correctly, i.e, extend to surrounding walls.

                # TODO: rotate the elevation if required
                # You can check the orientation of any view by getting View.ViewDirection. To reorient the ElevationMarker and all of the views it hosts, call ElementTransformUtils.RotateElement with the ElevationMarker as an argument.




                # create all other markers but 3
                view_zero = elevation_marker.CreateElevation(doc, view_plan.Id, 0)
                view_one = elevation_marker.CreateElevation(doc, view_plan.Id, 1)
                view_two = elevation_marker.CreateElevation(doc, view_plan.Id, 2)

                # delete marker 3
                doc.Delete(view_three.Id)

                # create elevation for 3
                view_three = elevation_marker.CreateElevation(doc, view_plan.Id, 3)

                # rename views to match room number and name
                view_zero.Name = "{} {}".format(room_spatial.number_name_comb, "Elevation 0")
                action_return_value.append_message("View Zero Name: {}".format(view_zero.Name))
                view_one.Name = "{} {}".format(room_spatial.number_name_comb, "Elevation 1")
                action_return_value.append_message("View One Name: {}".format(view_one.Name))
                view_two.Name = "{} {}".format(room_spatial.number_name_comb, "Elevation 2")
                action_return_value.append_message("View Two Name: {}".format(view_two.Name))
                view_three.Name = "{} {}".format(room_spatial.number_name_comb, "Elevation 3")
                action_return_value.append_message("View Three Name: {}".format(view_three.Name))


                # set the phasing of the views (this is most likely drive by the view plan...but just in case)
                result_phase = set_builtin_parameter_without_transaction_wrapper_by_name(
                    element=view_zero, 
                    parameter_definition=BuiltInParameter.VIEW_PHASE, 
                    parameter_value=room_spatial.phase_object.Id
                )
                action_return_value.append_message("Setting phase for view zero: {} with status {}".format(result_phase.message, result_phase.status))
                
                result_phase = set_builtin_parameter_without_transaction_wrapper_by_name(
                    element=view_one,
                    parameter_definition=BuiltInParameter.VIEW_PHASE,
                    parameter_value=room_spatial.phase_object.Id
                )
                action_return_value.append_message("Setting phase for view one: {} with status {}".format(result_phase.message, result_phase.status))

                result_phase = set_builtin_parameter_without_transaction_wrapper_by_name(
                    element=view_two,
                    parameter_definition=BuiltInParameter.VIEW_PHASE,
                    parameter_value=room_spatial.phase_object.Id
                )
                action_return_value.append_message("Setting phase for view two: {} with status {}".format(result_phase.message, result_phase.status))

                result_phase = set_builtin_parameter_without_transaction_wrapper_by_name(
                    element=view_three,
                    parameter_definition=BuiltInParameter.VIEW_PHASE,
                    parameter_value=room_spatial.phase_object.Id
                )

                action_return_value.append_message("Setting phase for view three: {} with status {}".format(result_phase.message, result_phase.status))

                # do I need to check 
                # - elevation depth - only want to look to the wall not beyond it
                # - elevation line location ( 1m out from wall max )

                # return the created views (and reset the return value)
                action_return_value.result = [view_zero, view_one, view_two, view_three]
               
            except Exception as e:
                action_return_value.update_sep(False, "An exception occured: {}".format(e))
            
            return action_return_value

        # execute the action
        # define failure handling for the transaction ( roll back on any warnings or errors )
        failure_handling_settings = FailureHandlingConfig(
            roll_back_on_warning=True,
            print_warnings=False,
            roll_back_on_error=True,
            print_errors=False,
        )
       
        # set up the transaction
        trans = Transaction(doc, "creating view elevation(s) {}")

        # execute the transaction with failure handling
        result_transaction = in_transaction_with_failure_handling(
            transaction=trans,
            action=action,
            failure_config=failure_handling_settings,
        )

        # update the return value with the result of the transaction
        return_value.update(result_transaction)

    except Exception as e:
        return_value.update_sep(False, "An exception occured: {}".format(e))

    return return_value

def create_3D_view_of_room(doc, room):
    return_value = Result()

    try:
        pass
    except Exception as e:
        return_value.update_sep(False, "An exception occured: {}".format(e))

    return return_value

def create_schedule_for_room_content(doc, room):
    return_value = Result()

    try:
        pass
    except Exception as e:
        return_value.update_sep(False, "An exception occured: {}".format(e))

    return return_value

def create_views(doc, room, view_plan_type, view_elevation_type):

    return_value = Result()

    views_created = {}

    try:
        return_value.append_message("Creating plan view...")
        # create plan view
        create_plan_view_status = create_plan_view_from_room(doc=doc, room=room, view_plan_type=view_plan_type)
        return_value.update(create_plan_view_status)
        # store the created view
        if(create_plan_view_status.status):
            views_created[DataViewPortTypeNames.FLOOR_PLAN] = create_plan_view_status.result

        # create elevations
        return_value.append_message("Creating elevation views...")
        create_elevation_views_status = create_elevation_views_in_room(
            doc=doc, 
            room=room, 
            view_plan=views_created[DataViewPortTypeNames.FLOOR_PLAN][0],
            view_elevation_type=view_elevation_type,
            scale=50)
        
        return_value.update(create_elevation_views_status)
        # store the created views
        if(create_elevation_views_status.status):
            views_created[DataViewPortTypeNames.ELEVATION] = create_elevation_views_status.result

        # create 3D view
        create_3D_view_status = create_3D_view_of_room(doc=doc, room=room)
        return_value.update(create_3D_view_status)
        # store the created view
        if(create_3D_view_status.status):
            views_created[DataViewPortTypeNames.THREE_D] = create_3D_view_status.result

        # create schedule
        create_schedule_status = create_schedule_for_room_content(doc=doc, room=room)
        return_value.update(create_schedule_status)
        # store the created view
        if(create_schedule_status.status):
            views_created[DataViewPortTypeNames.SCHEDULE] = create_schedule_status.result

        # overwrite any objects the return value object will ahve at this point
        # keep to the standard format of a list
        return_value.result = [views_created]


    except Exception as e:
        return_value.update_sep(False, "Creating views of room failed with exception: {}".format(e))

    return return_value