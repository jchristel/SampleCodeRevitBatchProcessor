"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a class to store revision information by sheet with sequence type 'None'.
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
#

from duHast.Revit.Revisions.Objects.Storage.revision_by_sheet_storage_base import RevisionBySheetStorageBase

class RevisionBySheetStorageNone(RevisionBySheetStorageBase):
	"""
	Revision by sheet storage for sequence type 'None'.
	"""
 
	def __init__(self, revit_id,revit_revision, revision_index_on_sheet, revision_are_by_sheet):
		
		super(RevisionBySheetStorageNone, self).__init__(
            revit_id=revit_id,
            revit_revision=revit_revision, 
            revision_index_on_sheet=revision_index_on_sheet, 
            revision_are_by_sheet=revision_are_by_sheet
        )
		
	def get_revision(self, revision_index_on_sheet):
		"""
  		Gets the revision value for the given revision index on sheet. (Will always be None for 'None' sequence type)
    
		:param revision_index_on_sheet: The index of the revision on the sheet.
		:type revision_index_on_sheet: int
  
		:return: The revision value.
		:rtype: None
		"""
  
		return None

