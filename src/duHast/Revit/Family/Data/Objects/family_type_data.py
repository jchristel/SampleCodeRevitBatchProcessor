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


import tempfile
import os

from duHast.Revit.Family.Data.Objects import ifamily_data as IFamData
from duHast.Revit.Family.Data.Objects.family_type_data_storage import (
    FamilyTypeDataStorage,
)
from duHast.Revit.Family.Data.Objects.family_type_data_processor_defaults import (
    NESTING_SEPARATOR,
)

from duHast.Revit.Family.Data.Objects.family_type_parameter_data_storage import FamilyTypeParameterDataStorage
from duHast.Revit.Family.Data.Objects.family_type_data_storage import FamilyTypeDataStorage

from duHast.Utilities.files_io import get_directory_path_from_file_path, get_file_name_without_ext

import clr
clr.AddReference("System.Xml")
from System.Xml import XmlDocument, XmlNamespaceManager

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

    def update_function(self, doc):

        # Set up list of type information to be returned
        type_data = []

        # this path is potentially empty if the document has not been saved...
        # not sure how revit wil react to that just yet
        path = self.saved_file_name
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_file:
            temp_path_xml = temp_file.name

        try:
            # Save XML file to temporary location
            doc.Application.ExtractPartAtomFromFamilyFile(path, temp_path_xml)

            # Load XML file back in
            with open(temp_path_xml, 'r') as file:
                xml_content = file.read()

            # Load the XML content
            doc_xml = XmlDocument()
            doc_xml.LoadXml(xml_content)

            # Add an XML namespace manager
            nsmgr = XmlNamespaceManager(doc_xml.NameTable)
            nsmgr.AddNamespace("atom", "http://www.w3.org/2005/Atom")
            nsmgr.AddNamespace("A", "urn:schemas-autodesk-com:partatom")

            # Select the family node
            family_node = doc_xml.SelectSingleNode("//A:family", nsmgr)

            # Get the family parameters
            for part_node in family_node.SelectNodes('A:part', nsmgr):
                # Get the family type name
                family_type_name = None
                for child_node in part_node.ChildNodes:
                    if child_node.Name == 'title':
                        family_type_name = child_node.InnerText
                        break

                # If we got a type name, add the parameters, their values and units, parameter type and type of parameter
                if family_type_name:
                    parameters = []
                    for child_node in part_node.ChildNodes:
                        if child_node.Name != 'title':
                            parameter = FamilyTypeParameterDataStorage(
                                name=child_node.Name,
                                type=child_node.Attributes['type'].Value,
                                type_of_Parameter=child_node.Attributes['typeOfParameter'].Value,
                                units=child_node.Attributes['units'].Value,
                                value=child_node.InnerText,
                            )
                            # Add type to family
                            parameters.append(parameter)

                    # Set up a family type data storage object
                    fam_type = FamilyTypeDataStorage(
                        root_name_path=self.root_path,
                        root_category_path=self.root_category_path,
                        family_name=self._strip_file_extension(doc.Title),
                        family_file_path=self.saved_file_name,
                        family_type_name=family_type_name,
                        parameters=parameters,
                    )

                    # Add the family type to the list of types
                    type_data.append(fam_type)

        finally:
            # Delete the temporary file
            if os.path.exists(temp_path_xml):
                os.remove(temp_path_xml)
        
        return type_data

    
    def process(self, doc, session_id):
        """
        Collects all base data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        """

        # make sure to get a value for the file path which is not empty if the document has not been saved
        if doc.PathName != "":
            self.saved_file_name = doc.PathName


        # save out xml and read family type data back in
        types_data = self._get_type_data_via_XML(self, doc)

        # add type data to data
        for type_data in types_data:
            self.add_data(type_data)

    def get_data(self):
        return self.data

    def add_data(self, storage_instance):
        if isinstance(storage_instance, FamilyTypeDataStorage):
            self.data.append(storage_instance)
        else:
            raise ValueError(
                "storage instance must be an instance of FamilyTypeDataStorage"
            )
