'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family warnings data processor class.
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
from duHast.APISamples.Warnings import RevitWarningsData as rWarnData
from duHast.APISamples.Family.Reporting import IFamilyData as IFamData

class WarningsProcessor(IFamilyProcessor):

    def __init__(self,preActions = None, postActions = None):
        '''
        Class constructor.
        '''

        # setup report header
        stringReportHeaders = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            rWarnData.WARNING_TEXT,
            rWarnData.WARNING_GUID,
            rWarnData.WARNING_RELATED_IDS,
            rWarnData.WARNING_OTHER_IDS
        ]

        # store data type  in base class
        super(WarningsProcessor, self).__init__(
            preActions=preActions, 
            postActions=postActions, 
            dataType='Warnings', 
            stringReportHeaders=stringReportHeaders
        )

        #self.data = []
        #self.dataType = 'Warnings'
        #self.preActions = preActions
        #self.postActions = postActions

    def process(self, doc, rootPath, rootCategoryPath):
        '''
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param rootCategoryPath: The categroy path of the nested family in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategoryPath: str
        '''
         
        dummy = rWarnData.WarningsData(rootPath, rootCategoryPath, self.dataType)
        dummy.process(doc)
        self.data.append(dummy)