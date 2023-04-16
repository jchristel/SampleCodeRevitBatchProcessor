'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family line pattern data class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from duHast.APISamples.Family.Reporting import IFamilyData as IFamData
from duHast.Utilities import Utility as util
from duHast.APISamples.Categories import RevitCategories as rCats
from duHast.APISamples.LinePattern import RevitLineStylesPatterns as rPat
from duHast.APISamples import RevitLevels as rLevel


# import Autodesk
import Autodesk.Revit.DB as rdb

# data dictionary key values specific to this class
PATTERN_NAME = 'patternName'
PATTERN_ID = 'patternId'

class LinePatternData(IFamData.IFamilyData):
    
    def __init__(self, root_path=None, root_category_path=None, data_type=None):
        '''
        Class constructor

        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param dataType: Human readable data type descriptor
        :type dataType: str
        '''

        super(LinePatternData, self).__init__(root_path=root_path, root_category_path=root_category_path, data_type=data_type)
        # super(CategoryData, self).__init__(rootPath, dataType)
        '''
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
        '''

    def _add_category_to_dic(self, line_pattern_ids, pattern_id, category):
        '''
        Adds a category to a dictionary using the line pattern ID as value

        :param linePatternIds: dictionary in format: Key: line Pattern Id, value list of categories using that line pattern
        :type linePatternIds: {ElementId:[Autodesk.revit.DB.Category]}
        :param patternId: the pattern element id
        :type patternId: Autodesk.Revit.DB.ElementId
        :param category: the category using the line pattern
        :type category: Autodesk.Revit.DB.Category
        '''

        if(pattern_id in line_pattern_ids):
            line_pattern_ids[pattern_id].append(category)
        else:
            line_pattern_ids[pattern_id] = [category]

    def _get_line_pattern_from_categories(self, doc):
        '''
        Loops over all family categories and sub categories and any other categories and sub categories with a positive Id (custom sub category) and
        returns a dictionary of line pattern ids to categories using them.

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        :return: a dictionary in format: Key: line Pattern Id, value list of categories using that line pattern
        :rtype: {ElementId:[Autodesk.revit.DB.Category]}
        '''

        linePatternIdsToCategories = {}

        # get any line pattern added to the family category itself
        mainCat = rCats.get_family_category(doc)
        for mCatName in mainCat:
            lStyle = rPat.GetLinePatternFromCategory (mainCat[mCatName], doc)
            # update dictionary
            self._add_category_to_dic(linePatternIdsToCategories, lStyle[rPat.PROPERTY_PATTERN_ID], mainCat[mCatName])
        
        # get line patterns from sub categories of the family category
        mainCats = rCats.get_main_sub_categories(doc)
        for mCatName in mainCats:
            lStyle = rPat.GetLinePatternFromCategory (mainCats[mCatName], doc)
            # update dictionary
            self._add_category_to_dic(linePatternIdsToCategories, lStyle[rPat.PROPERTY_PATTERN_ID], mainCats[mCatName])
        
        # get line pattern from unrelated sub categories
        subCatsOther = rCats.get_other_sub_categories(doc)
        for sCatName in subCatsOther:
            for sCatItem in subCatsOther[sCatName]:
                # only use custom categories not build in ones (id smaller then 0)
                if(subCatsOther[sCatName][sCatItem].Id.IntegerValue > 0):
                    lStyle = rPat.GetLinePatternFromCategory (subCatsOther[sCatName][sCatItem], doc)
                    # update dictionary
                    self._add_category_to_dic(linePatternIdsToCategories, lStyle[rPat.PROPERTY_PATTERN_ID], subCatsOther[sCatName][sCatItem])
        
        # get line pattern from reference lines and planes categories import in families main cat
        otherCats = rCats.get_category_by_built_in_def_name(
            doc, [
            rdb.BuiltInCategory.OST_ReferenceLines, # reference lines
            rdb.BuiltInCategory.OST_CLines,     # reference planes
            rdb.BuiltInCategory.OST_ImportObjectStyles] # import in families
        )
        for oCat in otherCats:
            lStyle = rPat.GetLinePatternFromCategory (oCat, doc)
            # update dictionary
            self._add_category_to_dic(linePatternIdsToCategories, lStyle[rPat.PROPERTY_PATTERN_ID], oCat)
        
        return linePatternIdsToCategories


    def _get_pattern_from_level_element(self, doc):
        '''
        Gets the pattern data from all level types in document.

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document

        :return: a dictionary in format: Key: line Pattern Id, value list of levels using that line pattern
        :rtype: {ElementId:[Autodesk.revit.DB.Category]}
        '''
        
        levelPatternData = {}
        levels = rLevel.GetLevelsListAscending(doc)
        for level in levels:
            patternData = rPat.GetLinePatternFromLevelElement(doc, level)
            self._add_category_to_dic(levelPatternData, patternData[rPat.PROPERTY_PATTERN_ID], level)
        return levelPatternData

    def _get_pattern_name(self, element):
        '''
        Get the element name.

        :param element: _description_
        :type element: _type_
        :return: Element name, or exception stating name is not unicode
        :rtype: str
        '''

        elementName = 'unknown_notUnicode'
        try:   
            elementName = util.EncodeAscii(rdb.Element.Name.GetValue(element))
        except Exception as ex:
            elementName = elementName + ' Exception: ' + str(ex)
        return elementName

    def _get_pattern_usage_data_from_categories(self, line_pattern_ids, element):
        '''
        Returns how often and on which category a line pattern is used

        :param linePatternIds: a dictionary in format: Key: line Pattern Id, value list of categories using that line pattern
        :type linePatternIds: {ElementId:[Autodesk.revit.DB.Category]}
        :param element: The line pattern element.
        :type element: _type_
        
        :return: counter and  a list of dictionaries in format {categoryId: int, categoryName: str}
        :rtype: int, [{categoryId:int, categoryName:str}]
        '''

        counter = 0
        patternNames = []
        # how often used
        if (element.Id in line_pattern_ids):
            counter = len(line_pattern_ids[element.Id])
            for pat in  line_pattern_ids[element.Id]:
                patternNames.append({"categoryId" : pat.Id.IntegerValue, "categoryName" : pat.Name})
        return counter, patternNames

    def _get_pattern_usage_data_from_level(self, line_pattern_ids, element):
        '''
        Returns how often and on which Level type a line pattern is used

        :param linePatternIds: 
        :type linePatternIds: {ElementId:[Autodesk.revit.DB.Category]}
        :param element: The line pattern element.
        :type element: _type_
        
        :return: counter and  a list of dictionaries in format {categoryId: int, categoryName: str}
        :rtype: int, [{categoryId:int, categoryName:str}]
        '''

        counter = 0
        patternNames = []

        # how often used
        if (element.Id in line_pattern_ids):
            counter = len(line_pattern_ids[element.Id])
            for pat in  line_pattern_ids[element.Id]:
                patternNames.append({"levelId" : pat.Id.IntegerValue, "levelTypeName" : rdb.Element.Name.GetValue(pat)})
        return counter, patternNames

    def process(self, doc):
        '''
        Collects all line pattern data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        '''

        # get all line patterns used in categories (includes sub categories of family category and any custom subcategories of non family category present, includes also 
        # ref planes , ref lines, import styles)
        linePatternIdsByCategory = self._get_line_pattern_from_categories(doc)
        # get line pattern used on level element
        linePatternIdsByFromLevel = self._get_pattern_from_level_element(doc)

        collector = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement)
        for element in collector:
            # just in case parameter name is not unicode
            elementName = self._get_pattern_name(element)
            # get usage data from categories
            counter, patternNames = self._get_pattern_usage_data_from_categories(linePatternIdsByCategory, element)
            # get usage data from levels
            counterLevel, patternNamesLevel = self._get_pattern_usage_data_from_level(linePatternIdsByFromLevel, element)
            
            # get overall count
            counter = counter + counterLevel
            # get overall usage data
            usageAll = patternNames + patternNamesLevel

            # build data
            self.data.append(
                {
                    IFamData.ROOT : self.root_path,
                    IFamData.ROOT_CATEGORY : self.root_category_path,
                    IFamData.FAMILY_NAME : self._strip_file_extension(doc.Title),
                    IFamData.FAMILY_FILE_PATH : doc.PathName,
                    IFamData.USAGE_COUNTER : counter,
                    IFamData.USED_BY : usageAll,
                    PATTERN_NAME : elementName,
                    PATTERN_ID : element.Id.IntegerValue
                }
            )
    
    def get_data(self):
        return self.data
