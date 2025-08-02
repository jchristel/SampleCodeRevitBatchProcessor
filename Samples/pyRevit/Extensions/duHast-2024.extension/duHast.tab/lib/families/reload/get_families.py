# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

import clr

clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)
from System.Collections.Generic import List

# import Autodesk
from Autodesk.Revit.DB import BuiltInCategory

from duHast.Revit.Family.family_functions import get_name_to_family_dict
from duHast.Revit.Family.family_utils import is_shared_from_family

from duHast.pyRevit.net_dll_loader import load_net_dll_path



from Models.RevitFamily import RevitFamily

from duHast.Revit.Categories.categories_model import get_category_from_builtInCategory

from Objects.match_status_names import MatchStatusNames
from Models.RevitFamilyId import FamilyID


def get_families_in_model(doc, library_path=None):
    """
    Get all families in a model and discard any family that occurs more than once

    :param doc: the revit document
    :type doc: Autodesk.Revit.DB.Document
    :param library_path: the directory to search for families
    :type library_path: str

    :return: a list of unique RevitFamily objects
    :rtype: [:class:`.RevitFamily`]
    """

    family_data = []
    families = get_name_to_family_dict(doc)

    cat_mullion = get_category_from_builtInCategory(
        doc, BuiltInCategory.OST_CurtainWallMullions
    )
    # print("mullion_cat",cat_mullion, cat_mullion.Name)

    for revit_family_name, revit_family in families.items():
        # check if in place or mullion
        if (
            revit_family.IsInPlace == False
            and revit_family.FamilyCategory.Name != cat_mullion.Name
        ):

            # build new data entry
            family_container = RevitFamily(
                id=FamilyID(revit_family.Id.IntegerValue),
                family_name=revit_family_name,
                family_category=revit_family.FamilyCategory.Name,
                is_shared=is_shared_from_family(revit_family),
                match_status=MatchStatusNames.MATCH_OK.value,
            )

            family_data.append(family_container)

    return family_data


def get_families_in_model_net(doc):
    """
    Get all families in a model and discard any family that occurs more than once

    :param doc: the revit document
    :type doc: Autodesk.Revit.DB.Document
    :param library_path: the directory to search for families
    :type library_path: str

    :return: a list of unique RevitFamily objects
    :rtype: [:class:`.RevitFamily`]
    """

    # import RevitFamily class namespace
    from duHastNet.UI.FamilyReloaderUI.Models import RevitFamily as RevitFamilyNet
    
    # build a list of RevitFamily objects
    family_data = List[RevitFamilyNet]()
    
    # get all families in file
    families = get_name_to_family_dict(doc)

    # exclude mullions
    cat_mullion = get_category_from_builtInCategory(
        doc, BuiltInCategory.OST_CurtainWallMullions
    )
    # print("mullion_cat",cat_mullion, cat_mullion.Name)

    for revit_family_name, revit_family in families.items():
        # check if in place or mullion
        if (
            revit_family.IsInPlace == False
            and revit_family.FamilyCategory.Name != cat_mullion.Name
        ):
            #string familyName, string familyCategory,  bool isShared, int revitElementId
            # build new data entry
            family_container = RevitFamilyNet(
                revitElementId=FamilyID(revit_family.Id.IntegerValue),
                familyName=revit_family_name,
                familyCategory=revit_family.FamilyCategory.Name,
                isShared=is_shared_from_family(revit_family),
            )

            family_data.append(family_container)

    return family_data
