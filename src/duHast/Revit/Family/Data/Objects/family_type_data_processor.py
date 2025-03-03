"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family type data processor class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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
from duHast.Revit.Family.Data.Objects.family_type_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_family_base_processor,
)
from duHast.Revit.Family.Data.Objects import family_type_data as rFamData
from duHast.Revit.Family.family_types_get_data_from_xml import get_type_data_via_XML_from_family_file
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities import util_batch_p as uBP
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.Objects.family_type_data_storage_manager import FamilyTypeDataStorageManager


class FamilyTypeProcessor(IFamilyProcessor):

    data_type = data_type_family_base_processor

    def __init__(
        self,
        session_id=None,
        pre_actions=None,
        post_actions=None,
        family_file_path=None,
        revit_application=None,
    ):
        """
        Class constructor.
        """

        # store data type  in base class
        super(FamilyTypeProcessor, self).__init__(
            data_type=FamilyTypeProcessor.data_type,
            pre_actions=pre_actions,
            post_actions=post_actions,
        )

        if session_id != None:
            self.session_id = uBP.adjust_session_id_for_directory_name(session_id)
        else:
            self.session_id = session_id
        
        # store the file path of the family file
        self.family_file_path = family_file_path

        # store the revit application object
        self.revit_application = revit_application

        # add default pre actions
        if pre_actions == None:
            self.pre_actions=[self._pre_action_get_xml_root]
        else:
            self.pre_actions.append(self._pre_action_get_xml_root)
        
        # currently no post actions...
       

    def process(self, doc, root_path, root_category_path):
        """
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param rootPath: The path of the nested family in a tree: rootFamilyName :: nestedFamilyNameOne :: nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param rootCategoryPath: The path of the nested family in in terms of category in a tree: rootFamilyCategory :: nestedFamilyOneCategory :: nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategoryPath: str
        """

        dummy = rFamData.FamilyTypeData(root_path, root_category_path)
        dummy.process(
            doc,
            self.session_id,
        )
        self.data.append(dummy)
    

    def _pre_action_get_xml_root(self, doc):
        """
        Pre action to get the xml data from the root family.
        
        - need to use the family file on disc to get the xml data...which I can get through the ini...

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        """

        return_value = res.Result()
        try:
            # note to self:
            # this will add an xml family_type_data_storage_manager of the root family to the data property of the processor
            # will need to return a result object confirming success or failure
            family_name = get_file_name_without_ext(self.family_file_path)
            family_category = doc.OwnerFamily.FamilyCategory.Name

            # get the type data from the family file
            type_data_result = get_type_data_via_XML_from_family_file(
                self.revit_application,
                family_name, 
                self.family_file_path, 
                True
            )

            # check if type data was retrieved successfully
            if type_data_result.status and len(type_data_result.result) > 0:
                # in the moment data contains a list of storage objects rather than a single storage manager object
                storage_manager = type_data_result.result[0]

                # data needs to be of type FamilyTypeData...
                dummy = rFamData.FamilyTypeData(family_name, family_category)
                # add the parameter storage to the dummy object
                for type_storage in storage_manager.family_type_data_storage:
                    # we actually want the nested parameter storage here to get a single entry per
                    # family, family type and parameter
                    for  parameter_storage in type_storage.parameters:
                        dummy.add_data(parameter_storage)
                    
                # add the dummy object to the data property of the processor
                self.data.append(dummy)

                return_value.update_sep(True, "Pre Action Get XML Root successful.")
            else:
                return_value.update_sep(False, type_data_result.message)

        except Exception as e:
            return_value.update_sep(
                False,
                "Post Action Update shared parameters data failed with exception: {}".format(
                    e
                ),
            )
        return return_value
