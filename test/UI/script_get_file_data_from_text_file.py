"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains get_file_data_from_text_file tests . 
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
import uuid
from collections import namedtuple

from test.utils import test
from duHast.UI.file_list import is_back_up_file
from duHast.UI.script import get_file_data
from duHast.UI.file_select_settings import FileSelectionSettings
from duHast.UI.file_item import MyFileItem
from duHast.Utilities.files_csv import write_report_data_as_csv


TEST_RESULT = namedtuple("test_result", "test_id all_items")


class GetFileDataFromTextFile(test.Test):
    def __init__(self):
        # store document in base class
        super(GetFileDataFromTextFile, self).__init__(
            test_name="get_file_data_from_text_file"
        )

    def _bim360_files_in_csv(self, tmp_dir):
        """
        Test getting file data from bim360 settings file.

        Format:
        - [Revit version, Project GUID, File GUID, file size in MB, file name]

        :param tmp_dir: A temporary directory
        :type tmp_dir: str
        :return: flag ( true if everything checked out ok, otherwise False), message : showing expected vs actual result
        :rtype: boolean, str
        """

        flag = True
        message = "-"
        try:
            # create csv file
            # test data for BIM 360 files
            test_files_BIM_360 = [
                MyFileItem(
                    "test_file_01_size.rvt",
                    100,
                    uuid.uuid4(),
                    uuid.uuid4(),
                    uuid.uuid4(),
                ),
                MyFileItem(
                    "test_file_02_size.rvt",
                    50,
                    uuid.uuid4(),
                    uuid.uuid4(),
                    uuid.uuid4(),
                ),
            ]
            data = []
            # list of str in format [Revit version, Project GUID, File GUID, file size in MB, file name]
            for test_file in test_files_BIM_360:
                data.append(
                    [
                        test_file.bim_360_revit_version,
                        test_file.bim_360_project_guid,
                        test_file.bim_360_file_guid,
                        test_file.size,
                        test_file.name,
                    ]
                )
            data_file_name = os.path.join(tmp_dir, "test_file.csv")
            # write test file
            write_report_data_as_csv(data_file_name, "", data)
            # set up settings object
            settings = FileSelectionSettings(
                inputDirectory=tmp_dir,
                include_sub_dirs_in_search=False,
                output_directory=tmp_dir,
                output_file_number=2,
                revitFileExtension=".rvt",
            )
            # attempt to get file data
            file_items = get_file_data(settings=settings)
            # update message and test result
            message = "file data bim 360 result:{} vs expected: {}".format(
                file_items, test_files_BIM_360
            )
            assert sorted(file_items, key=lambda obj: obj.name) == sorted(
                test_files_BIM_360, key=lambda obj: obj.name
            )
        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function _bim360_files_in_csv {} : {}".format(
                        self.test_name, e
                    )
                )
            )
        return flag, message

    def _server_files_in_csv(self, tmp_dir):
        """
        Test getting file data from file data file

        Format:
        - single column fully qualified file name

        :param tmp_dir: A temporary directory
        :type tmp_dir: str
        :return: flag ( true if everything checked out ok, otherwise False), message : showing expected vs actual result
        :rtype: boolean, str
        """

        flag = True
        message = "-"
        try:
            # create csv file
            # test data for BIM 360 files
            test_files_server = [
                MyFileItem(
                    "test_file_01_size.rvt",
                    100,
                ),
                MyFileItem(
                    "test_file_02_size.rvt",
                    50,
                ),
            ]
            data = []
            # list of str in format [file name]
            for test_file in test_files_server:
                data.append(
                    [
                        test_file.name,
                    ]
                )
            data_file_name = os.path.join(tmp_dir, "test_file.csv")
            # write test file
            write_report_data_as_csv(data_file_name, "", data)
            # set up settings object
            settings = FileSelectionSettings(
                inputDirectory=tmp_dir,
                include_sub_dirs_in_search=False,
                output_directory=tmp_dir,
                output_file_number=2,
                revitFileExtension=".rvt",
            )

            # attempt to get file data
            file_items = get_file_data(settings=settings)
            # update message and test result
            message = "file data test file result:{} vs expected: {}".format(
                file_items, test_files_server
            )
            assert sorted(file_items, key=lambda obj: obj.name) == sorted(
                test_files_server, key=lambda obj: obj.name
            )
        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function _server_files_in_csv {} : {}".format(
                        self.test_name, e
                    )
                )
            )
        return flag, message

    def _server_files_in_directory(self, tmp_dir):
        """
        Test of getting revit files from a server.

        :param tmp_dir: A temporary directory
        :type tmp_dir: str
        :return: flag ( true if everything checked out ok, otherwise False), message : showing expected vs actual result
        :rtype: boolean, str
        """

        flag = True
        message = "-"
        try:
            # test data
            test_files = [
                "test_file_01_size.rvt",
                "test_file_02_size.rvt",
            ]
            self.write_test_files(test_files, tmp_dir)
            # test data for server files
            test_files_server = [
                MyFileItem(
                    "test_file_01_size.rvt",
                    1,
                ),
                MyFileItem(
                    "test_file_02_size.rvt",
                    1,
                ),
            ]
            # set up settings object
            settings = FileSelectionSettings(
                inputDirectory=tmp_dir,
                include_sub_dirs_in_search=False,
                output_directory=tmp_dir,
                output_file_number=2,
                revitFileExtension=".rvt",
            )

            # attempt to get file data
            file_items = get_file_data(settings=settings)
            # update message and test result
            message = "file data test server file result:{} vs expected: {}".format(
                file_items, test_files_server
            )
            assert sorted(file_items, key=lambda obj: obj.name) == sorted(
                test_files_server, key=lambda obj: obj.name
            )

        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function _server_files_in_directory {} : {}".format(
                        self.test_name, e
                    )
                )
            )
        return flag, message

    def test(self):
        """
        Test get_file_data_from_text_file.

        :return: True if all tests past, otherwise False
        :rtype: bool
        """

        flag = True
        message = "-"
        try:
            # test bim360 files in csv file
            flag_bim360, message_bim360 = self.call_with_temp_directory(
                self._bim360_files_in_csv()
            )
            # test server file in csv file
            flag_server_csv, message_server_csv = self.call_with_temp_directory(
                self._server_files_in_csv()
            )
            # test server files in directory
            flag_server_dir, message_server_dir = self.call_with_temp_directory(
                self._server_files_in_directory()
            )

            flag = flag_bim360 & flag_server_csv & flag_server_dir
            message = "{}\n{}\n{}".format(
                message_bim360, message_server_csv, message_server_dir
            )

        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function {} : {}".format(
                        self.test_name, e
                    )
                )
            )
        return flag, message