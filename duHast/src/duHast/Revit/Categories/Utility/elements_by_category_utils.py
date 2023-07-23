"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit elements to category helper functions.
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

import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import parameter_set_utils as rParaSet
from duHast.Utilities.Objects import result as res
from duHast.Revit.Links import cad_links_geometry as rCadLinkGeo
from duHast.Revit.Common import parameter_get_utils as rParaGet

from duHast.Revit.Categories.categories import (
    ELEMENTS_PARAS_SUB,
    get_main_sub_categories,
)
from duHast.Revit.Categories.Utility.category_properties_get_utils import (
    get_category_graphic_style_ids,
)
from duHast.Revit.Categories.Utility.category_property_names import (
    CATEGORY_GRAPHIC_STYLE_3D,
)
from duHast.Revit.Family import family_element_utils as rFamElementUtils


def sort_elements_by_category(elements, element_dic):
    """
    Returns a dictionary of element ids where key is the category they belong to.
    :param elements:  List of revit elements.
    :type elements: [Autodesk.Revit.DB.Element]
    :param element_dic:  Dictionary where key is subcategory and values are element ids.
    :type element_dic: {Autodesk.Revit.DB.Category: [Autodesk.Revit.DB.ElementId]}
    :return: Dictionary where key is subcategory id and values are element ids.
    :rtype: {Autodesk.Revit.DB.ElementId: [Autodesk.Revit.DB.ElementId]}
    """

    for el in elements:
        for builtin_def in ELEMENTS_PARAS_SUB:
            value = rParaGet.get_built_in_parameter_value(
                el, builtin_def, rParaGet.get_parameter_value_as_element_id
            )
            if value != None:
                if value in element_dic:
                    element_dic[value].append(el.Id)
                else:
                    element_dic[value] = [el.Id]
                break
    return element_dic


def sort_geometry_elements_by_category(elements, element_dic, doc):
    counter = 0
    for el in elements:
        counter = counter + 1
        graphic_style_id = rdb.ElementId.InvalidElementId
        if type(el) is rdb.Solid:
            # get graphic style id from edges
            edge_array = el.Edges
            if edge_array.IsEmpty == False:
                for edge in edge_array:
                    graphic_style_id = edge.GraphicsStyleId
        else:
            graphic_style_id = el.GraphicsStyleId
        # failed to get an id?
        if graphic_style_id != rdb.ElementId.InvalidElementId:
            graphic_style = doc.GetElement(graphic_style_id)
            graph_cat_id = graphic_style.GraphicsStyleCategory.Id
            # geometry elements have no Id property ... Doh!! pass in invalid element id...
            if graph_cat_id != None:
                if graph_cat_id in element_dic:
                    element_dic[graph_cat_id].append(rdb.ElementId.InvalidElementId)
                else:
                    element_dic[graph_cat_id] = [rdb.ElementId.InvalidElementId]
    return element_dic


def _sort_all_elements_by_category(doc):
    """
    Sorts all elements in a family by category.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Dictionary where key is subcategory id and values are element ids.
    :rtype: {Autodesk.Revit.DB.ElementId: [Autodesk.Revit.DB.ElementId]}
    """

    # get all elements in family
    dic = {}
    el_curve = rFamElementUtils.get_all_curve_based_elements_in_family(doc)
    el_forms = rFamElementUtils.get_all_generic_forms_in_family(doc)
    el_m_text = rFamElementUtils.get_all_model_text_elements_in_family(doc)
    el_ref_planes = rFamElementUtils.get_all_reference_planes_in_family(doc)
    # get import Instance elements
    el_import = rCadLinkGeo.get_all_cad_import_instances_geometry(doc)
    # build dictionary where key is category or graphic style id of  a category
    dic = sort_elements_by_category(el_curve, dic)
    dic = sort_elements_by_category(el_forms, dic)
    dic = sort_elements_by_category(el_m_text, dic)
    dic = sort_elements_by_category(el_ref_planes, dic)
    # geometry instances use a property rather then a parameter to store the category style Id
    dic = sort_geometry_elements_by_category(el_import, dic, doc)
    return dic


def get_elements_by_category(doc, cat):
    """
    Returns elements in family assigned to a specific category
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :return: Dictionary where key is subcategory and values are element ids.
    :rtype: {Autodesk.Revit.DB.Category: [Autodesk.Revit.DB.ElementId]}
    """

    # get all elements in family
    dic = _sort_all_elements_by_category(doc)
    # get id and graphic style id of category to be filtered by
    category_ids = get_category_graphic_style_ids(cat)
    # check whether category past in is same as owner family category
    if doc.OwnerFamily.FamilyCategory.Name == cat.Name:
        # 3d elements within family which have subcategory set to 'none' belong to owner family
        # category. Revit uses a None value as id rather then the actual category id
        # my get parameter value translates that into -1 (invalid element id)
        category_ids[CATEGORY_GRAPHIC_STYLE_3D] = rdb.ElementId.InvalidElementId
    dic_filtered = {}
    # filter elements by category ids
    for key, value in category_ids.items():
        # print (key + ' ' + str(value))
        if value in dic:
            dic_filtered[key] = dic[value]
        else:
            dic_filtered[key] = []
    return dic_filtered


def move_elements_to_category(doc, elements, to_category_name, destination_cat_ids):
    """
    Moves elements provided in dictionary to another category specified by name.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param elements: Dictionary of elements, key are graphic style names.
    :type elements: {Autodesk.Revit.DB.Category: [Autodesk.Revit.DB.ElementId]}
    :param to_category_name: The name of the subcategory elements are to be moved to.
    :type to_category_name: str
    :param destination_cat_ids: Dictionary of ids of graphic style, key are graphic style names
    :type destination_cat_ids: dictionary {str: Autodesk.Revit.DB.ElementId}
    :return:
        Result class instance.
        - result.status. True if all elements where moved to destination subcategories, otherwise False.
        - result.message will contain the name of the destination subcategory by element.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # check whether destination category exist in file
    cats = get_main_sub_categories(doc)
    if to_category_name in cats:
        for key, value in elements.items():
            # anything needing moving?
            if len(value) > 0:
                for el_id in value:
                    el = doc.GetElement(el_id)
                    paras = el.GetOrderedParameters()
                    # find the parameter driving the subcategory
                    for p in paras:
                        if p.Definition.BuiltInParameter in ELEMENTS_PARAS_SUB:
                            # get the subcategory style id
                            target_id = destination_cat_ids[key]
                            # check if a 'cut' style id exists...if not move to 'projection' instead
                            # not sure how this works in none - english versions of Revit...
                            if (
                                key == "Cut"
                                and target_id == rdb.ElementId.InvalidElementId
                            ):
                                target_id = destination_cat_ids["Projection"]
                                return_value.append_message(
                                    "No cut style present in family, using projection style instead"
                                )
                            updated_para = rParaSet.set_parameter_value(
                                p, str(target_id), doc
                            )
                            return_value.update(updated_para)
                            break
    else:
        return_value.update_sep(
            False,
            "Destination category: {} does not exist in file!".format(to_category_name),
        )
    return return_value


def move_elements_from_sub_category_to_sub_category(
    doc, from_category_name, to_category_name
):
    """
    Moves elements from one subcategory to another one identified by their names.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param from_category_name: The source subcategory name.
    :type from_category_name: str
    :param to_category_name: The destination subcategory name.
    :type to_category_name: str
    :return:
        Result class instance.
        - result.status. True if all elements from source subcategory where moved to destination subcategory, otherwise False.
        - result.message will contain the name of the destination subcategory by element.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # check whether source and destination category exist in file
    cats = get_main_sub_categories(doc)
    if from_category_name in cats:
        if to_category_name in cats:
            # dictionary containing destination category ids (3D, cut and projection)
            destination_cat_ids = get_category_graphic_style_ids(cats[to_category_name])
            # get elements on source category
            dic = get_elements_by_category(doc, cats[from_category_name])
            # move elements
            return_value = move_elements_to_category(
                doc, dic, to_category_name, destination_cat_ids
            )
        else:
            return_value.update_sep(
                False,
                "Destination category: {} does not exist in file!".format(
                    to_category_name
                ),
            )
    else:
        return_value.update_sep(
            False,
            "Source category: {} does not exist in file!".format(from_category_name),
        )
    return return_value


def get_used_category_ids(doc):
    """
    Returns all category ids in a family which have an element assigned to them
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of categories.
    :rtype: [Autodesk.Revit.DB.Category]
    """

    # get all elements in family
    dic = _sort_all_elements_by_category(doc)
    return dic.keys()
