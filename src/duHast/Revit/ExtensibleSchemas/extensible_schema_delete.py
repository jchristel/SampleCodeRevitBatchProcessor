"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Extensible storage deletion in Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notes from the building coder website: https://thebuildingcoder.typepad.com/blog/2022/11/extensible-storage-schema-deletion.html


The dev team replied: After running DeleteSchemas macro, open Manage > Purge Unused. In the tree, select Extensible Storage Schema. Check the schema a9dc2b48 and click OK to purge it. Run ListSchemas - the schema is purged. So, please use Purge Unused to delete schemas without entities.

Extensible storage schema is an application-wide object. If it exists at all in the application, it will populate and "infect" every single document that you touch. That makes it hard to remove, and complicated to understand.


Personally I found:

- The schema is not removed from the document when you delete it. You have to purge it manually.
- If the schema exists in a link and you delete it, it will not go away ... unload  any links or replace any links with dummy links without the schema and attempt to delete and purge again.
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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



from duHast.Utilities.Objects.result import Result

from System import Guid

from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.DB.ExtensibleStorage import  Schema

from duHast.Revit.Common.transaction import in_transaction

def delete_schema_by_guid(doc, guid, transaction_manager = in_transaction):
	"""
	Deletes a schema by its guid. This will also delete all entities that are using this schema.

	Note:


	:param doc: The Revit document
	:type doc: Autodesk.Revit.DB.Document
	:param guid: The guid of the schema to delete
	:type guid: str
	:param transaction_manager: The transaction manager to use. Defaults to in_transaction.
	:type transaction_manager: function
	:return: A Result object with the result of the operation
	:rtype: Result
	"""

	return_value = Result()
	try:
		
		schemas = Schema.ListSchemas()
	
		# define an action to be executed in a transaction
		def action ():
			action_return_value = Result()

			found_match = False
			for schema in schemas:
				if schema.GUID.ToString() == guid:
					action_return_value.append_message("Schema found")
					found_match = True
					doc.EraseSchemaAndAllEntities(schema)
					action_return_value.append_message("Schema erased")
					# there should only be one schema with this guid...get out of the loop
					return action_return_value
			
			#  check if we found a match
			if not found_match:
				action_return_value.append_message("Schema not found")
				
				return action_return_value
		
		if transaction_manager:
			# run the action in a transaction
			tranny = Transaction(doc, "Erase EStorage: {}".format(guid))
			return_value = transaction_manager(tranny, action)
		
		else:
			# run the action without a transaction
			return_value = action()

		return return_value
	except Exception as e:
		return_value.update_sep(False, str(e))
		return return_value

