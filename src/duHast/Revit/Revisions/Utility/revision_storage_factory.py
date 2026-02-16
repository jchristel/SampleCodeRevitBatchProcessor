"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of factory functions relating to Revit revision on sheets storage classes.
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

from duHast.Revit.Revisions.Objects.Storage.revision_by_sheet_storage_alphanumeric import RevisionBySheetStorageAlphaNumeric
from duHast.Revit.Revisions.Objects.Storage.revision_by_sheet_storage_numeric import RevisionBySheetStorageNumeric
from duHast.Revit.Revisions.Objects.Storage.revision_by_sheet_storage_none import RevisionBySheetStorageNone


def get_revision_storage_sequence_numeric(revision, revision_sequence,revision_index_on_sheet,revision_are_by_sheet):
	"""
	Initializes the revision by sheet storage for numeric sequence type.
  
	:param revision: The Revit revision element.
	:type revision: Autodesk.Revit.DB.Revision
	:param revision_sequence: The Revit revision sequence element.
	:type revision_sequence: Autodesk.Revit.DB.RevisionSequence
	:param revision_index_on_sheet: The index of the revision on the sheet.
	:type revision_index_on_sheet: int
	:param revision_are_by_sheet: Flag indicating if revisions are by sheet.
	:type revision_are_by_sheet: bool
 
	:return: The revision by sheet storage numeric instance.
	:rtype: RevisionBySheetStorageNumeric
	"""

	settings = revision_sequence.GetNumericRevisionSettings()
	seq_number = RevisionBySheetStorageNumeric(
		revision_sequence.Id.Value, 
		revision,
		settings.Prefix,
		settings.Suffix,
		settings.StartNumber,
		settings.MinimumDigits,
		revision_index_on_sheet,
		revision_are_by_sheet
	)
	return seq_number
	

def get_revision_storage_sequence_alphanumeric(revision, revision_sequence,revision_index_on_sheet,revision_are_by_sheet):
	"""
	Initializes the revision by sheet storage for alphanumeric sequence type.
 
	:param revision: The Revit revision element.
	:type revision: Autodesk.Revit.DB.Revision
	:param revision_sequence: The Revit revision sequence element.
	:type revision_sequence: Autodesk.Revit.DB.RevisionSequence
	:param revision_index_on_sheet: The index of the revision on the sheet.
	:type revision_index_on_sheet: int
	:param revision_are_by_sheet: Flag indicating if revisions are by sheet.
	:type revision_are_by_sheet: bool
	:return: The revision by sheet storage alphanumeric instance.
	:rtype: RevisionBySheetStorageAlphaNumeric
	"""
 
	settings = revision_sequence.GetAlphanumericRevisionSettings()
	sequence = settings.GetSequence()
	seq_number=RevisionBySheetStorageAlphaNumeric(
		revision_sequence.Id.Value,
		revision,
		settings.Prefix,
		settings.Suffix,
		sequence,
		revision_index_on_sheet,
		revision_are_by_sheet
	)
	return seq_number


def get_revision_storage_sequence_none(revision, revision_index_on_sheet, revisions_are_by_sheet):
	"""
	Initializes the revision by sheet storage for 'None' sequence type.
	
	:param revision: The Revit revision element.
	:type revision: Autodesk.Revit.DB.Revision
	:param revision_index_on_sheet: The index of the revision on the sheet.
	:type revision_index_on_sheet: int
	:param revision_are_by_sheet: Flag indicating if revisions are by sheet.
	:type revision_are_by_sheet: bool
 
	:return: The revision by sheet storage none instance.
	:rtype: RevisionBySheetStorageNone
	"""
 
	seq_number=RevisionBySheetStorageNone(-1, revision,revision_index_on_sheet,revisions_are_by_sheet)
	return seq_number
