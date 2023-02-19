'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family shared parameter data class.
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
from duHast.APISamples import RevitSharedParameters as rSharedPara

# import Autodesk
import Autodesk.Revit.DB as rdb


PARAMETER_GUID = 'parameterGUID' 
PARAMETER_NAME = 'parameterName' 
PARAMETER_ID = 'parameterId' 

class SharedParameterData(IFamData.IFamilyData):
    
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
        collector = rSharedPara.GetAllSharedParameters(doc)
        for para in collector:
            # just in case parameter name is not unicode
            parameterName = 'unknown'
            try:   
                parameterName = util.EncodeAscii(rdb.Element.Name.GetValue(para))
            except Exception as ex:
                parameterName = 'Exception: ' + str(ex)
            # check if used:
            useCounter = 0
            usedByData = {}
            if(rSharedPara.IsSharedParameterDefinitionUsed(doc, para)):
                useCounter = 1
                # build used by data as required to be the same as post process update
                usedByData = { 
                    PARAMETER_GUID : para.GuidValue.ToString(),
                    PARAMETER_NAME : parameterName,
                    IFamData.ROOT : self.rootPath
            }
            
            # build data
            self.data.append({
                IFamData.ROOT : self.rootPath,
                IFamData.ROOT_CATEGORY : self.rootCategoryPath,
                IFamData.FAMILY_NAME : self._stripFileExtension(doc.Title),
                IFamData.FAMILY_FILE_PATH : doc.PathName,
                PARAMETER_GUID : para.GuidValue.ToString(),
                PARAMETER_NAME : parameterName,
                PARAMETER_ID : para.Id.IntegerValue,
                IFamData.USAGE_COUNTER : useCounter,
                IFamData.USED_BY : [usedByData]
                }
            )
        
        # check if any shared parameter was found
        if(len(self.data) == 0):
            # add message no shared parameter found
            self.data.append({
                IFamData.ROOT : self.rootPath,
                IFamData.ROOT_CATEGORY : self.rootCategoryPath,
                IFamData.FAMILY_NAME : self._stripFileExtension(doc.Title),
                IFamData.FAMILY_FILE_PATH : doc.PathName,
                PARAMETER_GUID : '',
                PARAMETER_NAME : 'No shared parameter present in family.',
                PARAMETER_ID : -1,
                IFamData.USAGE_COUNTER : 0,
                IFamData.USED_BY : []
                }
            )

        
    def get_Data(self):
        return self.data