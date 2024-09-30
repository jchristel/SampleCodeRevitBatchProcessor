"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family line pattern data processor class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#


from duHast.Revit.Family.Data.Objects.ifamily_processor import IFamilyProcessor
from duHast.Revit.LinePattern.Data.Objects import line_pattern_data as rLinePatData
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_line_pattern_processor,
)
from duHast.Revit.Family.Data.Objects import ifamily_data as IFamData
from duHast.Revit.Family.Data.Objects.ifamily_data_storage import IFamilyDataStorage
from duHast.Utilities.Objects import result as res


class LinePatternProcessor(IFamilyProcessor):

    data_type = data_type_line_pattern_processor

    def __init__(self, pre_actions=None, post_actions=None):
        """
        Class constructor.
        """

        # store data type  in base class
        super(LinePatternProcessor, self).__init__(
            pre_actions=pre_actions,
            post_actions=[self._post_action_update_used_line_patterns],
            data_type=LinePatternProcessor.data_type,
        )

        # set default post action to updated line patterns used in root processor with any line patterns found in nested
        # families
        # self.postActions = [self._postActionUpdateUsedLinePatterns]
        # add any other post actions
        if post_actions != None:
            for post_action in post_actions:
                self.post_actions.append(post_action)

    def process(self, doc, root_path, root_category_path):
        """
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param rootCategoryPath: The categroy path of the nested family in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategoryPath: str
        """

        dummy = rLinePatData.LinePatternData(root_path, root_category_path)
        dummy.process(doc)
        self.data.append(dummy)

    # TODO: this could go into a base class function
    def _is_sub_line_pattern_present(
        self, root_family_data, nested_family_line_pattern_storage
    ):
        """
        Check if a line pattern is already present in the root family data.

        :param root_family_data: The root family data.
        :type root_family_data: list
        :param nested_family_line_pattern_storage: The nested family line pattern data storage.
        :type nested_family_line_pattern_storage: IFamilyDataStorage
        :return: The root family data if the line pattern is present, otherwise None.
        :rtype: IFamData.IFamilyData
        """

        # check what came is a list
        if isinstance(root_family_data, list) == False:
            raise ValueError(
                "Root family data must be a list but is type: {}".format(
                    type(root_family_data)
                )
            )

        # check what came is a IFamilyDataStorage instance
        # I could check for the exact data storage type here(?)
        if isinstance(nested_family_line_pattern_storage, IFamilyDataStorage) == False:
            raise ValueError(
                "Nested family line pattern storage must be an instance of IFamilyDataStorage but is type: {}".format(
                    type(nested_family_line_pattern_storage)
                )
            )

        match = None
        for root_fam in root_family_data:
            if isinstance(root_fam, IFamData.IFamilyData) == False:
                raise ValueError(
                    "Root family data must be a list of IFamilyData objects but is type: {}".format(
                        type(root_fam)
                    )
                )
            storage_instances = root_fam.get_data()
            for storage_root in storage_instances:
                if (
                    storage_root.pattern_name
                    == nested_family_line_pattern_storage.pattern_name
                ):
                    match = root_fam
                    break
        return match

    # TODO: this could go into a base class function
    def _update_root_family_data(self, root_family_data, nested_families_line_patterns):
        """
        Update the root family data with the nested family line patterns.

        :param root_family_data: The root family data.
        :type root_family_data: list
        :param nested_families_line_patterns: The nested families line patterns.
        :type nested_families_line_patterns: list
        """

        # check what came is a list
        if isinstance(root_family_data, list) == False:
            raise ValueError(
                "Root family data must be a list but is type: {}".format(
                    type(root_family_data)
                )
            )
        if isinstance(nested_families_line_patterns, list) == False:
            raise ValueError(
                "Nested families line patterns must be a list but is type: {}".format(
                    type(nested_families_line_patterns)
                )
            )

        # loop over nested family line pattern data
        for nested_line_pattern_storage in nested_families_line_patterns:
            # check this is an instance of IFamilyDataStorage
            if isinstance(nested_line_pattern_storage, IFamilyDataStorage) == False:
                raise ValueError(
                    "Nested family line pattern must be an instance of IFamilyDataStorage but is type: {}".format(
                        type(nested_line_pattern_storage)
                    )
                )

            # check if pattern is already in root family
            matching_root_fam_pattern_data = self._is_sub_line_pattern_present(
                root_family_data, nested_line_pattern_storage
            )
            if matching_root_fam_pattern_data != None:
                root_storage_all = matching_root_fam_pattern_data.get_root_storage()
                # some data instances might have more than one root storage instance to represent multiple shared parameters present in the family
                for root_storage in root_storage_all:
                    # update used by list
                    if (
                        nested_line_pattern_storage.pattern_name
                        == root_storage.pattern_name
                    ):
                        # add the root path to the used by list for ease of identification of the origin of this pattern usage
                        root_storage.update_usage(nested_line_pattern_storage)
            else:
                pass
                # nothing to do if that pattern has not been reported to start off with
                # this patter could, for example, belong to the section marker family present in most 3d families

    # TODO: this could go into a base class function
    def _get_used_line_patterns(self, data_instances):
        """
        Get all used line patterns from the data instances.

        :param data_instances: List of IFamilyData objects.
        :type data_instances: list

        :return: List of storage instances representing used line patterns.
        :rtype: list
        """

        # data_instances should be a list of IFamilyData objects
        if isinstance(data_instances, list) == False:
            raise ValueError(
                "Data must be a list but is type: {}".format(type(data_instances))
            )

        used_items = []
        for d in data_instances:
            # check what is being processed...should be an IFamilyData object
            if isinstance(d, IFamData.IFamilyData) == False:
                raise ValueError(
                    "Data must be an instance of IFamilyData but is type: {}".format(
                        type(d)
                    )
                )

            # loop over storage of the data instance
            data_storage_instances = d.get_data()
            for storage in data_storage_instances:
                if storage.use_counter > 0:
                    used_items.append(storage)
        return used_items

    def _post_action_update_used_line_patterns(self, doc):
        return_value = res.Result()
        try:
            # find all line patterns of nested families
            nested_family_data = self._find_nested_families_data()
            # get used sub categories from nested data
            nested_family_used_line_patterns = self._get_used_line_patterns(
                nested_family_data
            )
            # update root family data only
            rootFamilyData = self._find_root_family_data()
            # update root processor data as required
            self._update_root_family_data(
                rootFamilyData, nested_family_used_line_patterns
            )
            return_value.update_sep(
                True, "Post Action Update line pattern data successful completed."
            )
        except Exception as e:
            return_value.update_sep(
                False,
                "Post Action Update line pattern data failed with exception: " + str(e),
            )
        return return_value
