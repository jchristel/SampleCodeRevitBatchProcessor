'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family warnings data class.
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
from duHast.APISamples import RevitWarnings as rWarn

# import Autodesk
#import Autodesk.Revit.DB as rdb

WARNING_TEXT = 'warningText'
WARNING_GUID = 'warningGUID'
WARNING_RELATED_IDS = 'warningRelatedIds' 
WARNING_OTHER_IDS = 'warningOtherIds' 

class WarningsData(IFamData.IFamilyData):
    
    def __init__(self, rootPath=None, rootCategoryPath=None, dataType=None):

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
    
    def process(self, doc):
        # get all warnings in document
        warnings = rWarn.GetWarnings(doc)
        # loop over warnings and extract data
        for warning in warnings:
            # check for a guid
            warGUID = ''
            try:
                warGUID = warning.GetFailureDefinitionId().Guid
            except Exception as e:
                pass
            # warning text
            warText = ''
            try:
                warText = warning.GetDescriptionText()
            except Exception as e:
                pass
            # affected element ids
            warElementIdsAsInteger = []
            try:
                for el in warning.GetFailingElements():
                    warElementIdsAsInteger.append(el.IntegerValue)
            except Exception as e:
                pass
            # other element ids
            warOtherElementIdsAsInteger = []
            try:
                for el in warning.GetAdditionalElements():
                    warOtherElementIdsAsInteger.append(el.IntegerValue)
            except Exception as e:
                pass

            # build data
            self.data.append({
                IFamData.ROOT : self.rootPath,
                IFamData.ROOT_CATEGORY : self.rootCategoryPath,
                IFamData.FAMILY_NAME : doc.Title,
                IFamData.FAMILY_FILE_PATH : doc.PathName,
                WARNING_TEXT : warText,
                WARNING_GUID : warGUID,
                WARNING_RELATED_IDS : warElementIdsAsInteger,
                WARNING_OTHER_IDS: warOtherElementIdsAsInteger
                }
            )
        
        # check if any shared parameter was found
        if(len(self.data) == 0):
            # add message no warnings found
            # build data
            self.data.append({
                IFamData.ROOT : self.rootPath,
                IFamData.ROOT_CATEGORY : self.rootCategoryPath,
                IFamData.FAMILY_NAME : doc.Title,
                IFamData.FAMILY_FILE_PATH : doc.PathName,
                WARNING_TEXT : 'No warnings present in family.',
                WARNING_GUID : '',
                WARNING_RELATED_IDS : [],
                WARNING_OTHER_IDS: []
                }
            )

    def get_Data(self):
        return self.data