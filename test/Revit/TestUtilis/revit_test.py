"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit test base class . 
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

import tempfile
from duHast.Utilities import base
from duHast.Utilities.directory_io import directory_delete
from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Utilities import result as res


class RevitTest(base.Base):
    def __init__(self, doc, requires_temp_dir=False):
        """
        Class constructor.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        """

        # initialise base class
        super(RevitTest, self).__init__()

        self.document = doc
        # set up document revit version
        self.revit_version_number = get_revit_version_number(doc)
        # set up a temp directory if required
        if requires_temp_dir:
            self.tmp_dir = self.create_tmp_dir()
        else:
            self.tmp_dir = None
    
    def test(self):
        return_value = res.Result()
        return return_value

    def in_transaction_group(self, action):
        """
        Encapsulates action in a transaction group which will be rolled back.

        :param action: An action taking the document as an argument only.
        :type action: foo(doc)
        :return: A flag indicating the action was completed successfully and a message from the action.
        :rtype: bool, str
        """

        return_value = res.Result()
        # create a transaction group
        tg = rdb.TransactionGroup(self.document, "test")
        tg.Start()

        return_value = action(self.document)

        # roll every thing back
        tg.RollBack()

        return return_value

    def create_temp_dir(self):
        # set up a temp dir and test file path
        tmp_dir = tempfile.mkdtemp()

    def clean_up(self):
        # remove temp directory
        if self.tmp_dir is not None:
            directory_delete(self.tmp_dir)
