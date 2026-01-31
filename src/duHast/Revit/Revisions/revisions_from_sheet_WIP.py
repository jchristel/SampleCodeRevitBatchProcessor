def get_all_sheets(doc):
    """
    Gets all sheets in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list of sheet views
    :rtype: list of Autodesk.Revit.DB.View
    """

    collector_views = FilteredElementCollector(doc).OfClass(ViewSheet)
    return collector_views

class SequenceBase():
	"""
	Revision sequence utility base class
	"""
	
	def __init__(self, revit_id,revit_revision, revision_index_on_sheet):
		
		self._revit_id=revit_id
		self._revit_revision = revit_revision
		self._revision_index_on_sheet = revision_index_on_sheet
		
	@property
	def revit_id(self):
		return self._revit_id

	@property
	def revit_revision(self):
		return self._revit_revision
		
	@property
	def revision_index_on_sheet(self):
		return self._revision_index_on_sheet
	
	def get_revision(self, revision_index_on_sheet):
		return None

class SequenceNone():
	def __init__(self, revit_id,revit_revision, revision_index_on_sheet):
		
		self._revit_id=revit_id
		self._revit_revision = revit_revision
		self._revision_index_on_sheet = revision_index_on_sheet
		
	@property
	def revit_id(self):
		return self._revit_id

	@property
	def revit_revision(self):
		return self._revit_revision
		
	@property
	def revision_index_on_sheet(self):
		return self._revision_index_on_sheet
	
	def get_revision(self, revision_index_on_sheet):
		return None


class SequenceNumeric():
	def __init__(self, revit_id,revit_revision, prefix,suffix,start_number,min_digits,revision_index_on_sheet):
		
		self._revit_id=revit_id
		self._revit_revision = revit_revision
		self._prefix=prefix
		self._suffix=suffix
		self._start_number=start_number
		self._min_digits=min_digits
		self._revision_index_on_sheet = revision_index_on_sheet

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
		
		# calculate the revision number
		rev = self._start_number+revision_index_on_sheet
		
		# format number to show min digits
		formatted_rev = "{:0{width}d}".format(rev, width=self._min_digits)
		
		return "{}{}{}".format(self._prefix, formatted_rev, self._suffix)	


class SequenceAlphaNumeric():
	def __init__(self, revit_id, revit_revision,prefix,suffix, sequence,revision_index_on_sheet):
		
		self._revit_id=revit_id
		self._revit_revision = revit_revision
		self._prefix=prefix
		self._suffix=suffix
		self._sequence = sequence
		self._revision_index_on_sheet = revision_index_on_sheet

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
		
		# get the revision string from the sequence
		rev = self.index_to_revision(revision_index_on_sheet)
		
		# build the complete revision string inluding pre and suffix
		return "{}{}{}".format(self._prefix,rev,self._suffix)	


def get_sequence_numeric(revision, revision_sequence,revision_index_on_sheet):
	settings = revision_sequence.GetNumericRevisionSettings()
	seq_number = SequenceNumeric(
		revision_sequence.Id.Value, 
		revision,
		settings.Prefix,
		settings.Suffix,
		settings.StartNumber,
		settings.MinimumDigits,
		revision_index_on_sheet
	)
	return seq_number
	

def get_sequence_alphanumeric(revision, revision_sequence,revision_index_on_sheet):
	settings = revision_sequence.GetAlphanumericRevisionSettings()
	sequence = settings.GetSequence()
	seq_number=SequenceAlphaNumeric(
		revision_sequence.Id.Value,
		revision,
		settings.Prefix,
		settings.Suffix,
		sequence,
		revision_index_on_sheet
	)
	return seq_number

def get_sequence_none(revision, revision_index_on_sheet):
	seq_number=SequenceNone(ElementId.InvalidElementId, revision,revision_index_on_sheet)
	return seq_number


def build_revision_data(rev_dictionary, number_of_revs_on_sheet):
	
	print("\nbuilding revision data...from {} revision on sheet\n".format(number_of_revs_on_sheet))
	data = []
	
	# start getting data in order of revisions on sheet
	index_counter = 0
	
	# loop over all revisions on a sheet by index
	for i in range(0, number_of_revs_on_sheet):
		print ("...checking revision on sheet of index: {}".format(i))
		
		# set default flag to false
		found_match = False
		
		# loop over items and build a revision data
		for sequence_id, revision_data_list in rev_dictionary.items():
			
			# setup counter by type
			seq_by_revision_type_counter = 0
			for rev_data_entry in revision_data_list:
				
				# check if this revision index, stored in a tuple at index 1, is matching the current sheet index 
				if rev_data_entry.revision_index_on_sheet == i:
					
					# get the actual revision value from the first value in the tuple which is a 
					# helper class inststance stored in tuple at index 0
					revision_value = rev_data_entry.get_revision(seq_by_revision_type_counter)
					
					# get the revit revision object instance
					revision_revit_element = rev_data_entry.revit_revision
					
					print ("...found match. Revision value: {}".format(revision_value))
					
					# build data
					data.append((revision_value, revision_revit_element))
					
					# set flag
					found_match = True
					# time to move to next
					break
					
				seq_by_revision_type_counter = seq_by_revision_type_counter + 1
			
			if found_match:
				break
			
			index_counter = index_counter +1
	return data
		

def get_revisions(doc, sheet):
	"""
	Generates a dictionary where the key is the revision sequence id as an int and the value is a list of duHast sequence utility
	classes each representing a revision on the sheet belonging to the Revit revision sequence
	"""
	revision_ids_on_sheet = sheet.GetAllRevisionIds()
	
	# check if any revisions on sheet
	if (revision_ids_on_sheet.Count == 0):
		return None
	
	revision_data = []
	
	# revision index counter
	rev_index_on_sheet = 0
	
	#revision data
	revision_data = {}
	
	for revision_id in revision_ids_on_sheet:
		revision = doc.GetElement(revision_id)
		revision_sequence_id = revision.RevisionNumberingSequenceId
		
		# a class generating the actual revision number
		rev_sequence_generator = None
		
		# check if this is a None revision
		if revision_sequence_id == ElementId.InvalidElementId:
			rev_sequence_generator = get_sequence_none(revision,rev_index_on_sheet)
		else:
			
			# get the revision sequence
			revision_sequence = doc.GetElement(revision_sequence_id)
		
			# check what type of sequence and get helper class accordingly
			if (revision_sequence.NumberType ==  RevisionNumberType.Numeric):
				rev_sequence_generator = get_sequence_numeric(revision,revision_sequence,rev_index_on_sheet)
			elif (revision_sequence.NumberType ==  RevisionNumberType.Alphanumeric):
				rev_sequence_generator = get_sequence_alphanumeric(revision,revision_sequence,rev_index_on_sheet)
			else:
				print("Not supported")

		# move to next if there is no revision
		if (rev_sequence_generator == None):
			continue
		
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

sheets= get_all_sheets(doc)
for sheet in sheets:
	formatted_data = revisions_on_sheet = get_revisions(doc, sheet)
	print (formatted_data)