"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class to store file information.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
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

# An item to represent a file name in a row in a grid.

from duHast.Utilities.Objects import base


class MyFileItem(base.Base):
    def __init__(
        self,
        name,
        size,
        bim360_project_guid=None,
        bim360_file_guid=None,
        bim360_revit_version="-",
    ):
        """
        Class constructor.

        :param name: The fully qualified file path.
        :type name: str
        :param size: The file size.
        :type size: int
        :param  bim360_project_guid: The BIM360 project GUID, defaults to None
        :type  bim360_project_guid: str, optional
        :param bim360_file_guid: The BIM360 file GUID, defaults to None
        :type bim360_file_guid: str, optional
        :param bim360_revit_version: The revit file version (year only), defaults to '-'
        :type bim360_revit_version: str, optional
        """

        # ini super class to allow multi inheritance in children!
        super(MyFileItem, self).__init__()

        self.name = name
        self.size = size
        self.bim_360_project_guid = bim360_project_guid
        self.bim_360_file_guid = bim360_file_guid
        self.bim_360_revit_version = bim360_revit_version
