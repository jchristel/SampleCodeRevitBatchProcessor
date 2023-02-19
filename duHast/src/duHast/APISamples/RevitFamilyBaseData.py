'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family base data class.
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

from duHast.APISamples import IFamilyData as IFamData
from duHast.Utilities import Utility as util
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitFamilyBaseDataUtils as rFamBaseDataUtils

# import Autodesk
#import Autodesk.Revit.DB as rdb

# data dictionary key values specific to this class
CATEGORY_NAME = 'categoryName'

class FamilyBaseData(IFamData.IFamilyData):
    
    def __init__(self, rootPath=None, rootCategoryPath=None, dataType=None):
        '''
        Class constructor

        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param dataType: Human readable data type descriptor
        :type dataType: str
        '''

        # todo: check inheritance!!
        # super(CategoryData, self).__init__(rootPath, dataType)

        self.data = []
        
        if(dataType != None):
            self.dataType = dataType
        else:
            self.dataType = 'not declared'
        
        if(rootPath != None):
            self.rootPath = rootPath
        else:
            self.rootPath = '-'

        if(rootCategoryPath != None):
            self.rootCategoryPath = rootCategoryPath
        else:
            self.rootCategoryPath = '-'
        
        if(rootCategoryPath != None):
            categoryChunks = rootCategoryPath.split(' :: ')
            self.category = categoryChunks[-1]
        else:
            self.category = 'unknown'

    def _saveOut(self, doc, referenceFilePath, docName, docCategory, familyOutFolderPath, sessionId):
        '''
        Saves a family to file if there is no match for it in the provided reference file. 
        The reference file is a FamilyBaseDataCombinedReport and is read into tuples using RevitFamilyBaseDataUtils.

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        :param referenceFilePath: Fully qualified file path to FamilyBaseDataCombinedReport file.
        :type referenceFilePath: str
        :param docName: The current family name.
        :type docName: str_
        :param docCategory: The family Revit category.
        :type docCategory: str
        :param familyOutFolderPath: The root directory path to which a family is saved. The script will create a sub directory\
            based on the revit batch processor session id and within that folder another sub directory based on the family Revit category:\
                familyOutFolderPath\\SessionId\\RevitCategory\\Myfamily.rfa
        :type familyOutFolderPath: str
        :param sessionId: The batchprocessor session Id (formatted so it can be used as a folder name)
        :type sessionId: str
        '''

        # process reference file list and look for a match:
        # based on file name and category
        if(util.FileExist(referenceFilePath)):
            # read overall family base data from file 
            overallFamilyBaseRootData, overallFamilyBaseNestedData = rFamBaseDataUtils.ReadOverallFamilyDataList(referenceFilePath)
            foundMatch = False
            for rootFam in overallFamilyBaseRootData:
                # check whether name and category are a match
                if(rootFam.name == docName and rootFam.category == docCategory):
                    foundMatch = True
                    break
            # check if family needs saving out
            if(foundMatch == False):
                # check session id folder exists
                if(util.CreateTargetFolder(familyOutFolderPath, sessionId)):
                    # check category folder exists
                    if(util.CreateTargetFolder(familyOutFolderPath + '\\' + sessionId, docCategory)):
                        # save family out
                        com.SaveAsFamily(
                            doc,
                            familyOutFolderPath + '\\' + sessionId + '\\'+ docCategory,
                            docName,
                            [[docName, docName]]
                            )

    def process(self, doc, referenceFilePath, familyOutFolderPath, sessionId):
        '''
        Collects all base data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        '''

        # get the family category name 
        #famCatName = doc.OwnerFamily.FamilyCategory.Name

        # check if a reference file list was provided and if so if family needs to be saved out
        if (referenceFilePath != None and familyOutFolderPath != None and sessionId != None):
            self._saveOut(
                doc, 
                referenceFilePath, 
                self._stripFileExtension(doc.Title), 
                self.category, 
                familyOutFolderPath, 
                sessionId
                )
        
        # build data
        self.data.append(
            {
                IFamData.ROOT : self.rootPath,
                IFamData.ROOT_CATEGORY : self.rootCategoryPath,
                IFamData.FAMILY_NAME : self._stripFileExtension(doc.Title),
                IFamData.FAMILY_FILE_PATH : doc.PathName, # this property will often be an empty string in nested families
                CATEGORY_NAME : self.category
            }
        )

    def get_Data(self):
        return self.data