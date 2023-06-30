"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family warnings data processor class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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


from duHast.Revit.Family.Data.ifamily_processor import IFamilyProcessor
from duHast.Revit.Warnings.Data import warnings_data as rWarnData
from duHast.Revit.Family.Data import ifamily_data as IFamData


class WarningsProcessor(IFamilyProcessor):
    def __init__(self, pre_actions=None, post_actions=None):
        """
        Class constructor.
        """

        # setup report header
        string_report_headers = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            rWarnData.WARNING_TEXT,
            rWarnData.WARNING_GUID,
            rWarnData.WARNING_RELATED_IDS,
            rWarnData.WARNING_OTHER_IDS,
        ]

        # store data type  in base class
        super(WarningsProcessor, self).__init__(
            pre_actions=pre_actions,
            post_actions=post_actions,
            data_type="Warnings",
            string_report_headers=string_report_headers,
        )

    def process(self, doc, root_path, root_category_path):
        """
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param rootCategoryPath: The category path of the nested family in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategoryPath: str
        """

        dummy = rWarnData.WarningsData(root_path, root_category_path, self.data_type)
        dummy.process(doc)
        self.data.append(dummy)
