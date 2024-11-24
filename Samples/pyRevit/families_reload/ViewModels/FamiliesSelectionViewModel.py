import clr
clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase
from duHast.UI.Objects.WPF.Commands.RelayCommand import RelayCommand
from duHast.Utilities.files_get import get_files_from_directory_walker_with_filters_simple

from System.Collections.ObjectModel import ObservableCollection
from System.Windows.Data import CollectionViewSource
from System.ComponentModel import ListSortDirection, SortDescription

from ViewModels.FamilyViewModel import FamilyViewModel
from Commands.ReloadfamiliesCommand import ReloadFamiliesCommand
from Objects.match_status_names import MatchStatusNames

import os

class FamiliesSelectionViewModel(ViewModelBase):
    def __init__(self, revit_model, navigation_service):
        super(FamiliesSelectionViewModel, self).__init__()

        # properties
        self._families = ObservableCollection[FamilyViewModel]()
        self._families_view = CollectionViewSource.GetDefaultView(self._families)
        self._sort_command = RelayCommand(self.sort_families)
        
        # properties
        self._families_filtered = ObservableCollection[FamilyViewModel]()
        self._revit_model = revit_model

        # commands
        self._reload_families_command = ReloadFamiliesCommand(
            revit_model=revit_model,
            families_selection_view_model=self,
            family_selection_view_navigation_service=navigation_service,
            execute=self.close_window
        )

        # add room reservations to view model
        self.update_families()

        # Set initial sort state
        self._current_sort_column = "FamilyName"
        self._current_sort_direction = ListSortDirection.Ascending
        self._families_view.SortDescriptions.Add(SortDescription(self._current_sort_column, self._current_sort_direction))
    
    @property
    def FamiliesView(self):
        return self._families_view

    @property
    def SortCommand(self):
        return self._sort_command

    def sort_families(self, sort_by):
        current_sort = None
        if self._families_view.SortDescriptions.Count > 0:
            current_sort = self._families_view.SortDescriptions[0]

        direction = ListSortDirection.Ascending
        if current_sort and current_sort.PropertyName == sort_by:
            if current_sort.Direction == ListSortDirection.Ascending:
                direction = ListSortDirection.Descending
            else:
                direction = ListSortDirection.Ascending

        self._families_view.SortDescriptions.Clear()
        self._families_view.SortDescriptions.Add(SortDescription(sort_by, direction))
        self._families_view.Refresh()

        # Update current sort column and direction
        self._current_sort_column = sort_by
        self._current_sort_direction = direction

    @property
    def LibraryPath(self):
        print("accessing library path getter")
        return self._revit_model.settings.library_path
    
    @LibraryPath.setter
    def LibraryPath(self, value):
        print("accessing library path setter: [{}]".format(value))
        if not(isinstance (value,str)):
            raise ValueError("Value must be of type str, got {} instead.".format(type(value)))
        self._revit_model.settings.library_path = value
        print("settings: {}".format(self._revit_model.settings.to_json()))
        
        # update the match status of all families
        self.update_families()

        # raise the change event in order for the reload buttons availbiltiy check to be triggerd
        self.RaisePropertyChanged("LibraryPath")

    @property
    def Families(self):
        print("accessing families")
        return self._families
    
    @property
    def ReloadFamiliesCommand(self):
        print("in  Reload command")
        return self._reload_families_command 

    def find_files(self, file_paths, file_name):
        return [path for path in file_paths if os.path.basename(path) == file_name]

    def update_families(self):
        # clear the collection
        self._families.Clear()
        
        families_in_directory = []
        if(self._revit_model.settings.library_path):
            families_in_directory = get_files_from_directory_walker_with_filters_simple(
                folder_path=self._revit_model.settings.library_path,
                file_extension=".rfa"
            )
        
        if(families_in_directory):
            print("found {} revit families".format(len(families_in_directory)))
        else:
            print("Found no families in directory")
            families_in_directory = []

        # update the collection with values from the revit model
        for family in self._revit_model.get_all_families():
            family_view_model = FamilyViewModel(family=family)
            # check the match status!!
            files_matching = self.find_files(families_in_directory, family_view_model.FamilyName+".rfa")
            
            if len(files_matching) == 1:
                family_view_model.MatchStatus = MatchStatusNames.MATCH_OK.value
                family_view_model.FamilyFilePath = files_matching[0]
            elif len(files_matching) == 0:
                family_view_model.MatchStatus = MatchStatusNames.NO_MATCH.value
                family_view_model.FamilyFilePath = None
            else:
                family_view_model.MatchStatus = MatchStatusNames.MULTIPLE_MATCHES.value
                family_view_model.FamilyFilePath = None

            self._families.Add(family_view_model)

    def close_window(self, window):
        if window:
            window.Close()