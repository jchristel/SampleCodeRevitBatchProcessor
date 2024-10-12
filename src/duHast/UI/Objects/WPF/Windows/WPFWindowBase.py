"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
An implementation of a custom wpf window base class which can be shown in the Revit context.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

clr.AddReference("PresentationFramework")
# clr.AddReference("PresentationCore")

from System.Windows import Window
from duHast.UI.Objects.WPF.Xaml.XamlLoader import XamlLoader


class WPFWindowBase(Window):
    def __init__(self, xaml_path, view_model):

        # make sure to initialize the base class
        super(WPFWindowBase, self).__init__()

        # load xaml data
        xaml = XamlLoader(xaml_path)

        # get the xaml root
        xaml_window = xaml.Root

        # Ensure xaml_window is of type Window and use it
        if isinstance(xaml_window, Window):
            self.Content = xaml_window.Content
            self.Title = xaml_window.Title
            self.Width = xaml_window.Width
            self.SizeToContent = xaml_window.SizeToContent
        else:
            self.Content = xaml_window

        # Set DataContext
        self.DataContext = view_model

        # Wire up the Closed event
        self.Closed += self.on_closed

    def on_closed(self, sender, event):
        # Handle cleanup here
        pass
