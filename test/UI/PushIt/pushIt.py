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

from duHast.Utilities.files_csv import read_csv_file
        

#from families_reload.get_families import get_families_in_model
from PushIt.ViewModels.RoomsSelectionViewModel import RoomsSelectionViewModel
from PushIt.Models.RevitModel import RevitModel
from PushIt.Models.Room import Room
from PushIt.Models.RoomId import RoomID
from PushIt.Models.RoomProperty import RoomProperty
from PushIt.Objects.MainWindow import PushIt
from PushIt.Objects.CSVColumnsMapper import CSVColumnMapper

#from Autodesk.Revit.DB import ElementId

# view model types and their XAML file path
XAML_BY_VIEW ={
    RoomsSelectionViewModel: os.path.join(settings.SCRIPT_DIRECTORY,  r"Views\RoomsSelectionView.xaml"),
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
    
    print("Loading rooms from file: {}".format(file_path))
    
    # read the file
    read_result = read_csv_file(file_path)
    if(read_result.status == False):
        print("Error: {}".format(read_result.message))
        return None
    
    data_rows = read_result.result
    print("Found {} rows.".format(len(data_rows)))
    
    # do some sanity checks...
    if(len(data_rows) == 0):
        print("No data found in file.")
        return None
    
    if (len(data_rows[0]) < 3):
        print("Error: Not enough columns found in file.")
        return None
    
    if (len(data_rows) <=2 ):
        print("Warning: Not enough rows found in file.")
        
    # create a list of rooms from the data from row 3 onwards
    
    rooms_list = []
    
    for row in data_rows[2:]:
        # create a room object
        id_room = RoomID(
                id=row[CSVColumnMapper.COLUMN_ROOM_ID.value],
                parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][CSVColumnMapper.COLUMN_ROOM_ID.value]
            )
        print("...Room ID: {}".format(id_room.id))
        area_room_briefed =RoomProperty(name="{}".format(
                data_rows[CSVColumnMapper.ROW_PROPERTY_DESCRIPTION.value][CSVColumnMapper.COLUMN_AREA_BRIEFED.value]), 
                value=row[CSVColumnMapper.COLUMN_AREA_BRIEFED.value], 
                parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][CSVColumnMapper.COLUMN_AREA_BRIEFED.value]
            )
        print("...Area briefed: {}".format(area_room_briefed.value))
        area_room_designed=RoomProperty(name="{}".format(
                data_rows[CSVColumnMapper.ROW_PROPERTY_DESCRIPTION.value][CSVColumnMapper.COLUMN_AREA_DESIGNED.value]), 
                value=row[CSVColumnMapper.COLUMN_AREA_DESIGNED.value], 
                parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][CSVColumnMapper.COLUMN_AREA_DESIGNED.value]
            )
        print("...Area designed: {}".format(area_room_designed.value))
        
        room = Room(id=id_room,area_briefed=area_room_briefed,area_designed=area_room_designed)
        
        # get additional data from the row
        if (len(row) > 3):
            
            for i in range(3, len(row)):
                # create a property object
                prop=RoomProperty(
                    name="{}".format(data_rows[CSVColumnMapper.ROW_PROPERTY_DESCRIPTION.value][i]), 
                    value=row[i], 
                    parameter_guid=data_rows[CSVColumnMapper.ROW_PARAMETER_GUID.value][i]
                )
                print("...Property: {}".format(prop))
                # add it to room
                room.add_property(prop)
        rooms_list.append(room)
    
    return rooms_list



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

    # load rooms from sample file
    
    if(rooms is None):
        # get all families in file
        #families = get_families_in_model(doc=doc, library_path=None)
        return

    print_header ("Starting UI...")
    print("\nFound {} room(s).".format(len(rooms)))
    
    # sort by room id value ( to get to the actual is value use obj.id.id)
    sorted_rooms_list = sorted(rooms, key=lambda obj: obj.id.id)
    
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
    my_window.ShowDialog()

    print("Finished.")
    return return_value


if __name__ == "__main__":
    #dummy_rooms = load_rooms (file_path=os.path.join(settings.SCRIPT_DIRECTORY,  r"Samples\Data_Min.csv"))
    dummy_rooms = load_rooms (file_path=os.path.join(settings.SCRIPT_DIRECTORY,  r"Samples\Data_Extended.csv"))
    test_result = pushIt_entry(doc=None, output=None, forms=None, rooms = dummy_rooms)