"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sample showing how to find which floors are in which rooms.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module requires python >3.9 due to dependencies:

    - numpy
    - shapely

This module:

    - collects floor and room data instances by level (assumes a floor is always modelled within the room it belongs to)
    - converts room and floor outlines to shapely polygons
    - tests for intersection of all floors on a given level with all rooms on a given level
    - stores any intersections found (checks how much area is intersecting; if too small it is assumed not an intended intersection)
    - reports all rooms and any associated floor(s) found

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
from duHast.Data.Objects.Collectors import data_floor as df
from duHast.Data.Objects.Collectors import data_room as dr
from duHast.Data.Objects.Collectors.data_floor_in_room import DataFloorInRoom
from duHast.Data.Utils import data_import as dReader
from duHast.Data import data_to_shapely as dToS

try:
    from duHast.Utilities.files_csv import write_report_data_as_csv
except ImportError as e:
    raise ImportError(
        "This module requires the duHast.Utilities.files_csv module to be available. Error: {}".format(
            e
        )
    )


# --------------- reading data ------------------


def _read_data(file_path):
    """
    Reads a json-formatted data file into a data reader instance.

    :param file_path: Fully qualified path to json formatted data file.
    :type file_path: str

    :return: A file data reader instance.
    :rtype: :class:`.ReadDataFromFile`
    """

    data_reader = dReader.ReadDataFromFile(file_path)
    data_reader.load_data()
    return data_reader


# --------------- data processing ------------------


def _build_dictionary_by_level_and_data_type(data_reader):
    """
    Returns a dictionary where:

    - key: level name
    - value: a tuple of two lists - (rooms, floors) on that level

    :param data_reader: A data reader class instance.
    :type data_reader: :class:`.ReadDataFromFile`

    :return: A dictionary keyed by level name. Each value is a tuple:
        index 0 = list of :class:`.DataRoom`, index 1 = list of :class:`.DataFloor`.
    :rtype: dict{str: (list[:class:`.DataRoom`], list[:class:`.DataFloor`])}
    """

    dic = {}
    for d_object in data_reader.data:
        if d_object.level.name not in dic:
            rooms_by_level = data_reader.get_data_by_level_and_data_type(
                d_object.level.name, dr.DataRoom.data_type
            )
            floors_by_level = data_reader.get_data_by_level_and_data_type(
                d_object.level.name, df.DataFloor.data_type
            )
            dic[d_object.level.name] = (rooms_by_level, floors_by_level)
    return dic


def _get_property_values_as_list(properties, property_keys):
    """
    Returns a list of property values in the order defined by property_keys.

    Looks up each key by name against a list of :class:`.DataProperty` objects.
    Returns the string ``"null"`` for any key not found.

    :param properties: A list of DataProperty instances.
    :type properties: list[:class:`.DataProperty`]
    :param property_keys: Names of the properties to extract, in order.
    :type property_keys: list[str]

    :return: Extracted values as strings, one entry per key.
    :rtype: list[str]
    """

    props_dict = {p.name: p.value for p in properties}
    values = []
    for property_key in property_keys:
        if property_key in props_dict:
            values.append(str(props_dict[property_key]))
        else:
            values.append("null")
    return values


def _convert_object_data_into_report_data(
    dic_object,
    room_instance_property_keys,
    floor_type_property_keys,
    floor_instance_property_keys,
):
    """
    Converts a dictionary of DataRoom objects (with associated floors) into a
    list of rows ready to be written to a CSV file.

    One row is written per associated floor per room.

    :param dic_object: Dictionary keyed by level name.
    :type dic_object: dict{str: (list[:class:`.DataRoom`], list[:class:`.DataFloor`])}
    :param room_instance_property_keys: Room instance parameter names to include.
    :type room_instance_property_keys: list[str]
    :param floor_type_property_keys: Floor type parameter names to include.
    :type floor_type_property_keys: list[str]
    :param floor_instance_property_keys: Floor instance parameter names to include.
    :type floor_instance_property_keys: list[str]

    :return: List of rows (each row is a list of strings).
    :rtype: list[list[str]]
    """

    data = []
    for level_name in dic_object:
        for room in dic_object[level_name][0]:
            # fixed room columns
            room_row = [
                room.level.name,
                room.revit_model.name,
                str(room.instance_properties.id),
                room.design_set_and_option.set_name,
                room.design_set_and_option.option_name,
                str(room.design_set_and_option.is_primary),
            ]
            # custom room columns
            room_row = room_row + _get_property_values_as_list(
                room.instance_properties.properties, room_instance_property_keys
            )

            for floor_in_room in room.floors:
                floor = floor_in_room.floor
                # fixed floor columns
                floor_row = [
                    floor.level.name,
                    floor.revit_model.name,
                    str(floor.instance_properties.id),
                    floor.design_set_and_option.set_name,
                    floor.design_set_and_option.option_name,
                    str(floor.design_set_and_option.is_primary),
                ]
                # custom floor columns
                floor_row = floor_row + _get_property_values_as_list(
                    floor.type_properties.properties,
                    floor_type_property_keys,
                )
                floor_row = floor_row + _get_property_values_as_list(
                    floor.instance_properties.properties,
                    floor_instance_property_keys,
                )
                floor_row.append(str(floor_in_room.area))
                data.append(room_row + floor_row)
    return data


def _intersect_floor_vs_room(
    floor_poly_id,
    floor_polygon,
    room_poly_id,
    room_polygon,
    data_objects,
    level_name,
):
    """
    Intersection check of a floor polygon against a room polygon.

    If the overlap area exceeds 0.1 % of the room area the floor object is
    appended to the room's ``associated_elements`` list.

    .. note::
        Mutates ``data_objects`` in place.

    :param floor_poly_id: Revit element id of the floor.
    :type floor_poly_id: int
    :param floor_polygon: Shapely polygon representing the floor.
    :type floor_polygon: shapely.geometry.Polygon
    :param room_poly_id: Revit element id of the room.
    :type room_poly_id: int
    :param room_polygon: Shapely polygon representing the room.
    :type room_polygon: shapely.geometry.Polygon
    :param data_objects: Dictionary keyed by level name holding (rooms, floors) tuples.
    :type data_objects: dict{str: (list[:class:`.DataRoom`], list[:class:`.DataFloor`])}
    :param level_name: The level name being processed.
    :type level_name: str

    :return: Result instance with status and messages.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        if floor_polygon.is_empty or room_polygon.is_empty:
            raise Exception(
                "Floor {} or room {} polygon is empty. Ignored!".format(
                    floor_poly_id, room_poly_id
                )
            )

        if floor_polygon.intersects(room_polygon):
            area_intersection_percentage = (
                floor_polygon.intersection(room_polygon).area / room_polygon.area
            ) * 100

            if area_intersection_percentage < 0.1:
                return_value.append_message(
                    "Floor {} has an overlap of {} % with room {}. Ignored!".format(
                        floor_poly_id,
                        area_intersection_percentage,
                        room_poly_id,
                    )
                )
            else:
                data_object_room = list(
                    filter(
                        lambda x: (x.instance_properties.id == room_poly_id),
                        data_objects[level_name][0],
                    )
                )[0]
                data_object_floor = list(
                    filter(
                        lambda x: (x.instance_properties.id == floor_poly_id),
                        data_objects[level_name][1],
                    )
                )[0]
                # wrap the floor and its specific intersection area in a typed
                # container so the same floor can appear in multiple rooms with
                # the correct area for each (avoids the overwrite-on-re-entry bug)
                floor_in_room = DataFloorInRoom()
                floor_in_room.floor = data_object_floor
                floor_in_room.area = (
                    floor_polygon.intersection(room_polygon).area * 304.8 * 304.8
                )
                data_object_room.floors.append(floor_in_room)
                return_value.append_message(
                    "Added floor {} to room {}".format(floor_poly_id, room_poly_id)
                )

    except Exception as e:
        data_object_room = list(
            filter(
                lambda x: (x.instance_properties.id == room_poly_id),
                data_objects[level_name][0],
            )
        )[0]
        room_name = "unknown"
        room_number = "unknown"
        room_id = "unknown"
        if data_object_room:
            props = {p.name: p.value for p in data_object_room.instance_properties.properties}
            room_name = props.get("Name", "unknown")
            room_number = props.get("Number", "unknown")
            room_id = data_object_room.instance_properties.id

        data_object_floor = list(
            filter(
                lambda x: (x.instance_properties.id == floor_poly_id),
                data_objects[level_name][1],
            )
        )[0]
        floor_id = "unknown"
        if data_object_floor:
            floor_id = data_object_floor.instance_properties.id

        return_value.append_message(
            "Exception: {} \noffending room: name: {}, number: {}, id: {} "
            "\n...is valid polygon: {}\n...is empty polygon: {}"
            "\noffending floor id: {} "
            "\n...is valid polygon: {}\n...is empty polygon: {}".format(
                e,
                room_name,
                room_number,
                room_id,
                room_polygon.is_valid,
                room_polygon.is_empty,
                floor_id,
                floor_polygon.is_valid,
                floor_polygon.is_empty,
            )
        )

    return return_value


# --------------- main functions ------------------


def write_data_to_file(
    data,
    output_file_path,
    room_instance_property_keys=["Number", "Name"],
    floor_type_property_keys=["Type Mark"],
    floor_instance_property_keys=["Height Offset From Level"],
):
    """
    Writes room + associated floor data to a CSV file.

    The report contains one row per associated floor per room.

    :param data: Dictionary keyed by level name, values are (rooms, floors) tuples.
    :type data: dict{str: (list[:class:`.DataRoom`], list[:class:`.DataFloor`])}
    :param output_file_path: Fully qualified path for the output CSV file.
    :type output_file_path: str
    :param room_instance_property_keys: Room instance parameter names to report.
        Defaults to ``['Number', 'Name']``.
    :type room_instance_property_keys: list[str], optional
    :param floor_type_property_keys: Floor type parameter names to report.
        Defaults to ``['Type Mark']``.
    :type floor_type_property_keys: list[str], optional
    :param floor_instance_property_keys: Floor instance parameter names to report.
        Defaults to ``['Height Offset From Level']``.
    :type floor_instance_property_keys: list[str], optional

    :return: Result instance with status and messages.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        converted_data = _convert_object_data_into_report_data(
            data,
            room_instance_property_keys,
            floor_type_property_keys,
            floor_instance_property_keys,
        )

        # build header
        data_header = [
            "room level name",
            "room model name",
            "room revit id",
            "room design set name",
            "room design option name",
            "room design option is primary",
        ]
        data_header = data_header + room_instance_property_keys
        data_header = data_header + [
            "floor level name",
            "floor model name",
            "floor revit id",
            "floor design set name",
            "floor design option name",
            "floor design option is primary",
        ]
        data_header = (
            data_header + floor_type_property_keys + floor_instance_property_keys
            + ["floor intersection area mm2"]
        )

        return_value.update(
            write_report_data_as_csv(output_file_path, data_header, converted_data)
        )

    except Exception as e:
        return_value.update_sep(
            False, "Failed to write report with exception {}".format(e)
        )
    return return_value


def get_floors_by_room(data_source_path):
    """
    Reads Revit data from file and runs an intersection check of each floor on a
    level with each room on the same level.

    Any floor whose polygon overlaps a room by more than 0.1 % of the room area
    is added to that room's ``associated_elements`` list.

    :param data_source_path: Fully qualified path to a json file containing
        :class:`.DataRoom` and :class:`.DataFloor` objects.
    :type data_source_path: str

    :return:
        Result class instance.

        - result.status: False if an exception occurred, otherwise True.
        - result.message: processing messages.
        - result.result: dictionary keyed by level name, values are
          (rooms, floors) tuples with rooms populated with associated floors.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    data_reader = _read_data(data_source_path)
    if len(data_reader.data) == 0:
        return_value.update_sep(
            False, "File: {} did not contain any valid data.".format(data_source_path)
        )
        return return_value

    print("\n".join(data_reader.debug_messages))

    data_objects = _build_dictionary_by_level_and_data_type(data_reader)
    return_value.append_message(
        "Data loaded contains {} levels: \n{}".format(
            len(data_objects),
            "...\n".join(
                [
                    "{}: {} entries, Rooms: {}, Floors: {}".format(
                        key,
                        len(value[0]) + len(value[1]),
                        len(value[0]),
                        len(value[1]),
                    )
                    for key, value in data_objects.items()
                ]
            ),
        )
    )

    for level_name in data_objects:
        if len(data_objects[level_name][0]) > 0:
            if len(data_objects[level_name][1]) > 0:
                # convert geometry to shapely polygons
                room_polygons = dToS.get_shapely_polygons_from_geo_object(
                    data_objects[level_name][0], dr.DataRoom.data_type
                )
                floor_polygons = dToS.get_shapely_polygons_from_geo_object(
                    data_objects[level_name][1], df.DataFloor.data_type
                )

                # intersection check: each room vs each floor
                for room_poly_id, room_poly_list in room_polygons.items():
                    if len(room_poly_list) > 0:
                        for room_polygon in room_poly_list:
                            for floor_poly_id, floor_poly_list in floor_polygons.items():
                                for floor_polygon in floor_poly_list:
                                    return_value.update(
                                        _intersect_floor_vs_room(
                                            floor_poly_id,
                                            floor_polygon,
                                            room_poly_id,
                                            room_polygon,
                                            data_objects,
                                            level_name,
                                        )
                                    )
                    else:
                        return_value.append_message(
                            "Room with id {} has no valid polygon.".format(room_poly_id)
                        )
            else:
                return_value.append_message(
                    "No floors found for level: {}".format(
                        data_objects[level_name][0][0].level.name
                    )
                )
        else:
            return_value.append_message(
                "No rooms found for level: {}".format(level_name)
            )

    return_value.result = data_objects
    return return_value
