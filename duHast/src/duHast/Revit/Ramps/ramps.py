"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit ramps.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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
import System

# import Autodesk
import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import common as com
from duHast.Revit.Ramps.Utility import RevitRampsFilter as rRampFilter

# --------------------------------------------- utility functions ------------------


def get_all_ramp_types_by_category(doc):
    """
    Gets a filtered element collector of all Ramp types in the model.

    :param doc: _description_
    :type doc: _type_

    :return: A filtered element collector containing ramp types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rRampFilter._get_all_ramp_types_by_category(doc)
    return collector


# -------------------------------- none in place Ramp types -------------------------------------------------------


def get_all_ramp_instances_by_category(doc):
    """
    Gets all ramp elements placed in model...ignores in place families (to be confirmed!)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ramp instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Ramps)
        .WhereElementIsNotElementType()
    )


def get_all_ramp_types_ids_by_category(doc):
    """
    Gets all ramp element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of ramp types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_cat = get_all_ramp_types_by_category(doc)
    ids = com.get_ids_from_element_collector(col_cat)
    return ids
