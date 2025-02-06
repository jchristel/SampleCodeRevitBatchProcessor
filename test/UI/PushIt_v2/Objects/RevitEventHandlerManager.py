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
import traceback

from duHast.Utilities.Objects.base import Base
from duHast.Revit.UI.Objects.ExernalEventHandler import ExternalEventHandler
from PushIt_v2.RevitActions.UpdateAllRevitFamilesFromUI import UpdateAllRevitFamiliesFromUI
from PushIt_v2.RevitActions.UpdateSingleRevitFamilyFromUI import (
    UpdateSingleRevitFamilyFromUI,
)
from PushIt_v2.RevitActions.UpdateDataModelFromRevit import UpdateDataModelFromRevit
from PushIt_v2.RevitActions.InitialiseRoomData import InitialiseRoomData
from PushIt_v2.RevitActions.WipeStaleDataInRevitFamilies import WipeStaleDataInRevitFamilies
from PushIt_v2.RevitActions.HighlightRoomsInRevit import HighlightRoomsInRevit
from PushIt_v2.Utilities import event_names

from Autodesk.Revit.UI import (
    ExternalEvent,
)

import clr
clr.AddReference('PresentationFramework')
from Microsoft.Win32 import OpenFileDialog

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

        # set up the data for the event handlers
        self.ex_event_handler_setup_data = ExternalEventHandler(
            execute_at_event_raised=self.setup_data_action
        )
        self.ext_event_setup_data = ExternalEvent.Create(
            self.ex_event_handler_setup_data
        )
        
        # highlight elements in Revit
        self.ex_event_handler_highlight_elements_in_revit = ExternalEventHandler(
            execute_at_event_raised=self.highlight_rooms_in_revit_action
        )
        self.ext_event_highlight_elements_in_revit = ExternalEvent.Create(
            self.ex_event_handler_highlight_elements_in_revit
        )

    def dispose(self):
        """
        Dispose the external event handlers
        """

        # dispose the external event
        self.ext_event_push_single_room.Dispose()
        self.ext_event_push_single_room = None
        self.ext_event_update_all_revit_rooms.Dispose()
        self.ext_event_update_all_revit_rooms = None
        self.ext_event_pull_data_from_revit.Dispose()
        self.ext_event_pull_data_from_revit = None
        self.ext_event_wipe_stale_data.Dispose()
        self.ext_event_wipe_stale_data = None
        self.ext_event_setup_data.Dispose()
        self.ext_event_setup_data = None
        self.ext_event_highlight_elements_in_revit.Dispose()
        self.ext_event_highlight_elements_in_revit = None

        # dispose the external event handlers
        self.ex_event_handler_push_single_room = None
        self.ex_event_handler_update_all_revit_rooms = None
        self.ex_event_handler_pull_data_from_revit = None
        self.ex_event_handler_wipe_stale_data = None
        self.ex_event_handler_setup_data = None
        self.ex_event_handler_highlight_elements_in_revit = None

    def push_single_room_data(self, *args, **kwargs):
        """
        Push single room data from the WPF UI to Revit
        """

        # print(
        #    "raising external event to push single room data from the WPF UI to Revit.."
        # )
        self.ext_event_push_single_room.Raise()

    def push_single_room_data_action(self, uiapp):
        """
        Push single room data from the WPF UI to Revit
        """

        try:
            # current revit document
            doc = uiapp.ActiveUIDocument.Document

            # get the UIDocument
            uidoc = uiapp.ActiveUIDocument

            # get the current selection
            element_ids = uidoc.Selection.GetElementIds()

            if len(element_ids) != 1:
                print("Please select exactly one room to push data to Revit")
                return

            
            try:
                # set up the revit action to update the room with the data from the WPF UI
                action = UpdateSingleRevitFamilyFromUI(revit_model=self._revit_model)
                # populate room data from file and match families from the Revit document to rooms
                action.execute(doc=doc, selected_element_id=element_ids[0])
            except Exception as e:
                print(
                    "Error while calling function pushing single room into Revit: {}".format(
                        e
                    )
                )
                print(traceback.format_exc())
                return
        except Exception as e:
            print(
                "Error while prepping for pushing single room into Revit: {}".format(e)
            )
            return

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

        #print("Updating all revit rooms with the data from the WPF UI..")
        # current revit document
        doc = uiapp.ActiveUIDocument.Document

        try:
            # set up the revit action to update all revit rooms with the data from the WPF UI
            action = UpdateAllRevitFamiliesFromUI(revit_model=self._revit_model)
            # execute the action
            action.execute(doc=doc)
        except Exception as e:
            print("Error while Updating all revit rooms from the WPF UI: {}".format(e))
            return

    def pull_data_from_revit(self, *args, **kwargs):
        """
        Pull data from Revit to the WPF UI (refresh the rooms list)
        """

        # print("raising external event to pull data from Revit to the WPF UI..")
        self.ext_event_pull_data_from_revit.Raise()

    def pull_data_from_revit_action(self, uiapp):
        """
        Pull data from Revit to the WPF UI (refresh the rooms list)
        """

        # current revit document
        doc = uiapp.ActiveUIDocument.Document

        try:
            # set up the revit action to update the data model from the Revit model
            action = UpdateDataModelFromRevit(revit_model=self._revit_model)
            # execute the action
            action.execute(doc=doc)
        except Exception as e:
            print("Error while pulling data from Revit to the WPF UI: {}".format(e))
            return

    def wipe_stale_data(self, *args, **kwargs):
        """
        wipe stale data from the rooms in the revit model
        """
        
        self.ext_event_wipe_stale_data.Raise()

    def wipe_stale_data_action(self, uiapp):
        """
        wipe stale data from the rooms in the revit model
        """
        
        # current revit document
        doc = uiapp.ActiveUIDocument.Document
        
        try:
            # set up the revit action to wipe stale data in the Revit model
            action = WipeStaleDataInRevitFamilies(revit_model=self._revit_model)
            # execute the action
            action.execute(doc=doc)
        except Exception as e:
            print("Error while wiping stale data in the Revit model: {}".format(e))
            return
        

    def setup_data(self, *args, **kwargs):
        """
        Set up the data for ui event handler.
        """

        # print("Raising set up data event...")
        self.ext_event_setup_data.Raise()

    def setup_data_action(self, uiapp):
        """
        Set up the data for ui:

        - read data from file
        - get families from model
        - set up rooms with revit matches (make sure the current design set / option are taken into account)
        """

        # current revit document
        doc = uiapp.ActiveUIDocument.Document

        try:
            # set up the revit action to initialise the room data
            action = InitialiseRoomData(revit_model=self._revit_model)
            # execute the action
            action.execute(doc=doc)
        except Exception as e:
            print("Error while loading and setting up data for ui: {}".format(e))
            return


    def highlight_rooms_in_revit(self, *args, **kwargs):
        """
        Set up the highlight elements in Revit event handler.
        """
        self.ext_event_highlight_elements_in_revit.Raise()
        
    
    def highlight_rooms_in_revit_action(self, uiapp):
        """
        Highlight elements in Revit
        """

        # current revit document
        doc = uiapp.ActiveUIDocument.Document

        try:
            # set up the revit action to highlight elements in Revit
            action = HighlightRoomsInRevit(revit_model=self._revit_model)
            # execute the action
            action.execute(doc=doc, ui_app=uiapp)
        except Exception as e:
            print("Error while highlighting elements in Revit: {}".format(e))
            return


    def browse_for_file_action(self, *args, **kwargs):
        """
        Browse for file
        """

        print("Raising browse for file event...")
        # Create an OpenFileDialog
        dialog = OpenFileDialog()
        dialog.Title = "Select a file"
        dialog.Filter = "Text files (*.txt)|*.txt|CSV files (*.csv)|*.csv"

        # Show the dialog and get the selected file path
        result = dialog.ShowDialog()
        if result:
            self._revit_model._data_file_path_intermittent = dialog.FileName
            # raise the event to load the data from the file
            # check the new file path and save it if it is valid and different
            self._revit_model.RaisePropertyChanged(event_names.VIEW_MODEL_DATA_FILE_PATH)
        
        