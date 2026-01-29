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


class SequenceNumeric():
	def __init__(self, revit_id,revit_revision, prefix,suffix,start_number,min_digits):
		
		self._revit_id=revit_id
		self._revit_revision = revit_revision
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
		
	def get_revision(self, revision_index_on_sheet):
		# TODO: format sequence number in accordance to min_digits value
		rev = self._start_number+revision_index_on_sheet
		return "{}{}{}".format(self._prefix,rev,self._suffix)	


class SequenceAlphaNumeric():
	def __init__(self, revit_id, revit_revision,prefix,suffix, sequence):
		
		self._revit_id=revit_id
		self._revit_revision = revit_revision
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
	
	def get_revision(self, revision_index_on_sheet):
		# TODO: what happends if a sheet get issued more times than there are characters in the sequence?
		rev = "Out_of_bounds"
		if self._sequence.Count>=revision_index_on_sheet:
			rev = self._sequence[revision_index_on_sheet]
	
		return "{}{}{}".format(self._prefix,rev,self._suffix)	


def get_sequence_numeric(revision, revision_sequence):
	settings = revision_sequence.GetNumericRevisionSettings()
	seq_number = SequenceNumeric(
		revision_sequence.Id.Value, 
		revision,
		settings.Prefix,
		settings.Suffix,
		settings.StartNumber,
		settings.MinimumDigits
	)
	return seq_number
	

def get_sequence_alphanumeric(revision, revision_sequence):
	settings = revision_sequence.GetAlphanumericRevisionSettings()
	sequence = settings.GetSequence()
	seq_number=SequenceAlphaNumeric(
		revision_sequence.Id.Value,
		revision,
		settings.Prefix,
		settings.Suffix,
		sequence
	)
	return seq_number
	

def build_revision_data(rev_dictionary, number_of_revs_on_sheet):
	
	print("\nbuilding revision data...from {} revision on sheet\n".format(number_of_revs_on_sheet))
	data = []
	
	# start getting data in order of revisions on sheet
	index_counter = 0
	
	for i in range(0, number_of_revs_on_sheet):
		print ("...checking revision on sheet of index: {}".format(i))
		
		found_match = False
		
		# loop over items and build a revision data
		for sequence_id, revision_data_list in rev_dictionary.items():
			
			
			seq_by_revision_type = 0
			for rev_data_entry in revision_data_list:
				print ("rev index on sheet: {} overal index: {} type: {} ".format(rev_data_entry[1], i, type(rev_data_entry[1])))
				if rev_data_entry[1] == i:
					
					# get the local index...
					revision_value = rev_data_entry[0].get_revision(seq_by_revision_type)
					revision_revit_element = rev_data_entry[0].revit_revision
					
					print ("...found match. Revision value: {}".format(revision_value))
					
					# build data
					data.append((revision_value, revision_revit_element))
					
					# set flag
					found_match = True
					# time to move to next
					break
				seq_by_revision_type = seq_by_revision_type +1
			
			if found_match:
				break
			
			index_counter = index_counter +1
	return data
		

def get_revisions(doc, sheet):
	revision_ids_on_sheet = sheet.GetAllRevisionIds()
	
	# check if any revisions on sheet
	if (revision_ids_on_sheet.Count == 0):
		return None
	print(type(revision_ids_on_sheet))
	
	revision_data = []
	
	#revision index counter
	rev_index = 0
	
	#revision data
	revision_data = {}
	
	for revision_id in revision_ids_on_sheet:
		revision = doc.GetElement(revision_id)
		revision_sequence_id = revision.RevisionNumberingSequenceId
		revision_sequence = doc.GetElement(revision_sequence_id)
		
		print(type(revision_sequence))
		
		# a class generating the actual revision number
		rev_sequence_generator = None
		
		if (revision_sequence.NumberType ==  RevisionNumberType.Numeric):
			print ("numeric")
			rev_sequence_generator = get_sequence_numeric(revision,revision_sequence)
		elif (revision_sequence.NumberType ==  RevisionNumberType.Alphanumeric):
			print ("alpha")
			rev_sequence_generator = get_sequence_alphanumeric(revision,revision_sequence)
		else:
			print("Not supported")

		print(rev_sequence_generator)
		
		# move to next if there is no revision
		if (rev_sequence_generator == None):
			continue
		
		# generate a node if there isnt one already
		if rev_sequence_generator.revit_id not in revision_data:
			revision_data[rev_sequence_generator.revit_id] = []
		
		# add the generator and index to the dictionary
		revision_data[rev_sequence_generator.revit_id].append((rev_sequence_generator, rev_index))
		
		
		# increase revision index counter
		rev_index = rev_index + 1
		
	# build revision data
	formatted_data = build_revision_data(revision_data, revision_ids_on_sheet.Count)
	
	return formatted_data

sheets= get_all_sheets(doc)
for sheet in sheets:
	formatted_data = revisions_on_sheet = get_revisions(doc, sheet)
	print (formatted_data)