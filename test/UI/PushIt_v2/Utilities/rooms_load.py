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


from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_csv import read_csv_file

from PushIt_v2.Models.Room import Room
from PushIt_v2.Models.RoomId import RoomID
from PushIt_v2.Models.RoomProperty import RoomProperty
from PushIt_v2.Objects.CSVColumnsMapper import CSVColumnMapper
from PushIt_v2.Utilities.property_names import DEFAULT_PROPERTIES

def load_rooms_from_file(file_path):
    """
    Loads rooms data from a file.

    :param file_path: path to the file to load rooms from.
    :type file_path: str

    :return:
        Result class instance.

        - result.status (bool) True if file was read and converted into rooms without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be the rooms list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    try:

        return_value.append_message("Loading rooms from file: {}".format(file_path))

        # read the file
        read_result = read_csv_file(file_path)
        if read_result.status == False:
            return_value.update(read_result)
            return return_value

        data_rows = read_result.result
        return_value.append_message("Found {} rows.".format(len(data_rows)))
        print("Found {} rows.".format(len(data_rows)))

        # do some sanity checks...
        if len(data_rows) == 0:
            return_value.update_sep(False, "Error: No data found in file.")
            return return_value

        if len(data_rows[0]) < len(DEFAULT_PROPERTIES):
            return_value.update_sep(False, "Error: Not enough columns found in file. Expected: {}, Found: {}".format(len(DEFAULT_PROPERTIES), len(data_rows[0])))
            return return_value

        if len(data_rows) <= 2:
            return_value.update_sep(False, "Error: Not enough rows found in file. Expected at least 3, Found: {}".format(len(data_rows)))

        # create a list of rooms from the data from row 3 onwards
        rooms_list = []

        # store the required row length for each row
        row_length_required = len(data_rows[0])
        # set up a counter for the rows
        row_counter = 2

        # iterate over the rows and create rooms
        for row in data_rows[2:]:

            # check the length of the row
            if len(row) != row_length_required:
                return_value.update_sep(
                    False,
                    "Error: Row {} length mismatch. Required: {}, Found: {}".format(
                        row_counter, row_length_required, len(row)
                    ),
                )
                return return_value

            # create a room object
            # room id
            id_room = RoomID(
                id=row[CSVColumnMapper.COLUMN_ROOM_ID.value],
                parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][
                    CSVColumnMapper.COLUMN_ROOM_ID.value
                ],
            )
            return_value.append_message("...Room ID: {}".format(id_room.id))
            
            # area briefed
            area_room_briefed = RoomProperty(
                name="{}".format(
                    data_rows[CSVColumnMapper.ROW_PROPERTY_DESCRIPTION.value][
                        CSVColumnMapper.COLUMN_AREA_BRIEFED.value
                    ]
                ),
                value=row[CSVColumnMapper.COLUMN_AREA_BRIEFED.value],
                parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][
                    CSVColumnMapper.COLUMN_AREA_BRIEFED.value
                ],
            )
            return_value.append_message(
                "...Area briefed: {}".format(area_room_briefed.value)
            )

            # area designed
            area_room_designed = RoomProperty(
                name="{}".format(
                    data_rows[CSVColumnMapper.ROW_PROPERTY_DESCRIPTION.value][
                        CSVColumnMapper.COLUMN_AREA_DESIGNED.value
                    ]
                ),
                value=row[CSVColumnMapper.COLUMN_AREA_DESIGNED.value],
                parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][
                    CSVColumnMapper.COLUMN_AREA_DESIGNED.value
                ],
            )
            return_value.append_message(
                "...Area designed: {}".format(area_room_designed.value)
            )

            # room name short
            room_name_short = RoomProperty(
                name="{}".format(
                    data_rows[CSVColumnMapper.ROW_PROPERTY_DESCRIPTION.value][
                        CSVColumnMapper.COLUMN_ROOM_NAME_SHORT.value
                    ]
                ),
                value=row[CSVColumnMapper.COLUMN_ROOM_NAME_SHORT.value],
                parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][
                    CSVColumnMapper.COLUMN_ROOM_NAME_SHORT.value
                ],
            )

            # sub department
            sub_department = RoomProperty(
                name="{}".format(
                    data_rows[CSVColumnMapper.ROW_PROPERTY_DESCRIPTION.value][
                        CSVColumnMapper.COLUMN_SUB_DEPARTMENT.value
                    ]
                ),
                value=row[CSVColumnMapper.COLUMN_SUB_DEPARTMENT.value],
                parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][
                    CSVColumnMapper.COLUMN_SUB_DEPARTMENT.value
                ],
            )

            # department
            department = RoomProperty(
                name="{}".format(
                    data_rows[CSVColumnMapper.ROW_PROPERTY_DESCRIPTION.value][
                        CSVColumnMapper.COLUMN_DEPARTMENT.value
                    ]
                ),
                value=row[CSVColumnMapper.COLUMN_DEPARTMENT.value],
                parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][
                    CSVColumnMapper.COLUMN_DEPARTMENT.value
                ],
            )

            # create a room object
            room = Room(
                id=id_room,
                area_briefed=area_room_briefed,
                area_designed=area_room_designed,
                room_name_short=room_name_short,
                sub_department=sub_department,
                department=department,
            )

            # get additional data from the row
            if len(row) > 3:

                for i in range(len(DEFAULT_PROPERTIES), len(row)):
                    # create a property object
                    prop = RoomProperty(
                        name="{}".format(
                            data_rows[CSVColumnMapper.ROW_PROPERTY_DESCRIPTION.value][i]
                        ),
                        value=row[i],
                        parameter_guid=data_rows[
                            CSVColumnMapper.ROW_PARAMETER_GUID.value
                        ][i],
                    )
                    return_value.append_message("...Property: {}".format(prop))
                    # add it to room
                    room.add_property(prop)

            # add the room to the list
            rooms_list.append(room)

            # increment the row counter
            row_counter += 1

        # store the list of rooms in the return value
        return_value.result = rooms_list

    except Exception as e:
        return_value.update_sep(False, "Error: {}".format(e))
        print("exception in room loader: {}".format(e))

    print("Found {} rooms.".format(len(return_value.result)))
    return return_value
