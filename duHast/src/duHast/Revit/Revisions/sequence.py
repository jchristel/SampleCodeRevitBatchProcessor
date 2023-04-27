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

# import Autodesk
import Autodesk.Revit.DB as rdb

def get_revision_seq_of_name(doc, revision_sequence_name):
    '''
    Gets a revision sequence by its name. If no match is found None is returned!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_sequence_name: The sequence name
    :type revision_sequence_name: str

    :return: The matching sequence or None
    :rtype: Autodesk.Revit.DB.RevisionNumberingSequence
    '''

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.RevisionNumberingSequence)
    for c in col:
        if (c.Name == revision_sequence_name):
            return c
    return None