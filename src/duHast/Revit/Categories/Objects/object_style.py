"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class used to store category graphics styles.
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

import json

from duHast.Utilities.Objects import base
from duHast.Revit.Common.Objects.Data.line_projection import LineProjection
from duHast.Revit.Common.Objects.Data.line_cut import LineCut


class ObjectStyle(base.Base):
    def __init__(
        self,
        main_category_name="",
        sub_category_name="",
        category_id=-1,
        data_type="object_style",
        j=None,
        **kwargs
    ):
        """
        Class constructor.

        """

        super(ObjectStyle, self).__init__(**kwargs)
        # set defaults ( note other properties are set in base class!)
        self.data_type = data_type
        self.main_category_name = main_category_name
        self.sub_category_name = sub_category_name
        self.category_id = category_id
        self.data_type = data_type
        self.material_id = -1
        self.line_projection = LineProjection()
        self.line_cut = LineCut()

        # check if any data was past in with constructor!
        if j != None and len(j) > 0:
            # check type of data that came in:
            if type(j) == str:
                # a string
                j = json.loads(j)
            elif type(j) == dict:
                # no action required
                pass
            else:
                raise ValueError(
                    "Argument supplied must be of type string or type dictionary"
                )

            # load values and throw exception if something is missing!
            try:
                self.main_category_name = j["main_category_name"]
                self.sub_category_name = j["sub_category_name"]
                self.category_id = j["category_id"]
                self.material_id = j["material_id"]
                self.line_projection = LineProjection(j=j[LineProjection.data_type])
                self.line_cut = LineCut(j=j[LineCut.data_type])
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        "ObjectStyle.data_type", e
                    )
                )

    def compare_object_styles(self, other):
        """
        Ignores material property when comparing!

        :param other: An instance of ObjectStyle
        :type other: :class:`.ObjectStyle`
        :return: True if all graphical properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """
        return isinstance(other, ObjectStyle) and (
            self.line_projection,
            self.line_cut,
        ) == (
            other.line_projection,
            other.line_cut,
        )

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of ObjectStyle base class
        :type other: :class:`.ObjectStyle`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, ObjectStyle) and (
            self.line_projection,
            self.line_cut,
            self.material_id,
        ) == (
            other.line_projection,
            other.line_cut,
            other.material_id,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def __hash__(self):
        """
        Custom hash override

        Required due to custom __eq__ override present in this class
        """
        try:
            return hash(
                (
                    self.line_projection,
                    self.line_cut,
                    self.material_id,
                )
            )
        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} object style projection: {}, object style cut: {}, object style material id: {}".format(
                    e,
                    self.data_type,
                    self.line_projection,
                    self.line_cut,
                    self.material_id,
                )
            )

    def get_all_used_line_patterns(self):
        """
        Extract dictionary of line pattern names to line pattern objects

        :return: Dictionary of line pattern names to line pattern objects
        :rtype: {str: :class:`.LinePatternSettings`}
        """

        used_line_patterns = {}

        # from projection
        if self.line_projection.line_pattern_settings.name not in used_line_patterns:
            used_line_patterns[
                self.line_projection.line_pattern_settings.name
            ] = self.line_projection.line_pattern_settings

        # from cut
        if self.line_cut.line_pattern_settings.name not in used_line_patterns:
            used_line_patterns[
                self.line_cut.line_pattern_settings.name
            ] = self.line_cut.line_pattern_settings

        return used_line_patterns
