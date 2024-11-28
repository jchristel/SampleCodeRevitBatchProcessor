"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module with helper function around family types catalogue files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Revit.Family.family_types_get_data import get_type_data_via_XML_from_family_file

def export_catalogue_file(doc, file_path = None):
    """
    Export the family types catalogue file.

    :param doc: The family document to extract the type data from.
    :type doc: rdb.Family
    :param file_path: The path to save the catalogue file. If None, the file will be saved in the same location as the family with the same name as the family.
    :type file_path: str
    """

    # check if a family document...


    # get the family name
    family_name = doc.Name

    # remove the file extension
    if family_name.lower().endswith(".rfa"):
        family_name = family_name[:-4]

    # get the family path
    family_path = doc.PathName

    # get the root path (same as the family path)
    root_path = doc.Name

    # get the root category path (same as the family category)
    root_category_path = doc.FamilyCategory.Name

    # get the family type data
    family_type_data = get_type_data_via_XML_from_family_file(doc, family_name, family_path, root_path, root_category_path)

    # convert type data into catalogue file

    