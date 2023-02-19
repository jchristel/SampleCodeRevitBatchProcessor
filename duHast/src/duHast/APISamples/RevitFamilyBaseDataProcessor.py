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

from duHast.APISamples.IFamilyProcessor import IFamilyProcessor
from duHast.APISamples import RevitFamilyBaseData as rFamData
from duHast.APISamples import IFamilyData as IFamData
from duHast.Utilities import UtilBatchP as uBP

class FamilyBaseProcessor(IFamilyProcessor):

    def __init__(self, 
        referenceFilePath = None, 
        familyOutFolderPath = None, 
        sessionId = None,
        preActions = None, 
        postActions = None
        ):
        '''
        Class constructor.
        '''
        self.data = []
        self.dataType = 'FamilyBase'
        self.referenceFilePath = referenceFilePath
        self.familyOutFolderPath = familyOutFolderPath
        if(sessionId != None):
            self.sessionId = uBP.AdjustSessionIdForFolderName(sessionId)
        else:
            self.sessionId = sessionId

        self.stringReportHeaders = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            rFamData.CATEGORY_NAME
        ]

        self.preActions = preActions
        self.postActions = postActions

    def process(self, doc, rootPath, rootCategoryPath):
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

        dummy = rFamData.FamilyBaseData(rootPath, rootCategoryPath, self.dataType)
        dummy.process(doc, self.referenceFilePath, self.familyOutFolderPath, self.sessionId)
        self.data.append(dummy)
