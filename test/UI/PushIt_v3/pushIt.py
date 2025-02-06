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
PushIt.

For further documentation please refer to the README.rst file in the _docs directory of this project.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import os
import settings

from duHast.Utilities.Objects.result import Result
from duHast.UI.Objects.WPF.ViewModels.MainViewModel import MainViewModel
from duHast.UI.Objects.WPF.Stores.NavigationStore import NavigationStore
from duHast.UI.Objects.WPF.Services.NavigationService import NavigationService

try:
    from duHast.pyRevit.console_output import print_header
except ImportError:

    def print_header(message):
        print(message)

#from PushIt_v2.ViewModels.RoomsSelectionViewModel import RoomsSelectionViewModel
#from PushIt_v2.Models.RevitModel import RevitModel
from PushIt_v3.Objects.MainWindow import PushIt
#from PushIt_v2.Utilities.rooms_load import load_rooms_from_file
#from PushIt_v2.Utilities.categories_get import get_revit_categories
#from PushIt_v2.Objects.RevitEventHandlerManager import RevitEventHandlerManager

# # view model types and their XAML file path
# XAML_BY_VIEW = {
#     RoomsSelectionViewModel: os.path.join(
#         settings.SCRIPT_DIRECTORY, r"Views\RoomsSelectionView.xaml"
#     ),
# }

# # set up a navigation store
NAVIGATION_STORE = NavigationStore()

# # set up the revit model container with a settings file name
# REVIT_MODEL = None #RevitModel(settings_file_path = settings.APP_SETTINGS_FILE_NAME)

# # set up the revit event handler manager
# REVIT_EVENT_HANDLER_MANAGER = RevitEventHandlerManager(REVIT_MODEL)

# def Create_Rooms_Selection_View_Model():
#     """
#     Create a RoomsSelectionViewModel instance.
    
#     :return: RoomsSelectionViewModel instance.
#     :rtype: RoomsSelectionViewModel
#     """
    
#     # used to create a family selection view model
#     fam_view_model = RoomsSelectionViewModel(
#         revit_model=REVIT_MODEL,
#         revit_model_event_handler_manager=REVIT_EVENT_HANDLER_MANAGER,
#         navigation_service=NavigationService(
#             navigation_store=NAVIGATION_STORE,
#             create_view_model=Create_Rooms_Selection_View_Model,
#         ),
#     )

#     return fam_view_model


def pushIt_entry(doc, uiapp, output, forms, rooms=None):
    """
    Start the PushIt UI.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: _type_
    :param forms: pyRevit progressbar
    :type forms: _type_
    :return: Result class instance.
        - `result` (bool): True if warnings where reported without an exception, otherwise False.
        - `message` (str): details how many warnings where retrieved.
    :rtype: :class:`.Result`
    """

    print_header("Starting UI...")
    
    try:
        # load the settings
        #REVIT_MODEL.settings.load_settings()
        #REVIT_MODEL.load_room_data()
        # add revit categories to model
        #REVIT_MODEL.revit_categories = get_revit_categories(doc=doc)
        
        # set up UI
        # set up initial data for the main view model
        # this is not requiredt since the ini of the view model raises the same event
        #REVIT_EVENT_HANDLER_MANAGER.setup_data_action(uiapp=uiapp)
        
        # set up the initial view to be displayed
        #NAVIGATION_STORE.CurrentViewModel = Create_Rooms_Selection_View_Model()
        
        # the main view model ( container for all other view models)
        #main_view_model = MainViewModel(navigation_store=NAVIGATION_STORE)
        main_view_model = MainViewModel(navigation_store=NAVIGATION_STORE)
        path=r"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\test\UI\PushIt_v3\Views\RoomsSelectionView.xaml"
        # set up a window instance
        my_window = PushIt(
            xaml_path=path,
            main_view_model=main_view_model,
            xaml_by_view_model=None,
            resources_xaml_path=None,
            settings=None,
            event_handler_manager=None,
        )

        # show the window to the user
        my_window.Show()
    except Exception as e:
        print_header("An exception occurred in the PushIt UI: {}".format(e))

# if __name__ == "__main__":
#     # dummy_rooms = load_rooms (file_path=os.path.join(settings.SCRIPT_DIRECTORY,  r"Samples\Data_Min.csv"))
#     dummy_rooms_result = load_rooms_from_file(
#         file_path=os.path.join(settings.SCRIPT_DIRECTORY, r"Samples\Data_Extended.csv")
#     )
#     if dummy_rooms_result.status:
#         dummy_rooms = dummy_rooms_result.result
#         test_result = pushIt_entry(doc=None, output=None, forms=None, rooms=dummy_rooms)
#     else:
#         print (dummy_rooms_result.message)

#test_result = pushIt_entry(doc=None, output=None, forms=None, rooms=None)
