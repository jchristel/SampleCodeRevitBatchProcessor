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

from duHast.Revit.Family.Data.Objects import ifamily_data as IFamData
from duHast.Utilities import utility as util
from duHast.Revit.SharedParameters import shared_parameters as rSharedPara
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_storage import (
    FamilySharedParameterDataStorage,
)

# import Autodesk
from Autodesk.Revit.DB import Element


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

    def process(self, doc):
        collector = rSharedPara.get_all_shared_parameters(doc)
        for para in collector:
            # just in case parameter name is not unicode
            parameter_name = "unknown"
            try:
                parameter_name = util.encode_ascii(Element.Name.GetValue(para))
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
            storage = FamilySharedParameterDataStorage(
                data_type=self.data_type,
                root_name_path=self.root_path,
                root_category_path=self.root_category_path,
                family_name=self._strip_file_extension(doc.Title),
                family_file_path=doc.PathName,
                parameter_guid=para.GuidValue.ToString(),
                parameter_name=parameter_name,
                parameter_id=para.Id.IntegerValue,
                use_counter=use_counter,
                used_by=[used_by_data],
            )
            self.add_data(storage_instance=storage)

        # check if any shared parameter was found
        if len(self.data) == 0:
            # add message no shared parameter found
            storage = FamilySharedParameterDataStorage(
                data_type=self.data_type,
                root_name_path=self.root_path,
                root_category_path=self.root_category_path,
                family_name=self._strip_file_extension(doc.Title),
                family_file_path=doc.PathName,
                parameter_guid="",
                parameter_name="No shared parameter present in family.",
                parameter_id=-1,
                use_counter=0,
                used_by=[],
            )
            self.add_data(storage_instance=storage)

    def get_data(self):
        return self.data

    def add_data(self, storage_instance):
        if isinstance(storage_instance, FamilySharedParameterDataStorage):
            self.data.append(storage_instance)
        else:
            raise ValueError(
                "storage instance must be an instance of FamilySharedParameterDataStorage"
            )
