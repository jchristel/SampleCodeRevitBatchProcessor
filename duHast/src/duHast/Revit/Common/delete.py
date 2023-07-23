"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Delete elements from model.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res

# required for .ToList()
import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)


def delete_by_element_ids(
    doc,
    ids,
    transaction_name,  # type: str
    element_name,  # type: str
):
    """
    Deleting elements in list all at once.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List containing ids of all elements to be deleted.
    :type ids: list of Autodesk.Revit.DB.ElementId
    :param transaction_name: The transaction name used for the deletion.
    :type transaction_name: str
    :param element_name: The element name added to deletion status message.
    :type element_name: str
    :return:
        Result class instance.
        - .result = True if successfully deleted all elements. Otherwise False.
        - .message will contain deletion status
    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    def action():
        action_return_value = res.Result()
        try:
            doc.Delete(ids.ToList[rdb.ElementId]())
            action_return_value.message = "Deleted {} {}".format(len(ids), element_name)
        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to delete {} with exception: {}".format(element_name, e)
            )
        return action_return_value

    transaction = rdb.Transaction(doc, transaction_name)
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def delete_by_element_ids_one_by_one(
    doc,
    ids,
    transaction_name,  # type: str
    element_name,  # type: str
):
    """
    Deleting elements in list one at the time.
    Each element gets deleted in its own transaction. If the deletion fails the transaction is rolled back.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List containing ids of all elements to be deleted.
    :type ids: list of Autodesk.Revit.DB.ElementId
    :param transaction_name: The transaction name used for the deletion.
    :type transaction_name: str
    :param element_name: The name of the element (?) Not used!!
    :type element_name: str
    :return:
        Result class instance.
        - .result = True if successfully deleted all elements. Otherwise False.
        - .message will contain each id and its deletion status
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    for id in ids:

        def action():
            action_return_value = res.Result()
            element = doc.GetElement(id)
            n = rdb.Element.Name.GetValue(element)
            try:
                doc.Delete(id)
                action_return_value.message = "Deleted [{}] {}".format(id, n)
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to delete {} [{}] with exception: {}".format(n, id, e),
                )
            return action_return_value

        transaction = rdb.Transaction(doc, transaction_name)
        return_value.update(rTran.in_transaction(transaction, action))
    return return_value
