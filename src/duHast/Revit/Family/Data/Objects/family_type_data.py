"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family type data class.
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
from duHast.Revit.Family.Data.Objects.family_type_data_storage import (
    FamilyTypeDataStorage,
)
from duHast.Revit.Family.Data.Objects.family_type_data_processor_defaults import (
    NESTING_SEPARATOR,
)

from duHast.Revit.Family.Data.Objects.family_type_data_storage import (
    FamilyTypeDataStorage,
)

# import Autodesk
# import Autodesk.Revit.DB as rdb

# data dictionary key values specific to this class
CATEGORY_NAME = "categoryName"


class FamilyTypeData(IFamData.IFamilyData):
    def __init__(self, root_path=None, root_category_path=None):
        """
        Class constructor

        :param rootPath: The path of the nested family in a tree: rootFamilyName :: nestedFamilyNameOne :: nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param rootCategoryPath: The path of the family category in a tree: rootCategoryName :: nestedCategoryNameOne :: nestedCategoryTwo\
            This includes the actual category name as the last node.
        :type rootCategoryPath: str
        """

        # store data type  in base class
        super(FamilyTypeData, self).__init__(
            root_path=root_path,
            root_category_path=root_category_path,
        )
        # super(CategoryData, self).__init__(rootPath, dataType)

        if root_category_path != None:
            category_chunks = root_category_path.split(NESTING_SEPARATOR)
            self.category = category_chunks[-1]
        else:
            self.category = "unknown"

        self.saved_file_name = ""

    def process(self, doc, session_id):
        """
        Collects all base data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        """

        # make sure to get a value for the file path which is not empty if the document has not been saved
        if doc.PathName != "":
            self.saved_file_name = doc.PathName

        # TODO: xml out may be tricky to implement, there only exist 2 functions:
        #   1. gxml from family file ( gets data from a family file on disc)
        #   2. xml from family class instance
        # Need to implement a version whicj just works with the open family document
            

        # save out xml and read family type data back in
        # types_data = get_type_data_via_XML_from_family_file(
        #     doc=doc,
        #     family_name=doc.Title,
        #     family_path=self.saved_file_name,
        #     root_path=self.root_path,
        #     root_category_path=self.root_category_path,
        # )

        # # add type data to data
        # for type_data in types_data:
        #     self.add_data(type_data)

    def get_data(self):
        return self.data

    def add_data(self, storage_instance):
        if isinstance(storage_instance, FamilyTypeDataStorage):
            self.data.append(storage_instance)
        else:
            raise ValueError(
                "storage instance must be an instance of FamilyTypeDataStorage"
            )
