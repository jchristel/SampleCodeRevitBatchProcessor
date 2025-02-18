"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module with helper function around family types data extraction using Revit xml export functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Supports 2 methods of data extraction:

- from family file on disk
- from family element instance in document

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


import tempfile
import os

from Autodesk.Revit.DB import Element

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Utility.xml_family_type_reader import read_xml_into_storage
from duHast.Revit.Family.family_functions import get_symbol_names_of_family
from duHast.Revit.Family.Utility.xml_create_atom_exports import write_data_to_temp_xml_file_and_read_it_back


def get_type_data_via_XML_from_family_object(revit_family, family_name_nesting_path = None, root_category_path = None):
    """
    Get the family type data from the family element in a REvit document using the XML extraction method.

    :param revit_family: The Revit family object.
    :type revit_family: Autodesk.Revit.DB.Family
    :param family_name_nesting_path: The nesting path of the family in a tree: rootFamilyName :: nestedFamilyNameOne :: nestedFamilyTwo\
        This includes the actual family name as the last node.
    :type family_name_nesting_path: str
    :param root_category_path: The path of the family category in a tree: rootCategoryName :: nestedCategoryNameOne :: nestedCategoryTwo\
        This includes the actual category name as the last node.

    :return: A result object with .result containing a single FamilyTypeDataStorage object. (or empty if failed)
    :rtype: Result
    """

    return_value = Result()
    try:
        # set up action to write xml data
        def action(temp_path_xml):
            action_return_value = Result()
            try:
                # Save XML file to temporary location
                revit_family.ExtractPartAtom(temp_path_xml)
                action_return_value.update_sep(True, "Wrote data to XML file")
            except Exception as e:
                action_return_value.update_sep(
                    False, "Failed to write XML data: {}".format(e)
                )
            return action_return_value

        # Write the data to an XML file and read it back
        doc_xml_result = write_data_to_temp_xml_file_and_read_it_back(action)
        return_value.update(doc_xml_result)

        # check if an xml document was created
        if doc_xml_result.status is False:
            return return_value

        # set the family name and root category path
        fam_name = Element.Name.GetValue(revit_family) if family_name_nesting_path is None else family_name_nesting_path
        root_category_path = "None" if root_category_path is None else root_category_path

        # read the xml data into the storage object
        type_data = read_xml_into_storage(
            doc_xml_result.result,
            family_name=fam_name,
            family_path="",
            root_category_path=root_category_path,
        )

        # it looks like the part atom extraction does sometime include types which are no longer present
        # in the family document (ghost types) so we need to check if we have any types
        # since family inherits from Element, I should be able to get the document from the family object
        # and check if the types are still present in the document
        symbol_names = get_symbol_names_of_family(revit_family)
        type_data.remove_ghost_types(symbol_names)
    
        # store list in return object ( clear any previous results )
        return_value.result = [type_data]
    except Exception as e:
        return_value.update_sep(False, "{}".format(e))

    return return_value
