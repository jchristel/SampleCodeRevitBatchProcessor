#
#License:
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
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# import WPF creator and base window
import wpf
from System import Windows

# import settings class
import FileSelectSettings as set

# UI class
class MyWindow (Windows.Window):
    def __init__(self, xamlFullFileName, revitFiles, settings):
        wpf.LoadComponent(self,xamlFullFileName)
        # populate fields
        self.revitfiles = revitFiles
        self.files.ItemsSource = revitFiles
        self.tbSourceFolder.Text = settings.inputDir
        self.tbDestinationFolder.Text = settings.outputDir
        self.tbFileType.Text = settings.revitFileExtension
        self.tbNoOfFiles.Text = str(settings.outputFileNum)
        #disable editing of text boxes
    def BtnOK(self, sender, EventArgs):
        print('ok')
    
    def BtnCancel(self, sender, EventArgs):
        print('cancel')