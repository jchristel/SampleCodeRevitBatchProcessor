'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family category data class.
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

from duHast.APISamples import IFamilyData as IFamData
from duHast.Utilities import Utility as util
from duHast.APISamples import RevitCategories as rCat

# import Autodesk
#import Autodesk.Revit.DB as rdb

# data dictionary key values specific to this class
CATEGORY_NAME = 'categoryName'
SUB_CATEGORY_NAME = 'subCategoryName'
SUB_CATEGORY_ID = 'subCategoryId' 
GRAPHIC_PROPERTY_KEY_PREFIX = 'graphicProperty'
GRAPHIC_PROPERTY_KEY_PREFIX_DELIMITER = '_'

class CategoryData(IFamData.IFamilyData):
    
    def __init__(self, rootPath=None, rootCategoryPath=None, dataType=None):
        '''
        Class constructor

        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param dataType: Human readable data type descriptor
        :type dataType: str
        '''
        # todo: check inheritance!!
        # super(CategoryData, self).__init__(rootPath, dataType)

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


    def add_Data(self,root, rootCategoryPath, famName, famPath, useCounter, usedBy, famCatName, subCatName, subCatId, catGraStyleThreeD,
        catGraStyleCut, catGraStylePro, propMatName, propMatId, propLineWeightCutName, propLineWeightProjectionName, propLineColRed, propLineColGreen, propLineColBlue):
        
        dic = {
            IFamData.ROOT: root,
            IFamData.ROOT_CATEGORY: rootCategoryPath,
            IFamData.FAMILY_NAME: famName,
            IFamData.FAMILY_FILE_PATH : famPath,
            IFamData.USAGE_COUNTER: useCounter,
            IFamData.USED_BY : usedBy,
            CATEGORY_NAME : famCatName,
            SUB_CATEGORY_NAME : subCatName,
            SUB_CATEGORY_ID : subCatId,
            rCat.CATEGORY_GRAPHIC_STYLE_3D : catGraStyleThreeD,
            rCat.CATEGORY_GRAPHIC_STYLE_CUT : catGraStyleCut,
            rCat.CATEGORY_GRAPHIC_STYLE_PROJECTION : catGraStylePro,
            rCat.PROPERTY_MATERIAL_NAME : propMatName,
            rCat.PROPERTY_MATERIAL_ID : propMatId,
            rCat.PROPERTY_LINE_WEIGHT_CUT_NAME : propLineWeightCutName,
            rCat.PROPERTY_LINE_WEIGHT_PROJECTION_NAME : propLineWeightProjectionName,
            rCat.PROPERTY_LINE_COLOUR_RED_NAME : propLineColRed,
            rCat.PROPERTY_LINE_COLOUR_GREEN_NAME : propLineColGreen,
            rCat.PROPERTY_LINE_COLOUR_BLUE_NAME : propLineColBlue
            }

        self.data.append(dic)
    
    def _createData(self,root, rootCategoryPath, famName, famPath, useCounter, usedBy, famCatName, subCatName, subCatId, categoryGraphicProperties):
        '''
        Generates dictionary object from data past in.

        CategoryGraphicProperties will be flattened with prefix 'graphicProperty'

        :param root: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type root: str
        :param famName: The family name
        :type famName: str
        :param famPath: The family saved file path
        :type famPath: str
        :param useCounter: Counter of how many objects in the family are of this category
        :type useCounter: int
        :param usedBy: List of element ids of elements of this category.
        :type usedBy: [Autodesk.Revit.DB.ElementId]
        :param famCatName: The families category.
        :type famCatName: str
        :param subCatName: The subcategory name.
        :type subCatName: str
        :param subCatId: The subcategory id.
        :type subCatId: Autodesk.Revit.DB.ElementId
        :param categoryGraphicProperties: List of dictionaries describing the graphic properties of this category.
        :type categoryGraphicProperties: [dict]
        
        :return: A flatt dictionary describing key values and properties of a category.
        :rtype: dict
        '''

        dic = {
            IFamData.ROOT: root,
            IFamData.ROOT_CATEGORY: rootCategoryPath,
            IFamData.FAMILY_NAME: famName,
            IFamData.FAMILY_FILE_PATH : famPath,
            IFamData.USAGE_COUNTER: useCounter,
            IFamData.USED_BY : usedBy,
            CATEGORY_NAME : famCatName,
            SUB_CATEGORY_NAME : subCatName,
            SUB_CATEGORY_ID : subCatId
            }
        
        # flatten dictionary
        for  d in categoryGraphicProperties:
            dummy = util.flatten(d, GRAPHIC_PROPERTY_KEY_PREFIX, GRAPHIC_PROPERTY_KEY_PREFIX_DELIMITER)
            dic.update(dummy)

        return dic

    def _buildData(self, mainSubCats, mainCatName, doc):
        '''
        Extracts for each category past in, its properties and usage and adds that data to class property .data

        :param mainSubCats: List of sub categories to be processed.
        :type mainSubCats: [Autodesk.Revit.DB.Category]
        :param mainCatName: The parent category name.
        :type mainCatName: str
        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        '''

        # get usage of each main sub category
        for key,subCat in mainSubCats.items():
            # get elements using category
            elementDic = rCat.GetElementsByCategory(doc, subCat)
            # get category property
            catProps = rCat.GetCategoryProperties(subCat, doc)
            # add element counter for 3D, Cut, Elevation style
            useCounter = 0
            for key in elementDic:
                useCounter = useCounter + len (elementDic[key])        
            # add element ids integer value in 3D, Cut, Elevation style
            usedByIds = []
            for key in elementDic:
                for id in elementDic[key]:
                    usedByIds.append(id.IntegerValue)

            # build data dictionary   
            dic = self._createData(
                self.rootPath,
                self.rootCategoryPath,
                self._stripFileExtension(doc.Title),
                doc.PathName,
                useCounter,
                usedByIds,
                mainCatName,
                subCat.Name,
                subCat.Id.IntegerValue,
                catProps
            )
            self.data.append(dic)

    def _buildDataNonMainSubCats(self, mainSubCats, mainCatName, doc):
        '''
        Extracts for each category past in, its properties and usage and adds that data to class property .data

        :param mainSubCats: List of sub categories to be processed.
        :type mainSubCats: [Autodesk.Revit.DB.Category]
        :param mainCatName: The parent category name.
        :type mainCatName: str
        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        '''

        # get usage of each main sub category
        for key,subCat in mainSubCats.items():
            # set up an empty dic for any sub category not belonging to the main category (no elements in this family can be on those)
            # Exception: the only elements will be Imports and reference planes
            elementDic = {}
            if(mainCatName == 'Imports in Families' or mainCatName == 'Reference Planes'):
                # get elements using category
                elementDic = rCat.GetElementsByCategory(doc, subCat)
            # get category property
            catProps = rCat.GetCategoryProperties(subCat, doc)
            # add element counter for 3D, Cut, Elevation style
            useCounter = 0
            for key in elementDic:
                useCounter = useCounter + len (elementDic[key])        
            # add element ids integer value in 3D, Cut, Elevation style
            usedByIds = []
            for key in elementDic:
                for id in elementDic[key]:
                    usedByIds.append(id.IntegerValue)

            # build data dictionary   
            dic = self._createData(
                self.rootPath,
                self.rootCategoryPath,
                self._stripFileExtension(doc.Title),
                doc.PathName,
                useCounter,
                usedByIds,
                mainCatName,
                subCat.Name,
                subCat.Id.IntegerValue,
                catProps
            )
            self.data.append(dic)

    def process(self, doc):
        '''
        Collects all category data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        '''

        # get the family category name:
        famCatName = list(rCat.GetFamilyCategory(doc))[0]
        # get all sub categories of the family category
        mainSubCats = rCat.GetMainSubCategories(doc)
        # get all sub categories of non family category with a positive Id (indicates a custom category)
        # this include imported element categories
        otherCustomSubCats = rCat.GetOtherCustomSubCategories(doc)
        # get usage of each main sub category
        self._buildData(mainSubCats, famCatName, doc)
         # add any other sub category if exist
        if(len(otherCustomSubCats) > 0):
            for categoryKey, otherSubMainCat in otherCustomSubCats.items():
                if(len(otherSubMainCat) > 0):
                    # get usage of each other sub category
                    self._buildDataNonMainSubCats(otherSubMainCat, categoryKey, doc)
        
    def get_Data(self):
        return self.data
