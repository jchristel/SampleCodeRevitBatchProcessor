"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family base data processor class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

from duHast.Revit.Family.Data.ifamily_processor import IFamilyProcessor
from duHast.Revit.Family.Data import family_base_data as rFamData
from duHast.Revit.Family.Data import ifamily_data as IFamData
from duHast.Utilities import util_batch_p as uBP


class FamilyBaseProcessor(IFamilyProcessor):
    def __init__(
        self,
        reference_file_path=None,
        family_out_directory_path=None,
        session_id=None,
        pre_actions=None,
        post_actions=None,
    ):
        """
        Class constructor.
        """

        # store data type  in base class
        string_report_headers = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            rFamData.CATEGORY_NAME,
        ]

        # store data type  in base class
        super(FamilyBaseProcessor, self).__init__(
            data_type="FamilyBase",
            pre_actions=pre_actions,
            post_actions=post_actions,
            string_report_headers=string_report_headers,
        )

        # self.data = []
        # self.dataType = 'FamilyBase'
        self.reference_file_path = reference_file_path
        self.family_out_directory_path = family_out_directory_path
        if session_id != None:
            self.session_id = uBP.adjust_session_id_for_directory_name(session_id)
        else:
            self.session_id = session_id

        # self.preActions = preActions
        # self.postActions = postActions

    def process(self, doc, root_path, root_category_path):
        """
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param rootCategoryPath: The path of the nested family in in terms of category in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategoryPath: str
        """

        dummy = rFamData.FamilyBaseData(root_path, root_category_path, self.data_type)
        dummy.process(
            doc,
            self.reference_file_path,
            self.family_out_directory_path,
            self.session_id,
        )
        self.data.append(dummy)
