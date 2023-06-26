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
# Copyright (c) 2023  Jan Christel
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
