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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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
