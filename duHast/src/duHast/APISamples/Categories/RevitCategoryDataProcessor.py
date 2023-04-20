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

from duHast.APISamples.Family.Reporting.IFamilyProcessor import IFamilyProcessor
from duHast.APISamples.Categories import RevitCategoryData as rCatData
from duHast.APISamples.Family.Reporting import IFamilyData as IFamData
from duHast.Utilities import Result as res
from duHast.APISamples.Categories.Utility import RevitCategoryPropertyNames as rCatPropNames

class CategoryProcessor(IFamilyProcessor):

    def __init__(self, pre_actions = None, post_actions = None):
        '''
        Class constructor.
        '''

        # setup report header
        key_prefix = rCatData.GRAPHIC_PROPERTY_KEY_PREFIX + rCatData.GRAPHIC_PROPERTY_KEY_PREFIX_DELIMITER
        string_report_headers = [
            IFamData.ROOT,
            IFamData.ROOT_CATEGORY,
            IFamData.FAMILY_NAME,
            IFamData.FAMILY_FILE_PATH,
            IFamData.USAGE_COUNTER,
            IFamData.USED_BY,
            rCatData.CATEGORY_NAME,
            rCatData.SUB_CATEGORY_NAME,
            rCatData.SUB_CATEGORY_ID,
            key_prefix + rCatPropNames.CATEGORY_GRAPHIC_STYLE_3D,
            key_prefix + rCatPropNames.CATEGORY_GRAPHIC_STYLE_CUT,
            key_prefix + rCatPropNames.CATEGORY_GRAPHIC_STYLE_PROJECTION,
            key_prefix + rCatPropNames.PROPERTY_MATERIAL_NAME,
            key_prefix + rCatPropNames.PROPERTY_MATERIAL_ID,
            key_prefix + rCatPropNames.PROPERTY_LINE_WEIGHT_CUT_NAME,
            key_prefix + rCatPropNames.PROPERTY_LINE_WEIGHT_PROJECTION_NAME,
            key_prefix + rCatPropNames.PROPERTY_LINE_COLOUR_RED_NAME,
            key_prefix + rCatPropNames.PROPERTY_LINE_COLOUR_GREEN_NAME,
            key_prefix + rCatPropNames.PROPERTY_LINE_COLOUR_BLUE_NAME
        ]

        # store data type  in base class
        super(CategoryProcessor, self).__init__(
            pre_actions=pre_actions, 
            post_actions=[self._post_action_update_used_subcategories], 
            data_type='Category', 
            string_report_headers=string_report_headers
        )

        #self.data = []
        #self.dataType = 'Category'

        # list of corner cases when it comes to category checking: imports in families or Reference planes ... ( english language specific!! )
        self.category_check_corner_cases = [
            'Imports in Families',
            'Reference Planes'
        ]

        #self.preActions = preActions
        # set default post action to updated categories used in root processor with any categories found in nested 
        # families
        #self.postActions = [self._postActionUpdateUsedSubcategories]
        # add any other post actions
        if (post_actions != None):
            for p_action in post_actions:
                self.post_actions.append(p_action)

    def process(self, doc, root_path, root_category_path):
        '''
        Calls processor instance with the document and root path provided and adds processor instance to class property .data

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :param root_path: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type root_path: str
        :param root_category_path: The category path of the nested family in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type root_category_path: str
        '''

        dummy = rCatData.CategoryData(root_path, root_category_path, self.data_type)
        dummy.process(doc)
        self.data.append(dummy)
    
    # --------------------------------------------- post action ----------------------------------------------------------

    def _add_data(self, processor, root, root_category_path, fam_name, fam_path, use_counter, used_by, fam_cat_name, sub_cat_name, sub_cat_id, cat_gra_style_three_d,
        cat_gra_style_cut, cat_gra_style_pro, prop_mat_name, prop_mat_id, prop_line_weight_cut_name, prop_line_weight_projection_name, prop_line_col_red, prop_line_col_green, prop_line_col_blue):
        
        processor.add_Data(
            root,
            root_category_path, 
            fam_name, 
            fam_path, 
            use_counter, 
            used_by, 
            fam_cat_name, 
            sub_cat_name, 
            sub_cat_id,
            cat_gra_style_three_d,
            cat_gra_style_cut,
            cat_gra_style_pro,
            prop_mat_name,
            prop_mat_id,
            prop_line_weight_cut_name,
            prop_line_weight_projection_name,
            prop_line_col_red,
            prop_line_col_green,
            prop_line_col_blue)
        

    def _is_sub_category_present(self,root_family_data, nested_family_sub_category):
        match = None
        # check whether sub category is present
        for root_fam in root_family_data:
            if (root_fam[rCatData.CATEGORY_NAME] == nested_family_sub_category[rCatData.CATEGORY_NAME] and root_fam[rCatData.SUB_CATEGORY_NAME] == nested_family_sub_category[rCatData.SUB_CATEGORY_NAME]):
                match = root_fam
                break
        return match

    def _update_root_family_data(self, root_family_data, nested_families_sub_categories):
        # loop over nested family subcategory data
        for nested_sub_category in nested_families_sub_categories:
            # check if sub category is already in root family
            matching_root_fam_category = self._is_sub_category_present(root_family_data, nested_sub_category)
            if(matching_root_fam_category != None):
                # update used by list
                if(nested_sub_category[IFamData.FAMILY_NAME] not in matching_root_fam_category[IFamData.USED_BY]):
                    # add the root path to the used by list for ease of identification of the origin of this subcategory usage
                    matching_root_fam_category[IFamData.USED_BY].append(nested_sub_category[IFamData.ROOT])
                    # update used by counter
                    matching_root_fam_category[IFamData.USAGE_COUNTER] = matching_root_fam_category[IFamData.USAGE_COUNTER] + 1
            else:
                pass
                # nothing to do if that category has not been reported to start off with 
                # this category could, for example, belong to the section marker family present in most 3d families

    def _get_used_subcategories(self, data):
        used_subcategories = []
        for d in data:
            if(d[IFamData.USAGE_COUNTER] > 0):
                # get the family category
                category_path = d[IFamData.ROOT_CATEGORY].split(' :: ')
                # which is the last entry in the root category path
                category = category_path[len(category_path)-1]
                # select only items which either belong to the category of the family or 
                # are corner cases like imports in families or Reference planes ... ( english language specific!! )
                if (category == d[rCatData.CATEGORY_NAME] or d[rCatData.CATEGORY_NAME] in self.category_check_corner_cases):
                    used_subcategories.append(d)
        return used_subcategories

    def _post_action_update_used_subcategories(self, doc):
        return_value = res.Result()
        try:
            # find all subcategories of nested families
            nested_family_data = self._find_nested_families_data()
            # get used sub categories from nested data
            nested_family_used_sub_categories = self._get_used_subcategories(nested_family_data)
            # update root family data only
            root_family_data = self._find_root_family_data()
            # update root processor data as required
            self._update_root_family_data(root_family_data, nested_family_used_sub_categories)
            return_value.update_sep(True, 'Post Action Update subcategories data successful completed.')
        except Exception as e:
            return_value.update_sep(False, 'Post Action Update subcategories data failed with exception: {}'.format(e))
        return return_value