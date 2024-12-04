import clr
from System.Collections.ObjectModel import ObservableCollection
from System.ComponentModel import INotifyPropertyChanged, PropertyChangedEventArgs

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase

class FilterItem(ViewModelBase):
    def __init__(self, value, view_model):
        super(FilterItem, self).__init__()
        self.Value = value
        self._is_checked = True
        self.ViewModel = view_model  # Keep a reference to the ViewModel

    @property
    def IsChecked(self):
        return self._is_checked

    @IsChecked.setter
    def IsChecked(self, value):
        if self.IsChecked != value:
            self._is_checked = value
            self.RaisePropertyChanged("IsChecked")
            #if self.ViewModel:  # Check if we have a reference to the ViewModel
            #    self.ViewModel.apply_filter()  # Call filtering method

        

