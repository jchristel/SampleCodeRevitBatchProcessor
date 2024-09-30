"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit railings utility functions. 
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


from Autodesk.Revit.DB import ElementMulticategoryFilter, FilteredElementCollector
from Autodesk.Revit.DB.Architecture import RailingType

from duHast.Revit.Railings.Utility.railing_categories import RAILING_CATEGORY_FILTER


def _get_all_railing_types_by_category(doc):
    """
    Gets a filtered element collector of all Railing types in the model.

    Collector will include types of:
    - Top Rail
    - Rail support
    - Hand rail
    - Rail termination
    - Railing Systems
    - In place families or loaded families

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing related types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    multi_cat_filter = ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    collector = (
        FilteredElementCollector(doc)
        .WherePasses(multi_cat_filter)
        .WhereElementIsElementType()
    )
    return collector


def _get_railing_types_by_class(doc):
    """
    Gets a filtered element collector of all Railing types in the model:

    Collector will include types of:
    - Railing

    It will therefore not return any top rail or hand rail or in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return FilteredElementCollector(doc).OfClass(RailingType)
