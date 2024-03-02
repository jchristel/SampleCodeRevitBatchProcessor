
from ViewModelBase import ViewModelBase
from Command import Command

class ViewModel(ViewModelBase):
    def __init__(
        self,
        window,
        directory_source_path, 
        directory_destination_path,
        source_file_extension,
        number_of_task_files,
        include_sub_dirs,
        filter_text
        ):
        
        ViewModelBase.__init__(self)
        self.window = window
        
        self.revit_files = []
        self.selected_files = []
        self.source_path = directory_source_path
        self.destination_path = directory_destination_path
        self.source_file_extension = source_file_extension
        self.number_of_task_files = number_of_task_files
        self.include_sub_dirs = include_sub_dirs
        self.filter_text = filter_text
        
        # hook up ok and cancel buttons
        self.BtnOkCommand = Command(self.BtnOK)
        self.BtnCancelCommand = Command(self.BtnCancel)
    
    
    def _HandleFileChange(self):
        '''
        _summary_
        '''
        
        pass
        
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
        self.window.Close()
        """
        # get selected items
        rows = self.files.SelectedItems
        if rows != None and len(rows) > 0:
            self.selected_files = []
            for row in rows:
                # get the original file element
                for o_rev in self.revit_files:
                    if o_rev.name == row.name:
                        self.selected_files.append(o_rev)
                        break
            # Mbox('ok',str(len(self.selectedFiles)), 1)
            self.DialogResult = True
            self.window.Close()
        else:
            self.window.Close()
            # pass
            #Mbox("Attention", "No files selected", 1)
        """
        
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
        #self.Close()
    
    def TextBoxSourcePath_TextChanged(self):
        '''
        Source Path text box change event handler

        :param sender: _description_
        :type sender: _type_
        :param TextChangedEventArgs: _description_
        :type TextChangedEventArgs: _type_
        '''

        self.source_path = "ohj dea"
    
    def CheckBoxSubDir_Checked(self,):
        '''
        _summary_

        :param sender: _description_
        :type sender: _type_
        :param RoutedEventArgs: _description_
        :type RoutedEventArgs: _type_
        '''
        self._HandleFileChange()

    def CheckBoxSubDir_UnChecked(self):
        '''
        _summary_

        :param sender: _description_
        :type sender: _type_
        :param RoutedEventArgs: _description_
        :type RoutedEventArgs: _type_
        '''
        self._HandleFileChange()