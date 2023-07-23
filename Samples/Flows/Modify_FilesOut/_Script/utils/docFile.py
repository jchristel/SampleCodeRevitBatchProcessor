"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class used to store file meta data.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# import settings
import settings as settings  # sets up all commonly used variables and path locations!
from duHast.Utilities.Objects import base as base


class docFile(base.Base):
    """
    a class used to store file date for renaming
    """

    def __init__(self, data):
        super(docFile, self).__init__()

        try:
            self.existing_file_name = data[0]
            self.file_extension = data[4]
            self.file_name_new_parts = []
            self.file_name_new_parts.append(data[1])
            if len(data[3]) > 0:
                self.file_name_new_parts.append(data[3])
            if len(data[2]) > 0:
                self.revision = data[2]
            else:
                self.revision = "-"
            self.aconex_doc_number = data[5]
            self.aconex_doc_name = data[6]
            self.new_revision = False
        except Exception as e:
            print(str(e))
            pass

    def get_new_file_name(self):
        """
        returns the file name including revision information

        :return: _description_
        :rtype: _type_
        """

        suffix = ""
        if len(self.file_name_new_parts) > 1:
            suffix = self.file_name_new_parts[1]
        return (
            self.file_name_new_parts[0] + self.revision + suffix
        )  # ignore revision brackets

    def get_data(self):
        """
        returns a list of all property values of this class

        :return: list of file properties
        :rtype: [str]
        """

        return_value = []
        return_value.append(self.existing_file_name)
        return_value.append(self.file_name_new_parts[0])
        return_value.append(self.revision)
        if len(self.file_name_new_parts) > 1:
            return_value.append(self.file_name_new_parts[1])
        else:
            return_value.append("")
        return_value.append(self.file_extension)
        return_value.append(self.aconex_doc_number)
        return_value.append(self.aconex_doc_name)
        return return_value

    def update_numerical_rev(self):
        """
        Increase the numerical revision by +1. If start revision value is "-", numerical revision is set to 1.
        """

        try:
            # default start value
            rev = 1
            # check if start value is to be applied
            if self.revision != "-":
                rev = int(self.revision)
                rev = rev + 1
            # apply new rev value as string
            self.revision = str(rev)
        except Exception as e:
            # no need to do anything
            self.revision = self.revision
