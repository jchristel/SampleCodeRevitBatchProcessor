"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around creating Revit doors.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from Autodesk.Revit.DB import (
    Element,
)

from Autodesk.Revit.DB.Structure import (
    StructuralType,
)


def door_in_basic_wall(doc, door_symbol, door_location, wall, wall_level):
    return_value = res.Result()
    try:
        # the symbol needs to be activated before using it
        # https://thebuildingcoder.typepad.com/blog/2014/08/activate-your-family-symbol-before-using-it.html
        if not door_symbol.IsActive:
            return_value.append_message(
                "Activating symbol {}".format(Element.Name.GetValue(door_symbol))
            )
            door_symbol.Activate()
            doc.Regenerate()

        # create door instance in wall
        door_instance = doc.Create.NewFamilyInstance(
            door_location,
            door_symbol,
            wall,
            wall_level,
            StructuralType.NonStructural,
        )

        # return the newly created door instance
        return_value.result.append(door_instance)

        # update messages
        return_value.append_message(
            "Added door {} to wall.".format(Element.Name.GetValue(door_symbol))
        )
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to create door with exception: {}".format(
                e,
            ),
        )

        return return_value
