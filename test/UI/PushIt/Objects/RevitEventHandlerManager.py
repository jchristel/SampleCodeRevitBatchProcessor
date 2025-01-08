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


"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class managing the varies event handlers set up in Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Event handlers are set up in Revit to handle the communication between the Revit API and the WPF UI.

- Push single room data from the WPF UI to Revit
- Update all revit rooms with the data from the WPF UI
- Pull data from Revit to the WPF UI (refresh the rooms list)
- wipe stale data from the rooms in the revit model

"""


from duHast.Utilities.Objects.base import Base
from duHast.Revit.UI.Objects.ExernalEventHandler import ExternalEventHandler

from Autodesk.Revit.UI import (
    ExternalEvent,
)


class RevitEventHandlerManager(Base):

    def __init__(self, revit_model):

        # ini super class to allow multi inheritance in children!
        super(RevitEventHandlerManager, self).__init__()

        # store the revit model object so we can access it later
        self._revit_model = revit_model

        # set up an external event handlers
        # push single room data from the WPF UI to Revit
        self.ex_event_handler_push_single_room = ExternalEventHandler(
            execute_at_event_raised=self.push_single_room_data_action
        )
        self.ext_event_push_single_room = ExternalEvent.Create(
            self.ex_event_handler_push_single_room
        )

        # update all revit rooms with the data from the WPF UI
        self.ex_event_handler_update_all_revit_rooms = ExternalEventHandler(
            execute_at_event_raised=self.update_all_revit_rooms_action
        )
        self.ext_event_update_all_revit_rooms = ExternalEvent.Create(
            self.ex_event_handler_update_all_revit_rooms
        )

        # pull data from Revit to the WPF UI (refresh the rooms list)
        self.ex_event_handler_pull_data_from_revit = ExternalEventHandler(
            execute_at_event_raised=self.pull_data_from_revit_action
        )
        self.ext_event_pull_data_from_revit = ExternalEvent.Create(
            self.ex_event_handler_pull_data_from_revit
        )

        # wipe stale data from the rooms in the revit model
        self.ex_event_handler_wipe_stale_data = ExternalEventHandler(
            execute_at_event_raised=self.wipe_stale_data_action
        )
        self.ext_event_wipe_stale_data = ExternalEvent.Create(
            self.ex_event_handler_wipe_stale_data
        )

    def push_single_room_data(self, *args, **kwargs):
        """
        Push single room data from the WPF UI to Revit
        """

        print(
            "raising external event to push single room data from the WPF UI to Revit.."
        )
        self.ext_event_push_single_room.Raise()

    def push_single_room_data_action(self, uiapp):
        """
        Push single room data from the WPF UI to Revit
        """

        print("Pushing single room data to Revit..")
        pass

    def update_all_revit_rooms(self, *args, **kwargs):
        """
        Update all revit rooms with the data from the WPF UI
        """

        print(
            "raising external event to update all revit rooms with the data from the WPF UI.."
        )
        self.ext_event_update_all_revit_rooms.Raise()

    def update_all_revit_rooms_action(self, uiapp):
        """
        Update all revit rooms with the data from the WPF UI
        """

        print("Updating all revit rooms with the data from the WPF UI..")
        pass

    def pull_data_from_revit(self, *args, **kwargs):
        """
        Pull data from Revit to the WPF UI (refresh the rooms list)
        """

        print("raising external event to pull data from Revit to the WPF UI..")
        self.ext_event_pull_data_from_revit.Raise()

    def pull_data_from_revit_action(self, uiapp):
        """
        Pull data from Revit to the WPF UI (refresh the rooms list)
        """

        print("Pulling data from Revit to the WPF UI..")
        pass

    def wipe_stale_data(self, *args, **kwargs):
        """
        wipe stale data from the rooms in the revit model
        """

        print(
            "raising external event to wipe stale data from the rooms in the revit model.."
        )
        self.ext_event_wipe_stale_data.Raise()
        pass

    def wipe_stale_data_action(self, uiapp):
        """
        wipe stale data from the rooms in the revit model
        """

        print("Wiping stale data from the rooms in the revit model..")
        pass
