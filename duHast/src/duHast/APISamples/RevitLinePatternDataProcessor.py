'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family line pattern data processor class.
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
from duHast.APISamples import RevitLinePatternData as rLinePatData
from duHast.APISamples import IFamilyData as IFamData
from duHast.Utilities import Result as res

class LinePatternProcessor(IFamilyProcessor):

    def __init__(self, preActions = None, postActions = None):
        '''
        Class constructor.
        '''
        self.data = []
        self.dataType = 'LinePattern'
        self.stringReportHeaders = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            IFamData.USAGE_COUNTER,
            IFamData.USED_BY,
            rLinePatData.PATTERN_NAME,
            rLinePatData.PATTERN_ID
        ]

        self.preActions = preActions
        # set default post action to updated line patterns used in root processor with any line patterns found in nested 
        # families
        self.postActions = [self._postActionUpdateUsedLinePatterns]
        # add any other post actions
        if (postActions != None):
            for pAction in postActions:
                self.postActions.append(pAction)

    def process(self, doc, rootPath, rootCategoryPath):
        '''
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        '''

        dummy = rLinePatData.LinePatternData(rootPath, rootCategoryPath, self.dataType)
        dummy.process(doc)
        self.data.append(dummy)
    
    def _isSubLinePatternPresent(self,rootFamilyData, nestedFamilyLinePattern):
        match = None
        for rootFam in rootFamilyData:
            if (rootFam[rLinePatData.PATTERN_NAME] == nestedFamilyLinePattern[rLinePatData.PATTERN_NAME]):
                match = rootFam
                break
        return match
    
    def _updateRootFamilyData(self, rootFamilyData, nestedFamiliesLinePatterns):
        # loop over nested family line pattern data
        for nestedLinePattern in nestedFamiliesLinePatterns:
            # check if pattern is already in root family
            matchingRootFamPattern = self._isSubLinePatternPresent(rootFamilyData, nestedLinePattern)
            if(matchingRootFamPattern != None):
                # update used by list
                if( nestedLinePattern[rLinePatData.PATTERN_NAME] not in matchingRootFamPattern[IFamData.USED_BY]):
                    # add the root path to the used by list for ease of identification of the origin of this pattern usage
                    matchingRootFamPattern[IFamData.USED_BY].append(
                        { 
                            rLinePatData.PATTERN_ID : nestedLinePattern[rLinePatData.PATTERN_ID],
                            IFamData.ROOT : nestedLinePattern[IFamData.ROOT]
                        }
                    )
                    # update used by counter
                    matchingRootFamPattern[IFamData.USAGE_COUNTER] = matchingRootFamPattern[IFamData.USAGE_COUNTER] + 1
            else:
                pass
                # nothing to do if that pattern has not been reported to start off with 
                # this patter could, for example, belong to the section marker family present in most 3d families

    def _getUsedLinePatterns(self, data):
        usedLinePatterns = []
        for d in data:
            if(d[IFamData.USAGE_COUNTER] > 0):
                usedLinePatterns.append(d)
        return usedLinePatterns

    def _postActionUpdateUsedLinePatterns(self, doc):
        returnValue = res.Result()
        try:
            # find all line patterns of nested families
            nestedFamilyData = self._findNestedFamiliesData()
            # get used sub categories from nested data
            nestedFamilyUsedLinePatterns = self._getUsedLinePatterns(nestedFamilyData)
            # update root family data only
            rootFamilyData = self._findRootFamilyData()
            # update root processor data as required
            self._updateRootFamilyData(rootFamilyData, nestedFamilyUsedLinePatterns)
            returnValue.UpdateSep(True, 'Post Action Update line pattern data successful completed.')
        except Exception as e:
            returnValue.UpdateSep(False, 'Post Action Update line pattern data failed with exception: ' + str(e))
        return returnValue
