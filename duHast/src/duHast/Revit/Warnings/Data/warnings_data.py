"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family warnings data class.
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

# from duHast.Utilities import Utility as util
from duHast.Revit.Warnings import warnings as rWarn

# import Autodesk
# import Autodesk.Revit.DB as rdb

WARNING_TEXT = "warningText"
WARNING_GUID = "warningGUID"
WARNING_RELATED_IDS = "warningRelatedIds"
WARNING_OTHER_IDS = "warningOtherIds"


class WarningsData(IFamData.IFamilyData):
    def __init__(self, root_path=None, root_category_path=None, data_type=None):

        super(WarningsData, self).__init__(
            root_path=root_path,
            root_category_path=root_category_path,
            data_type=data_type,
        )

    def process(self, doc):
        # get all warnings in document
        warnings = rWarn.get_warnings(doc)
        # loop over warnings and extract data
        for warning in warnings:
            # check for a guid
            war_guid = ""
            try:
                war_guid = warning.GetFailureDefinitionId().Guid
            except Exception as e:
                pass
            # warning text
            war_text = ""
            try:
                war_text = warning.GetDescriptionText()
            except Exception as e:
                pass
            # affected element ids
            war_element_ids_as_integer = []
            try:
                for el in warning.GetFailingElements():
                    war_element_ids_as_integer.append(el.IntegerValue)
            except Exception as e:
                pass
            # other element ids
            war_other_element_ids_as_integer = []
            try:
                for el in warning.GetAdditionalElements():
                    war_other_element_ids_as_integer.append(el.IntegerValue)
            except Exception as e:
                pass

            # build data
            self.data.append(
                {
                    IFamData.ROOT: self.rootPath,
                    IFamData.ROOT_CATEGORY: self.rootCategoryPath,
                    IFamData.FAMILY_NAME: doc.Title,
                    IFamData.FAMILY_FILE_PATH: doc.PathName,
                    WARNING_TEXT: war_text,
                    WARNING_GUID: war_guid,
                    WARNING_RELATED_IDS: war_element_ids_as_integer,
                    WARNING_OTHER_IDS: war_other_element_ids_as_integer,
                }
            )

        # check if any shared parameter was found
        if len(self.data) == 0:
            # add message no warnings found
            # build data
            self.data.append(
                {
                    IFamData.ROOT: self.rootPath,
                    IFamData.ROOT_CATEGORY: self.rootCategoryPath,
                    IFamData.FAMILY_NAME: doc.Title,
                    IFamData.FAMILY_FILE_PATH: doc.PathName,
                    WARNING_TEXT: "No warnings present in family.",
                    WARNING_GUID: "",
                    WARNING_RELATED_IDS: [],
                    WARNING_OTHER_IDS: [],
                }
            )

    def get_data(self):
        return self.data
