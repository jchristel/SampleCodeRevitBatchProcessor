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

from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)

from Autodesk.Revit.DB import (
    Element,
    FamilySymbol,
    FilteredElementCollector,
)

FAM_NAME_TYPE_NAME_CATEGORY_SEPARATOR = " {} ".format(NESTING_SEPARATOR)

def family_types_getter_target(doc, category_name_filter):
    try:
        # get all family types of families not in place
        col = FilteredElementCollector(doc).OfClass(FamilySymbol)

        # filter out types by category name only
        fam_types = [f for f in col if f.Category.Name == category_name_filter]

        if fam_types is None or len(fam_types) == 0:
            return []

        return fam_types
    except Exception as e:
        print("Error getting family types", e)
        return []


def ui_data_builder(element):
    # element is a family type, UI to contain the family name , family type and category
    # in format "Family Name::Family Type :Category"
    try:
        return "{}{}{}{}{}".format(
            Element.Name.GetValue(element.Family),
            FAM_NAME_TYPE_NAME_CATEGORY_SEPARATOR,
            Element.Name.GetValue(element),
            FAM_NAME_TYPE_NAME_CATEGORY_SEPARATOR,
            element.Category.Name
        )
    except Exception as e:
        return "Unknown {}".format(e)

def get_target_category_name(doc, selection_id):

    fam_type = doc.GetElement(selection_id)
    return fam_type.Category.Name