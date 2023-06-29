"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A file selection GUI.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("IronPython.Wpf")

# import WPF creator and base window
import wpf
from System import Windows
import ctypes

# import settings class
# from duHast.UI import FileSelectSettings as set
def Mbox(title, text, style):
    """
    A simple win forms message box.

    :param title: The title of the message box.
    :type title: str
    :param text: The text displayed in the message box.
    :type text: str
    :param style: An int representing the type of buttons shown.
        (https://docs.microsoft.com/en-us/dotnet/api/system.windows.forms.messageboxbuttons?view=windowsdesktop-6.0)
    :type style: int

    :return: A win form message box.
    :rtype: _type_
    """

    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


# UI class
class MyWindow(Windows.Window):
    def __init__(self, xaml_full_file_name, revitFiles, settings):
        """
        Class constructor

        :param xaml_full_file_name: Fully qualified file path to wpf XAML file.
        :type xaml_full_file_name: str
        :param revitFiles: List containing path to files.
        :type revitFiles: [str]
        :param settings: A settings object.
        :type settings: :class:`.FileSelectionSettings`
        """

        wpf.LoadComponent(self, xaml_full_file_name)

        # populate fields
        self.selectedFiles = []
        self.revitfiles = revitFiles
        self.files.ItemsSource = revitFiles
        self.tbSourceFolder.Text = settings.input_directory
        self.tbDestinationFolder.Text = settings.output_dir
        self.tbFileType.Text = settings.revit_file_extension
        self.tbNoOfFiles.Text = str(settings.output_file_num)
        self.cbInclSubDirs.IsChecked = settings.incl_sub_dirs

    def BtnOK(self, sender, EventArgs):
        """
        Ok button event handler.

        Gets the selected rows of files and adds them to .selectedFiles property
        Sets the dialog result value to True.

        :param sender: _description_
        :type sender: _type_
        :param EventArgs: _description_
        :type EventArgs: _type_
        """

        # get selected items
        rows = self.files.SelectedItems
        if rows != None and len(rows) > 0:
            self.selectedFiles = []
            for row in rows:
                # get the original file element
                for o_rev in self.revitfiles:
                    if o_rev.name == row.name:
                        self.selectedFiles.append(o_rev)
                        break
            # Mbox('ok',str(len(self.selectedFiles)), 1)
            self.DialogResult = True
            self.Close()
        else:
            Mbox("Attention", "No files selected", 1)

    def BtnCancel(self, sender, EventArgs):
        """
        Cancel button event handler.
        Sets the dialogue result value to False.

        :param sender: _description_
        :type sender: _type_
        :param EventArgs: _description_
        :type EventArgs: _type_
        """

        # print('cancel')
        self.DialogResult = False
        self.Close()
