import clr
clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase
from duHast.UI.Objects.WPF.Commands.RelayCommand import RelayCommand
from duHast.UI.Objects.WPF.ViewModels.FilterItem import FilterItem


from System.Collections.ObjectModel import ObservableCollection
from System.Windows.Data import CollectionViewSource, PropertyGroupDescription
from System.ComponentModel import ListSortDirection, SortDescription

from test.UI.PushIt.ViewModels.RoomViewModel import RoomViewModel
#from ViewModels.FilterItem import FilterItem
from test.UI.PushIt.Commands.PushRoomDataCommand import PushRoomDataCommand
from Objects.match_status_names import MatchStatusNames

import os

class RoomsSelectionViewModel(ViewModelBase):
    def __init__(self, revit_model, navigation_service):
        super(RoomsSelectionViewModel, self).__init__()

        # properties
        # the collection of families to be displayed in the view
        self._rooms = ObservableCollection[RoomViewModel]()
        
        # the command used to sort when the user clicks on the column headers
        self._sort_command = RelayCommand(self.sort_families)
        
        # the revit wpf model object containing the settings and families to be displayed
        self._revit_model = revit_model

        # commands
        self.push_data_command = PushRoomDataCommand(
            revit_model=revit_model,
            rooms_selection_view_model=self,
            rooms_selection_view_navigation_service=navigation_service,
            execute=self.close_window
        )
        
        # add families to view model
        self.update_families()
        
        # Set initial sort state
        self._current_sort_column = "Id"
        self._current_sort_direction = ListSortDirection.Ascending
        self._rooms_view.SortDescriptions.Add(SortDescription(self._current_sort_column, self._current_sort_direction))
        
    
    @property
    def FamiliesView(self):
        """
        The collection view of the families collection.
        """
        return self._rooms_view

    @property
    def SortCommand(self):
        """
        The command used to sort the collection view of the families collection.
        """
        return self._sort_command
    
    @property
    def ReloadFamiliesCommand(self):
        """
        The command used to when the reload button in the view is clicked.
        
        Stores the selected family objects in the revit model object and triggers the close of the window.
        """
        return self.push_data_command 

    def update_families(self):
        """
        Updates the families collection with the families from the revit model object and sets the match status of the families based on the library path.
        
        Also sets up the collection view for the families collection.
        Set up includes grouping the families by match status.
        
        """
        # clear the collection
        self._rooms.Clear()
        
        # set up collection view based on the observable collection of families
        # this is what the xaml view is binding to
        # this is required to be able to sort, group and filter the collection view without affecting the observable collection
        self._rooms_view = CollectionViewSource.GetDefaultView(self._rooms)
        
        # group the families by match status (this will mean that the families will be sorted by match status first and than by any other sort criteria)
        # MatchStatus is a property of the FamilyViewModel
        #self._rooms_view.GroupDescriptions.Add(PropertyGroupDescription("MatchStatus"))
        
        # set up a filter for the collection view
        self._rooms_view.Filter = self.filter_families
        
        # update the collection with families from the revit model object
        for room_model_instance in self._revit_model.get_all_rooms():
            room_view_model = RoomViewModel(room=room_model_instance)
            
            # add the room to the observable collection
            self._rooms.Add(room_view_model)
    
    def refresh_view(self):
        """
        Refreshes the view by updating the families collection and the unique values for the column filters.
        """
        # refreshes the view in the UI
        self._rooms_view.Refresh()
    
    def close_window(self, window):
        """
        Closes the window that is passed in as an argument. 
        """
        
        if window:
            window.Close()