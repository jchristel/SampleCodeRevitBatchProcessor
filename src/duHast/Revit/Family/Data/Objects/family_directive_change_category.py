"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family category change directives.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
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

import os

from duHast.Revit.Family.Data.Objects.family_directive_base import FamilyDirectiveBase


class FamilyDirectiveChangeCategory(FamilyDirectiveBase):

    # directive file row structure (no header row)
    CHANGE_CATEGORY_DIRECTIVE_INDEX_FAMILY_FILE_PATH = 0
    CHANGE_CATEGORY_DIRECTIVE_INDEX_NEW_CATEGORY_NAME = 1

    # file name identifiers for category change directives
    CHANGE_CATEGORY_DIRECTIVE_FILE_NAME_PREFIX = "CategoryChangeDirective"
    CHANGE_CATEGORY_DIRECTIVE_FILE_EXTENSION = ".csv"

    EXCEPTION_NO_CHANGE_CATEGORY_DIRECTIVE_FILES = (
        "Category change directive file does not exist."
    )
    EXCEPTION_EMPTY_CHANGE_CATEGORY_DIRECTIVE_FILES = (
        "Empty category change directive file!"
    )

    def __init__(self, file_path, new_category_name):
        """
        A directive to change the category of a family.

        :param file_path: Fully qualified file path of the family.
        :type file_path: str
        :param new_category_name: The Revit category the family is to be changed to.
        :type new_category_name: str
        """

        # the family name is the file name, the current category is not part of the directive
        super(FamilyDirectiveChangeCategory, self).__init__(
            name=os.path.splitext(os.path.basename(file_path))[0], category=None
        )
        self.file_path = file_path
        self.new_category_name = new_category_name
