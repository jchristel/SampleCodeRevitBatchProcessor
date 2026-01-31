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


class RevisionBySheetStorageAlphaNumeric(RevisionBySheetStorageBase):
	"""
	Revision by sheet storage for sequence type 'Alpha Numeric'.
	"""
	def __init__(self, revit_id, revit_revision,prefix,suffix, sequence,revision_index_on_sheet,revision_are_by_sheet):
		"""
		Initializes the revision by sheet storage for alphanumeric sequence type.
  
		:param revit_id: The Revit element id of the revision.
		:type revit_id: int
		:param revit_revision: The Revit revision element.
		:type revit_revision: Autodesk.Revit.DB.Revision
		:param prefix: The prefix for the revision number.
		:type prefix: str
		:param suffix: The suffix for the revision number.
		:type suffix: str
		:param sequence: The alphanumeric sequence for the revision.
		:type sequence: [str]
		:param revision_index_on_sheet: The index of the revision on the sheet.
		:type revision_index_on_sheet: int
		:param revision_are_by_sheet: Flag indicating if revisions are by sheet.
		:type revision_are_by_sheet: bool
		"""
  
		super(RevisionBySheetStorageAlphaNumeric, self).__init__(
			revit_id=revit_id,
			revit_revision=revit_revision, 
			revision_index_on_sheet=revision_index_on_sheet, 
			revision_are_by_sheet=revision_are_by_sheet
        )
		
		self._prefix=prefix
		self._suffix=suffix
		self._sequence = sequence
		

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
	def sequence(self):
		return self._sequence
	
	@property
	def revision_index_on_sheet(self):
		return self._revision_index_on_sheet
	
	def index_to_revision(self, index):
		"""
		Convert a sequential index to Revit revision format.

		Revit assigns alphanumerical revisions to a sheet as follows:

		Assume pre defined revision sequence contains letters: A,B,C
		Revisions on sheet look like so:

		1st revision A (within sequence, sequence repetition is 1)
		2nd revision B
		3rd revision C
		4th revision AA (outside of sequence, start with first letter again  n times, where n is the number of sequence repetitions, here 2)
		5th revision BB
		6th revision CC
		7th revision AAA (outside of sequence, start with first letter again n times, where n is the number of sequence repetitions, here 3)
		8th revision BBB
		9th revision CCC

		And so on.

		Args:
			index: Sequential index (1-based, e.g., 1, 2, 3, 4...)

		Returns:
			Revision string (e.g., 'A', 'B', 'C', 'AA', 'BB', etc.)
		"""
		if index < 1:
			return None
	    
		base = len(self._sequence)
	    
	    # Determine how many repetitions of the letter
		repetitions = 1
		cumulative = 0
	    
		while cumulative + base < index:
			cumulative += base
			repetitions += 1
	    
	    # Find which letter in the sequence
		position = index - cumulative - 1
		letter = self._sequence[position]
	    
		# Return the letter repeated
		return letter * repetitions
    
	def get_revision(self, revision_index_on_sheet):
		"""
		Gets the revision value for the given revision index on sheet.

		:param revision_index_on_sheet: The index of the revision on the sheet.
		:type revision_index_on_sheet: int
  
		:return: The revision value.
		:rtype: str
		"""
  
		if self._revision_are_by_sheet:
			# get the revision string from the sequence
			rev = self.index_to_revision(revision_index_on_sheet)
			
			# build the complete revision string inluding pre and suffix
			return "{}{}{}".format(self._prefix,rev,self._suffix)
		else:
			# get the revision number property instead
			if self._revit_revision:
				return self._revit_revision.RevisionNumber
			else:
				raise ValueError("There is no Revit revision element available.")
				
