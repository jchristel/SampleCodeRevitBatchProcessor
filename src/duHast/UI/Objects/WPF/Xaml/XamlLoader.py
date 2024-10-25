"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class to load xaml files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on:

https://markheath.net/post/wpf-and-mvvm-in-ironpython

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

import codecs
from System.Windows.Markup import XamlReader


class XamlLoader(object):
    def __init__(self, xaml_path):
        """
        Loads a XAML file and provides access to its objects.

        :param xaml_path: The path to the XAML file to load
        :type xaml_path: str
        """
        self.Root = self.load_xaml(xaml_path)

    def load_xaml(self, xaml_path):
        """
        Load the XAML file and parse it.

        :param xaml_path: The path to the XAML file to load
        :type xaml_path: str
        :return: The root element of the loaded XAML
        :rtype: System.Windows.UIElement
        """
        # Read the XAML fil
        with codecs.open(xaml_path, 'r', encoding='utf-8-sig') as file:
            xaml_content = file.read()

        # Parse the XAML content
        return XamlReader.Parse(xaml_content)

    def __getattr__(self, item):
        """
        Maps values to attributes.
        Only called if there *isn't* an attribute with this name.

        :param item: The name of the attribute
        :return: The value of the attribute, if found
        """
        if hasattr(self.Root, "FindName"):
            return self.Root.FindName(item)
        raise AttributeError(
            "{} object has no attribute {}".format(self.__class__.__name__, item)
        )
