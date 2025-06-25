# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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


from duHast.Utilities.Objects.base import Base

from pushIt_associated.push_it_family_property import PushItFamilyProperty
from duHast.Revit.Common.Objects.design_set_property_names import DesignSetPropertyNames

class PushItFamilyInstance(Base):

    def __init__(self):
        """
        Class constructor.

        Contains the properties of a family instance in Revit.
        """

        super(PushItFamilyInstance, self).__init__()

        self.revit_element_id_integer_value = -1
        self.properties = []
        self.location_point = None
        self.centroid = None
        self.placement_level_name = None
        self.design_set_option_info = None


    def add_property(self, property):
        """
        Add a property to the family instance.

        :param property: The property to add.
        :type property: :class:`.PushItFamilyProperty`
        """

        if not isinstance(property, PushItFamilyProperty):
            raise TypeError("property must be an instance of PushItFamilyProperty")
        
        self.properties.append(property)
    
    def set_location_point(self, location_x, location_y, location_z):
        """
        Set the location point of the family instance.

        :param location_point: The location point to set.
        :type location_point: :class:`Autodesk.Revit.DB.XYZ`
        """

        self.location_point = (location_x, location_y, location_z)

    def set_centroid(self, centroid_x, centroid_y, centroid_z):
        """
        Set the centroid of the family instance.

        :param centroid: The centroid to set.
        :type centroid: :class:`Autodesk.Revit.DB.XYZ`
        """

        self.centroid = (centroid_x, centroid_y, centroid_z)

    def set_design_set_option_info_value(self, value):
        """
        Set the design set option info value of the family instance.

        :param value: The design set option info value to set.
        :type value: str
        """

        self.design_set_option_info = value

    def get_ui_name(self, key_id_property_guid=None):
        """
        Get the UI name of the family instance.

        :return: The UI name of the family instance.
        :rtype: str
        """

        key = ""
        level_name = ""

        if (self.placement_level_name is not None ):
            level_name = self.placement_level_name
            if level_name != "":
                level_name = " on Level: {}".format(level_name)


        if key_id_property_guid is not None:
            for property in self.properties:
                if property.parameter_guid == key_id_property_guid:
                    key = property.parameter_value
                    break

        if key == "":
            key = str(self.revit_element_id_integer_value)


        if self.design_set_option_info is not None:

            key_options = DesignSetPropertyNames.combine_set_and_option_name(set_name=self.design_set_option_info[DesignSetPropertyNames.DESIGN_SET_NAME], option_name=self.design_set_option_info[DesignSetPropertyNames.DESIGN_OPTION_NAME])

            return "{} {} ({}  [{}])".format(
                key,
                level_name,
                key_options,
                self.revit_element_id_integer_value,
                )
        else:
            return key