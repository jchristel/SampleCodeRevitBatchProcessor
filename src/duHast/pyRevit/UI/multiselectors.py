"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module to provide pyRevit multiselectors for some standard Revit elements.
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

from collections import defaultdict
from duHast.Revit.Levels.Objects.LevelBaseObject import LevelBaseObj
from pyrevit import forms
from duHast.Revit.Rooms.rooms import get_all_placed_rooms
from duHast.Revit.Rooms.room_common_parameters import get_room_number
from duHast.Revit.Rooms.Objects.RoomBaseObject import RoomBaseObj
from duHast.Revit.Levels.levels import get_levels_list_ascending

# ---------------------------------------------------------------------------- Rooms


def room_selector(rvt_doc, multiple=True):
    """
    pyRevit Select from list UI object to pick room or rooms.
    :param rvt_doc: Revit Document
    :type rvt_doc: Document
    :param multiple: Allow multiple selection
    :type multiple: bool
    :return: Room or list of rooms
    :rtype: Room or list[Room]
    """
    all_rooms = get_all_placed_rooms(rvt_doc)
    sorted_rooms = sorted(all_rooms, key=lambda rm: str(get_room_number(rm)))
    rooms_for_ui = defaultdict(list)

    for rm in sorted_rooms:
        obj = RoomBaseObj(rvt_doc, rm)
        rooms_for_ui[obj.level.Name].append(obj)
        rooms_for_ui["All levels"].append(obj)

    btn_name = "Select Rooms" if multiple else "Select Room"

    select_room_ui = forms.SelectFromList.show(
        rooms_for_ui,
        multiselect=multiple,
        group_selector_title="Filter by level:",
        name_attr="number_name_comb",
        button_name=btn_name,
    )

    if select_room_ui:
        if multiple:
            return [x.room for x in select_room_ui]
        else:
            return select_room_ui.room

    return None


def pick_room(rvt_doc):
    """
    PyRevit multiselector to pick a single room.
    """
    return room_selector(rvt_doc, multiple=False)


def pick_rooms(rvt_doc):
    """
    PyRevit multiselector to pick multiple rooms.
    """
    return room_selector(rvt_doc, multiple=True)


# ---------------------------------------------------------------------------- Levels


def level_selector(rvt_doc, multiple=True):
    lvls = get_levels_list_ascending(rvt_doc)
    lvl_objs = [LevelBaseObj(lvl) for lvl in lvls]
    btn_name = "Select Levels" if multiple else "Select Level"

    select_level_ui = forms.SelectFromList.show(
        lvl_objs,
        multiselect=multiple,
        name_attr="name_elev_comb",
        button_name=btn_name,
    )

    if select_level_ui:
        if multiple:
            lvl_list = [x.level for x in select_level_ui]
        else:
            lvl_list = select_level_ui.level

        return lvl_list

    return None


def pick_level(rvt_doc):
    """
    PyRevit multiselector to pick a single level.
    """
    return level_selector(rvt_doc, multiple=False)


def pick_levels(rvt_doc):
    """
    PyRevit multiselector to pick multiple levels.
    """
    return level_selector(rvt_doc, multiple=True)
