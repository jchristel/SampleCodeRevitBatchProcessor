"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
data to revit api FilterValueRule conversion helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
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

from duHast.Revit.Views.Objects.Data.view_filter_rule import ViewFilterRule

from Autodesk.Revit.DB import FilterValueRule

from Autodesk.Revit.DB import  (
    FilterDoubleRule,
    FilterIntegerRule,
    FilterElementIdRule,
    FilterStringRule,
)

# dictionary containing varies rule mappings

# numeric rules (all of these inherit from: Autodesk.Revit.DB.FilterNumericValueRule)
# string rules (just one : Autodesk.Revit.DB.FilterStringRule)

class_mapping = {
    "FilterDoubleRule": FilterDoubleRule,
    "FilterElementIdRule":  FilterElementIdRule,
    "FilterIntegerRule": FilterIntegerRule,
    "FilterStringRule":  FilterStringRule,

}


def convert_data_to_rule(doc, rule_data_instance):
    """
    Converts a ViewFilterRule data instance to a Revit FilterValueRule.

    Args:
        doc (Revit Document): The Revit document object.
        rule_data_instance (ViewFilterRule): An instance of the ViewFilterRule class containing the rule data.

    Returns:
        FilterValueRule or None: The created FilterValueRule object if successful, otherwise None.
    """
    return_value = None

    # check input
    if not isinstance(rule_data_instance, ViewFilterRule):
        return return_value
    
    
    return return_value