"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class used to implement deleted and modified element counts when using purge by delete.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adjust deleted and modified elements if necessary:
this might be required where an element is presented through 2 or more elements in the revit api:
e.g. a line style is represented to a line style and a graphics style
this function will only purge elements which result in only 1 element  deleted and no other element modified
hence a delete modifier should check the deleted elements and if appropriate return only one element to be deleted
same applies to modified elements: a custom modifier should return 0 elements if appropriate in order for the element to be purged
   
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

from duHast.Utilities.Objects import base


class ModifierBase(base.Base):
    def __init__(self):
        """
        Class constructor.

        """

        super(ModifierBase, self).__init__()

    def modify_deleted(self, doc, deleted):
        """
        Base implementation to modify the deleted element count.

        Returns deleted element list unchanged

        Args:
            deleted: The deleted element count

        """

        if isinstance(deleted, list) == False:
            raise TypeError("deleted must be a list")

        return deleted

    def modify_modified(self, doc, modified):
        """
        Base implementation to modify the modified element count.

        Returns modified element list unchanged

        Args:
            modified: The modified element count

        """

        if isinstance(modified, list) == False:
            raise TypeError("modified must be a list")

        return modified
