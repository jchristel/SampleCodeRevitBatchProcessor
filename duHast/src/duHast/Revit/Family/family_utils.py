"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families helper functions.
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


clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)
clr.AddReference("System")


# import common library
# utility functions for most commonly used Revit API tasks
from duHast.Revit.Common import parameter_get_utils as rParaGet

# utilities
from duHast.Utilities import files_io as fileIO

# class used for stats reporting
from duHast.Utilities.Objects import result as res

# implementation of Revit API callback required when loading families into a Revit model
from duHast.Revit.Family import family_load_option as famLoadOpt

# load everything required from family load call back
from duHast.Revit.Family.family_load_option import *
from duHast.Revit.Common import transaction as rTran

# import Autodesk Revit DataBase namespace
import Autodesk.Revit.DB as rdb

from duHast.Revit.Family.Utility.loadable_family_categories import (
    CATEGORIES_LOADABLE_3D,
    CATEGORIES_LOADABLE_TAGS,
)

# --------------------------------------------------- Family Loading / inserting -----------------------------------------


def load_family(doc, family_file_path):
    """
    Loads or reloads a single family into a Revit document.

    Will load/ reload family provided in in path. By default the parameter values in the project file will be overwritten
    with parameter values in family.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param family_file_path: The fully qualified file path of the family to be loaded.
    :type family_file_path: str
    :raise: None

    :return:
        Result class instance.

        - Reload status (bool) returned in result.status.
        - Reload status returned from Revit in result.message property.
        - Return family reference stored in result.result property on successful reload only

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    """

    result = res.Result()
    try:
        # set up load / reload action to be run within a transaction
        def action():
            # set up return value for the load / reload
            return_family = clr.Reference[rdb.Family]()
            action_return_value = res.Result()
            try:
                reload_status = doc.LoadFamily(
                    family_file_path,
                    famLoadOpt.FamilyLoadOption(),  # overwrite parameter values etc
                    return_family,
                )
                action_return_value.update_sep(
                    reload_status,
                    "Loaded family: " + family_file_path + " :: " + str(reload_status),
                )
                if reload_status:
                    action_return_value.result.append(return_family.Value)
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to load family "
                    + family_file_path
                    + " with exception: "
                    + str(e),
                )
            return action_return_value

        transaction = rdb.Transaction(
            doc,
            "Loading Family: "
            + str(fileIO.get_file_name_without_ext(family_file_path)),
        )
        dummy = rTran.in_transaction(transaction, action)
        result.update(dummy)
    except Exception as e:
        result.update_sep(False, "Failed to load families with exception: " + str(e))
    return result


# ------------------------ filter functions -------------------------------------------------------------------------------------


def get_family_symbols(doc, cats):
    """
    Filters all family symbols (Revit family types) of given built in categories from the Revit model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param cats: ICollection of Autodesk.Revit.DB.BuiltInCategory values.
    :type cats: ICollection
        :cats sample: cats = List[rdb.BuiltInCategory] ([rdb.BuiltInCategory.OST_Furniture, rdb.BuiltInCategory.OST_Parking])

    :return: A collector of Autodesk.Revit.DB.Element matching filter.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    elements = []
    try:
        multi_cat_filter = rdb.ElementMulticategoryFilter(cats)
        elements = (
            rdb.FilteredElementCollector(doc)
            .OfClass(rdb.FamilySymbol)
            .WherePasses(multi_cat_filter)
            .ToElements()
        )
        return elements
    except Exception:
        return elements


def get_family_instances_by_built_in_categories(doc, cats):
    """
    Filters all family instances of given built in categories from the Revit model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param cats: ICollection of Autodesk.Revit.DB.BuiltInCategory values:
    :type cats: ICollection
        :cats sample: cats = List[rdb.BuiltInCategory] ([rdb.BuiltInCategory.OST_Furniture, rdb.BuiltInCategory.OST_Parking])

    :return: A collector of Autodesk.Revit.DB.Element matching filter.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    elements = []
    try:
        multi_cat_filter = rdb.ElementMulticategoryFilter(cats)
        elements = (
            rdb.FilteredElementCollector(doc)
            .OfClass(rdb.FamilyInstance)
            .WherePasses(multi_cat_filter)
            .ToElements()
        )
        return elements
    except Exception:
        return elements


def get_family_instances_of_built_in_category(doc, builtin_cat):
    """
    Filters all family instances of a single given built in category from the Revit model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param builtin_cat: single revit builtInCategory Enum value.
    :type builtin_cat: Autodesk.Revit.DB.BuiltInCategory

    :return: A collector of Autodesk.Revit.DB.FamilyInstance matching filter.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    filter = rdb.ElementCategoryFilter(builtin_cat)
    col = (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdb.FamilyInstance)
        .WherePasses(filter)
    )
    return col


def get_all_loadable_families(doc):
    """
    Filters all families in revit model by whether it is not an InPlace family.

    Note: slow filter due to use of lambda and cast to list.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of families matching filter.
    :rtype: list Autodesk.Revit.DB.Family
    """

    collector = rdb.FilteredElementCollector(doc)
    families = (
        collector.OfClass(rdb.Family).Where(lambda e: (e.IsInPlace == False)).ToList()
    )
    return families


def get_all_loadable_family_ids_through_types(doc):
    """
    Get all loadable family ids in file.

    :param doc: Current family document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list of family ids
    :rtype: [Autodesk.Revit.DB.ElementId]
    """

    family_ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol)
    # get families from symbols and filter out in place families
    for fam_symbol in col:
        if (
            fam_symbol.Family.Id not in family_ids
            and fam_symbol.Family.IsInPlace == False
        ):
            family_ids.append(fam_symbol.Family.Id)
    return family_ids


def get_all_in_place_families(doc):
    """
    Filters all families in revit model by whether it is an InPlace family.

    Note: slow filter due to use of lambda and cast to list

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of families matching filter.
    :rtype: list Autodesk.Revit.DB.Family
    """

    collector = rdb.FilteredElementCollector(doc)
    families = (
        collector.OfClass(rdb.Family).Where(lambda e: (e.IsInPlace == True)).ToList()
    )
    return families


def get_all_family_instances(doc):
    """
    Returns all family instances in document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A collector with all family instances in document.
    :rtype: Autodesk.Revit.DB.Collector
    """

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance)
    return col


# --------------------------family data ----------------


def is_any_nested_family_instance_label_driven(doc):
    """
    Checks whether any family isntance in document is driven by the 'Label' property.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if at least one instance is driven by label property. Othewise False
    :rtype: bool
    """

    flag = False
    fam_instances = get_all_family_instances(doc)

    for fam_instance in fam_instances:
        # get the Label parameter value
        p_value = rParaGet.get_built_in_parameter_value(
            fam_instance,
            rdb.BuiltInParameter.ELEM_TYPE_LABEL,
            rParaGet.get_parameter_value_as_element_id,
        )
        # a valid Element Id means family instance is driven by Label
        if p_value != rdb.ElementId.InvalidElementId:
            flag = True
            break

    return flag


def get_symbols_from_type(doc, type_ids):
    """
    Get all family types belonging to the same family as types past in.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param type_ids: - list of element id's representing family symbols (family types)
    :type type_ids: list of Autodesk.Revit.DB.ElementId

    :return: dictionary:
        where key is the family id as Autodesk.Revit.DB.ElementId
        value is a list of all symbol(family type) ids as Autodesk.Revit.DB.ElementId belonging to the family
    :rtype: dic {Autodesk.Revit.DB.ElementId: list[Autodesk.Revit.DB.ElementId]}
    """

    families = {}
    for t_id in type_ids:
        # get family element
        type_el = doc.GetElement(t_id)
        fam_el = type_el.Family
        # check whether family was already processed
        if fam_el.Id not in families:
            # get all available family types
            s_ids = fam_el.GetFamilySymbolIds().ToList()
            families[fam_el.Id] = s_ids
    return families


def get_family_instances_by_symbol_type_id(doc, type_id):
    """
    Filters all family instances of a single given family symbol (type).

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param Autodesk.Revit.DB.ElementId type_id: The symbol (type) id

    :return: A collector of Autodesk.Revit.DB.FamilyInstance matching filter.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    pvp_symbol = rdb.ParameterValueProvider(
        rdb.ElementId(rdb.BuiltInParameter.SYMBOL_ID_PARAM)
    )
    equals = rdb.FilterNumericEquals()
    id_filter = rdb.FilterElementIdRule(pvp_symbol, equals, type_id)
    element_filter = rdb.ElementParameterFilter(id_filter)
    collector = rdb.FilteredElementCollector(doc).WherePasses(element_filter)
    return collector


def get_all_in_place_type_ids_in_model_of_category(doc, fam_built_in_category):
    """
    Filters family symbol (type) ids off all available in place families of single given built in category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param fam_built_in_category: built in revit category
    :type fam_built_in_category: Autodesk.Revit.DB.BuiltInCategory

    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    # filter model for family symbols of given built in category
    filter = rdb.ElementCategoryFilter(fam_built_in_category)
    col = (
        rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    )
    ids = []
    for c in col:
        fam = c.Family
        # check if this an in place or loaded family!
        if fam.IsInPlace == True:
            ids.append(c.Id)
    return ids


# --------------------------family purge  ----------------


def get_family_symbols_ids(doc, cats, exclude_shared_fam=True):
    """
    Filters family symbols belonging to list of built in categories past in.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ICollection cats: ICollection of Autodesk.Revit.DB.BuiltInCategory values.
    :type cats: cats = List[rdb.BuiltInCategory] ([rdb.BuiltInCategory.OST_Furniture, rdb.BuiltInCategory.OST_Parking])

    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    try:
        multi_cat_filter = rdb.ElementMulticategoryFilter(cats)
        elements = (
            rdb.FilteredElementCollector(doc)
            .OfClass(rdb.FamilySymbol)
            .WherePasses(multi_cat_filter)
        )
        for el in elements:
            # check if shared families are to be excluded from return list
            if exclude_shared_fam:
                fam = el.Family
                p_value = rParaGet.get_built_in_parameter_value(
                    fam, rdb.BuiltInParameter.FAMILY_SHARED
                )
                if p_value != None:
                    if p_value == "No" and el.Id not in ids:
                        ids.append(el.Id)
                else:
                    # some revit families cant be of type shared...()
                    ids.append(el.Id)
            else:
                ids.append(el.Id)
        return ids
    except Exception:
        return ids


def get_all_non_shared_family_symbol_ids(doc):
    """
    Filters family symbols (types) belonging to hard coded categories lists (catsLoadableThreeD, catsLoadableTags)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    all_loadable_three_d_type_ids = get_family_symbols_ids(doc, CATEGORIES_LOADABLE_3D)
    all_loadable_tags_type_ids = get_family_symbols_ids(doc, CATEGORIES_LOADABLE_TAGS)
    ids = all_loadable_three_d_type_ids + all_loadable_tags_type_ids
    return ids
