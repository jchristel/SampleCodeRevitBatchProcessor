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

from duHast.APISamples.Family.Reporting import IFamilyData as IFamData
from duHast.Utilities import Utility as util
from duHast.APISamples.Categories import RevitCategories as rCat
from duHast.APISamples.Categories.Utility import RevitCategoryPropertiesGetUtils as rCatPropGet
from duHast.APISamples.Categories.Utility import RevitCategoryPropertyNames as rCatPropNames
from duHast.APISamples.Categories.Utility import RevitElementsByCategoryUtils as rElementByCatUtils


# import Autodesk
#import Autodesk.Revit.DB as rdb

# data dictionary key values specific to this class
CATEGORY_NAME = 'categoryName'
SUB_CATEGORY_NAME = 'subCategoryName'
SUB_CATEGORY_ID = 'subCategoryId' 
GRAPHIC_PROPERTY_KEY_PREFIX = 'graphicProperty'
GRAPHIC_PROPERTY_KEY_PREFIX_DELIMITER = '_'

class CategoryData(IFamData.IFamilyData):
    
    def __init__(self, root_path=None, root_category_path=None, data_type=None):
        '''
        Class constructor

        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param dataType: Human readable data type descriptor
        :type dataType: str
        '''

        # store data type  in base class
        super(CategoryData, self).__init__(root_path=root_path, root_category_path=root_category_path, data_type=data_type)
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

    def add_data(self,root, root_category_path, fam_name, fam_path, use_counter, used_by, fam_cat_name, sub_cat_name, sub_cat_id, cat_gra_style_three_d,
        cat_gra_style_cut, cat_gra_style_pro, prop_mat_name, prop_mat_id, prop_line_weight_cut_name, prop_line_weight_projection_name, prop_line_col_red, prop_line_col_green, prop_line_col_blue):
        
        dic = {
            IFamData.ROOT: root,
            IFamData.ROOT_CATEGORY: root_category_path,
            IFamData.FAMILY_NAME: fam_name,
            IFamData.FAMILY_FILE_PATH : fam_path,
            IFamData.USAGE_COUNTER: use_counter,
            IFamData.USED_BY : used_by,
            CATEGORY_NAME : fam_cat_name,
            SUB_CATEGORY_NAME : sub_cat_name,
            SUB_CATEGORY_ID : sub_cat_id,
            rCatPropNames.CATEGORY_GRAPHIC_STYLE_3D : cat_gra_style_three_d,
            rCatPropNames.CATEGORY_GRAPHIC_STYLE_CUT : cat_gra_style_cut,
            rCatPropNames.CATEGORY_GRAPHIC_STYLE_PROJECTION : cat_gra_style_pro,
            rCatPropNames.PROPERTY_MATERIAL_NAME : prop_mat_name,
            rCatPropNames.PROPERTY_MATERIAL_ID : prop_mat_id,
            rCatPropNames.PROPERTY_LINE_WEIGHT_CUT_NAME : prop_line_weight_cut_name,
            rCatPropNames.PROPERTY_LINE_WEIGHT_PROJECTION_NAME : prop_line_weight_projection_name,
            rCatPropNames.PROPERTY_LINE_COLOUR_RED_NAME : prop_line_col_red,
            rCatPropNames.PROPERTY_LINE_COLOUR_GREEN_NAME : prop_line_col_green,
            rCatPropNames.PROPERTY_LINE_COLOUR_BLUE_NAME : prop_line_col_blue
            }

        self.data.append(dic)
    
    def _create_data(self,root, root_category_path, fam_name, fam_path, use_counter, used_by, fam_cat_name, sub_cat_name, sub_cat_id, category_graphic_properties):
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
            IFamData.ROOT_CATEGORY: root_category_path,
            IFamData.FAMILY_NAME: fam_name,
            IFamData.FAMILY_FILE_PATH : fam_path,
            IFamData.USAGE_COUNTER: use_counter,
            IFamData.USED_BY : used_by,
            CATEGORY_NAME : fam_cat_name,
            SUB_CATEGORY_NAME : sub_cat_name,
            SUB_CATEGORY_ID : sub_cat_id
            }
        
        # flatten dictionary
        for  d in category_graphic_properties:
            dummy = util.flatten(d, GRAPHIC_PROPERTY_KEY_PREFIX, GRAPHIC_PROPERTY_KEY_PREFIX_DELIMITER)
            dic.update(dummy)

        return dic

    def _build_data(self, main_sub_cats, main_cat_name, doc):
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
        for key,subCat in main_sub_cats.items():
            # get elements using category
            element_dic = rElementByCatUtils.get_elements_by_category(doc, subCat)
            # get category property
            cat_props = rCatPropGet.get_category_properties(subCat, doc)
            # add element counter for 3D, Cut, Elevation style
            use_counter = 0
            for key in element_dic:
                use_counter = use_counter + len (element_dic[key])        
            # add element ids integer value in 3D, Cut, Elevation style
            used_by_ids = []
            for key in element_dic:
                for id in element_dic[key]:
                    used_by_ids.append(id.IntegerValue)

            # build data dictionary   
            dic = self._create_data(
                self.root_path,
                self.root_category_path,
                self._strip_file_extension(doc.Title),
                doc.PathName,
                use_counter,
                used_by_ids,
                main_cat_name,
                subCat.Name,
                subCat.Id.IntegerValue,
                cat_props
            )
            self.data.append(dic)

    def _build_data_non_main_sub_cats(self, main_sub_cats, main_cat_name, doc):
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
        for key,sub_category in main_sub_cats.items():
            # set up an empty dic for any sub category not belonging to the main category (no elements in this family can be on those)
            # Exception: the only elements will be Imports and reference planes
            element_dic = {}
            if(main_cat_name == 'Imports in Families' or main_cat_name == 'Reference Planes'):
                # get elements using category
                element_dic = rElementByCatUtils.get_elements_by_category(doc, sub_category)
            # get category property
            cat_props = rCatPropGet.get_category_properties(sub_category, doc)
            # add element counter for 3D, Cut, Elevation style
            use_counter = 0
            for key in element_dic:
                use_counter = use_counter + len (element_dic[key])        
            # add element ids integer value in 3D, Cut, Elevation style
            used_by_ids = []
            for key in element_dic:
                for id in element_dic[key]:
                    used_by_ids.append(id.IntegerValue)

            # build data dictionary   
            dic = self._create_data(
                self.root_path,
                self.root_category_path,
                self._strip_file_extension(doc.Title),
                doc.PathName,
                use_counter,
                used_by_ids,
                main_cat_name,
                sub_category.Name,
                sub_category.Id.IntegerValue,
                cat_props
            )
            self.data.append(dic)

    def process(self, doc):
        '''
        Collects all category data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        '''

        # get the family category name:
        fam_cat_name = list(rCat.get_family_category(doc))[0]
        # get all sub categories of the family category
        main_sub_cats = rCat.get_main_sub_categories(doc)
        # get all sub categories of non family category with a positive Id (indicates a custom category)
        # this include imported element categories
        other_custom_sub_cats = rCat.get_other_custom_sub_categories(doc)
        # get usage of each main sub category
        self._build_data(main_sub_cats, fam_cat_name, doc)
         # add any other sub category if exist
        if(len(other_custom_sub_cats) > 0):
            for category_key, otherSubMainCat in other_custom_sub_cats.items():
                if(len(otherSubMainCat) > 0):
                    # get usage of each other sub category
                    self._build_data_non_main_sub_cats(otherSubMainCat, category_key, doc)
        
    def get_data(self):
        return self.data
