"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit ceilings helper functions.
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

# import common library modules
from duHast.Revit.Common import common as com
from duHast.Revit.Family import family_utils as rFam

from duHast.Revit.Ceilings.Utility import ceilings_filter as rCeilingsFilter

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------------------------- utility functions ------------------


def get_all_ceiling_types_by_category(doc):
    """
    Gets a filtered element collector of all ceiling types in the model:

    - Compound Ceiling
    - In place families or loaded families
    - Basic Ceiling

    Filters by category.
    It will therefore not return any roof soffit types ..

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rCeilingsFilter._get_all_ceiling_types_by_category(doc)
    return collector


def get_ceiling_types_by_class(doc):
    """
    Gets a filtered element collector of all ceiling types in the model:

    - Roof Soffit
    - Compound Ceiling
    - Basic Ceiling

    Filters by class.
    It will therefore not return any in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rCeilingsFilter._get_ceiling_types_by_class(doc)
    return collector


# -------------------------------- none in place ceiling types -------------------------------------------------------


def get_all_ceiling_instances_in_model_by_category(doc):
    """
    Gets all ceiling elements placed in model. Ignores roof soffits.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Ceilings)
        .WhereElementIsNotElementType()
    )


def get_all_ceiling_instances_in_model_by_class(doc):
    """
    Gets all ceiling elements placed in model. Ignores in place families.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdb.Ceiling)
        .WhereElementIsNotElementType()
    )


def get_all_ceiling_type_ids_in_model_by_category(doc):
    """
    Gets all ceiling element type ids available in model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    ids = []
    col_cat = get_all_ceiling_types_by_category(doc)
    ids = com.get_ids_from_element_collector(col_cat)
    return ids


def get_all_ceiling_type_ids_in_model_by_class(doc):
    """
    Gets all ceiling element type ids available in model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    ids = []
    col_class = get_ceiling_types_by_class(doc)
    ids = com.get_ids_from_element_collector(col_class)
    return ids


# -------------------------------- In place ceiling types -------------------------------------------------------


def get_in_place_ceiling_family_instances(doc):
    """
    Gets all instances of in place families of category ceiling.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing in place ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Ceilings)
    return (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdb.FamilyInstance)
        .WherePasses(filter)
    )


def get_all_in_place_ceiling_type_ids_in_model(doc):
    """
    Gets all type ids off all available in place families of category ceiling.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing in place ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rFam.get_all_in_place_type_ids_in_model_of_category(
        doc, rdb.BuiltInCategory.OST_Ceilings
    )
    return ids
