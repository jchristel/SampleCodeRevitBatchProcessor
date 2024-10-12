"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family shared parameter data processor class.
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
from duHast.Revit.SharedParameters.Data.Objects import (
    shared_parameter_data as rSharedData,
)
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_shared_parameter_processor,
)
from duHast.Revit.Family.Data.Objects import ifamily_data as IFamData
from duHast.Revit.Family.Data.Objects.ifamily_data_storage import IFamilyDataStorage
from duHast.Utilities.Objects import result as res


class SharedParameterProcessor(IFamilyProcessor):

    data_type = data_type_shared_parameter_processor

    def __init__(self, pre_actions=None, post_actions=None):
        """
        Class constructor.
        """

        # store data type  in base class
        super(SharedParameterProcessor, self).__init__(
            pre_actions=pre_actions,
            post_actions=[self._post_action_update_used_shared_parameters],
            data_type=SharedParameterProcessor.data_type,
        )

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
        :param rootCategoryPath: The category path of the nested family in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategoryPath: str
        """

        dummy = rSharedData.SharedParameterData(root_path, root_category_path)
        dummy.process(doc)
        self.data.append(dummy)

    # TODO: this could go into a base class function
    def _is_shared_parameter_present(
        self, root_family_data, nested_family_shared_parameter_storage
    ):
        """
        Check if shared parameter is present in the root family data.

        :param root_family_data: List of root family data instances.
        :type root_family_data: list
        :param nested_family_shared_parameter_storage: Nested family shared parameter storage instance.
        :type nested_family_shared_parameter_storage: IFamilyDataStorage

        :return: Matched root family data instance.
        :rtype: IFamilyData
        """

        # check what came is a list
        if isinstance(root_family_data, list) == False:
            raise ValueError(
                "Root family data must be a list but is type: {}".format(
                    type(root_family_data)
                )
            )

        if (
            isinstance(nested_family_shared_parameter_storage, IFamilyDataStorage)
            == False
        ):
            raise ValueError(
                "Nested family shared parameter storage must be an instance of IFamilyDataStorage but is type: {}".format(
                    type(nested_family_shared_parameter_storage)
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
                    storage_root.parameter_guid
                    == nested_family_shared_parameter_storage.parameter_guid
                ):
                    match = root_fam
                    break
        return match

    # TODO: this could go into a base class function
    def _update_root_family_data(
        self, root_family_data, nested_families_shared_parameters
    ):
        """
        Update the root family data with the shared parameters from nested families.

        :param root_family_data: List of root family data instances. (one per shared parameter in the root family)
        :type root_family_data: list
        :param nested_families_shared_parameters: List of nested families shared parameters.
        :type nested_families_shared_parameters: list
        """

        # check what came is a list
        if isinstance(root_family_data, list) == False:
            raise ValueError(
                "Root family data must be a list but is type: {}".format(
                    type(root_family_data)
                )
            )
        if isinstance(nested_families_shared_parameters, list) == False:
            raise ValueError(
                "Nested families shared parameters must be a list but is type: {}".format(
                    type(nested_families_shared_parameters)
                )
            )

        # loop over nested family storage instances and check whether any parameter listed exists in the the root family
        for nested_shared_parameter_storage in nested_families_shared_parameters:

            # check this is an instance of IFamilyDataStorage
            if isinstance(nested_shared_parameter_storage, IFamilyDataStorage) == False:
                raise ValueError(
                    "Nested family sub category must be an instance of IFamilyDataStorage but is type: {}".format(
                        type(nested_shared_parameter_storage)
                    )
                )

            # check if parameter is in root family already
            matching_root_fam_parameter_data = self._is_shared_parameter_present(
                root_family_data, nested_shared_parameter_storage
            )
            if matching_root_fam_parameter_data != None:
                root_storage_all = matching_root_fam_parameter_data.get_root_storage()

                # some data instances might have more than one root storage instance to represent multiple shared parameters present in the family
                for root_storage in root_storage_all:
                    # update used by list
                    # by parameter guid
                    if (
                        nested_shared_parameter_storage.parameter_guid
                        == root_storage.parameter_guid
                    ):
                        root_storage.update_usage(nested_shared_parameter_storage)
                        # can stop looping at this point since there will be ever only one match
                        break
            else:
                pass
                # nothing to do if that shared parameter has not been reported to start off with

    # TODO: this could go into a base class function
    def _get_used_shared_parameters(self, data_instances):
        """
        Get used shared parameters from nested family data.

        :param data_instances: List of IFamilyData objects.
        :type data_instances: list

        :return: List of storage instances representing used shared parameters.
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

    def _post_action_update_used_shared_parameters(self, doc):
        """
        Post action to update shared parameters data in the root family data object.

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document

        :return: Result object with success or failure message.
        :rtype: duHast.Utilities.Objects.result.Result
        """

        return_value = res.Result()
        try:
            # find all shared parameters of nested families
            nested_family_data = self._find_nested_families_data()
            # get used shared parameters from nested data
            nested_family_shared_parameters = self._get_used_shared_parameters(
                nested_family_data
            )
            # update root family data only
            # this will return a list of root family data instances, should be one only per processor
            root_family_data = self._find_root_family_data()
            # update root processor data as required
            self._update_root_family_data(
                root_family_data, nested_family_shared_parameters
            )
            return_value.update_sep(
                True, "Post Action Update shared parameters data successful completed."
            )
        except Exception as e:
            return_value.update_sep(
                False,
                "Post Action Update shared parameters data failed with exception: {}".format(
                    e
                ),
            )
        return return_value
