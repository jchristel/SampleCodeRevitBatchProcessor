"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
storage to revit api evaluator conversion helper functions.
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

from Autodesk.Revit.DB import  (
    FilterNumericEquals,
    FilterNumericGreater,
    FilterNumericGreaterOrEqual,
    FilterNumericLess,
    FilterNumericLessOrEqual,
    FilterStringBeginsWith,
    FilterStringContains,
    FilterStringEndsWith,
    FilterStringEquals,
    FilterStringGreater,
    FilterStringGreaterOrEqual,
    FilterStringLess,
    FilterStringLessOrEqual,
)


# dictionary containing varies evaluator mappings

# numeric rules (all of these inherit from: Autodesk.Revit.DB.FilterNumericRuleEvaluator)
# string rules (all of these inherit from: Autodesk.Revit.DB.FilterStringRuleEvaluator)

class_mapping = {
    "FilterNumericEquals":  FilterNumericEquals,
    "FilterNumericGreater": FilterNumericGreater,
    "FilterNumericGreaterOrEqual": FilterNumericGreaterOrEqual,
    "FilterNumericLess": FilterNumericLess,
    "FilterNumericLessOrEqual": FilterNumericLessOrEqual,
    "FilterStringBeginsWith": FilterStringBeginsWith,
    "FilterStringContains": FilterStringContains,
    "FilterStringEndsWith": FilterStringEndsWith,
    "FilterStringEquals": FilterStringEquals,
    "FilterStringGreater": FilterStringGreater,
    "FilterStringGreaterOrEqual": FilterStringGreaterOrEqual,
    "FilterStringLess": FilterStringLess,
    "FilterStringLessOrEqual": FilterStringLessOrEqual,
}


def get_evaluator_class(class_name):
    """
    Returns an evaluator class based on the provided class name.
    None ignored or not found.

    :param class_name: Name of the evaluator class to retrieve.
    :type class_name: str

    :return: The evaluator class if found, otherwise None.
    :rtype: class or None
    """
    
    return_value = None
    if class_name and class_name in class_mapping:
        evaluator_class = class_mapping.get(class_name)
        return evaluator_class
    return return_value