"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family rename directives.
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


from duHast.Revit.Family.Data.Objects.family_directive_base import FamilyDirectiveBase

class FamilyDirectiveCopy(FamilyDirectiveBase):
    COPY_DIRECTIVE_LIST_INDEX_CURRENT_FAMILY_NAME = 0
    COPY_DIRECTIVE_INDEX_FAMILY_FILE_PATH = 1
    COPY_DIRECTIVE_INDEX_CATEGORY = 2
    COPY_DIRECTIVE_LIST_INDEX_NEW_FAMILY_NAME = 3
    COPY_DIRECTIVE_LIST_INDEX_NEW_DIRECTORY = 4

    # file name identifiers for rename directives
    COPY_DIRECTIVE_FILE_NAME_PREFIX = "CopyDirective"
    COPY_DIRECTIVE_FILE_EXTENSION = ".csv"

    EXCEPTION_NO_COPY_DIRECTIVE_FILES = "Copy directive file does not exist."
    EXCEPTION_EMPTY_COPY_DIRECTIVE_FILES = "Empty copy directive file!"

    def __init__(
        self, name, category, source_file_path, target_directory, new_name
    ):
        super(FamilyDirectiveCopy, self).__init__(name=name, category=category)

        self.source_file_path = source_file_path
        self.target_directory = target_directory
        self.new_name = new_name