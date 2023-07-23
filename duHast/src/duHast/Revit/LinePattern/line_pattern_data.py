"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family line pattern data class.
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

from duHast.Revit.Family.Data import ifamily_data as IFamData
from duHast.Utilities import utility as util
from duHast.Revit.Categories import categories as rCats
from duHast.Revit.LinePattern.line_patterns import (
    get_line_pattern_from_category,
    get_line_pattern_from_level_element,
    PROPERTY_PATTERN_ID,
)
from duHast.Revit.Levels.levels import get_levels_list_ascending


# import Autodesk
import Autodesk.Revit.DB as rdb

# data dictionary key values specific to this class
PATTERN_NAME = "patternName"
PATTERN_ID = "patternId"


class LinePatternData(IFamData.IFamilyData):
    def __init__(self, root_path=None, root_category_path=None, data_type=None):
        """
        Class constructor

        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param dataType: Human readable data type descriptor
        :type dataType: str
        """

        super(LinePatternData, self).__init__(
            root_path=root_path,
            root_category_path=root_category_path,
            data_type=data_type,
        )
        # super(CategoryData, self).__init__(rootPath, dataType)
        """
        self.data = []
        
        if(dataType != None):
            self.dataType = dataType
        else:
            self.dataType = 'not declared'
        
        if(rootPath != None):
            self.rootPath = rootPath
        else:
            self.rootPath = '-'

        if(rootCategoryPath != None):
            self.rootCategoryPath = rootCategoryPath
        else:
            self.rootCategoryPath = '-'
        """

    def _add_category_to_dic(self, line_pattern_ids, pattern_id, category):
        """
        Adds a category to a dictionary using the line pattern ID as value

        :param linePatternIds: dictionary in format: Key: line Pattern Id, value list of categories using that line pattern
        :type linePatternIds: {ElementId:[Autodesk.revit.DB.Category]}
        :param patternId: the pattern element id
        :type patternId: Autodesk.Revit.DB.ElementId
        :param category: the category using the line pattern
        :type category: Autodesk.Revit.DB.Category
        """

        if pattern_id in line_pattern_ids:
            line_pattern_ids[pattern_id].append(category)
        else:
            line_pattern_ids[pattern_id] = [category]

    def _get_line_pattern_from_categories(self, doc):
        """
        Loops over all family categories and sub categories and any other categories and sub categories with a positive Id (custom sub category) and
        returns a dictionary of line pattern ids to categories using them.

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        :return: a dictionary in format: Key: line Pattern Id, value list of categories using that line pattern
        :rtype: {ElementId:[Autodesk.revit.DB.Category]}
        """

        line_pattern_ids_to_categories = {}

        # get any line pattern added to the family category itself
        main_cat = rCats.get_family_category(doc)
        for m_cat_name in main_cat:
            l_style = get_line_pattern_from_category(main_cat[m_cat_name], doc)
            # update dictionary
            self._add_category_to_dic(
                line_pattern_ids_to_categories,
                l_style[PROPERTY_PATTERN_ID],
                main_cat[m_cat_name],
            )

        # get line patterns from sub categories of the family category
        main_cats = rCats.get_main_sub_categories(doc)
        for m_cat_name in main_cats:
            l_style = get_line_pattern_from_category(main_cats[m_cat_name], doc)
            # update dictionary
            self._add_category_to_dic(
                line_pattern_ids_to_categories,
                l_style[PROPERTY_PATTERN_ID],
                main_cats[m_cat_name],
            )

        # get line pattern from unrelated sub categories
        sub_cats_other = rCats.get_other_sub_categories(doc)
        for s_cat_name in sub_cats_other:
            for s_cat_item in sub_cats_other[s_cat_name]:
                # only use custom categories not build in ones (id smaller then 0)
                if sub_cats_other[s_cat_name][s_cat_item].Id.IntegerValue > 0:
                    l_style = get_line_pattern_from_category(
                        sub_cats_other[s_cat_name][s_cat_item], doc
                    )
                    # update dictionary
                    self._add_category_to_dic(
                        line_pattern_ids_to_categories,
                        l_style[PROPERTY_PATTERN_ID],
                        sub_cats_other[s_cat_name][s_cat_item],
                    )

        # get line pattern from reference lines and planes categories import in families main cat
        other_cats = rCats.get_category_by_built_in_def_name(
            doc,
            [
                rdb.BuiltInCategory.OST_ReferenceLines,  # reference lines
                rdb.BuiltInCategory.OST_CLines,  # reference planes
                rdb.BuiltInCategory.OST_ImportObjectStyles,
            ],  # import in families
        )
        for o_cat in other_cats:
            l_style = get_line_pattern_from_category(o_cat, doc)
            # update dictionary
            self._add_category_to_dic(
                line_pattern_ids_to_categories, l_style[PROPERTY_PATTERN_ID], o_cat
            )

        return line_pattern_ids_to_categories

    def _get_pattern_from_level_element(self, doc):
        """
        Gets the pattern data from all level types in document.

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document

        :return: a dictionary in format: Key: line Pattern Id, value list of levels using that line pattern
        :rtype: {ElementId:[Autodesk.revit.DB.Category]}
        """

        level_pattern_data = {}
        levels = get_levels_list_ascending(doc)
        for level in levels:
            pattern_data = get_line_pattern_from_level_element(doc, level)
            self._add_category_to_dic(
                level_pattern_data, pattern_data[PROPERTY_PATTERN_ID], level
            )
        return level_pattern_data

    def _get_pattern_name(self, element):
        """
        Get the element name.

        :param element: _description_
        :type element: _type_
        :return: Element name, or exception stating name is not unicode
        :rtype: str
        """

        element_name = "unknown_notUnicode"
        try:
            element_name = util.encode_ascii(rdb.Element.Name.GetValue(element))
        except Exception as ex:
            element_name = element_name + " Exception: " + str(ex)
        return element_name

    def _get_pattern_usage_data_from_categories(self, line_pattern_ids, element):
        """
        Returns how often and on which category a line pattern is used

        :param linePatternIds: a dictionary in format: Key: line Pattern Id, value list of categories using that line pattern
        :type linePatternIds: {ElementId:[Autodesk.revit.DB.Category]}
        :param element: The line pattern element.
        :type element: _type_

        :return: counter and  a list of dictionaries in format {categoryId: int, categoryName: str}
        :rtype: int, [{categoryId:int, categoryName:str}]
        """

        counter = 0
        pattern_names = []
        # how often used
        if element.Id in line_pattern_ids:
            counter = len(line_pattern_ids[element.Id])
            for pat in line_pattern_ids[element.Id]:
                pattern_names.append(
                    {"categoryId": pat.Id.IntegerValue, "categoryName": pat.Name}
                )
        return counter, pattern_names

    def _get_pattern_usage_data_from_level(self, line_pattern_ids, element):
        """
        Returns how often and on which Level type a line pattern is used

        :param linePatternIds:
        :type linePatternIds: {ElementId:[Autodesk.revit.DB.Category]}
        :param element: The line pattern element.
        :type element: _type_

        :return: counter and  a list of dictionaries in format {categoryId: int, categoryName: str}
        :rtype: int, [{categoryId:int, categoryName:str}]
        """

        counter = 0
        pattern_names = []

        # how often used
        if element.Id in line_pattern_ids:
            counter = len(line_pattern_ids[element.Id])
            for pat in line_pattern_ids[element.Id]:
                pattern_names.append(
                    {
                        "levelId": pat.Id.IntegerValue,
                        "levelTypeName": rdb.Element.Name.GetValue(pat),
                    }
                )
        return counter, pattern_names

    def process(self, doc):
        """
        Collects all line pattern data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        """

        # get all line patterns used in categories (includes sub categories of family category and any custom subcategories of non family category present, includes also
        # ref planes , ref lines, import styles)
        line_pattern_ids_by_category = self._get_line_pattern_from_categories(doc)
        # get line pattern used on level element
        line_pattern_ids_by_from_level = self._get_pattern_from_level_element(doc)

        collector = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement)
        for element in collector:
            # just in case parameter name is not unicode
            element_name = self._get_pattern_name(element)
            # get usage data from categories
            counter, pattern_names = self._get_pattern_usage_data_from_categories(
                line_pattern_ids_by_category, element
            )
            # get usage data from levels
            (
                counter_level,
                pattern_names_level,
            ) = self._get_pattern_usage_data_from_level(
                line_pattern_ids_by_from_level, element
            )

            # get overall count
            counter = counter + counter_level
            # get overall usage data
            usage_all = pattern_names + pattern_names_level

            # build data
            self.data.append(
                {
                    IFamData.ROOT: self.root_path,
                    IFamData.ROOT_CATEGORY: self.root_category_path,
                    IFamData.FAMILY_NAME: self._strip_file_extension(doc.Title),
                    IFamData.FAMILY_FILE_PATH: doc.PathName,
                    IFamData.USAGE_COUNTER: counter,
                    IFamData.USED_BY: usage_all,
                    PATTERN_NAME: element_name,
                    PATTERN_ID: element.Id.IntegerValue,
                }
            )

    def get_data(self):
        return self.data
