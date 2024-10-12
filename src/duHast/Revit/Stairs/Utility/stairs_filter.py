"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of base element filter functions relating to Revit stairs. 
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

# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Architecture as rdbA


def _get_all_stair_types_by_category(doc):
    """
    Gets a filtered element collector of all Stair types in the model.

    Return includes:
    - Stair
    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair
    - In place families or loaded families

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Stairs)
        .WhereElementIsElementType()
    )
    return collector


def _get_stair_types_by_class(doc):
    """
    Gets a filtered element collector of all Stair types in the model.

    Return includes:

    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair

    It will not return any in place family or Stair types! These are internally treated as Families or Family Symbols class objects.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return rdb.FilteredElementCollector(doc).OfClass(rdbA.StairsType)
