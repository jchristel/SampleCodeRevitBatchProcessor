"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family instances of type swap directives.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

#
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


from duHast.Revit.Family.Data.Objects.family_directive_base import FamilyDirectiveBase

class FamilyDirectiveSwap(FamilyDirectiveBase):
    SWAP_DIRECTIVE_LIST_INDEX_SOURCE_FAMILY_NAME = 0
    SWAP_DIRECTIVE_LIST_INDEX_SOURCE_FAMILY_CATEGORY_NAME = 1
    SWAP_DIRECTIVE_LIST_INDEX_SOURCE_FAMILY_TYPE_NAME = 2
    SWAP_DIRECTIVE_LIST_TARGET_FAMILY_NAME = 3
    SWAP_DIRECTIVE_LIST_TARGET_FAMILY_TYPE = 4

    # file name identifiers for rename directives
    SWAP_DIRECTIVE_FILE_NAME_PREFIX = "SwapDirective"
    SWAP_DIRECTIVE_FILE_EXTENSION = ".csv"

    EXCEPTION_NO_SWAP_DIRECTIVE_FILES = "Swap directive file does not exist."
    EXCEPTION_EMPTY_SWAP_DIRECTIVE_FILES = "Empty swap directive file!"

    def __init__(
        self, name, category, source_type_name, target_family_name, target_family_type_name
    ):
        super(FamilyDirectiveSwap, self).__init__(name=name, category=category)

        self.source_type_name = source_type_name
        self.target_family_name = target_family_name
        self.target_family_type_name = target_family_type_name