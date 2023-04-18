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


from duHast.APISamples.Family.Reporting.IFamilyProcessor import IFamilyProcessor
from duHast.APISamples.LinePattern import RevitLinePatternData as rLinePatData
from duHast.APISamples.Family.Reporting import IFamilyData as IFamData
from duHast.Utilities import Result as res

class LinePatternProcessor(IFamilyProcessor):

    def __init__(self, pre_actions = None, post_actions = None):
        '''
        Class constructor.
        '''

        # setup report header
        string_report_headers = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            IFamData.USAGE_COUNTER,
            IFamData.USED_BY,
            rLinePatData.PATTERN_NAME,
            rLinePatData.PATTERN_ID
        ]

        # store data type  in base class
        super(LinePatternProcessor, self).__init__(
            pre_actions=pre_actions, 
            post_actions=[self._post_action_update_used_line_patterns], 
            data_type='LinePattern', 
            string_report_headers=string_report_headers
        )

        #self.data = []
        #self.dataType = 'LinePattern'
        #self.preActions = preActions

        # set default post action to updated line patterns used in root processor with any line patterns found in nested 
        # families
        #self.postActions = [self._postActionUpdateUsedLinePatterns]
        # add any other post actions
        if (post_actions != None):
            for post_action in post_actions:
                self.post_actions.append(post_action)

    def process(self, doc, root_path, root_category_path):
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

        dummy = rLinePatData.LinePatternData(root_path, root_category_path, self.data_type)
        dummy.process(doc)
        self.data.append(dummy)
    
    def _is_sub_line_pattern_present(self,rootFamilyData, nestedFamilyLinePattern):
        match = None
        for rootFam in rootFamilyData:
            if (rootFam[rLinePatData.PATTERN_NAME] == nestedFamilyLinePattern[rLinePatData.PATTERN_NAME]):
                match = rootFam
                break
        return match
    
    def _update_root_family_data(self, root_family_data, nested_families_line_patterns):
        # loop over nested family line pattern data
        for nestedLinePattern in nested_families_line_patterns:
            # check if pattern is already in root family
            matchingRootFamPattern = self._is_sub_line_pattern_present(root_family_data, nestedLinePattern)
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

    def _get_used_line_patterns(self, data):
        usedLinePatterns = []
        for d in data:
            if(d[IFamData.USAGE_COUNTER] > 0):
                usedLinePatterns.append(d)
        return usedLinePatterns

    def _post_action_update_used_line_patterns(self, doc):
        returnValue = res.Result()
        try:
            # find all line patterns of nested families
            nestedFamilyData = self._find_nested_families_data()
            # get used sub categories from nested data
            nestedFamilyUsedLinePatterns = self._get_used_line_patterns(nestedFamilyData)
            # update root family data only
            rootFamilyData = self._find_root_family_data()
            # update root processor data as required
            self._update_root_family_data(rootFamilyData, nestedFamilyUsedLinePatterns)
            returnValue.update_sep(True, 'Post Action Update line pattern data successful completed.')
        except Exception as e:
            returnValue.update_sep(False, 'Post Action Update line pattern data failed with exception: ' + str(e))
        return returnValue
