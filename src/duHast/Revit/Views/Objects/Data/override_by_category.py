"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class used to store category overrides.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Stores common overrides between categories and filters

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

from duHast.Revit.Views.Objects.Data.override_by_base import OverrideByBase


class OverrideByCategory(OverrideByBase):
    data_type = "override_by_category"

    def __init__(
        self, main_category_name="", sub_category_name="", category_id=-1, j=None
    ):
        """
        Class constructor.

        """

        super(OverrideByCategory, self).__init__(data_type=self.data_type, j=j)

        # set defaults ( note other properties are set in base class!)
        self.main_category_name = main_category_name
        self.sub_category_name = sub_category_name
        self.category_id = category_id
        self.detail_level = -1  # not sure this works

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
                self.detail_level = j["detail_level"]
                # self.are_overrides_present = j["are_overrides_present"]
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        OverrideByCategory.data_type, e
                    )
                )

    def compare_overrides(self, other):
        """
        Ignores visibility property when comparing!

        :param other: _description_
        :type other: _type_
        :return: _description_
        :rtype: _type_
        """
        return isinstance(other, OverrideByCategory) and (
            self.halftone,
            self.transparency,
            self.override_projection,
            self.override_cut,
            self.detail_level,
        ) == (
            other.halftone,
            other.transparency,
            other.override_projection,
            other.override_cut,
            other.detail_level,
        )

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of OverrideByBase base class
        :type other: :class:`.OverrideByBase`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, OverrideByCategory) and (
            self.halftone,
            self.transparency,
            self.is_visible,
            self.override_projection,
            self.override_cut,
            self.detail_level,
            self.are_overrides_present,
        ) == (
            other.halftone,
            other.transparency,
            other.is_visible,
            other.override_projection,
            other.override_cut,
            other.detail_level,
            other.are_overrides_present,
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
                    self.halftone,
                    self.transparency,
                    self.is_visible,
                    self.override_projection,
                    self.override_cut,
                    self.detail_level,
                    self.are_overrides_present,
                )
            )
        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} with values: halftone:{}, transparency: {}, is visible: {}, projection: {}, cut: {}, detail level: {}, are overrides present: {}".format(
                    e,
                    self.data_type,
                    self.halftone,
                    self.transparency,
                    self.is_visible,
                    self.override_projection,
                    self.override_cut,
                    self.detail_level,
                    self.are_overrides_present,
                )
            )
