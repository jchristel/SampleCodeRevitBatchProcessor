from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase
from duHast.UI.Objects.WPF.Commands.CommandBase import CommandBase
from duHast.UI.Objects.file_item import MyFileItem
from duHast.UI.file_list import get_revit_files_for_processing


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
        filter_rules,
        filter_is_and,
    ):

        ViewModelBase.__init__(self)

        # check past in variable types
        if not (isinstance(filter_rules, list)):
            raise TypeError("filter_rules must be a list")

        self.window = window
        self.debug = []

        # set up an observable collection for files found
        self.revit_files = ObservableCollection[MyFileItem]()
        # set up an observable collection for files filtered
        self.filtered_revit_files = ObservableCollection[MyFileItem]()

        # variable to contain the selected files in the data grid
        self.selected_files = ObservableCollection[MyFileItem]()

        self.source_path = directory_source_path
        self.destination_path = directory_destination_path
        self.source_file_extension = source_file_extension
        self.number_of_task_files = number_of_task_files
        self.include_sub_dirs = include_sub_dirs
        self.filter_rules = filter_rules

        # build filter text string from filter rules
        if len(filter_rules) > 1:
            self.filter_text = ";".join(self.filter_rules)
        elif len(filter_rules) == 1:
            self.filter_text = filter_rules[0]
        else:
            self.filter_text = ""

        # set radio buttons defining filter type ( AND or OR)
        self.filter_is_and = filter_is_and
        self.filter_is_or = not (filter_is_and)

        # hook up ok and cancel buttons
        self.BtnOkCommand = CommandBase(self.button_ok)
        self.BtnCancelCommand = CommandBase(self.button_cancel)

        # get files
        self._get_files()

        # filter data of data grid view
        self.TextBox_Filter_TextChanged()

        # set the dialog result property to true as a default
        self.DialogResult = True

    @property
    def TextBoxText_SourcePath(self):
        return self.source_path

    @TextBoxText_SourcePath.setter
    def TextBoxText_SourcePath(self, value):
        if self.source_path != value:
            self.source_path = value
            self.OnPropertyChanged("TextBoxText_SourcePath")
            # this appears to be a bit of hack since I cant seem to be able to hook up an event handler to the text changed event via XAML
            self.text_box_source_path_change()

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

    @property
    def RadioButton_FilterAnd(self):
        return self.filter_is_and

    @RadioButton_FilterAnd.setter
    def RadioButton_FilterAnd(self, value):
        if self.filter_is_and != value:
            self.filter_is_and = value
            self.OnPropertyChanged("RadioButton_FilterAnd")
            # this appears to be a bit of hack since I cant seem to be able to hook up an event handler to the radio button changed event via XAML
            self.TextBox_Filter_TextChanged()

    @property
    def RadioButton_FilterOr(self):
        return self.filter_is_or

    @RadioButton_FilterOr.setter
    def RadioButton_FilterOr(self, value):
        if self.filter_is_or != value:
            self.filter_is_or = value
            self.OnPropertyChanged("RadioButton_FilterOr")
            # this appears to be a bit of hack since I cant seem to be able to hook up an event handler to the radio button changed event via XAML
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

    def OnPropertyChanged(self, name):
        if self.PropertyChanged:
            self.PropertyChanged(
                self, System.ComponentModel.PropertyChangedEventArgs(name)
            )

    def _apply_and_to_file_data(self):
        """
        Filters file data assuming logical AND rule

        Returns:
            _type_: _description_
        """
        filtered_revit_files_intermediate = []
        # filter file list
        for file in self.revit_files:
            all_match_by_file = True
            # check each filter
            for filter in self.filter_rules:
                if filter not in file.name:
                    # all filters need to match...this is not the case
                    # set flag accordingly
                    all_match_by_file = False
                    break
            # only add file if all filters returned true
            if all_match_by_file:
                filtered_revit_files_intermediate.append(file)

        return filtered_revit_files_intermediate

    def _apply_or_to_file_data(self):
        """
        Filters file data assuming logical OR rule

        Returns:
            _type_: _description_
        """
        filtered_revit_files_intermediate = []
        for file in self.revit_files:
            any_match_by_file = False
            # check each filter
            for filter in self.filter_rules:
                if filter in file.name:
                    # just one filters need to match...this is a match
                    # set flag accordingly
                    any_match_by_file = True
                    # one match is enough...move on
                    break
            # add file if any filters returned true
            if any_match_by_file:
                filtered_revit_files_intermediate.append(file)
        return filtered_revit_files_intermediate

    def TextBox_Filter_TextChanged(self):
        """
        Event handler for text changed in TextBox.
        """

        # break up filter text into individual rules if required
        if ";" in self.filter_text:
            self.filter_rules = [rule.strip() for rule in self.filter_text.split(";")]
        else:
            # just a single filter applied
            self.filter_rules = [self.filter_text]

        # clear the previous version of the filtered list
        self.filtered_revit_files.Clear()
        # set up a python vanilla list to contain filtered elements
        filtered_revit_files_intermediate = []

        # filter file data depending on filter type
        if self.filter_is_and:
            filtered_revit_files_intermediate = self._apply_and_to_file_data()
        else:
            filtered_revit_files_intermediate = self._apply_or_to_file_data()

        # transfer files from intermediate list to List[ObservableCollection]
        self.convert_list_to_observable_collection(
            filtered_revit_files_intermediate, self.filtered_revit_files
        )

    def _get_files(self):
        """
        Get initial, unfiltered file list
        """
        new_files = get_revit_files_for_processing(
            self.source_path, self.include_sub_dirs, self.source_file_extension
        )

        # convert past in files list
        self.convert_list_to_observable_collection(new_files, self.revit_files)

    def text_box_source_path_change(self):
        """
        when the source directory is changes
        """

        self._get_files()
        # update filtered list
        self.TextBox_Filter_TextChanged()

    def button_ok(self):
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

    def button_cancel(self):
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
