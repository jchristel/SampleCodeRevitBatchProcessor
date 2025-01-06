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

class RevitEventHandlerManager(Base):

    def __init__(self, ):
            
            # ini super class to allow multi inheritance in children!
            super(RevitEventHandlerManager, self).__init__()

    def setup_event_handlers(self, doc):
        """
        Set up the event handlers in Revit
        """
        pass
    

    def push_single_room_data(self):
        """
        Push single room data from the WPF UI to Revit
        """
        pass

    def update_all_revit_rooms(self):
        """
        Update all revit rooms with the data from the WPF UI
        """
        pass

    def pull_data_from_revit(self):
        """
        Pull data from Revit to the WPF UI (refresh the rooms list)
        """
        pass

    def wipe_stale_data(self):
        """
        wipe stale data from the rooms in the revit model
        """
        pass