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

import os

# import Autodesk
import Autodesk.Revit.DB as rdb

import tempfile
from duHast.Utilities import base
from duHast.Utilities.directory_io import directory_delete, directory_exists
from duHast.Utilities.files_io import file_exist
from duHast.Utilities.files_csv import read_csv_file
from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Utilities import result as res


class RevitTest(base.Base):
    def __init__(self, doc, test_name, requires_temp_dir=False):
        """
        Class constructor.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        """

        # initialise base class
        super(RevitTest, self).__init__()

        self.test_name = test_name
        self.document = doc
        # set up document revit version
        self.revit_version_number = get_revit_version_number(doc)
        # set up a temp directory if required
        if requires_temp_dir:
            self.tmp_dir = tempfile.mkdtemp()
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

    def clean_up(self):
        """
        Remove temp directory
        """
        try:
            if self.tmp_dir is not None:
                del_temp_dir = directory_delete(self.tmp_dir)
                assert del_temp_dir == True
                temp_dir_exists = directory_exists(self.tmp_dir)
                assert temp_dir_exists == False
                return True
            else:
                return True
        except Exception as e:
            # this should not be happening!
            print(e)
            return False

    def get_full_file_path(self, file_name):
        """
        returns fully qualified file path of file in temp directory if temp directory exists. Otherwise will return file name unchanged.

        :param file_name: A file name
        :type file_name: str
        :return: If temp directory exists: fully qualified file path of file in temp directory, otherwise the file name unchanged.
        :rtype: str
        """
        if self.tmp_dir == None:
            return file_name
        else:
            return os.path.join(self.tmp_dir, file_name)

    def test_csv_file(self, test_file_path, expected_file_content):
        """
            Checks whether a given CSV file exists and if so reads it content and compares it to an expected content

            :param test_file_path: The fully qualified csv file path.
            :type test_file_path: str
            :param expected_file_content: The expected content of csv file.
            :type expected_file_content: [[str,...]]
            :return:
                Result class instance.
                - Status True if csv file exists and content matches expected content, otherwise False.
                - result.message will contain file exist check outcome as well as content comparison outcome.
                On exception:
                - result.status (bool) will be False.
                - result.message will contain the exception message.
        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        try:
            # double check...
            file_exist_status = file_exist(test_file_path)
            return_value.append_message(
                " file exists check: {}".format(file_exist_status)
            )
            assert file_exist_status == True

            # read file content
            result_file_read = read_csv_file(test_file_path)
            return_value.append_message(
                " file read results: \n {} \n vs \n {}".format(
                    sorted(result_file_read), sorted(expected_file_content)
                )
            )
            assert sorted(result_file_read) == sorted(expected_file_content)

        except Exception as e:
            return_value.update_sep(
                False,
                "Failed to check CSV file: {} with exception: {}".format(
                    test_file_path, e
                ),
            )

        return return_value
