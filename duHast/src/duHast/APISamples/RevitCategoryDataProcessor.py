'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family category data processor class.
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

from duHast.APISamples.IFamilyProcessor import IFamilyProcessor
from duHast.APISamples import RevitCategories as rCat
from duHast.APISamples import RevitCategoryData as rCatData
from duHast.APISamples import IFamilyData as IFamData
from duHast.Utilities import Result as res

class CategoryProcessor(IFamilyProcessor):

    def __init__(self, preActions = None, postActions = None):
        '''
        Class constructor.
        '''
        self.data = []
        self.dataType = 'Category'

        # list of corner cases when it comes to category checking: imports in families or Reference planes ... ( english language specific!! )
        self.CategoryCheckCornerCases = [
            'Imports in Families',
            'Reference Planes'
        ]

        keyPrefix = rCatData.GRAPHIC_PROPERTY_KEY_PREFIX + rCatData.GRAPHIC_PROPERTY_KEY_PREFIX_DELIMITER
        self.stringReportHeaders = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            IFamData.USAGE_COUNTER,
            IFamData.USED_BY,
            rCatData.CATEGORY_NAME,
            rCatData.SUB_CATEGORY_NAME,
            rCatData.SUB_CATEGORY_ID,
            keyPrefix + rCat.CATEGORY_GRAPHIC_STYLE_3D,
            keyPrefix + rCat.CATEGORY_GRAPHIC_STYLE_CUT,
            keyPrefix + rCat.CATEGORY_GRAPHIC_STYLE_PROJECTION,
            keyPrefix + rCat.PROPERTY_MATERIAL_NAME,
            keyPrefix + rCat.PROPERTY_MATERIAL_ID,
            keyPrefix + rCat.PROPERTY_LINE_WEIGHT_CUT_NAME,
            keyPrefix + rCat.PROPERTY_LINE_WEIGHT_PROJECTION_NAME,
            keyPrefix + rCat.PROPERTY_LINE_COLOUR_RED_NAME,
            keyPrefix + rCat.PROPERTY_LINE_COLOUR_GREEN_NAME,
            keyPrefix + rCat.PROPERTY_LINE_COLOUR_BLUE_NAME
        ]
        self.preActions = preActions
        # set default post action to updated categories used in root processor with any categories found in nested 
        # families
        self.postActions = [self._postActionUpdateUsedSubcategories]
        # add any other post actions
        if (postActions != None):
            for pAction in postActions:
                self.postActions.append(pAction)


    def process(self, doc, rootPath, rootCategoryPath):
        '''
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        '''

        dummy = rCatData.CategoryData(rootPath, rootCategoryPath, self.dataType)
        dummy.process(doc)
        self.data.append(dummy)
    
    # --------------------------------------------- post action ----------------------------------------------------------

    def _add_Data(self, processor, root, rootCategoryPath, famName, famPath, useCounter, usedBy, famCatName, subCatName, subCatId, catGraStyleThreeD,
        catGraStyleCut, catGraStylePro, propMatName, propMatId, propLineWeightCutName, propLineWeightProjectionName, propLineColRed, propLineColGreen, propLineColBlue):
        
        processor.add_Data(
            root,
            rootCategoryPath, 
            famName, 
            famPath, 
            useCounter, 
            usedBy, 
            famCatName, 
            subCatName, 
            subCatId,
            catGraStyleThreeD,
            catGraStyleCut,
            catGraStylePro,
            propMatName,
            propMatId,
            propLineWeightCutName,
            propLineWeightProjectionName,
            propLineColRed,
            propLineColGreen,
            propLineColBlue)
        

    def _isSubCategoryPresent(self,rootFamilyData, nestedFamilySubCategory):
        match = None
        # check whether sub category is present
        for rootFam in rootFamilyData:
            if (rootFam[rCatData.CATEGORY_NAME] == nestedFamilySubCategory[rCatData.CATEGORY_NAME] and rootFam[rCatData.SUB_CATEGORY_NAME] == nestedFamilySubCategory[rCatData.SUB_CATEGORY_NAME]):
                match = rootFam
                break
        return match

    def _updateRootFamilyData(self, rootFamilyData, nestedFamiliesSubCategories):
        # loop over nested family subcategory data
        for nestedSubCategory in nestedFamiliesSubCategories:
            # check if sub category is already in root family
            matchingRootFamCategory = self._isSubCategoryPresent(rootFamilyData, nestedSubCategory)
            if(matchingRootFamCategory != None):
                # update used by list
                if(nestedSubCategory[IFamData.FAMILY_NAME] not in matchingRootFamCategory[IFamData.USED_BY]):
                    # add the root path to the used by list for ease of identification of the origin of this subcategory usage
                    matchingRootFamCategory[IFamData.USED_BY].append(nestedSubCategory[IFamData.ROOT])
                    # update used by counter
                    matchingRootFamCategory[IFamData.USAGE_COUNTER] = matchingRootFamCategory[IFamData.USAGE_COUNTER] + 1
            else:
                pass
                # nothing to do if that category has not been reported to start off with 
                # this category could, for example, belong to the section marker family present in most 3d families

    def _getUsedSubcategories(self, data):
        usedSubcategories = []
        for d in data:
            if(d[IFamData.USAGE_COUNTER] > 0):
                # get the family category
                categoryPath = d[IFamData.ROOT_CATEGORY].split(' :: ')
                # which is the last entry in the root category path
                category = categoryPath[len(categoryPath)-1]
                # select only items which either belong to the category of the family or 
                # are corner cases like imports in families or Reference planes ... ( english language specific!! )
                if (category == d[rCatData.CATEGORY_NAME] or d[rCatData.CATEGORY_NAME] in self.CategoryCheckCornerCases):
                    usedSubcategories.append(d)
        return usedSubcategories

    def _postActionUpdateUsedSubcategories(self, doc):
        returnValue = res.Result()
        try:
            # find all subcategories of nested families
            nestedFamilyData = self._findNestedFamiliesData()
            # get used sub categories from nested data
            nestedFamilyUsedSubCategories = self._getUsedSubcategories(nestedFamilyData)
            # update root family data only
            rootFamilyData = self._findRootFamilyData()
            # update root processor data as required
            self._updateRootFamilyData(rootFamilyData, nestedFamilyUsedSubCategories)
            returnValue.UpdateSep(True, 'Post Action Update subcategories data successful completed.')
        except Exception as e:
            returnValue.UpdateSep(False, 'Post Action Update subcategories data failed with exception: ' + str(e))
        return returnValue