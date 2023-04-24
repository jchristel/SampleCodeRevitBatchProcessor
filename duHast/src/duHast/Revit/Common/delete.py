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
# Copyright (c) 2020  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import transaction as rTran
from duHast.Utilities import result as res

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
                False, "Failed to delete {} with exception: {}".format(element_name,e)
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
                    "Failed to delete {} [{}] with exception: {}".format(n,id, e)
                )
            return action_return_value

        transaction = rdb.Transaction(doc, transaction_name)
        return_value.update(rTran.in_transaction(transaction, action))
    return return_value