"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Find all ceilings intersecting with rooms in a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to use DataSamples name space to find all ceilings intersecting a room in Revit.

- Requires:

    - python >3.8
    - shapely and numpy installed
    - An export of room and ceiling data from the model

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

# ---------------------------------
# default path locations
# ---------------------------------

# add library to du hast( if not on path )
import sys

DU_HAST_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
sys.path += [DU_HAST_PATH]

# import module processing ceilings and rooms in a model
from duHast.Data import process_ceilings_to_rooms as magic

# files required
# data previously exported from a given model
# refer to flow ....
data_in = r"path\to\your\jsonFromModel.json"

# location of out put file
report_out = r"path\to\your\ceilingsByRoom.csv"

# read data from file
print("Getting data from {}".format(data_in))
ceilings_by_room = magic.get_ceilings_by_room(data_in)
print(ceilings_by_room.message)

if ceilings_by_room.status:
    print("Writing data to file...")
    data_to_file = magic.write_data_to_file(
        ceilings_by_room.result,
        report_out,
        room_instance_property_keys=[
            "Number",
            "Name",
        ],  # export the following room instance properties: name and number
        ceiling_type_property_keys=[
            "Type Mark"
        ],  # export the following ceiling type properties: Type Mark
        ceiling_instance_property_keys=["Height Offset From Level"],
    )  # export the following ceiling instance properties: Height Offset From Level

    print(data_to_file.message)
else:
    print("Did not proceed due to error in reading data file: {}".format(ceilings_by_room.message))
