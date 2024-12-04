import clr
clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase
from duHast.UI.Objects.WPF.Commands.RelayCommand import RelayCommand
from duHast.Utilities.files_get import get_files_from_directory_walker_with_filters_simple

from System.Collections.ObjectModel import ObservableCollection
from System.Windows.Data import CollectionViewSource, PropertyGroupDescription
from System.ComponentModel import ListSortDirection, SortDescription

from ViewModels.FamilyViewModel import FamilyViewModel
from ViewModels.FilterItem import FilterItem
from Commands.ReloadfamiliesCommand import ReloadFamiliesCommand
from Objects.match_status_names import MatchStatusNames

import os

class FamiliesSelectionViewModel(ViewModelBase):
    def __init__(self, revit_model, navigation_service):
        super(FamiliesSelectionViewModel, self).__init__()

        # properties
        # the collection of families to be displayed in the view
        self._families = ObservableCollection[FamilyViewModel]()
        
        # the command used to sort when the user clicks on the column headers
        self._sort_command = RelayCommand(self.sort_families)
        
        # the revit wpf model object containing the settings and families to be displayed
        self._revit_model = revit_model

        # commands
        self._reload_families_command = ReloadFamiliesCommand(
            revit_model=revit_model,
            families_selection_view_model=self,
            family_selection_view_navigation_service=navigation_service,
            execute=self.close_window
        )

         # set filter lists for column filters
        self._unique_match_statuses = ObservableCollection[FilterItem]()  
        self._unique_categories = ObservableCollection[FilterItem]()  
        self._unique_names = ObservableCollection[FilterItem]()  
        self._unique_shared_statuses = ObservableCollection[FilterItem]() 
        
        # add families to view model
        self.update_families()
        
        # set unique values for the column context menu filters
        self.set_unique_values()
        
        # Set initial sort state
        self._current_sort_column = "FamilyName"
        self._current_sort_direction = ListSortDirection.Ascending
        self._families_view.SortDescriptions.Add(SortDescription(self._current_sort_column, self._current_sort_direction))
        
    
    @property
    def UniqueFamilyNames(self):
        """
        The collection of unique family names to be displayed in the column header context filter menu.
        """
        return self._unique_names 
    
    @property
    def UniqueMatchStatuses(self):
        """
        The collection of unique match statuses to be displayed in the column header context filter menu.
        """
        return self._unique_match_statuses
    
    @property
    def UniqueCategories(self):
        """
        The collection of unique categories to be displayed in the column header context filter menu.
        """
        return self._unique_categories
    
    @property
    def UniqueSharedStatuses(self):
        """
        The collection of unique shared statuses to be displayed in the column header context filter menu.
        """
        return self._unique_shared_statuses
    
    @property
    def FamiliesView(self):
        """
        The collection view of the families collection.
        """
        return self._families_view

    @property
    def SortCommand(self):
        """
        The command used to sort the collection view of the families collection.
        """
        return self._sort_command

    @property
    def LibraryPath(self):
        """
        The library path property of the revit model object.
        Describes the location of the revit families library on a file server. This location is used to determine the match status of the families.
        """
        print("accessing library path getter")
        return self._revit_model.settings.library_path
    
    @LibraryPath.setter
    def LibraryPath(self, value):
        """
        The setter for the library path property of the revit model object.
        
        This setter is used to update the library path property of the revit model object through a two binding to the view and to update the match status of the families based on the new library path when it changes.
        """
        print("accessing library path setter: [{}]".format(value))
        
        # type checking
        if not(isinstance (value,str)):
            raise ValueError("Value must be of type str, got {} instead.".format(type(value)))
        
        # set the new library path value
        self._revit_model.settings.library_path = value
        print("settings: {}".format(self._revit_model.settings.to_json()))
        
        # update the match status of all families
        self.update_families()

        # raise the change event in order for the reload buttons availability check to be triggered
        self.RaisePropertyChanged("LibraryPath")

    @property
    def Families(self):
        """
        The collection of families to be displayed in the view. ( Not used in the view, the collection view is used instead)
        """
        print("accessing families directly")
        return self._families
    
    @property
    def ReloadFamiliesCommand(self):
        """
        The command used to when the reload button in the view is clicked.
        
        Stores the selected family objects in the revit model object and triggers the close of the window.
        """
        print("in  Reload command")
        return self._reload_families_command 

    def find_files(self, file_paths, file_name):
        """
        Finds all files in the list of file paths that have the same file name as the file name passed in as an argument.
        Used to determine the match status of the families. ( is there no match, a single match or multiple matches)
        
        Args:
            file_paths (list): A list of file paths to search in.
            file_name (str): The file name to search for.
            
        Returns:
            list: A list of file paths that have the same file name as the file name passed in as an argument.
        """
        return [path for path in file_paths if os.path.basename(path) == file_name]

    def update_families(self):
        """
        Updates the families collection with the families from the revit model object and sets the match status of the families based on the library path.
        
        Also sets up the collection view for the families collection.
        Set up includes grouping the families by match status.
        
        """
        # clear the collection
        self._families.Clear()
        
        # set up collection view based on the observable collection of families
        # this is what the xaml view is binding to
        # this is required to be able to sort, group and filter the collection view without affecting the observable collection
        self._families_view = CollectionViewSource.GetDefaultView(self._families)
        
        # group the families by match status (this will mean that the families will be sorted by match status first and than by any other sort criteria)
        # MatchStatus is a property of the FamilyViewModel
        self._families_view.GroupDescriptions.Add(PropertyGroupDescription("MatchStatus"))
        
        # get all families in the library path ( required to set the match status of the families)
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

        # update the collection with families from the revit model object
        for family in self._revit_model.get_all_families():
            family_view_model = FamilyViewModel(family=family)
            # check the match status!!
            files_matching = self.find_files(families_in_directory, family_view_model.FamilyName+".rfa")
            
            # set the match status based on the number of files found
            if len(files_matching) == 1:
                family_view_model.MatchStatus = MatchStatusNames.MATCH_OK.value
                family_view_model.FamilyFilePath = files_matching[0]
            elif len(files_matching) == 0:
                family_view_model.MatchStatus = MatchStatusNames.NO_MATCH.value
                family_view_model.FamilyFilePath = None
            else:
                family_view_model.MatchStatus = MatchStatusNames.MULTIPLE_MATCHES.value
                family_view_model.FamilyFilePath = None

            # add the family to the observable collection
            self._families.Add(family_view_model)
            
    def set_unique_values(self):
        """
        Sets the unique values for the column filters context menu depending on the values in the families collection.
        """
        # Use sets to collect unique values for column filters
        unique_match_statuses_set = set()
        unique_categories_set = set()
        unique_names_set = set()
        unique_shared_statuses_set = set()
        
        # extract unique values for column filters ( name and category only)
        for family in self._families:
            unique_categories_set.add(family.FamilyCategory)
            unique_names_set.add(family.FamilyName)
            unique_shared_statuses_set.add(family.FamilyIsShared)
        
        # set unique values for match status
        unique_match_statuses_set.add(MatchStatusNames.NO_MATCH.value)
        unique_match_statuses_set.add(MatchStatusNames.MULTIPLE_MATCHES.value)
        unique_match_statuses_set.add(MatchStatusNames.MATCH_OK.value)
        
        # clear collection first before adding new values
        self._unique_match_statuses.Clear()
        self._unique_categories.Clear()
        self._unique_names.Clear() 
        self._unique_shared_statuses.Clear()
        
        # add unique values to the filter lists
        for match_status in unique_match_statuses_set:
            self._unique_match_statuses.Add(FilterItem(value=match_status, view_model=self))
        for category in unique_categories_set:
            self._unique_categories.Add(FilterItem(value=category, view_model=self))
        for name in unique_names_set:
            self._unique_names.Add(FilterItem(value=name, view_model=self))
        for shared_status in unique_shared_statuses_set:
            self._unique_shared_statuses.Add(FilterItem(value=shared_status, view_model=self))
           

    def sort_families(self, sort_by):
        """
        Sorts the families collection view based on the column header that was clicked.
        
        Args:
            sort_by (str): The property name of the FamilyViewModel to sort by.
        """
        
        # Check if the column is already sorted and if so, reverse the sort direction
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
        
        
    def close_window(self, window):
        """
        Closes the window that is passed in as an argument. 
        """
        
        if window:
            window.Close()