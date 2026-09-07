"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sample showing how to find which items (furniture, equipment, etc.) belong to which rooms.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module:

    - reads room and item data instances from a json file
    - matches each item to its room(s) using the room ids already stored on the item
      (populated during export via Revit's phase-aware room lookup)
    - reports all rooms and any associated item(s) found

No shapely / numpy dependency - room membership is resolved by id, not by geometry.

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
from duHast.Data.Objects.Collectors import data_item as di
from duHast.Data.Objects.Collectors import data_room as dr
from duHast.Data.Utils import data_import as dReader

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
    - value: a tuple of two lists - (rooms, items) on that level

    :param data_reader: A data reader class instance.
    :type data_reader: :class:`.ReadDataFromFile`

    :return: A dictionary keyed by level name. Each value is a tuple:
        index 0 = list of :class:`.DataRoom`, index 1 = list of :class:`.DataItem`.
    :rtype: dict{str: (list[:class:`.DataRoom`], list[:class:`.DataItem`])}
    """

    dic = {}
    for d_object in data_reader.data:
        if d_object.level.name not in dic:
            rooms_by_level = data_reader.get_data_by_level_and_data_type(
                d_object.level.name, dr.DataRoom.data_type
            )
            items_by_level = data_reader.get_data_by_level_and_data_type(
                d_object.level.name, di.DataItem.data_type
            )
            dic[d_object.level.name] = (rooms_by_level, items_by_level)
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


def _match_items_to_rooms(data_objects):
    """
    Matches each item to its room(s) using the room ids stored on the item.

    Each matched :class:`.DataItem` instance is appended to the
    ``associated_elements`` list of the corresponding :class:`.DataRoom`.

    An item whose ``rooms`` list contains more than one id (e.g. when phasing is
    applied) will be added to each matching room.

    .. note::
        Mutates ``data_objects`` in place.

    :param data_objects: Dictionary keyed by level name holding (rooms, items) tuples.
    :type data_objects: dict{str: (list[:class:`.DataRoom`], list[:class:`.DataItem`])}

    :return: Result instance with status and messages.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    for level_name in data_objects:
        rooms = data_objects[level_name][0]
        items = data_objects[level_name][1]

        if not rooms:
            return_value.append_message(
                "No rooms found for level: {}".format(level_name)
            )
            continue

        if not items:
            return_value.append_message(
                "No items found for level: {}".format(level_name)
            )
            continue

        # build a fast room-id lookup for this level
        room_by_id = {r.instance_properties.id: r for r in rooms}

        for item in items:
            if not item.rooms:
                return_value.append_message(
                    "Item {} has no room ids assigned. Skipped.".format(
                        item.instance_properties.id
                    )
                )
                continue

            matched = False
            for room_id in item.rooms:
                if room_id in room_by_id:
                    room_by_id[room_id].associated_elements.append(item)
                    return_value.append_message(
                        "Added item {} to room {}".format(
                            item.instance_properties.id, room_id
                        )
                    )
                    matched = True
                else:
                    return_value.append_message(
                        "Item {} references room id {} which was not found on level {}.".format(
                            item.instance_properties.id, room_id, level_name
                        )
                    )

            if not matched:
                return_value.append_message(
                    "Item {} could not be matched to any room on level {}.".format(
                        item.instance_properties.id, level_name
                    )
                )

    return return_value


def _convert_object_data_into_report_data(
    dic_object,
    room_instance_property_keys,
    item_type_property_keys,
    item_instance_property_keys,
):
    """
    Converts a dictionary of DataRoom objects (with associated items) into a
    list of rows ready to be written to a CSV file.

    One row is written per associated item per room.

    :param dic_object: Dictionary keyed by level name.
    :type dic_object: dict{str: (list[:class:`.DataRoom`], list[:class:`.DataItem`])}
    :param room_instance_property_keys: Room instance parameter names to include.
    :type room_instance_property_keys: list[str]
    :param item_type_property_keys: Item type parameter names to include.
    :type item_type_property_keys: list[str]
    :param item_instance_property_keys: Item instance parameter names to include.
    :type item_instance_property_keys: list[str]

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

            for associated_element in room.associated_elements:
                if associated_element.data_type == di.DataItem.data_type:
                    # fixed item columns
                    item_row = [
                        associated_element.level.name,
                        associated_element.revit_model.name,
                        str(associated_element.instance_properties.id),
                        associated_element.design_set_and_option.set_name,
                        associated_element.design_set_and_option.option_name,
                        str(associated_element.design_set_and_option.is_primary),
                    ]
                    # custom item columns
                    item_row = item_row + _get_property_values_as_list(
                        associated_element.type_properties.properties,
                        item_type_property_keys,
                    )
                    item_row = item_row + _get_property_values_as_list(
                        associated_element.instance_properties.properties,
                        item_instance_property_keys,
                    )
                    data.append(room_row + item_row)

    return data


# --------------- main functions ------------------


def write_data_to_file(
    data,
    output_file_path,
    room_instance_property_keys=["Number", "Name"],
    item_type_property_keys=["Type Mark"],
    item_instance_property_keys=[],
):
    """
    Writes room + associated item data to a CSV file.

    The report contains one row per associated item per room.

    :param data: Dictionary keyed by level name, values are (rooms, items) tuples.
    :type data: dict{str: (list[:class:`.DataRoom`], list[:class:`.DataItem`])}
    :param output_file_path: Fully qualified path for the output CSV file.
    :type output_file_path: str
    :param room_instance_property_keys: Room instance parameter names to report.
        Defaults to ``['Number', 'Name']``.
    :type room_instance_property_keys: list[str], optional
    :param item_type_property_keys: Item type parameter names to report.
        Defaults to ``['Type Mark']``.
    :type item_type_property_keys: list[str], optional
    :param item_instance_property_keys: Item instance parameter names to report.
        Defaults to ``[]``.
    :type item_instance_property_keys: list[str], optional

    :return: Result instance with status and messages.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        converted_data = _convert_object_data_into_report_data(
            data,
            room_instance_property_keys,
            item_type_property_keys,
            item_instance_property_keys,
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
            "item level name",
            "item model name",
            "item revit id",
            "item design set name",
            "item design option name",
            "item design option is primary",
        ]
        data_header = data_header + item_type_property_keys + item_instance_property_keys

        return_value.update(
            write_report_data_as_csv(output_file_path, data_header, converted_data)
        )

    except Exception as e:
        return_value.update_sep(
            False, "Failed to write report with exception {}".format(e)
        )
    return return_value


def get_items_by_room(data_source_path):
    """
    Reads Revit data from file and matches each item to the room(s) it belongs to
    using the room ids already stored on the item.

    Any matched item is added to that room's ``associated_elements`` list.

    :param data_source_path: Fully qualified path to a json file containing
        :class:`.DataRoom` and :class:`.DataItem` objects.
    :type data_source_path: str

    :return:
        Result class instance.

        - result.status: False if an exception occurred, otherwise True.
        - result.message: processing messages.
        - result.result: dictionary keyed by level name, values are
          (rooms, items) tuples with rooms populated with associated items.

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
                    "{}: {} entries, Rooms: {}, Items: {}".format(
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

    return_value.update(_match_items_to_rooms(data_objects))

    return_value.result = data_objects
    return return_value
