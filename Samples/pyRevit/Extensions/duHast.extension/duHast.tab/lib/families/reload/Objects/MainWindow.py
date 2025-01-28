# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The class representing the main window of the app.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from duHast.UI.Objects.WPF.Windows.WPFWindowBase import WPFWindowBase


class Reloader(WPFWindowBase):

    def __init__(
        self, xaml_path, main_view_model, xaml_by_view_model, resources_xaml_path
    ):
        """
        A window for the reloader app.

        :param xaml_path: path to the XAML file
        :type xaml_path: str
        :param main_view_model: the main view model
        :type main_view_model: :class:`.FamiliesSelectionViewModel`
        :param xaml_by_view_model: a dictionary mapping view models to XAML files
        :type xaml_by_view_model: dict
        :param resources_xaml_path: path to the resources XAML file
        :type resources_xaml_path: str
        """

        super(Reloader, self).__init__(
            xaml_path, main_view_model, xaml_by_view_model, resources_xaml_path
        )

        # Set the height of the window
        self.Height = 400  # Set to your desired height

        # Additional window setup can go here
        self.Title = "Reload(er)"
