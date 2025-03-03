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
from duHast.Revit.Family.Data.Objects.family_type_parameter_data_storage import FamilyTypeParameterDataStorage
from duHast.Revit.Family.Data.Objects.family_type_data_processor_defaults import (
    NESTING_SEPARATOR,
)

from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict
from duHast.Revit.Family.family_types_model_get_data_from_xml import get_type_data_via_XML_from_family_object
# import Autodesk
from  Autodesk.Revit.DB import Element

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

        # get all nested families and export to xml
        families = get_name_and_category_to_family_dict(doc)
        
        for family_name, family in families.items():
            
            
            fam_name = self.root_path
            
            
            # get the type data and make sure to pass in root category path and root name path
            try:
                # add the family processed to the path
                fam_name = Element.Name.GetValue(family)
                # strip .rfa of name
                if fam_name.lower().endswith(".rfa"):
                    fam_name = family_name[:-4]
                fam_root_path = "{}{}{}".format(self.root_path,NESTING_SEPARATOR ,fam_name)
            except Exception as e:
                #print("Failed to get family name: {}".format(e))
                fam_root_path = "{}{}{}".format(self.root_path, NESTING_SEPARATOR, e)

            fam_cat_name = self.root_category_path


            try:
                # get the category of the family to be processed
                fam_cat_name = family.FamilyCategory.Name
                fam_root_category_path = "{}{}{}".format(self.root_category_path , NESTING_SEPARATOR , fam_cat_name)
            except Exception as e:
                #print("Failed to get family category: {}".format(e))
                fam_root_category_path = "{}{}{}".format(self.root_category_path, NESTING_SEPARATOR, e)

            type_data_result = get_type_data_via_XML_from_family_object(family, fam_root_path, fam_root_category_path)
            if type_data_result.status and len(type_data_result.result) > 0:
                
                # in the moment data contains a list of storage objects rather than a single storage manager object
                storage_manager = type_data_result.result[0]
                for type_storage in storage_manager.family_type_data_storage:
                    # we actually want the nested parameter storage here to get a single entry per
                    # family, family type and parameter
                    for  parameter_storage in type_storage.parameters:
                        self.add_data(parameter_storage)
                    
                
    def get_data(self):
        return self.data

    def add_data(self, storage_instance):
        if isinstance(storage_instance, FamilyTypeParameterDataStorage):
            self.data.append(storage_instance)
        else:
            raise ValueError(
                "storage instance must be an instance of FamilyTypeParameterDataStorage got {}".format(type(storage_instance))
            )
