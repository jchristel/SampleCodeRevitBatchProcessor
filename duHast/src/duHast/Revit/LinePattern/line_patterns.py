"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit line line patterns helper functions. 
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

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)
import System

# import common library modules
from duHast.Revit.Common import delete as rDel, parameter_get_utils as rParaGet
from duHast.Utilities.Objects import result as res


# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------------PATTERN PROPERTIES ------------

#: pattern name
PROPERTY_PATTERN_NAME = "PatternName"
#: pattern name default value, hard coded solid line pattern name
PROPERTY_PATTERN_NAME_VALUE_DEFAULT = "Solid"
#: pattern id
PROPERTY_PATTERN_ID = "PatternId"


def get_line_pattern_from_category(cat, doc):
    """
    Returns the line pattern properties as a dictionary\
         where keys are pattern name and pattern id.

    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: str, str: Autodesk.Revit.DB.ElementId}
    """

    dic_pattern = {}
    dic_pattern[PROPERTY_PATTERN_NAME] = PROPERTY_PATTERN_NAME_VALUE_DEFAULT
    dic_pattern[PROPERTY_PATTERN_ID] = pattern_id = cat.GetLinePatternId(
        rdb.GraphicsStyleType.Projection
    )
    """check for 'solid' pattern which apparently is not a pattern at all
    *The RevitAPI.chm documents says: Note that Solid is special. It isn't a line pattern at all -- 
    * it is a special code that tells drawing and export code to use solid lines rather than patterned lines. 
    * Solid is visible to the user when selecting line patterns. 
    """
    if pattern_id != rdb.LinePatternElement.GetSolidPatternId():
        # not a solid line pattern
        collector = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement)
        line_pattern_element = None
        for c in collector:
            if pattern_id == c.Id:
                dic_pattern[PROPERTY_PATTERN_NAME] = rdb.Element.Name.GetValue(c)
    return dic_pattern


def get_line_pattern_from_level_element(doc, level):
    """
    Returns the line pattern properties as a dictionary\
         where keys are pattern name and pattern id.

    :param doc: Current Revit family document.
    :type doc: Current Revit family document.
    :param level: a level element
    :type level: Autodesk.Revit.DB.Level

    :return: A dictionary.
    :rtype: dictionary {str: str, str: Autodesk.Revit.DB.ElementId}
    """

    dic_pattern = {}
    dic_pattern[PROPERTY_PATTERN_NAME] = PROPERTY_PATTERN_NAME_VALUE_DEFAULT
    dic_pattern[PROPERTY_PATTERN_ID] = rdb.ElementId.InvalidElementId
    try:
        l_type_id = level.GetTypeId()
        level_type = doc.GetElement(l_type_id)
        line_pattern_id_string = rParaGet.get_built_in_parameter_value(
            level_type, rdb.BuiltInParameter.LINE_PATTERN
        )
        dic_pattern[PROPERTY_PATTERN_ID] = rdb.ElementId(int(line_pattern_id_string))
        dic_pattern[PROPERTY_PATTERN_NAME] = rdb.Element.Name.GetValue(level_type)
    except Exception as ex:
        dic_pattern[PROPERTY_PATTERN_NAME] = str(ex)
    return dic_pattern


# ------------------------------------------------ DELETE LINE PATTERNS ----------------------------------------------


def delete_line_patterns_contains(doc, contains):
    """
    Deletes all line patterns where the names contains a provided string

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param contains: Filter: pattern name needs to contain this string to be deleted.
    :type contains: str

    :return:
        Result class instance.

        - .result = True if line pattern where deleted successfully. Otherwise False.
        - .message will contain delete status per pattern.

    :rtype: :class:`.Result`
    """

    lps = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement).ToList()
    ids = list(
        lp.Id for lp in lps if lp.GetLinePattern().Name.Contains(contains)
    ).ToList[rdb.ElementId]()
    result = rDel.delete_by_element_ids(
        doc,
        ids,
        "Deleting line patterns where name contains: " + str(contains),
        "line patterns containing: " + str(contains),
    )
    return result


def delete_line_pattern_starts_with(doc, starts_with):
    """
    Deletes all line patterns where the name starts with provided string.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param starts_with: Filter: pattern name needs to start with this string to be deleted.
    :type starts_with: str

    :return:
        Result class instance.

        - .result = True if line pattern where deleted successfully. Otherwise False.
        - .message will contain delete status per pattern.

    :rtype: :class:`.Result`
    """

    lps = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement).ToList()
    ids = list(
        lp.Id for lp in lps if lp.GetLinePattern().Name.StartsWith(starts_with)
    ).ToList[rdb.ElementId]()
    result = rDel.delete_by_element_ids(
        doc,
        ids,
        "Delete line patterns where name starts with: " + str(starts_with),
        "line patterns starting with: " + str(starts_with),
    )
    return result


def delete_line_patterns_without(doc, contains):
    """
    Deletes all line patterns where the name does not contain the provided string.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param contains: Filter: pattern name needs not to contain this string to be deleted.
    :type contains: str

    :return:
        Result class instance.

        - .result = True if line pattern where deleted successfully. Otherwise False.
        - .message will contain delete status per pattern.

    :rtype: :class:`.Result`
    """

    lps = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement).ToList()
    ids = list(lp.Id for lp in lps).ToList[rdb.ElementId]()
    ids_contain = list(
        lp.Id for lp in lps if lp.GetLinePattern().Name.Contains(contains)
    ).ToList[rdb.ElementId]()
    delete_ids = list(set(ids) - set(ids_contain))
    result = rDel.delete_by_element_ids(
        doc,
        delete_ids,
        "Delete line patterns where name does not contain: " + str(contains),
        "line patterns without: " + str(contains),
    )
    return result


def get_all_line_patterns(doc):
    """
    Gets all line patterns in the model.

    :param doc: _description_
    :type doc: _type_

    :return: List of all line pattern elements in model.
    :rtype: list of Autodesk.Revit.DB.LinePatternElement
    """
    return rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement).ToList()


def build_patterns_dictionary_by_name(doc):
    """
    Returns a dictionary where line pattern name is key, values are all ids of line patterns with the exact same name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where line pattern name is key, values are all ids of line patterns with the exact same name
    :rtype: dictionary(key str, value list of Autodesk.Revit.DB.ElementId)
    """

    lp_dic = {}
    lps = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement)
    for lp in lps:
        if lp_dic.has_key(lp.GetLinePattern().Name):
            lp_dic[lp.GetLinePattern().Name].append(lp.Id)
        else:
            lp_dic[lp.GetLinePattern().Name] = [lp.Id]
    return lp_dic


def delete_duplicate_line_patter_names(doc):
    """
    Deletes all but the first line pattern by Id with the exact same name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - .result = True if all views where deleted. Otherwise False.
        - .message will contain deletion status.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    return_value.append_message(
        "Deletes all but the first line pattern by Id with the exact same name...start"
    )
    # get a dictionary: Key pattern name, value all ids of line patterns with the same name
    # anything where the value list is greater then 1 means duplicates of the same name...
    line_patterns = build_patterns_dictionary_by_name(doc)
    for key, value in line_patterns.items():
        if len(value) > 1:
            # keep the first one (original)
            value.remove(value[0])
            flag_delete = rDel.delete_by_element_ids(
                doc,
                value,
                "Deleting duplicate line patterns names: {}".format(key),
                "line patterns duplicates: {}".format(key),
            )
            return_value.update(flag_delete)
    return return_value
