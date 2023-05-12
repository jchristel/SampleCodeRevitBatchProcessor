
from test.Revit.TestUtilis import revit_test
from test.Revit.Revision.revision import TEST_DATA_2022, TEST_DATA_2023
from duHast.Revit.Revisions.revisions import create_revision
from duHast.Revit.Revisions.revisions import change_revision_sequence_number
from duHast.Utilities import result as res

class ChangeRevSeq(revit_test.RevitTest):

    def __init__(self, doc):
        # store document in base class
        super(ChangeRevSeq, self).__init__(doc=doc)

    def test(self):
        '''
        Change revision sequence test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :raises ValueError: Any exception occurred in creating a revision will be re-raised
        :return: True if revision was created successfully, otherwise False
        :rtype: Boolean
        '''

        return_value = res.Result()
        try:
            # add another few revision to model
            # check which revit version
            result = None
            test_data = None
            if self.revit_version_number <= 2022:
                test_data = TEST_DATA_2022
            else:
                test_data = TEST_DATA_2023
            
            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                try:
                    action_return_value = res.Result()
                    revisions = []
                    for i in range(5):
                        result = create_revision(doc, test_data)
                        if(result.status):
                            revisions.append(result.result[0])
                        else:
                            raise ValueError(result.message) 
                
                    # move revisions around...
                    # first test -> pass in same sequence number

                    expected_result = revisions[0].SequenceNumber
                    result = change_revision_sequence_number(doc, revisions[0], expected_result)
                    action_return_value.append_message (" {} vs {} vs status: {} message: {}".format(revisions[0].SequenceNumber, expected_result, result.status , result.message))
                    assert result.status == True
                    assert revisions[0].SequenceNumber == expected_result

                    # second test -> pass in sequence number + 1
                    expected_result = revisions[1].SequenceNumber + 1
                    result = change_revision_sequence_number(doc, revisions[1], expected_result)
                    action_return_value.append_message (" {} vs {} vs status: {} message: {}".format(revisions[1].SequenceNumber, expected_result, result.status , result.message))
                    assert result.status == True
                    assert revisions[1].SequenceNumber == expected_result

                    # third test -> pass in invalid sequence number (outside of range)
                    expected_result = revisions[2].SequenceNumber
                    result = change_revision_sequence_number(doc, revisions[2], 10)
                    action_return_value.append_message (" {} vs {} vs status: {} message: {}".format(revisions[2].SequenceNumber, expected_result, result.status , result.message))
                    assert result.status == False
                    assert revisions[2].SequenceNumber == expected_result
                except Exception as e:
                    action_return_value.update_sep(False, "An exception occurred in function test_change_revision_sequence_number {}".format(e))
                return action_return_value
            
            return_value = self.in_transaction_group(action)

        except Exception as e:
            return_value.update_sep(False, "An exception occurred in function test_change_revision_sequence_number {}".format(e))

        return return_value