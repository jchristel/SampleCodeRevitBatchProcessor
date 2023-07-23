"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to revit revision sequences.
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
from duHast.Revit.Common import transaction as rTran


def get_revision_seq_of_name(doc, revision_sequence_name):
    """
    Gets a revision sequence by its name. If no match is found None is returned!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_sequence_name: The sequence name
    :type revision_sequence_name: str

    :return: The matching sequence or None
    :rtype: Autodesk.Revit.DB.RevisionNumberingSequence
    """

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.RevisionNumberingSequence)
    for c in col:
        if c.Name == revision_sequence_name:
            return c
    return None


def create_revision_alpha_seq(
    doc, revision_sequence_name, alpha_settings=rdb.AlphanumericRevisionSettings()
):
    """
    Creates a revision sequence with provided name and settings.

    Will throw an exception if sequence creation failed.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_sequence_name: The name of the sequence
    :type revision_sequence_name: str
    :param alpha_settings: Custom settings, defaults to rdb.AlphanumericRevisionSettings()
    :type alpha_settings: Autodesk.Revit.DB.AlphanumericRevisionSettings, optional

    :return: The new sequence.
    :rtype: Autodesk.Revit.DB.RevisionNumberingSequence
    """

    def action():
        action_return_value = res.Result()
        try:
            seq = rdb.RevisionNumberingSequence.CreateAlphanumericSequence(
                doc, revision_sequence_name, alpha_settings
            )
            action_return_value.update_sep(
                True, "Created sequence: {}".format(revision_sequence_name)
            )
            action_return_value.result.append(seq)
        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to create sequence {} with exception: {}".format(
                    revision_sequence_name, e
                ),
            )
        return action_return_value

    transaction = rdb.Transaction(
        doc, "Creating sequence: {}".format(revision_sequence_name)
    )
    transaction_value = rTran.in_transaction(transaction, action)
    if transaction_value.status and len(transaction_value.result) > 0:
        return transaction_value.result[0]
    else:
        raise ValueError(
            "Failed to create sequence: {} with exception:{}".format(
                revision_sequence_name, transaction_value.message
            )
        )
