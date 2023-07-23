"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family shared parameter data class.
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

from duHast.Revit.Family.Data import ifamily_data as IFamData
from duHast.Utilities import utility as util
from duHast.Revit.SharedParameters import shared_parameters as rSharedPara

# import Autodesk
import Autodesk.Revit.DB as rdb


PARAMETER_GUID = "parameterGUID"
PARAMETER_NAME = "parameterName"
PARAMETER_ID = "parameterId"


class SharedParameterData(IFamData.IFamilyData):
    def __init__(self, root_path=None, root_category_path=None, data_type=None):

        super(SharedParameterData, self).__init__(
            root_path=root_path,
            root_category_path=root_category_path,
            data_type=data_type,
        )
        # super(CategoryData, self).__init__(rootPath, dataType)

        """
        self.data = []
        
        if(dataType != None):
            self.dataType = dataType
        else:
            self.dataType = 'not declared'
        
        if(rootPath != None):
            self.rootPath = rootPath
        else:
            self.rootPath = '-'

        if(rootCategoryPath != None):
            self.rootCategoryPath = rootCategoryPath
        else:
            self.rootCategoryPath = '-'
        """

    def process(self, doc):
        collector = rSharedPara.get_all_shared_parameters(doc)
        for para in collector:
            # just in case parameter name is not unicode
            parameter_name = "unknown"
            try:
                parameter_name = util.encode_ascii(rdb.Element.Name.GetValue(para))
            except Exception as ex:
                parameter_name = "Exception: " + str(ex)
            # check if used:
            use_counter = 0
            used_by_data = {}
            if rSharedPara.is_shared_parameter_definition_used(doc, para):
                use_counter = 1
                # build used by data as required to be the same as post process update
                used_by_data = {
                    PARAMETER_GUID: para.GuidValue.ToString(),
                    PARAMETER_NAME: parameter_name,
                    IFamData.ROOT: self.root_path,
                }

            # build data
            self.data.append(
                {
                    IFamData.ROOT: self.root_path,
                    IFamData.ROOT_CATEGORY: self.root_category_path,
                    IFamData.FAMILY_NAME: self._strip_file_extension(doc.Title),
                    IFamData.FAMILY_FILE_PATH: doc.PathName,
                    PARAMETER_GUID: para.GuidValue.ToString(),
                    PARAMETER_NAME: parameter_name,
                    PARAMETER_ID: para.Id.IntegerValue,
                    IFamData.USAGE_COUNTER: use_counter,
                    IFamData.USED_BY: [used_by_data],
                }
            )

        # check if any shared parameter was found
        if len(self.data) == 0:
            # add message no shared parameter found
            self.data.append(
                {
                    IFamData.ROOT: self.root_path,
                    IFamData.ROOT_CATEGORY: self.root_category_path,
                    IFamData.FAMILY_NAME: self._strip_file_extension(doc.Title),
                    IFamData.FAMILY_FILE_PATH: doc.PathName,
                    PARAMETER_GUID: "",
                    PARAMETER_NAME: "No shared parameter present in family.",
                    PARAMETER_ID: -1,
                    IFamData.USAGE_COUNTER: 0,
                    IFamData.USED_BY: [],
                }
            )

    def get_data(self):
        return self.data
