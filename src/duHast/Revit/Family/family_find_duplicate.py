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