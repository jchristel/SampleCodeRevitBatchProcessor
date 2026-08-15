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

from System import Int64 # revit element Id expects 64 bit integer

import csv

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.console_output import print_header#, print_error
from duHast.pyRevit.UI.ui_element_selection import get_element_selection_from_user
from duHast.Revit.Rooms.rooms import get_all_rooms
from duHast.Revit.Rooms.room_common_parameters import (
    get_room_name,
    get_room_num_name_comb,
    get_room_level,
    get_room_level, 
    get_room_phase,
    get_room_from_element,
)
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value
from duHast.Revit.Common.phases import get_name_to_phase_dict
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm
from duHast.Utilities.files_csv import write_report_data_as_csv

from rooms.wall_utils import (
    get_wall_segments_of_rooms,  
    #build_segment_and_room_to_wall_id,
    #update_walls_with_room_number_of_longest_segment,
    #get_wall_parameters,
    #get_wall_parameter_by_id,
)

from rooms.family_utils import get_window_families_by_host_id, window_area_instance, window_area_type

from Autodesk.Revit.DB import BuiltInParameter, Element, ElementId, SharedParameterElement

DEBUG = False

OPENING_FAMILY_NAMEs = ["WDW_Generic_Window Opening", "WDW_Generic_Window Opening_Instance"]

WINDOW_AREA_CALCULATION_MAPPER = {
    "WDW_Generic_Window Opening": window_area_type,
    "WDW_Generic_Window Opening_Instance": window_area_instance,
}

EXTERNAL_WALL_TYPE_NAMES = ["P43.E_(125)_PB13_S92 (Insulation) - External Lining"]



# the phase the rooms of interest are in
PHASE_NAME = "Project Scope"

REPORT_HEADER = [
    "room name",
    "room number", 
    "room area (sqm)",
    "external wall area (sqm)",
    "external window area combined (sqm)",
    "room level", 
    "room phase", 
    "room height (mm)", 
    "external wall type name", 
    "external window fam name(s)", 
    ]
   

def get_rooms_area(room):

    # returns the area in project units!!
    area_param = get_built_in_parameter_value(
        element=room, built_in_parameter_def=BuiltInParameter.ROOM_AREA
    )

    # that value may contain a unit type separated by a space, so just get the number
    index_space = area_param.find(" ")
    if index_space != -1:
        area_param = area_param[0:index_space]

    return  area_param

def get_rooms_height(room):
    # returns the height in project units!!
    height_param = get_built_in_parameter_value(
        element=room, built_in_parameter_def=BuiltInParameter.ROOM_HEIGHT
    )
    
    return  height_param

def room_name_builder_ui(doc, element):
    """
    Builds the room name using the provided string.

    :param element: The room element.
    :type element: Autodesk.Revit.DB.Element
    :param sheet_name_string: The string to build the sheet name.
    :type sheet_name_string: str
    :return: The built sheet name.
    :rtype: str
    """

    
    room_name = []

    room_name.append(get_room_num_name_comb(element))
    room_name.append(get_room_phase(doc, element))
    room_name.append(get_room_level(doc, element))

    # join the chunks with a space and return the sheet name
    room_name_string = "_".join(room_name)

    # Build the sheet name using the provided string
    return room_name_string

def get_window_areas(doc, openings):

    area_overall = 0.0
    for opening in openings:
        family_name = opening.Symbol.Family.Name
        if family_name in WINDOW_AREA_CALCULATION_MAPPER:
            area_calculation_function = WINDOW_AREA_CALCULATION_MAPPER[family_name]
            area = area_calculation_function(doc, opening)
            area_overall = area_overall + area
    
    return str(area_overall)
    
def get_wall_area (doc, room_height_string, wall_length_in_imperial):

    if DEBUG:
        print ("Calculating wall area for height {} and length {}".format(room_height_string, wall_length_in_imperial))
    
    wall_length_in_mm = convert_imperial_feet_to_metric_mm(wall_length_in_imperial)
    area_sqmm = wall_length_in_mm * float(room_height_string)

    # convert to sqm
    area =  area_sqmm / 1e6

    if DEBUG:
        print ("Wall area calculated as {} sqm".format(area))

    return str(area)

def report_room_data(doc, wall_segments_by_room, openings_by_host):
    """
    Reports room data including wall segments and openings.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param wall_segments_by_room: Dictionary mapping room IDs to wall segments.
    :type wall_segments_by_room: dict
    :param openings_by_host: Dictionary mapping host IDs to openings.
    :type openings_by_host: dict
    :return: None
    """

    data_per_room = []

    phase_dictionary = get_name_to_phase_dict(doc)

    for walls_by_room in wall_segments_by_room:

        # get the room element
        room = doc.GetElement(ElementId(Int64(walls_by_room.room_id)))
        room_name = get_room_name(room)
        room_level = get_room_level(doc, room)
        room_phase = get_room_phase(doc, room)
        room_area = get_rooms_area(room)
        room_height = get_rooms_height(room)

        has_match = False
        # check if any wall has an opening
        for wall_segment_id, wall_length in walls_by_room.wall_id_and_length.items():
            if wall_segment_id in openings_by_host:

                # get the wall type name
                wall_instance = doc.GetElement(ElementId(Int64(wall_segment_id)))
                wall_type_name = wall_instance.Name

                # check if this is a wall of interest
                if wall_type_name not in EXTERNAL_WALL_TYPE_NAMES:
                    continue

                # set overall found a match flag
                has_match = True

                # get the openings for this wall segment (if there are any)
                openings = openings_by_host[wall_segment_id]
                print(
                    "Wall of id {} has {} opening(s).".format(
                        wall_segment_id,
                        len(openings),
                    )
                )

                # remove any openings not in room ( but hosted in wall )
                openings_in_room = []
                for opening in openings:
                    room_of_opening = get_room_from_element(phase_dictionary, opening)
                    if room_of_opening and room_of_opening.Id.Value == room.Id.Value:
                        openings_in_room.append(opening)
                        continue

                    # get the too and from room properties of the opening
                    to_room = opening.ToRoom[phase_dictionary[PHASE_NAME]]
                    from_room = opening.FromRoom[phase_dictionary[PHASE_NAME]]
                    
                    if to_room and to_room.Id.Value == room.Id.Value:
                        openings_in_room.append(opening)
                        continue
                
                    if from_room and from_room.Id.Value == room.Id.Value:
                        openings_in_room.append(opening)
                        continue
                
                if DEBUG:
                    if len(openings_in_room) ==0 :
                        print("found no windows in room {}".format(room_name))

                # get the window areas
                area_openings = 0.0
                openings_family_names = set()
                if len(openings_in_room) != 0:
                    area_openings = get_window_areas(doc, openings_in_room)

                    # build the fame name set
                    for opening in openings_in_room:
                        openings_family_names.add(opening.Symbol.Family.Name)

                # convert to string if float
                if isinstance(area_openings, float):
                    area_openings = str(area_openings)

                # built the window family names string
                family_names = "No window families in room"
                if len(openings_family_names) > 0:
                    family_names = ",".join(openings_family_names)
                
                # get the wall area
                wall_area = get_wall_area(doc, room_height, wall_length)

                
                # set up room data
                room_data = [
                    room_name, # room name
                    walls_by_room.room_number, # room number
                    room_area, # room area
                    wall_area, # external wall area
                    area_openings, # external window area combined
                    room_level, # room level
                    room_phase, # room phase
                    room_height, # room height
                    wall_type_name, # external wall type name
                    family_names, # external window fam name(s)
                ]

                data_per_room.append(room_data)
            else:
                # check if this is an external wall without openings
                # get the wall type name
                wall_instance = doc.GetElement(ElementId(Int64(wall_segment_id)))
                wall_type_name = wall_instance.Name
                if wall_type_name in EXTERNAL_WALL_TYPE_NAMES:
                    has_match = True
                    # get the wall area
                    wall_area = get_wall_area(doc, room_height, wall_length)

                    # set up room data
                    room_data = [
                        room_name, # room name
                        walls_by_room.room_number, # room number
                        room_area, # room area
                        wall_area, # external wall area
                        "0.0", # external window area combined
                        room_level, # room level
                        room_phase, # room phase
                        room_height, # room height
                        wall_type_name, # external wall type name
                        "No window families in room", # external window fam name(s)
                    ]

                    data_per_room.append(room_data)
        
        if not has_match:
            if DEBUG:
                print("No wall openings found for room {}".format(room_name))
    
    return data_per_room

    
def rooms_facade_openings_entry(doc, output, forms):
    # set up a status tracker
    return_value = Result()

    try:

        print_header("Walls by rooms.")

        # get user selected library reports

        def action(element):
            """
            Action to be performed on each element in the selection.

            :param element: The selected element.
            :type element: Autodesk.Revit.DB.Element
            """
            return  room_name_builder_ui(doc, element=element) 

        # get the user to select which sheet to export
        selected_room_ids=get_element_selection_from_user(
            doc=doc,
            forms=forms,
            element_getter=get_all_rooms,
            element_selection_description="Select rooms to find walls for",
            ui_element_name_builder= action,
        )

        # convert ids to rooms
        if not selected_room_ids or len(selected_room_ids) == 0:
            message = "No rooms selected."
            print(message)
            return_value.update_sep(False, message=message)
            return return_value

        # convert selected ids to rooms
        rooms_selected = [doc.GetElement(room_id) for room_id in selected_room_ids]

        if DEBUG:
            print("Selected rooms:")
            for room in rooms_selected:
                print(
                    " - {} : {}".format(
                        room.Id,
                        room_name_builder_ui(doc, element=room),
                    )
                )
        
        # get the openings by host id
        openings = get_window_families_by_host_id(doc, OPENING_FAMILY_NAMEs)

        if DEBUG:
            print("Found {} openings:".format(len(openings)))
            for host_id, openings_collected in openings.items():
                
                for opening in openings_collected:
                
                    print(
                        " - {} : {} : {}".format(
                            host_id,
                            opening.Symbol.Family.Name,
                            opening.Id,
                        )
                    )

        # get the wall segments per room
        #set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Processing rooms: {value} of {max_value}",
            cancellable=True,
        ) as pb:
            
            # get the room segments
            wall_segments_result = get_wall_segments_of_rooms(doc=doc, rooms= rooms_selected, pb=pb)

            # check if the result is successful
            if not wall_segments_result.status:
                return_value.update_sep(False, "Failed to get wall segments: {}".format(wall_segments_result.message))
                return return_value
            
            wall_segments_by_room = wall_segments_result.result[0]
            # give user feed back
            print("\nFound {} rooms with wall segments".format(len(wall_segments_by_room)))

            # report data
            rooms_data=report_room_data(
                doc=doc, 
                wall_segments_by_room=wall_segments_by_room, 
                openings_by_host=openings)
            
            if DEBUG:
                for room_data in rooms_data:
                    print("Room data: {}".format(room_data))
            
            # save that data to a csv
            # save report to csv file
            file_path = forms.save_file(file_ext="csv", title="Save report to csv file")

            if file_path and len(file_path) > 0:
                write_result = write_report_data_as_csv(
                    file_name=file_path,
                    header=REPORT_HEADER,
                    data=rooms_data,
                    quoting=csv.QUOTE_MINIMAL,
                )
                if write_result.status:
                    return_value.append_message(
                        "Successfully wrote families report to: {} ".format(file_path)
                    )
                else:
                    return_value.update_sep(
                        False,
                        "Failed to write families report to: {} ".format(
                            write_result.status
                        ),
                    )
                print(
                    "Finished writing report to csv file: {} with status: {}".format(
                        file_path, write_result.status
                    )
                )

    except Exception as e:
        return_value.update_sep(
            False, "Failed to find walls by room: {}".format(e)
        )
        print(e)

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value