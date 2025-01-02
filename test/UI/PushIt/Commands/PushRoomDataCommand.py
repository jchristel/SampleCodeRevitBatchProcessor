from duHast.UI.Objects.WPF.Commands.CommandBase import CommandBase
from duHast.Utilities.directory_io import directory_exists

from PushIt.Models.Room import Room

class PushRoomDataCommand(CommandBase):

    def __init__(self, revit_model, rooms_selection_view_model, rooms_selection_view_navigation_service, execute=None):
        
        super(PushRoomDataCommand, self).__init__(execute=None)
    
        self.revit_model = revit_model
        self.rooms_selection_view_model = rooms_selection_view_model
        self.rooms_selection_view_navigation_service = rooms_selection_view_navigation_service
        self._execute = execute
        
        #sub scribe to property change event to enable or disable submit button
        self.rooms_selection_view_model.add_PropertyChanged(self.OnViewModelPropertyChanged)


    def CanExecute(self, parameter):
        """
        This method returns True if the file path  value is set  and points to a valid directory.
        """
        print("in can execute check: " )
        return True
    
    def Execute(self, parameter):
        print("In execute")
        rooms_in_data_model =  self.revit_model.get_all_rooms()
        
        # TODO: store selected rooms in revit model property
        for room_instance in self.rooms_selection_view_model.Families:
            if room_instance.IsSelected:
                # find the family in the revit family model
                # Finding the object
                result = [obj for obj in rooms_in_data_model if obj.id == room_instance.id]
                if(result):
                    # push it to the revit model
                    pass

        if self._execute:
            self._execute(parameter)

    def OnViewModelPropertyChanged(self, sender, property_changed_args):
        """
        Forces to re-evaluate the reload button availability.
        
        Number of arg to this function is not optional!!

        Args:
            sender (_type_): _description_
            property_changed_args (_type_): _description_
            
        """
        print("command property changed value: {}".format(property_changed_args.PropertyName))
        # check if a library path is provided and if
        if(property_changed_args.PropertyName == "LibraryPath"):
            self.on_can_execute_changed()