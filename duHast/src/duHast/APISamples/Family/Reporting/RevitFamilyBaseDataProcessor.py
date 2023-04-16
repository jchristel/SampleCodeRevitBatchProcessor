'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family base data processor class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
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

from duHast.APISamples.Family.Reporting.IFamilyProcessor import IFamilyProcessor
from duHast.APISamples.Family.Reporting import RevitFamilyBaseData as rFamData
from duHast.APISamples.Family.Reporting import IFamilyData as IFamData
from duHast.Utilities import UtilBatchP as uBP

class FamilyBaseProcessor(IFamilyProcessor):

    def __init__(self, 
        reference_file_path = None, 
        family_out_directory_path = None, 
        session_id = None,
        pre_actions = None, 
        post_actions = None
        ):
        '''
        Class constructor.
        '''

        # store data type  in base class
        string_report_headers = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            rFamData.CATEGORY_NAME
        ]

        # store data type  in base class
        super(FamilyBaseProcessor, self).__init__(
            data_type = 'FamilyBase',
            pre_actions=pre_actions, 
            post_actions=post_actions,
            string_report_headers=string_report_headers
        )

        #self.data = []
        #self.dataType = 'FamilyBase'
        self.reference_file_path = reference_file_path
        self.family_out_directory_path = family_out_directory_path
        if(session_id != None):
            self.session_id = uBP.AdjustSessionIdForFolderName(session_id)
        else:
            self.session_id = session_id

        #self.preActions = preActions
        #self.postActions = postActions

    def process(self, doc, root_path, root_category_path):
        '''
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param rootCategoryPath: The path of the nested family in in terms of category in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategoryPath: str
        '''

        dummy = rFamData.FamilyBaseData(root_path, root_category_path, self.data_type)
        dummy.process(doc, self.reference_file_path, self.family_out_directory_path, self.session_id)
        self.data.append(dummy)
