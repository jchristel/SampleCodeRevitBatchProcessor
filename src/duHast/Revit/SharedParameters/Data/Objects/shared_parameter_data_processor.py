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
from duHast.Revit.SharedParameters import shared_parameter_data as rSharedData
from duHast.Revit.Family.Data.Objects import ifamily_data as IFamData
from duHast.Revit.Family.Data.Objects.ifamily_data_storage import IFamilyDataStorage
from duHast.Utilities.Objects import result as res


class SharedParameterProcessor(IFamilyProcessor):
    def __init__(self, pre_actions=None, post_actions=None):
        """
        Class constructor.
        """

        # store data type  in base class
        super(SharedParameterProcessor, self).__init__(
            pre_actions=pre_actions,
            post_actions=[self._post_action_update_used_shared_parameters],
            data_type="SharedParameter",
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
        :param rootCategoryPath: The categroy path of the nested family in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategoryPath: str
        """

        dummy = rSharedData.SharedParameterData(
            root_path, root_category_path, self.data_type
        )
        dummy.process(doc)
        self.data.append(dummy)

    def _is_shared_parameter_present(
        self, root_family_data, nested_family_shared_parameter_storage
    ):
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

    def _update_root_family_data(self, root_family_data, nested_families_shared_parameters):
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
        
        # loop over nested family data
        for nested_shared_parameter_storage in nested_families_shared_parameters:
            
            if isinstance(nested_shared_parameter_storage, IFamilyDataStorage) == False:
                raise ValueError(
                    "Nested family sub category must be an instance of IFamilyDataStorage but is type: {}".format(
                        type(nested_shared_parameter_storage)
                    )
                )
            
            # check if item is already in root family
            matching_root_fam_parameter_data = self._is_shared_parameter_present(
                root_family_data, nested_shared_parameter_storage
            )
            if matching_root_fam_parameter_data != None:
                root_storage_all = matching_root_fam_parameter_data.get_root_storage()
                
                # some data instances might have more than one root storage instance to represent multiple categories present in the family
                for root_storage in root_storage_all:
                    # update used by list
                    # TODO: this check looks odd!! ( guid vs a dictionary?)
                    # used by is a list of dictionaries where one value is the guid
                    if (
                        nested_shared_parameter_storage.parameter_guid 
                        not in root_storage.used_by
                    ):
                        # add the root path to the used by list for ease of identification of the origin of this shared parameter
                        matching_root_fam_parameter_data[IFamData.USED_BY].append(
                            {
                                rSharedData.PARAMETER_GUID: nested_shared_parameter_storage[
                                    rSharedData.PARAMETER_GUID
                                ],
                                rSharedData.PARAMETER_NAME: nested_shared_parameter_storage[
                                    rSharedData.PARAMETER_NAME
                                ],
                                IFamData.ROOT: nested_shared_parameter_storage[IFamData.ROOT],
                            }
                        )
                        # update used by counter
                        matching_root_fam_parameter_data[IFamData.USAGE_COUNTER] = (
                            matching_root_fam_parameter_data[IFamData.USAGE_COUNTER] + 1
                        )
            else:
                pass
                # nothing to do if that shared parameter has not been reported to start off with

    def _get_used_shared_parameters(self, data):
        used_shared_paras = []
        for d in data:
            if d[IFamData.USAGE_COUNTER] > 0:
                used_shared_paras.append(d)
        return used_shared_paras

    def _post_action_update_used_shared_parameters(self, doc):
        return_value = res.Result()
        try:
            # find all shared parameters of nested families
            nested_family_data = self._find_nested_families_data()
            # get used shared parameters from nested data
            nested_family_shared_parameters = self._get_used_shared_parameters(
                nested_family_data
            )
            # update root family data only
            rootFamilyData = self._find_root_family_data()
            # update root processor data as required
            self._update_root_family_data(
                rootFamilyData, nested_family_shared_parameters
            )
            return_value.update_sep(
                True, "Post Action Update shared parameters data successful completed."
            )
        except Exception as e:
            return_value.update_sep(
                False,
                "Post Action Update shared parameters data failed with exception: "
                + str(e),
            )
        return return_value
