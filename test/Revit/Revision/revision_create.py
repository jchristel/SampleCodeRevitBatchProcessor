"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit create revision tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from test.Revit.TestUtils import revit_test
from test.Revit.Revision.revision import TEST_DATA_2022, TEST_DATA_2023
from duHast.Revit.Revisions.revisions import create_revision
from duHast.Utilities.Objects import result as res


class CreateRevision(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(CreateRevision, self).__init__(doc=doc, test_name="create_revision")

    def test(self):
        """
        Attempts to create a revision in revit.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if revision was created successfully, otherwise False
                - .message will contain result(s) vs expected result(s)
                - . result (empty list)

                on exception:

                - .result Will be False
                - .message will contain exception message.
                - . result (empty list)
        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        try:
            # check which revit version
            test_data = None
            if self.revit_version_number <= 2022:
                test_data = TEST_DATA_2022
                return_value.append_message("Using test data for Revit 2022")
            else:
                test_data = TEST_DATA_2023
                return_value.append_message("Using test data for Revit 2023")

            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    create_rev_value = create_revision(doc, test_data)
                    # return_value.update(create_rev_value)
                    assert create_rev_value.status == True
                    assert len(create_rev_value.result) == 1
                    assert (
                        create_rev_value.result[0].Description == test_data.description
                    )
                    assert create_rev_value.result[0].IssuedTo == test_data.issued_to
                    assert create_rev_value.result[0].IssuedBy == test_data.issued_by
                    assert (
                        create_rev_value.result[0].RevisionDate
                        == test_data.revision_date
                    )
                    assert (
                        create_rev_value.result[0].Visibility
                        == test_data.tag_cloud_visibility
                    )
                    # version dependent result testing required since API change with Revit 2023
                    if self.revit_version_number <= 2022:
                        assert (
                            create_rev_value.result[0].NumberType
                            == test_data.revision_number_type
                        )
                    else:
                        rev_sequence = self.document.GetElement(
                            create_rev_value.result[0].RevisionNumberingSequenceId
                        )
                        assert (
                            rev_sequence.SequenceName == test_data.revision_number_type
                        )
                    action_return_value.update_sep(
                        True, "Created revision successfully."
                    )
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in function {}: {}".format(
                            self.test_name, e
                        ),
                    )
                return action_return_value

            return_value.update(self.in_transaction_group(action))
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )

        return return_value
