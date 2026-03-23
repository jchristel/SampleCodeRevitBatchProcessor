"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains helper functions for retrieving Revit revisions from sheets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the complete revision history of a sheet, without using a revision schedule, use this module.

The flow is as follows:

1. Check if revisions vary by sheet or are project-wide
2. Get all revision IDs from the sheet using ViewSheet.GetAllRevisionIds()
3. Loop over each revision ID and get the revision element using Document.GetElement(revisionId)
4. For each revision:
   - Get the revision sequence ID using Revision.RevisionNumberingSequenceId
   - Determine the sequence type (Numeric, Alphanumeric, or None)
   - Create appropriate storage object based on sequence type:
     - Numeric: Uses prefix, suffix, start number, and minimum digits
     - Alphanumeric: Uses prefix, suffix, and predefined sequence
     - None: Uses the revision's RevisionNumber property directly
   - Store the revision data with its index position on the sheet

5. Build a dictionary with revision sequence ID as key and list of storage objects as values
   - Each storage object tracks:
     - The revision element
     - Its index on the sheet (for maintaining original order)
     - The sequence settings needed to generate the revision value

6. Build the final revision data list by:
   - Iterating through sheet positions (0 to number of revisions)
   - Finding the matching storage object for each position
   - Generating the actual revision value using the storage object's sequence counter
   - Pairing the revision value with its Revit element

7. Return list of tuples: (revision_value, revision_element) in sheet order


General notes:

- In alphanumeric mode: if the number of revisions exceeds the entries in the predefined sequence, 
  the sequence continues with A,B,C...Z,AA,BB,CC,AAA,BBB,CCC and so on.
- The module handles both "revisions vary by sheet" and "same revisions for all sheets" scenarios 
  through the storage objects' internal logic.
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

from duHast.Revit.Revisions.Utility.revision_storage_factory import get_revision_storage_sequence_numeric, get_revision_storage_sequence_alphanumeric, get_revision_storage_sequence_none
from duHast.Revit.Revisions.revisions import are_revisions_by_sheet

from Autodesk.Revit.DB import ElementId, RevisionNumberType

DEBUG = False

def build_revision_data(rev_dictionary, number_of_revs_on_sheet):
	"""
	Builds the revision data list from the revision dictionary and number of revisions on sheet.
	:param rev_dictionary: The revision dictionary with sequence id as key and list of revision by sheet storage instances as value.
	:type rev_dictionary: dict
	:param number_of_revs_on_sheet: The number of revisions on the sheet.
	:type number_of_revs_on_sheet: int
 
	:return: The list of revision data tuples (revision value, revision Revit element).
	:rtype: [(str, Autodesk.Revit.DB.Revision)]
	"""
 
	data = []
	
	# loop over all revisions on a sheet by index
	for i in range(0, number_of_revs_on_sheet):
		
		# set default flag to false
		found_match = False
		
		# loop over items and build a revision data
		for sequence_id, revision_data_list in rev_dictionary.items():
			if DEBUG:
				print("checking sequence id: {}".format(sequence_id))
				print("revision data list length: {}".format(len(revision_data_list)))
			# setup counter by type
			seq_by_revision_type_counter = 0
			for rev_data_entry in revision_data_list:
				
				# check if this revision index, stored in a tuple at index 1, is matching the current sheet index 
				if rev_data_entry.revision_index_on_sheet == i:
					if DEBUG:
						print("found match for sheet index: {} with revision value: {} with type index: {}".format(i, rev_data_entry.get_revision(seq_by_revision_type_counter), seq_by_revision_type_counter))
					# get the actual revision value from the first value in the tuple which is a 
					# helper class instance stored in tuple at index 0
					revision_value = rev_data_entry.get_revision(seq_by_revision_type_counter)
					
					# get the revit revision object instance
					revision_revit_element = rev_data_entry.revit_revision
					
					# build data
					data.append((revision_value, revision_revit_element))
					
					# set flag
					found_match = True
					# time to move to next
					break
				
				# increase counter
				seq_by_revision_type_counter = seq_by_revision_type_counter + 1
			
			if found_match:
				break
			
	return data


def get_revisions_from_sheet(doc, sheet):
	"""
	Gets the revisions from a sheet.
 
	:param doc: The Revit document.
	:type doc: Autodesk.Revit.DB.Document
	:param sheet: The Revit sheet (ViewSheet).
	:type sheet: Autodesk.Revit.DB.ViewSheet
 
	:return: The list of revision data tuples (revision value, revision Revit element).
	:rtype: [(str, Autodesk.Revit.DB.Revision)]
	"""
	
	# check if revisions are by sheet or by project
	revisions_are_by_sheet = are_revisions_by_sheet(doc)
	
	# get all revision ids on sheet
	# note: Autodesk docs say: "The Revisions are ordered according to the revision sequence in the project." I have had cases where this was not true.
	revision_ids_on_sheet = sheet.GetAllRevisionIds()
	
	# Convert .NET IList to Python list, then sort by SequenceNumber to be sure of order
	revision_ids_on_sheet = sorted(
    	list(revision_ids_on_sheet),
    	key=lambda rev_id: doc.GetElement(rev_id).SequenceNumber
	)

	# check if any revisions on sheet
	if (len(revision_ids_on_sheet) == 0):
		return None
	
	# revision index counter
	rev_index_on_sheet = 0
	
	# revision data dictionary
	revision_data = {}
	
	# loop over all revisions on sheet
	for revision_id in revision_ids_on_sheet:
		revision = doc.GetElement(revision_id)
  
		if DEBUG:
			print("processing revision id: {} with rev number: {}".format(revision.Id, revision.RevisionNumber))
   
		revision_sequence_id = revision.RevisionNumberingSequenceId
		
		# a class generating the actual revision number
		rev_sequence_generator = None
		
		# check if this is a None revision
		if revision_sequence_id == ElementId.InvalidElementId:
			rev_sequence_generator = get_revision_storage_sequence_none(revision,rev_index_on_sheet,revisions_are_by_sheet)
   
			if DEBUG:
				print("none revision: {}".format(rev_sequence_generator))
		else:
			
			# get the revision sequence
			revision_sequence = doc.GetElement(revision_sequence_id)
		
			# check what type of sequence and get helper class accordingly
			if (revision_sequence.NumberType ==  RevisionNumberType.Numeric):
				rev_sequence_generator = get_revision_storage_sequence_numeric(revision,revision_sequence,rev_index_on_sheet,revisions_are_by_sheet)
				if DEBUG:
					print("numeric revision: {}".format(rev_sequence_generator))
			elif (revision_sequence.NumberType ==  RevisionNumberType.Alphanumeric):
				rev_sequence_generator = get_revision_storage_sequence_alphanumeric(revision,revision_sequence,rev_index_on_sheet,revisions_are_by_sheet)
				if DEBUG:
					print("alphanumeric revision: {}".format(rev_sequence_generator))
			else:
				raise ValueError("Not supported")
		
		# generate a node if there isnt one already
		if rev_sequence_generator.revit_id not in revision_data:
			revision_data[rev_sequence_generator.revit_id] = []
		
		# add the generator and index to the dictionary
		revision_data[rev_sequence_generator.revit_id].append(rev_sequence_generator)
		
		# increase revision index counter
		rev_index_on_sheet = rev_index_on_sheet + 1
		
	# build revision data
	formatted_data = build_revision_data(revision_data, revision_ids_on_sheet.Count)
	
	return formatted_data
