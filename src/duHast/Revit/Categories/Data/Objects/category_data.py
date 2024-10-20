"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family category data class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from duHast.Revit.Family.Data.Objects import ifamily_data as IFamData
from duHast.Revit.Categories import categories as rCat
from duHast.Revit.Categories.Utility import category_properties_get_utils as rCatPropGet
from duHast.Revit.Categories.Utility import (
    elements_by_category_utils as rElementByCatUtils,
)
from duHast.Revit.Categories.Data.Objects.category_data_storage import (
    FamilyCategoryDataStorage,
)
from duHast.Revit.Categories.Data.Objects.category_data_storage_used_by import (
    FamilyCategoryDataStorageUsedBy,
)

# data dictionary key values specific to this class
CATEGORY_NAME = "categoryName"
SUB_CATEGORY_NAME = "subCategoryName"
SUB_CATEGORY_ID = "subCategoryId"
GRAPHIC_PROPERTY_KEY_PREFIX = "graphicProperty"
GRAPHIC_PROPERTY_KEY_PREFIX_DELIMITER = "_"

from duHast.Revit.Categories.Utility.category_property_names import (
    CATEGORY_GRAPHIC_STYLE_3D,
    CATEGORY_GRAPHIC_STYLE_CUT,
    CATEGORY_GRAPHIC_STYLE_PROJECTION,
    PROPERTY_LINE_COLOUR_BLUE_NAME,
    PROPERTY_LINE_COLOUR_GREEN_NAME,
    PROPERTY_LINE_COLOUR_RED_NAME,
    PROPERTY_LINE_WEIGHT_CUT_NAME,
    PROPERTY_LINE_WEIGHT_PROJECTION_NAME,
    PROPERTY_MATERIAL_ID,
    PROPERTY_MATERIAL_NAME,
)


class CategoryData(IFamData.IFamilyData):
    def __init__(self, root_path=None, root_category_path=None):
        """
        Class constructor

        :param root_path: The path of the nested family in a tree: rootFamilyName :: nestedFamilyNameOne :: nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type root_path: str
        :param root_category_path: The category path of the nested family in a tree: rootFamilyCategory :: nestedFamilyOneCategory :: nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type root_category_path: str
        """

        # store data type  in base class
        super(CategoryData, self).__init__(
            root_path=root_path,
            root_category_path=root_category_path,
        )

    def _create_data(
        self,
        root,
        root_category_path,
        fam_name,
        fam_path,
        use_counter,
        used_by,
        fam_cat_name,
        sub_cat_name,
        sub_cat_id,
        category_graphic_properties,
    ):
        """
        Generates dictionary object from data past in.

        CategoryGraphicProperties will be flattened with prefix 'graphicProperty'

        :param root: The path of the nested family in a tree: rootFamilyName :: nestedFamilyNameOne :: nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type root: str
        :param root_category_path: The path of the nested family in a tree of categories. This includes the actual family category as the last node.
        :type root_category_path: str
        :param fam_name: The family name
        :type fam_name: str
        :param fam_path: The family saved file path
        :type fam_path: str
        :param use_counter: Counter of how many objects in the family are of this category
        :type use_counter: int
        :param used_by: List of element ids of elements of this category.
        :type used_by: [Autodesk.Revit.DB.ElementId]
        :param fam_cat_name: The families category.
        :type fam_cat_name: str
        :param sub_cat_name: The subcategory name.
        :type sub_cat_name: str
        :param sub_cat_id: The subcategory id.
        :type sub_cat_id: Autodesk.Revit.DB.ElementId
        :param category_graphic_properties: List of dictionaries describing the graphic properties of this category.
        :type category_graphic_properties: [dict]
        
        :return: A flatt dictionary describing key values and properties of a category.
        :rtype: dict
        """

        used_by_list = []
        for id in used_by:
            dummy = FamilyCategoryDataStorageUsedBy(
                family_name=fam_name,
                element_id=id,
            )
            used_by_list.append(dummy)

        # make sure to get a value for the file path which is not empty if the document has not been saved
        if fam_path == "":
            fam_path = "-"

        dummy = FamilyCategoryDataStorage(
            root_name_path=root,
            root_category_path=root_category_path,
            family_name=fam_name,
            family_file_path=fam_path,
            use_counter=use_counter,
            used_by=used_by_list,  # assign used by list
            category_name=fam_cat_name,
            sub_category_name=sub_cat_name,
            sub_category_id=sub_cat_id,
            category_graphics_style_three_d=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[CATEGORY_GRAPHIC_STYLE_3D],
            )[
                0
            ],
            category_graphics_style_cut=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[CATEGORY_GRAPHIC_STYLE_CUT],
            )[0],
            category_graphics_style_projection=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[CATEGORY_GRAPHIC_STYLE_PROJECTION],
            )[
                0
            ],
            property_material_name=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[PROPERTY_MATERIAL_NAME],
            )[0],
            property_material_id=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[PROPERTY_MATERIAL_ID],
            )[0],
            property_line_weight_cut_name=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[PROPERTY_LINE_WEIGHT_CUT_NAME],
            )[
                0
            ],
            property_line_weight_projection_name=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[PROPERTY_LINE_WEIGHT_PROJECTION_NAME],
            )[
                0
            ],
            property_line_colour_red_name=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[PROPERTY_LINE_COLOUR_RED_NAME],
            )[
                0
            ],
            property_line_colour_green_name=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[PROPERTY_LINE_COLOUR_GREEN_NAME],
            )[
                0
            ],
            property_line_colour_blue=rCatPropGet.get_saved_category_property_by_name(
                properties=category_graphic_properties,
                prop_names=[PROPERTY_LINE_COLOUR_BLUE_NAME],
            )[0],
        )

        return dummy

    def _build_data(self, main_sub_cats, main_cat_name, doc):
        """
        Extracts for each category past in, its properties and usage and adds that data to class property .data

        :param main_sub_cats: List of sub categories to be processed.
        :type main_sub_cats: [Autodesk.Revit.DB.Category]
        :param main_cat_name: The parent category name.
        :type main_cat_name: str
        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        """

        # get usage of each main sub category
        for key, subCat in main_sub_cats.items():
            # get elements using category
            element_dic = rElementByCatUtils.get_elements_by_category(doc, subCat)
            # get category property
            cat_props = rCatPropGet.get_category_properties(subCat, doc)

            # add element counter for 3D, Cut, Elevation style
            use_counter = 0
            used_by_ids = []
            for key_elements in element_dic:
                # update usage counter
                use_counter = use_counter + len(element_dic[key_elements])
                # add element ids integer value in 3D, Cut, Elevation style
                for id in element_dic[key_elements]:
                    used_by_ids.append(id.IntegerValue)

            # build data dictionary
            storage = self._create_data(
                self.root_path,
                self.root_category_path,
                self._strip_file_extension(doc.Title),
                doc.PathName,
                use_counter,
                used_by_ids,
                main_cat_name,
                subCat.Name,
                subCat.Id.IntegerValue,
                cat_props,
            )
            self.add_data(storage_instance=storage)

    def _build_data_non_main_sub_cats(self, main_sub_cats, main_cat_name, doc):
        """
        Extracts for each category past in, its properties and usage and adds that data to class property .data

        :param  main_sub_cats: List of sub categories to be processed.
        :type  main_sub_cats: [Autodesk.Revit.DB.Category]
        :param main_cat_name: The parent category name.
        :type main_cat_name: str
        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        """

        # get usage of each main sub category
        for key, sub_category in main_sub_cats.items():
            # set up an empty dic for any sub category not belonging to the main category (no elements in this family can be on those)
            # Exception: the only elements will be Imports and reference planes
            element_dic = {}
            if (
                main_cat_name == "Imports in Families"
                or main_cat_name == "Reference Planes"
            ):
                # get elements using category
                element_dic = rElementByCatUtils.get_elements_by_category(
                    doc, sub_category
                )
            # get category property
            cat_props = rCatPropGet.get_category_properties(sub_category, doc)
            # add element counter for 3D, Cut, Elevation style
            use_counter = 0
            for key in element_dic:
                use_counter = use_counter + len(element_dic[key])
            # add element ids integer value in 3D, Cut, Elevation style
            used_by_ids = []
            for key in element_dic:
                for id in element_dic[key]:
                    used_by_ids.append(id.IntegerValue)

            # build data dictionary
            storage = self._create_data(
                self.root_path,
                self.root_category_path,
                self._strip_file_extension(doc.Title),
                doc.PathName,
                use_counter,
                used_by_ids,
                main_cat_name,
                sub_category.Name,
                sub_category.Id.IntegerValue,
                cat_props,
            )
            self.add_data(storage_instance=storage)

    def process(self, doc):
        """
        Collects all category data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        """

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
        if len(other_custom_sub_cats) > 0:
            for category_key, otherSubMainCat in other_custom_sub_cats.items():
                if len(otherSubMainCat) > 0:
                    # get usage of each other sub category
                    self._build_data_non_main_sub_cats(
                        otherSubMainCat, category_key, doc
                    )

    def get_data(self):
        return self.data

    def add_data(self, storage_instance):
        if isinstance(storage_instance, FamilyCategoryDataStorage):
            self.data.append(storage_instance)
        else:
            raise ValueError(
                "storage instance must be an instance of FamilyCategoryDataStorage"
            )
