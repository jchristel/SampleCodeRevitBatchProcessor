"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a class to store revision information by sheet with sequence type 'Numeric'.
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


class RevisionBySheetStorageNumeric(RevisionBySheetStorageBase):
	"""
	Revision by sheet storage for sequence type 'Numeric'.
	"""
	def __init__(self, revit_id,revit_revision, prefix,suffix,start_number,min_digits,revision_index_on_sheet,revision_are_by_sheet):
		"""
		Initializes the revision by sheet storage for numeric sequence type.
  
		:param revit_id: The Revit element id of the revision.
		:type revit_id: int
		:param revit_revision: The Revit revision element.
		:type revit_revision: Autodesk.Revit.DB.Revision
		:param prefix: The prefix for the revision number.
		:type prefix: str
		:param suffix: The suffix for the revision number.
		:type suffix: str
		:param start_number: The starting number for the revision sequence.
		:type start_number: int
		:param min_digits: The minimum number of digits for the revision number.
		:type min_digits: int
		:param revision_index_on_sheet: The index of the revision on the sheet.
		:type revision_index_on_sheet: int
		:param revision_are_by_sheet: Flag indicating if revisions are by sheet.
		:type revision_are_by_sheet: bool
		"""
  
		super(RevisionBySheetStorageNumeric, self).__init__(
			revit_id=revit_id,
			revit_revision=revit_revision, 
			revision_index_on_sheet=revision_index_on_sheet, 
			revision_are_by_sheet=revision_are_by_sheet
		)
  
		self._prefix=prefix
		self._suffix=suffix
		self._start_number=start_number
		self._min_digits=min_digits

	@property
	def revit_id(self):
		return self._revit_id

	@property
	def revit_revision(self):
		return self._revit_revision
		
	@property
	def prefix(self):
		return self._prefix
		
	@property
	def suffix(self):
		return self._suffix

	@property
	def start_number(self):
		return self._start_number

	@property
	def min_digits(self):
		return self._min_digits

	@property
	def revision_index_on_sheet(self):
		return self._revision_index_on_sheet
		
	def get_revision(self, revision_index_on_sheet):
		"""
		Gets the revision value for the given revision index on sheet.

		:param revision_index_on_sheet: The index of the revision on the sheet.
		:type revision_index_on_sheet: int
  
		:return: The revision value.
		:rtype: str
		"""
  
		if self._revision_are_by_sheet:
			# calculate the revision number
			rev = self._start_number+revision_index_on_sheet
			
			# format number to show min digits
			formatted_rev = "{:0{width}d}".format(rev, width=self._min_digits)
			
			# return the formatted revision
			return "{}{}{}".format(self._prefix, formatted_rev, self._suffix)
		else:
			# get the revision number property instead
			if self._revit_revision:
				return self._revit_revision.RevisionNumber
			else:
				raise ValueError("There is no Revit revision element available.")
