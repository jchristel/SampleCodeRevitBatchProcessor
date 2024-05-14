"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family base data storage class.
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

from duHast.Revit.Family.Data.Objects import ifamily_data_storage as IFamDataStorage


class FamilyCategoryDataStorage(IFamDataStorage.IFamilyDataStorage):

    def __init__(
        self,
        data_type,
        root_name_path,
        root_category_path,
        family_name,
        family_file_path,
        use_counter,
        used_by,
        category_name,
        sub_category_name,
        sub_category_id,
        category_graphics_style_three_d,
        category_graphics_style_cut,
        category_graphics_style_projection,
        property_material_name,
        property_material_id,
        property_line_weight_cut_name,
        property_line_weight_projection_name,
        property_line_colour_red_name,
        property_line_colour_green_name,
        property_line_colour_blue,
        **kwargs
    ):

        # store args in base class
        super(FamilyCategoryDataStorage, self).__init__(
            data_type=data_type,
            root_name_path=root_name_path,
            root_category_path=root_category_path,
            family_name=family_name,
            family_file_path=family_file_path,
        )

        # store other args in this class
        self.use_counter = use_counter
        self.used_by = used_by
        self.category_name = category_name
        self.sub_category_name = sub_category_name
        self.sub_category_id = sub_category_id
        self.category_graphics_style_3d = category_graphics_style_three_d
        self.category_graphics_style_cut = category_graphics_style_cut
        self.category_graphics_style_projection = category_graphics_style_projection
        self.property_material_name = property_material_name
        self.property_material_id = property_material_id
        self.property_line_weight_cut_name = property_line_weight_cut_name
        self.property_line_weight_projection_name = property_line_weight_projection_name
        self.property_line_colour_red_name = property_line_colour_red_name
        self.property_line_colour_green_name = property_line_colour_green_name
        self.property_line_colour_blue_name = property_line_colour_blue

    def update_usage(self, other_storage):
        """
        Update the usage of this storage object with the usage of another storage object by:

        - adding the use counter of the other storage object to this storage object's use counter
        - appending the root name path of the other storage object to this storage object's used_by list
        
        """

        if (isinstance(other_storage, FamilyCategoryDataStorage)):
            self.use_counter = self.use_counter + other_storage.use_counter
            # rather than appending the ids of items using the category, just append the root name path of the family
            self.used_by.append(other_storage.root_name_path)
        else:
            raise ValueError("other_storage is not of type FamilyCategoryDataStorage but of type: {}".format(type(other_storage)))