"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit stair landing elements. 
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

import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Architecture as rdbA

from duHast.Revit.Common import common as com

#: list of built in parameters attached to stair sub types
STAIR_LANDING_TYPE_PARAS = [rdb.BuiltInParameter.STAIRSTYPE_LANDING_TYPE]


def get_stair_landing_types_by_class(doc):
    """
    Gets a filtered element collector of all Stair landing types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing stair landing types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return rdb.FilteredElementCollector(doc).OfClass(rdbA.StairsLandingType)


def get_stair_landing_types_ids_by_class(doc):
    """
    Gets all Stair landing element type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing stair landing types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_class = get_stair_landing_types_by_class(doc)
    ids = com.get_ids_from_element_collector(col_class)
    return ids
