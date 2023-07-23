"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class to store file select UI settings.
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

from duHast.Utilities.Objects import base

# An item to represent a file name in a row in a grid.
class FileSelectionSettings(base.Base):
    def __init__(
        self,
        inputDirectory,
        include_sub_dirs_in_search,
        output_directory,
        output_file_number,
        revitFileExtension,
    ):
        """
        Class constructor

        :param inputDirectory: A fully qualified directory path containing files to be shown in UI.
        :type inputDirectory: str
        :param include_sub_dirs_in_search: If True include subdirectories in file search, otherwise just root directory.
        :type include_sub_dirs_in_search: bool
        :param output_directory: A fully qualified directory path to where task files will be written.
        :type output_directory: str
        :param output_file_number: The number of task files to be written out.
        :type output_file_number: int
        :param revitFileExtension: A file extension filter applied to directory search.
        :type revitFileExtension: str
        """

        self.input_directory = inputDirectory
        self.incl_sub_dirs = include_sub_dirs_in_search
        self.output_dir = output_directory
        self.output_file_num = output_file_number
        self.revit_file_extension = revitFileExtension

        # ini super class to allow multi inheritance in children!
        super(FileSelectionSettings, self).__init__()
