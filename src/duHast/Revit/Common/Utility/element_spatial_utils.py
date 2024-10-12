"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of utilities for an elements spatial properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from Autodesk.Revit.DB import BuiltInParameter


def get_room_element_is_in_by_element_phase_created(element, phase_dict):
    """
    Get the room an element is in.The room phase need to match the phase the element is created in.

    :param element: The element to check
    :type element: FamilyInstance
    :param phase_dict: The dictionary of phase name to phase element id ( key is the phase name, value is the phase element id)
    :type phase_dict: dict

    :return: The room the element is in or None if no room exists or the element is not in a room
    :rtype: Room
    """

    # get the phase the element is created in
    el_phase = element.get_Parameter(BuiltInParameter.PHASE_CREATED)
    if el_phase != None:
        # get the phase name
        el_phase_name = el_phase.AsValueString()
        try:
            # get the phase element
            el_phase_elem = phase_dict[el_phase_name]
        except:
            print(
                "Element has phase created but phase not found: {}".format(
                    element.Id.IntegerValue
                )
            )
            return None
        # attempt to get the room the element is in
        # this can throw an exception if the element is created in a phase where there in no room enclosing the element
        try:
            el_room = element.get_Room(el_phase_elem)
            return el_room
        except:
            return None

    else:
        print("Element has no phase created: {}".format(element.Id.IntegerValue))
        return None
