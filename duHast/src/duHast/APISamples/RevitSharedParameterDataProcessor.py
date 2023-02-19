'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family shared parameter data processor class.
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
from duHast.APISamples import RevitSharedParameterData as rSharedData
from duHast.APISamples import IFamilyData as IFamData
from duHast.Utilities import Result as res

class SharedParameterProcessor(IFamilyProcessor):

    def __init__(self,preActions = None, postActions = None):
        self.data = []
        self.dataType = 'SharedParameter'
        self.stringReportHeaders = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            rSharedData.PARAMETER_NAME,
            rSharedData.PARAMETER_GUID,
            rSharedData.PARAMETER_ID,
            IFamData.USAGE_COUNTER,
            IFamData.USED_BY
        ]

        self.preActions = preActions
        # set default post action to updated shared parameters used in root processor with any shared parameters found in nested 
        # families
        self.postActions = [self._postActionUpdateUsedSharedParameters]
        # add any other post actions
        if (postActions != None):
            for pAction in postActions:
                self.postActions.append(pAction)

    def process(self, doc, rootPath, rootCategoryPath):
        dummy = rSharedData.SharedParameterData(rootPath, rootCategoryPath, self.dataType)
        dummy.process(doc)
        self.data.append(dummy)
    

    def _isSharedParameterPresent(self,rootFamilyData, nestedFamilyLinePattern):
        match = None
        for rootFam in rootFamilyData:
            if (rootFam[rSharedData.PARAMETER_GUID] == nestedFamilyLinePattern[rSharedData.PARAMETER_GUID]):
                match = rootFam
                break
        return match

    def _updateRootFamilyData(self, rootFamilyData, nestedFamiliesData):
        # loop over nested family data
        for nestedItem in nestedFamiliesData:
            # check if item is already in root family
            matchingRootFamPattern = self._isSharedParameterPresent(rootFamilyData, nestedItem)
            if(matchingRootFamPattern != None):
                # update used by list
                # TODO: this check looks odd!! ( guid vs a dictionary?)
                if(nestedItem[rSharedData.PARAMETER_GUID] not in matchingRootFamPattern[IFamData.USED_BY]):
                    # add the root path to the used by list for ease of identification of the origin of this shared parameter
                    matchingRootFamPattern[IFamData.USED_BY].append(
                        { 
                            rSharedData.PARAMETER_GUID : nestedItem[rSharedData.PARAMETER_GUID],
                            rSharedData.PARAMETER_NAME : nestedItem[rSharedData.PARAMETER_NAME],
                            IFamData.ROOT : nestedItem[IFamData.ROOT]
                        }
                    )
                    # update used by counter
                    matchingRootFamPattern[IFamData.USAGE_COUNTER] = matchingRootFamPattern[IFamData.USAGE_COUNTER] + 1
            else:
                pass
                # nothing to do if that shared parameter has not been reported to start off with 

    def _getUsedSharedParameters(self, data):
        usedSharedParas = []
        for d in data:
            if(d[IFamData.USAGE_COUNTER] > 0):
                usedSharedParas.append(d)
        return usedSharedParas

    def _postActionUpdateUsedSharedParameters(self, doc):
        returnValue = res.Result()
        try:
            # find all shared parameters of nested families
            nestedFamilyData = self._findNestedFamiliesData()
            # get used shared parameters from nested data
            nestedFamilySharedParameters = self._getUsedSharedParameters(nestedFamilyData)
            # update root family data only
            rootFamilyData = self._findRootFamilyData()
            # update root processor data as required
            self._updateRootFamilyData(rootFamilyData, nestedFamilySharedParameters)
            returnValue.UpdateSep(True, 'Post Action Update shared parameters data successful completed.')
        except Exception as e:
            returnValue.UpdateSep(False, 'Post Action Update shared parameters data failed with exception: ' + str(e))
        return returnValue