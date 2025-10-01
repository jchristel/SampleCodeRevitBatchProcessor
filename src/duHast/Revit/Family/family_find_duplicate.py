"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families helper functions retrieving duplicated families.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A duplicated family is a family which has the name of another family with an appended (1) or (2) etc.
Revit seems to do this when loading families with the same name into a project and the family loaded in has the same name as one already in the project but is slightly different. (May hav to do with versioning of families but not sure yet).


Samples:
NRS_Button_NurseCall_Emergency_ITCL-004
NRS_Button_NurseCall_Emergency_ITCL1

Last characters of a family are removed if they represent a none alphabetical character and are replaced with a 1 or 2 etc to indicate a duplicate family.

LevelHead
LevelHead1

If there are no numbers at the end of the family name then a 1 or 2 etc is appended to indicate a duplicate family.

To identify a duplicated family:
1. check if the last character is a number
2. if so, check if the character before is an alphabetical character, if not ignore ( assume we dont have more than 9 duplicates in a file... )
3. if so, remove the number and check if the remaining string is a match with another family name in the project.
    A match is defined as either
        - the remaining string being the same as another family name of the same Revit category or 
        - the remaining string being the same as another family, of the same Revit category, followed by none alphabetical characters ( make sure its not the same family )




A second part of this module is to find matching types for two given families by their type names. This is useful when replacing a family with another one and wanting to keep the same type (i.e. duplicate families).

When creating duplicate families in a project Revit either keeps the type name the same or appends a " 1" or " 2" etc to the type name.

A match therefore is defined as either:
- the type name being the same as another type name in the other family
- the type name being the same as another type name in the other family followed by 2 none none alphabetical characters (first character is a space, second character is a number)


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


from duHast.Revit.Family.family_functions import get_category_name_to_family_dict
from Autodesk.Revit.DB import Element

def get_duplicate_family_root_name (family_name):
    """
    Returns the root name of a duplicate family or None if not a duplicate family.

    :param family_name: Name of the family to check.
    :type family_name: str

    :return: Root name of duplicate family or None if not a duplicate family.
    :rtype: str | None
    """

    # return none if this is not a duplicate family ( ie. does not end with a number )
    duplicate_root_name = None

    # check if last character is a number
    if family_name[-1].isnumeric() == False:
        return duplicate_root_name

    # check if the character before is an alphabetical character, if not ignore ( assume we dont have more than 9 duplicates in a file... )
    if family_name[-2].isalpha() == False:
        return duplicate_root_name
    
    # remove the number
    duplicate_root_name = family_name[:-1]
    return duplicate_root_name


def find_original_family_based_on_duplicate_family (original_families_by_category,  original_family_name, duplicate_family_root_name, duplicate_family_category_name):
    """
    Finds the original family based on the duplicate family root name.

    :param original_families_by_category: Dictionary of original families by category.
    :type original_families_by_category: dict[str, list[Autodesk.Revit.DB.Family]]

    :param duplicate_family_root_name: Root name of the duplicate family.
    :type duplicate_family_root_name: str

    :return: The original family or None if not found.
    :rtype: Autodesk.Revit.DB.Family | None
    """

    # check if the remaining string is a match with another family name in the project.
    # A match is defined as either
    # - the remaining string being the same as another family name of the same Revit category or 
    # - the remaining string being the same as another family, of the same Revit category, followed by none alphabetical characters ( make sure its not the same family )

    for family in original_families_by_category[duplicate_family_category_name]:
        if family.Name == duplicate_family_root_name:
            return family
        else:
            # check if the family name starts with the duplicate root name and is followed by none alphabetical characters
            if family.Name.startswith(duplicate_family_root_name) and original_family_name != family.Name:
                # check if the character after the root name is a none alphabetical character
                if len(family.Name) > len(duplicate_family_root_name):
                    if family.Name[len(duplicate_family_root_name)].isalpha() == False:
                        return family
    return None


def find_duplicate_families (doc):
    """
    Find duplicate families in the document.

    :param doc: Revit document
    :type doc: Autodesk.Revit.DB.Document
    :return: Dictionary of original family id and list of duplicate families.
    :rtype: dict[int, list[Autodesk.Revit.DB.Family]]
    """

    # dictionary in format source family_id: [duplicated family]
    duplicate_families = {}
    
    # get all families in the document
    all_families = get_category_name_to_family_dict(doc)
   
    for category_name, families in all_families.items():
        if len(families) > 1:
            # we have multiple families in this category, check for duplicates
            for family in families:
                duplicate_root_name = get_duplicate_family_root_name(family.Name)
                if duplicate_root_name:
                    # we have a duplicate family, find the original family
                    original_family = find_original_family_based_on_duplicate_family(all_families, family.Name, duplicate_root_name, category_name)
                    if original_family:
                        #print("Duplicate family found: {} (original: {})".format(family.Name, original_family.Name))
                        if original_family.Id not in duplicate_families:
                            duplicate_families[original_family.Id] = []
                        duplicate_families[original_family.Id].append(family)
                    else:
                        #print("Duplicate family found: {} (original not found)".format(family.Name))
                        pass
    
    return duplicate_families


def find_matching_types_between_families (source_family, target_family):
    """
    Finds matching types between two families based on type names.

    :param source_family: Source family to find matching types for.
    :type source_family: Autodesk.Revit.DB.Family

    :param target_family: Target family to find matching types in.
    :type target_family: Autodesk.Revit.DB.Family

    :return: Dictionary of source type id and target type id. If no match is found the source type id is not included in the dictionary.
    :rtype: dict[int, int]
    """

    matching_types = {}

    # get all types in the source family
    source_types = list(source_family.GetFamilySymbolIds())
    target_types = list(target_family.GetFamilySymbolIds())

    # compare type names
    for source_type_id in source_types:
        source_type = source_family.Document.GetElement(source_type_id)
        source_type_name = Element.Name.GetValue(source_type)
        for target_type_id in target_types:
            target_type = target_family.Document.GetElement(target_type_id)
            target_type_name = Element.Name.GetValue(target_type)
            if source_type_name == target_type_name:
                matching_types[source_type.Id.IntegerValue] = target_type.Id.IntegerValue
            else:
                # check if the type name starts with the source type name and is followed by " " and a number
                if target_type_name.startswith(source_type_name):
                    if len(target_type_name) > len(source_type_name) + 2:
                        if target_type_name[len(source_type_name)] == " " and target_type_name[len(source_type_name)+1].isnumeric():
                            matching_types[source_type.Id.IntegerValue] = target_type.Id.IntegerValue

    return matching_types