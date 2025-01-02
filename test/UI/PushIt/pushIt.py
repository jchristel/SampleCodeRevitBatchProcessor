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
        

#from families_reload.get_families import get_families_in_model
from test.UI.PushIt.ViewModels.RoomsSelectionViewModel import RoomsSelectionViewModel
from test.UI.PushIt.Models.RevitModel import RevitModel
from test.UI.PushIt.Models.Room import Room
from test.UI.PushIt.Models.RoomId import RoomID
from Objects.MainWindow import PushIt

#from Autodesk.Revit.DB import ElementId

# view model types and their XAML file path
XAML_BY_VIEW ={
    RoomsSelectionViewModel: os.path.join(settings.SCRIPT_DIRECTORY,  r"Views\FamiliesSelectionView.xaml"),
}

# set up a navigation store
NAVIGATION_STORE = NavigationStore()

# set up the revit model container
REVIT_MODEL = RevitModel()


def Create_Rooms_Selection_View_Model():

    # used to create a family selection view model
    fam_view_model = RoomsSelectionViewModel(
        revit_model = REVIT_MODEL,
        navigation_service=NavigationService(
            navigation_store=NAVIGATION_STORE,
            create_view_model=Create_Rooms_Selection_View_Model
        )
    )

    return fam_view_model


def load_rooms(file_path):
    """
    Loads rooms from a file.

    :param file_path: path to the file to load rooms from.
    :type file_path: str
    :return: list of rooms
    :rtype: list
    """
    pass



def pushIt_entry(doc, output, forms, rooms = None):
    """
    Reports on loaded families in a project file.

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

    # set up a status tracker
    return_value = Result()

    if(rooms is None):
        # get all families in file
        #families = get_families_in_model(doc=doc, library_path=None)
        pass

    print_header ("Starting UI...")
    print("\nFound {} room(s).".format(len(rooms)))
    
    # sort by family names
    sorted_rooms_list = sorted(rooms, key=lambda obj: obj.id)
    
    # add family to the model
    for room_instance in sorted_rooms_list:
        REVIT_MODEL.add_room(room_model=room_instance)

    # get the settings path from file and assign the revit model
    settings_data = settings.get_settings()
    # check if any settings where found otherwise go with default
    if(settings_data):
        REVIT_MODEL.settings=settings_data
        print("found settings: {}\n{}".format(settings_data, REVIT_MODEL.settings))

    # set up UI
    # set up the initial view to be displayed
    NAVIGATION_STORE.CurrentViewModel = Create_Rooms_Selection_View_Model()

    # the main view model ( container for all other view models)
    main_view_model = MainViewModel(
        navigation_store=NAVIGATION_STORE
    )

    # set up a window instance
    my_window = PushIt(
        xaml_path= os.path.join(settings.DUH_AST_DIRECTORY,  r"UI\Objects\WPF\Views\MainWindow_py.xaml"),
        main_view_model=main_view_model,
        xaml_by_view_model=XAML_BY_VIEW,
        resources_xaml_path=None
    )

    # show the window to the user
    my_window.Show()

    print("Finished.")
    return return_value


if __name__ == "__main__":
    dummy_rooms = load_rooms (file_path=os.path.join(settings.SCRIPT_DIRECTORY,  r"Samples\Data_Min.csv"))
    test_result = pushIt_entry(doc=None, output=None, forms=None, rooms = dummy_rooms)