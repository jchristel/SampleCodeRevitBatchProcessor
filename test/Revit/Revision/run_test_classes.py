"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all revit revision related tests . 
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


from test.Revit.TestUtils.run_revit_tests import RevitRunTest
from duHast.Utilities.Objects import result as res

# import test classes
import test.Revit.Revision.revision_change_seq as change_rev_seq
import test.Revit.Revision.revision_re_order as re_order_rev
import test.Revit.Revision.revision_create as rev_create
import test.Revit.Revision.revision_mark_issued as rev_mark_issued
import test.Revit.Revision.revision_mark_issued_id as rev_mark_issued_id
import test.Revit.Revision.revision_get_issued as rev_get_issued
import test.Revit.Revision.revision_get_last_issued as rev_get_last_issued

import test.Revit.Revision.sequence_create_alpha as seq_create_alpha
import test.Revit.Revision.sequence_get_by_name as seq_get_by_name


def run_revision_tests(doc):
    """
    Runs all revision related tests.

    :param doc: Current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if all tests completed successfully, otherwise False.
    :rtype: bool
    """

    return_value = res.Result()

    # start tests -> should run revision sequence tests first since they form
    # part of revision tests

    run_tests = [
        ["Sequence Alpha Create", seq_create_alpha.CreateAlphaSequence],
        ["Sequence Get By Name", seq_get_by_name.GetSequenceByName],
        ["Revision Create", rev_create.CreateRevision],
        ["Revision Mark As Issued", rev_mark_issued.MarkIssued],
        ["Revision Mark As Issued By Id", rev_mark_issued_id.MarkIssuedById],
        ["Revision Get Issued", rev_get_issued.GetIssuedRevisions],
        ["Revision Get Last Issued", rev_get_last_issued.GetLastIssuedRevisions],
        ["Revision Sequence", change_rev_seq.ChangeRevSeq],
        ["Revision Order", re_order_rev.ChangeRevOrder],
    ]

    runner = RevitRunTest(run_tests)
    return_value = runner.run_tests(doc)

    return return_value
