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

from duHast.APISamples.Family.Reporting.IFamilyProcessor import IFamilyProcessor
from duHast.APISamples.SharedParameters import RevitSharedParameterData as rSharedData
from duHast.APISamples.Family.Reporting import IFamilyData as IFamData
from duHast.Utilities import Result as res

class SharedParameterProcessor(IFamilyProcessor):

    def __init__(self,pre_actions = None, post_actions = None):
        '''
        Class constructor.
        '''

        # setup report header
        string_report_headers = [
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

        # store data type  in base class
        super(SharedParameterProcessor, self).__init__(
            pre_actions=pre_actions, 
            post_actions=[self._post_action_update_used_shared_parameters], 
            data_type='SharedParameter', 
            string_report_headers=string_report_headers
        )

        #self.data = []
        #self.dataType = 'SharedParameter'
        #self.preActions = preActions
        # set default post action to updated shared parameters used in root processor with any shared parameters found in nested 
        # families
        #self.postActions = [self._postActionUpdateUsedSharedParameters]
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

        dummy = rSharedData.SharedParameterData(root_path, root_category_path, self.data_type)
        dummy.process(doc)
        self.data.append(dummy)
    

    def _is_shared_parameter_present(self,root_family_data, nested_family_line_pattern):
        match = None
        for rootFam in root_family_data:
            if (rootFam[rSharedData.PARAMETER_GUID] == nested_family_line_pattern[rSharedData.PARAMETER_GUID]):
                match = rootFam
                break
        return match

    def _update_root_family_data(self, root_family_data, nested_families_data):
        # loop over nested family data
        for nestedItem in nested_families_data:
            # check if item is already in root family
            matchingRootFamPattern = self._is_shared_parameter_present(root_family_data, nestedItem)
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

    def _get_used_shared_parameters(self, data):
        usedSharedParas = []
        for d in data:
            if(d[IFamData.USAGE_COUNTER] > 0):
                usedSharedParas.append(d)
        return usedSharedParas

    def _post_action_update_used_shared_parameters(self, doc):
        returnValue = res.Result()
        try:
            # find all shared parameters of nested families
            nestedFamilyData = self._find_nested_families_data()
            # get used shared parameters from nested data
            nestedFamilySharedParameters = self._get_used_shared_parameters(nestedFamilyData)
            # update root family data only
            rootFamilyData = self._find_root_family_data()
            # update root processor data as required
            self._update_root_family_data(rootFamilyData, nestedFamilySharedParameters)
            returnValue.update_sep(True, 'Post Action Update shared parameters data successful completed.')
        except Exception as e:
            returnValue.update_sep(False, 'Post Action Update shared parameters data failed with exception: ' + str(e))
        return returnValue