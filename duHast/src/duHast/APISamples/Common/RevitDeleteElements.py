import Autodesk.Revit.DB as rdb

from duHast.APISamples.Common import RevitTransaction as rTran
from duHast.Utilities import Result as res

def DeleteByElementIds(
    doc,
    ids,
    transactionName, # type: str
    elementName # type: str
    ):
    '''
    Deleting elements in list all at once.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List containing ids of all elements to be deleted.
    :type ids: list of Autodesk.Revit.DB.ElementId
    :param transactionName: The transaction name used for the deletion.
    :type transactionName: str
    :param elementName: The element name added to deletion status message.
    :type elementName: str
    :return: 
        Result class instance.
        - .result = True if successfully deleted all elements. Otherwise False.
        - .message will contain deletion status
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    def action():
        actionReturnValue = res.Result()
        try:
            doc.Delete(ids.ToList[rdb.ElementId]())
            actionReturnValue.message = 'Deleted ' + str(len(ids)) + ' ' + elementName
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Failed to delete ' + elementName + ' with exception: ' + str(e))
        return actionReturnValue
    transaction = rdb.Transaction(doc,transactionName)
    returnValue = rTran.in_transaction(transaction, action)
    return returnValue


def DeleteByElementIdsOneByOne(
    doc,
    ids,
    transactionName, # type: str
    elementName # type: str
    ):
    '''
    Deleting elements in list one at the time.
    Each element gets deleted in its own transaction. If the deletion fails the transaction is rolled back.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List containing ids of all elements to be deleted.
    :type ids: list of Autodesk.Revit.DB.ElementId
    :param transactionName: The transaction name used for the deletion.
    :type transactionName: str
    :param elementName: The name of the element (?) Not used!!
    :type elementName: str
    :return: 
        Result class instance.
        - .result = True if successfully deleted all elements. Otherwise False.
        - .message will contain each id and its deletion status
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    for id in ids:
        def action():
            actionReturnValue = res.Result()
            element = doc.GetElement(id)
            n = rdb.Element.Name.GetValue(element)
            try:
                doc.Delete(id)
                actionReturnValue.message = 'Deleted [' + str(id) + '] ' + n
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to delete ' + n + '[' +str(id) + '] with exception: ' + str(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,transactionName)
        returnValue.Update( rTran.in_transaction(transaction, action))
    return returnValue