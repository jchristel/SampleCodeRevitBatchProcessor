"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around data storage in Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data storage can be used to project wide settings not associated with a specific element. 

Obsolete in Revit 2025 ... 
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

import duHast.Utilities.Objects.result as res
from duHast.Revit.Common.transaction import in_transaction


from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.DB.ExtensibleStorage import DataStorage, Entity


def create_project_data_storage(doc, schema):
    """
    Create a new DataStorage element in the Revit document and set its schema.
    
    :param doc: The Revit document to create the DataStorage element in.
    :type doc: Autodesk.Revit.DB.Document
    
    :param schema: The schema to set on the DataStorage element.
    :type schema: Autodesk.Revit.DB.ExtensibleStorage.Schema
    
    :return: A Result object containing the created DataStorage element in its result list or an error message.
    :rtype: duHast.Utilities.Objects.result.Result
    """
    
    return_value = res.Result()
    
    # build an action to create a new DataStorage element
    def action():
        action_return_value = res.Result()
        try:
            # Create a new DataStorage element
            data_storage = DataStorage.Create(doc)
            entity = Entity(schema)
            # Set the schema to the DataStorage element
            data_storage.SetEntity(entity)
            action_return_value.append_message(
                "DataStorage element created successfully."
            )
            action_return_value.result.append(data_storage)
        except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to set up data storage: {}".format(e),
                )
        return action_return_value
    
    # attempt to create the DataStorage element in a transaction
    transaction = Transaction(doc, "Creating data storage")
    data_storage_creation_result = in_transaction(transaction, action)
    return_value.update(data_storage_creation_result)

    return return_value

