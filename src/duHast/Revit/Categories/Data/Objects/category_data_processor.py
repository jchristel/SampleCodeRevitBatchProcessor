"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family category data processor class.
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
from duHast.Revit.Categories.Data.Objects import category_data as rCatData
from duHast.Revit.Categories.Data.Objects.category_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_category_processor,
)
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)
from duHast.Revit.Family.Data.Objects import ifamily_data as IFamData
from duHast.Revit.Family.Data.Objects.ifamily_data_storage import IFamilyDataStorage
from duHast.Utilities.Objects import result as res


class CategoryProcessor(IFamilyProcessor):

    data_type = data_type_category_processor

    def __init__(self, pre_actions=None, post_actions=None):
        """
        Class constructor.
        """

        # store data type  in base class
        super(CategoryProcessor, self).__init__(
            pre_actions=pre_actions,
            post_actions=[self._post_action_update_used_subcategories],
            data_type=CategoryProcessor.data_type,
        )

        # self.data = []
        # self.dataType = 'Category'

        # list of corner cases when it comes to category checking: imports in families or Reference planes ... ( english language specific!! )
        self.category_check_corner_cases = ["Imports in Families", "Reference Planes"]

        # self.preActions = preActions
        # set default post action to updated categories used in root processor with any categories found in nested
        # families
        # self.postActions = [self._postActionUpdateUsedSubcategories]
        # add any other post actions
        if post_actions != None:
            for p_action in post_actions:
                self.post_actions.append(p_action)

    def process(self, doc, root_path, root_category_path):
        """
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param root_path: The path of the nested family in a tree: rootFamilyName :: nestedFamilyNameOne :: nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type root_path: str
        :param root_category_path: The category path of the nested family in a tree: rootFamilyCategory :: nestedFamilyOneCategory :: nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type root_category_path: str
        """

        dummy = rCatData.CategoryData(root_path, root_category_path)
        dummy.process(doc)
        self.data.append(dummy)

    # --------------------------------------------- post action ----------------------------------------------------------

    def _is_sub_category_present(
        self, root_family_data, nested_family_sub_category_storage
    ):
        """
        Check if sub category is present in root family data.

        :param root_family_data: List of IFamilyData objects.
        :type root_family_data: list
        :param nested_family_sub_category_storage: IFamilyDataStorage object.
        :type nested_family_sub_category_storage: IFamilyDataStorage
        :return: IFamilyData object.
        :rtype: IFamilyData
        """

        # check what came is a list
        if isinstance(root_family_data, list) == False:
            raise ValueError(
                "Root family data must be a list but is type: {}".format(
                    type(root_family_data)
                )
            )
        if isinstance(nested_family_sub_category_storage, IFamilyDataStorage) == False:
            raise ValueError(
                "Nested family sub category storage must be an instance of IFamilyDataStorage but is type: {}".format(
                    type(nested_family_sub_category_storage)
                )
            )

        match = None
        # check whether sub category is present
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
                    storage_root.category_name
                    == nested_family_sub_category_storage.category_name
                    and storage_root.sub_category_name
                    == nested_family_sub_category_storage.sub_category_name
                ):
                    match = root_fam
                    break
        return match

    def _update_root_family_data(
        self, root_family_data, nested_families_sub_categories
    ):
        """
        Update root family data with used subcategories from nested families.

        :param root_family_data: List of IFamilyData objects.
        :type root_family_data: list
        :param nested_families_sub_categories: List of IFamilyDataStorage objects.
        :type nested_families_sub_categories: list
        """

        # check what came is a list
        if isinstance(root_family_data, list) == False:
            raise ValueError(
                "Root family data must be a list but is type: {}".format(
                    type(root_family_data)
                )
            )
        if isinstance(nested_families_sub_categories, list) == False:
            raise ValueError(
                "Nested families sub categories must be a list but is type: {}".format(
                    type(nested_families_sub_categories)
                )
            )

        # loop over nested family subcategory storage data
        for nested_sub_category_storage in nested_families_sub_categories:

            if isinstance(nested_sub_category_storage, IFamilyDataStorage) == False:
                raise ValueError(
                    "Nested family sub category must be an instance of IFamilyDataStorage but is type: {}".format(
                        type(nested_sub_category_storage)
                    )
                )

            # check if sub category is already in root family
            matching_root_fam_category_data = self._is_sub_category_present(
                root_family_data, nested_sub_category_storage
            )
            if matching_root_fam_category_data != None:
                root_storage_all = matching_root_fam_category_data.get_root_storage()

                # some data instances might have more than one root storage instance to represent multiple categories present in the family
                for root_storage in root_storage_all:
                    if (
                        nested_sub_category_storage.category_name
                        == root_storage.category_name
                    ) and (
                        nested_sub_category_storage.sub_category_name
                        == root_storage.sub_category_name
                    ):
                        # update used by list
                        if (
                            nested_sub_category_storage.family_name
                            not in root_storage.used_by
                        ):
                            root_storage.update_usage(nested_sub_category_storage)
            else:
                pass
                # nothing to do if that category has not been reported to start off with
                # this category could, for example, belong to the section marker family present in most 3d families

    def _get_used_subcategories(self, data_instances):
        """
        Get used subcategories from nested families data as list of IFamilyDataStorage objects.

        :param data_instances: List of IFamilyData objects.
        :type data_instances: list
        :return: List of IFamilyDataStorage objects.
        :rtype: list
        """

        # data_instances should be a list of IFamilyData objects
        if isinstance(data_instances, list) == False:
            raise ValueError(
                "Data must be a list but is type: {}".format(type(data_instances))
            )

        used_subcategories = []
        for d in data_instances:

            # check what is being processed...should be an IFamilyData object
            if isinstance(d, IFamData.IFamilyData) == False:
                raise ValueError(
                    "Data must be an instance of IFamilyData but is type: {}".format(
                        type(d)
                    )
                )

            # TODO: check if the root category path is correct
            # should I get the first or last entry?? Might need to be the first?
            # i'm not entirely sure why I'm checking this here...
            # is this so I only delete sub categories in the root family which are not in use any where in the nested families of the same category?
            # i.e Furniture.OverHead assumes the host family is of Category Furniture and I am checking whether the sub category OverHead is in use in any
            # of the nested families as well as the host family?

            # The report (storage data ) also contains two fields: Category and SubCategory. Category in this case can well be different to the category of the family!

            # loop over storage of the data instance
            data_storage_instances = d.get_data()
            for storage in data_storage_instances:
                if storage.use_counter > 0:
                    # get the family category
                    category_path = storage.root_category_path.split(NESTING_SEPARATOR)
                    # which is the last entry in the root category path
                    category_storage = category_path[len(category_path) - 1]
                    # select only items which either belong to the category of the family or
                    # are corner cases like imports in families or Reference planes ... ( english language specific!! )
                    if (
                        category_storage == storage.category_name
                        or storage.category_name in self.category_check_corner_cases
                    ):
                        used_subcategories.append(storage)
        return used_subcategories

    def _post_action_update_used_subcategories(self, doc):
        """
        Post action to update used subcategories data in the root family data object.

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :return: Result object.
        :rtype: Result
        """

        return_value = res.Result()
        try:
            # find all subcategories of nested families
            nested_family_data = self._find_nested_families_data()
            # get used sub categories from nested data
            nested_family_used_sub_categories = self._get_used_subcategories(
                data_instances=nested_family_data
            )
            # update root family data only
            root_family_data = self._find_root_family_data()
            # update root processor data as required
            self._update_root_family_data(
                root_family_data, nested_family_used_sub_categories
            )
            return_value.update_sep(
                True, "Post Action Update subcategories data successful completed."
            )
        except Exception as e:
            return_value.update_sep(
                False,
                "Post Action Update subcategories data failed with exception: {}".format(
                    e
                ),
            )
        return return_value
