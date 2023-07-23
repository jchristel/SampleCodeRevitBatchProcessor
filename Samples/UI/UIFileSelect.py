'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A file selection GUI.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# import WPF creator and base window
import wpf
from System import Windows
import ctypes

# import settings class
#from duHast.UI import FileSelectSettings as set

def Mbox(title, text, style):
    '''
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
    '''

    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

# UI class
class MyWindow (Windows.Window):
    def __init__(self, xamlFullFileName, revitFiles, settings):
        '''
        Class constructor

        :param xamlFullFileName: Fully qualified file path to wpf XAML file.
        :type xamlFullFileName: str
        :param revitFiles: List containing path to files.
        :type revitFiles: [str]
        :param settings: A settings object.
        :type settings: :class:`.FileSelectionSettings`
        '''
        
        wpf.LoadComponent(self,xamlFullFileName)

        # populate fields
        self.selectedFiles = []
        self.revitfiles = revitFiles
        self.files.ItemsSource = revitFiles
        self.tbSourceFolder.Text = settings.inputDir
        self.tbDestinationFolder.Text = settings.outputDir
        self.tbFileType.Text = settings.revitFileExtension
        self.tbNoOfFiles.Text = str(settings.outputFileNum)
        self.cbInclSubDirs.IsChecked = settings.inclSubDirs
        
    def BtnOK(self, sender, EventArgs):
        '''
        Ok button event handler.

        Gets the selected rows of files and adds them to .selectedFiles property
        Sets the dialog result value to True.

        :param sender: _description_
        :type sender: _type_
        :param EventArgs: _description_
        :type EventArgs: _type_
        '''

        # get selected items
        rows = self.files.SelectedItems
        if(rows != None and len(rows) > 0):
            self.selectedFiles = []
            for row in rows:
                # get the original file element
                for oRev in self.revitfiles:
                    if(oRev.name == row.name):
                        self.selectedFiles.append(oRev)
                        break
            # Mbox('ok',str(len(self.selectedFiles)), 1)
            self.DialogResult = True
            self.Close()
        else:
            Mbox('Attention','No files selected', 1)
    
    def BtnCancel(self, sender, EventArgs):
        '''
        Cancel button event handler.
        Sets the dialogue result value to False.

        :param sender: _description_
        :type sender: _type_
        :param EventArgs: _description_
        :type EventArgs: _type_
        '''
        
        #print('cancel')
        self.DialogResult = False
        self.Close()