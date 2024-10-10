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

# from duHast.Utilities import Utility as util
from duHast.Revit.Warnings import warnings as rWarn
from duHast.Revit.Warnings.Data.Objects.warnings_data_storage import (
    FamilyWarningsDataStorage,
)

# import Autodesk
# import Autodesk.Revit.DB as rdb

# WARNING_TEXT = "warningText"
# WARNING_GUID = "warningGUID"
# WARNING_RELATED_IDS = "warningRelatedIds"
# WARNING_OTHER_IDS = "warningOtherIds"


class WarningsData(IFamData.IFamilyData):
    def __init__(self, root_path=None, root_category_path=None):
        """
        Constructor for warnings data class.

        :param root_path: root path for data
        :type root_path: str
        :param root_category_path: root category path for data
        :type root_category_path: str
        """

        super(WarningsData, self).__init__(
            root_path=root_path,
            root_category_path=root_category_path,
        )

    def process(self, doc):

        # make sure to get a value for the file path which is not empty if the document has not been saved
        saved_file_name = "-"
        if doc.PathName != "":
            saved_file_name = doc.PathName

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
            storage = FamilyWarningsDataStorage(
                root_name_path=self.root_path,
                root_category_path=self.root_category_path,
                family_name=self._strip_file_extension(doc.Title),
                family_file_path=saved_file_name,
                warning_text=war_text,
                warning_guid=war_guid,
                warning_related_ids=war_element_ids_as_integer,
                warning_other_ids=war_other_element_ids_as_integer,
            )
            self.add_data(storage_instance=storage)

        # check if any shared parameter was found
        if len(self.data) == 0:
            # add message no warnings found
            # build data
            storage = FamilyWarningsDataStorage(
                root_name_path=self.root_path,
                root_category_path=self.root_category_path,
                family_name=self._strip_file_extension(doc.Title),
                family_file_path=saved_file_name,
                warning_text="No warnings present in family.",
                warning_guid="",
                warning_related_ids=[],
                warning_other_ids=[],
            )
            self.add_data(storage_instance=storage)

    def get_data(self):
        return self.data

    def add_data(self, storage_instance):
        if isinstance(storage_instance, FamilyWarningsDataStorage):
            self.data.append(storage_instance)
        else:
            raise ValueError(
                "storage instance must be an instance of FamilyWarningsDataStorage"
            )
