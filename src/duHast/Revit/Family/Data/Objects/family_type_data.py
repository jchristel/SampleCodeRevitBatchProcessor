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

import clr
clr.AddReference("System.Xml")
from System.Xml import XmlDocument, XmlNamespaceManager

# import Autodesk
# import Autodesk.Revit.DB as rdb

# data dictionary key values specific to this class
CATEGORY_NAME = "categoryName"


# TODO: replace the below classes with data classes
class Parameter(Base):
    def __init__(self, name, type, typeOfParameter, units, value):

        super(Parameter, self).__init__()
        self.name = name
        self.type = type
        self.typeOfParameter = typeOfParameter
        self.units = units
        self.value = value

class FamilyType(Base):
    def __init__(self, title):
        super(FamilyType, self).__init__()
        self.title = title
        self.parameters = []

    def add_parameter(self, parameter):
        self.parameters.append(parameter)

class Family(Base):
    def __init__(self, name, number_of_types):
        super(Family, self).__init__()
        self.name = name
        self.family_type_count = number_of_types
        self.family_types = []

    def add_family_type(self, part):
        self.family_types.append(part)





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

    def _get_type_data_via_XML(self, doc):
        path = doc.PathName

        # check for valid path
        if( len(path) == 0 ):
            path = r"C:\Users\chrjx\Documents\github\debug_modules\reload\CSW_Benchtop_Linear_SquareEdge"
        else:
            path_directory = get_directory_path_from_file_path(path)
            file_name = get_file_name_without_ext(doc.PathName)
            path_xml = path_directory + "\\" + file_name + ".xml"
        
        # save xml file
        doc.Application.ExtractPartAtomFromFamilyFile( path, path_xml )

        # load xml file back in
        with open(path_xml, 'r') as file:
            xml_content = file.read()
            # print(xml_content)  # Print the content to verify it was written correctly

        # load the xml content
        doc_xml = XmlDocument()
        doc_xml.LoadXml(xml_content)

        # add an xml name space amanger
        nsmgr = XmlNamespaceManager(doc_xml.NameTable)
        nsmgr.AddNamespace("atom", "http://www.w3.org/2005/Atom")
        nsmgr.AddNamespace("A", "urn:schemas-autodesk-com:partatom")

        # select the family node
        family_node = doc_xml.SelectSingleNode("//A:family", nsmgr)

        # set up a family object
        family = Family(family_node.Attributes['type'].Value, int(family_node.SelectSingleNode('A:variationCount', nsmgr).InnerText))
        
        # get the family parameters
        for part_node in family_node.SelectNodes('A:part', nsmgr):
            
            # get the family type name
            family_type = None
            for child_node in part_node.ChildNodes:
                if child_node.Name == 'title':
                    family_type = FamilyType(child_node.InnerText)
                    break
            
            # if we got a type name, add the parameters, their values and units, parameter type and type of parameter
            if(family_type):
                for child_node in part_node.ChildNodes:
                    if child_node.Name != 'title':
                        print("not title: ...child node: {} name:{} has child nodes: {} value:{}".format(child_node, child_node.Name, child_node.HasChildNodes, child_node.InnerText))
                        parameter = Parameter(
                            name=child_node.Name,
                            type=child_node.Attributes['type'].Value,
                            typeOfParameter=child_node.Attributes['typeOfParameter'].Value,
                            units=child_node.Attributes['units'].Value,
                            value=child_node.InnerText,
                        )

                        # add type to family
                        family_type.add_parameter(parameter)
                
                # add type to family
                family.add_family_type(family_type)

    
    def process(self, doc, session_id):
        """
        Collects all base data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        """

        # make sure to get a value for the file path which is not empty if the document has not been saved
        saved_file_name = "-"
        if doc.PathName != "":
            saved_file_name = doc.PathName


        # save out xml and read family type data back in


        # build data
        storage = FamilyTypeDataStorage(
            root_name_path=self.root_path,
            root_category_path=self.root_category_path,
            family_name=self._strip_file_extension(doc.Title),
            family_file_path=saved_file_name,
        )

        self.add_data(storage_instance=storage)

    def get_data(self):
        return self.data

    def add_data(self, storage_instance):
        if isinstance(storage_instance, FamilyTypeDataStorage):
            self.data.append(storage_instance)
        else:
            raise ValueError(
                "storage instance must be an instance of FamilyTypeDataStorage"
            )
