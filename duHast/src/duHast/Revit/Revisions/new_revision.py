"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to creating new revit revisions.
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

# import Autodesk
import Autodesk.Revit.DB as rdb
from duHast.Utilities.Objects import result as res
from duHast.Revit.Revisions.sequence import get_revision_seq_of_name


def new_revision_action_2022(doc, revision_data):
    """
    Creates a new revision in a revit document up to version 2022.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_data: Named tuple containing revision data
    :type revision_data: :class:`.revisionData`

    :return:
        Result class instance.

        - Revision created status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision created successfully.
        - result.result: will contain list with single entry: the new revision created

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    """

    action_return_value = res.Result()
    try:
        new_revision = rdb.Revision.Create(doc)
        new_revision.Description = revision_data.description
        new_revision.IssuedBy = revision_data.issued_by
        new_revision.IssuedTo = revision_data.issued_to
        new_revision.NumberType = revision_data.revision_number_type
        new_revision.RevisionDate = revision_data.revision_date
        new_revision.Visibility = (
            revision_data.tag_cloud_visibility
        )  # rdb.RevisionVisibility.Hidden
        action_return_value.result.append(new_revision)
        action_return_value.update_sep(True, "Created new revision in document.")
    except Exception as e:
        action_return_value.update_sep(
            False,
            "Failed to create new revision in document with exception: " + str(e),
        )
    return action_return_value


def new_revision_action_2023(doc, revision_data):
    """
    Creates a new revision in a revit document version 2023 and onwards.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_data: Named tuple containing revision data
    :type revision_data: :class:`.revisionData`

    :return:
        Result class instance.

        - Revision created status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision created successfully.
        - result.result: will contain list with single entry: the new revision created

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    """

    action_return_value = res.Result()
    try:
        new_revision = rdb.Revision.Create(doc)
        new_revision.Description = revision_data.description
        new_revision.IssuedBy = revision_data.issued_by

        # set the revision sequence based on revision number type property past in
        seq = doc.GetElement(new_revision.RevisionNumberingSequenceId)
        if seq.Name == revision_data.revision_number_type:
            action_return_value.append_message(
                "Using rev sequence type assigned by default: {}".format(seq.Name)
            )
        else:
            action_return_value.append_message(
                "Need to assign none default revision sequence type: {}".format(
                    revision_data.revision_number_type
                )
            )
            rev_sequence = get_revision_seq_of_name(
                doc, revision_data.revision_number_type
            )
            if rev_sequence != None:
                new_revision.RevisionNumberingSequenceId = rev_sequence.Id
                action_return_value.append_message(
                    "Successfully assigned non default revision sequence type: {}".format(
                        rev_sequence.Name
                    )
                )
            else:
                action_return_value.append_message(
                    "Rev sequence type: {} does not exist in model. Default used instead: {} !".format(
                        revision_data.revision_number_type, seq.Name
                    )
                )

        new_revision.IssuedTo = revision_data.issued_to
        new_revision.RevisionDate = revision_data.revision_date
        new_revision.Visibility = (
            revision_data.tag_cloud_visibility
        )  # rdb.RevisionVisibility.Hidden
        action_return_value.result.append(new_revision)
        action_return_value.update_sep(True, "Created new revision in document.")
    except Exception as e:
        action_return_value.update_sep(
            False,
            "Failed to create new revision in document with exception: {}".format(e),
        )
    return action_return_value
