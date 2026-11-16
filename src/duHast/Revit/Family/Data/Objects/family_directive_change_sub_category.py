"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family sub category change directives.
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

from duHast.Revit.Family.Data.Objects.family_directive_base import FamilyDirectiveBase


class FamilyDirectiveChangeSubCategory(FamilyDirectiveBase):

    # directive file row structure (no header row)
    CHANGE_SUB_CATEGORY_DIRECTIVE_INDEX_FAMILY_CATEGORY = 0
    CHANGE_SUB_CATEGORY_DIRECTIVE_INDEX_OLD_SUB_CATEGORY_NAME = 1
    CHANGE_SUB_CATEGORY_DIRECTIVE_INDEX_NEW_SUB_CATEGORY_NAME = 2

    # file name identifiers for sub category change directives
    CHANGE_SUB_CATEGORY_DIRECTIVE_FILE_NAME_PREFIX = "SubCategoryChangeDirective"
    CHANGE_SUB_CATEGORY_DIRECTIVE_FILE_EXTENSION = ".csv"

    EXCEPTION_NO_CHANGE_SUB_CATEGORY_DIRECTIVE_FILES = (
        "Sub category change directive file does not exist."
    )
    EXCEPTION_EMPTY_CHANGE_SUB_CATEGORY_DIRECTIVE_FILES = (
        "Empty sub category change directive file!"
    )

    def __init__(self, category, old_sub_category_name, new_sub_category_name):
        """
        A directive to rename a sub category in all families of a Revit category.

        :param category: The Revit category of the families to change.
        :type category: str
        :param old_sub_category_name: The current sub category name.
        :type old_sub_category_name: str
        :param new_sub_category_name: The new sub category name.
        :type new_sub_category_name: str
        """

        # the directive applies to all families of the category
        super(FamilyDirectiveChangeSubCategory, self).__init__(
            name=None, category=category
        )
        self.old_sub_category_name = old_sub_category_name
        self.new_sub_category_name = new_sub_category_name
