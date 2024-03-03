from duHast.UI.Objects.ViewModelBase import ViewModelBase
from duHast.UI.Objects.Command import Command
from duHast.UI.Objects.file_item import MyFileItem

from System.Collections.ObjectModel import ObservableCollection
import System


class ViewModel(ViewModelBase):

    PropertyChanged = None

    def __init__(
        self,
        window,
        directory_source_path,
        directory_destination_path,
        source_file_extension,
        number_of_task_files,
        include_sub_dirs,
        filter_text,
        files,
    ):

        ViewModelBase.__init__(self)
        self.window = window
        
        self.debug = []

        # set up an observable collection
        self.revit_files = ObservableCollection[MyFileItem]()

        self.filtered_revit_files = ObservableCollection[MyFileItem]()

        # convert past in files list
        self.convert_list_to_observable_collection(files, self.revit_files)

        # variable to contain the selected files in the data grid
        self.selected_files = ObservableCollection[MyFileItem]()

        self.source_path = directory_source_path
        self.destination_path = directory_destination_path
        self.source_file_extension = source_file_extension
        self.number_of_task_files = number_of_task_files
        self.include_sub_dirs = include_sub_dirs
        self.filter_text = filter_text

        # hook up ok and cancel buttons
        self.BtnOkCommand = Command(self.BtnOK)
        self.BtnCancelCommand = Command(self.BtnCancel)
        
        # filter data of data grid view
        self.TextBox_Filter_TextChanged()

    def convert_list_to_observable_collection(self, list_of_items, target_list):
        """
        Used transfer items from a standard python list to another list ( of a .net type)

        Args:
            list_of_items (_type_): _description_
            target_list (_type_): _description_
        """
        target_list.Clear()  # Clear existing items if any
        for item in list_of_items:
            target_list.Add(item)

    @property
    def TextBoxText_Filter(self):
        return self.filter_text

    @TextBoxText_Filter.setter
    def TextBoxText_Filter(self, value):
        if self.filter_text != value:
            self.filter_text = value
            self.OnPropertyChanged("TextBoxText_Filter")
            # this appears to be a bit of hack since I cant seem to be able to hook up an event handler to the text changed event via XAML
            self.TextBox_Filter_TextChanged()

    def OnPropertyChanged(self, name):
        if self.PropertyChanged:
            self.PropertyChanged(
                self, System.ComponentModel.PropertyChangedEventArgs(name)
            )

    def TextBox_Filter_TextChanged(self):
        """
        Event handler for text changed in TextBox.
        """
        
        # clear the previous version of the filtered list
        self.filtered_revit_files.Clear()
        # set up a python vanilla list to contain filtered elements
        filtered_revit_files_intermediate = []
        # filter file list
        for file in self.revit_files:
            if self.filter_text in file.name:
                filtered_revit_files_intermediate.append(file)
        # transfer files from intermediate list to List[ObservableCollection]
        self.convert_list_to_observable_collection(
            filtered_revit_files_intermediate, self.filtered_revit_files
        )


    def BtnOK(self):
        """
        Ok button event handler.

        Gets the selected rows of files and adds them to .selectedFiles property
        Sets the dialog result value to True.

        :param sender: _description_
        :type sender: _type_
        :param EventArgs: _description_
        :type EventArgs: _type_
        """

        self.DialogResult = True
        self.selected_files.Clear()  # Clear existing items if any
        # this is also a hack:
        # file item has a  property .is_selected which is bound to IsSelected Row style in XAML file
        # a work around to get all selected rows from the data grid view
        for file_item in self.revit_files:
            if file_item.is_selected:
                self.selected_files.Add(file_item)

        self.window.Close()

    def BtnCancel(self):
        """
        Cancel button event handler.
        Sets the dialogue result value to False.

        :param sender: _description_
        :type sender: _type_
        :param EventArgs: _description_
        :type EventArgs: _type_
        """

        self.DialogResult = False
        self.window.Close()
