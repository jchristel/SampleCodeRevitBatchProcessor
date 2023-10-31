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


class OverrideByFilter(OverrideByBase):
    data_type = "override_by_filter"

    def __init__(self, filter_name="", filter_id=-1, j={}):
        """
        Class constructor.

        """

        super(OverrideByFilter, self).__init__(data_type=self.data_type, j=j)

        # set defaults
        self.filter_name = filter_name
        self.filter_id = filter_id
        self.is_enabled = True

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
                self.is_enabled = j["is_enabled"]
                self.filter_name = j["filter_name"]
                self.filter_id = j["filter_id"]
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        OverrideByFilter.data_type, e
                    )
                )

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of OverrideByBase base class
        :type other: :class:`.OverrideByBase`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, OverrideByFilter) and (
            self.halftone,
            self.transparency,
            self.is_visible,
            self.override_projection,
            self.override_cut,
            self.is_enabled,
            self.are_overrides_present,
        ) == (
            other.halftone,
            other.transparency,
            other.is_visible,
            other.override_projection,
            other.override_cut,
            other.is_enabled,
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
                    self.is_enabled,
                    self.override_projection,
                    self.override_cut,
                    self.are_overrides_present,
                )
            )

        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} with values: halftone:{}, transparency: {}, is visible: {}, override projection: {}, override cut: {},is enabled: {}, override is present: {}".format(
                    e,
                    self.data_type,
                    self.halftone,
                    self.transparency,
                    self.is_visible,
                    self.override_projection,
                    self.override_cut,
                    self.is_enabled,
                    self.are_overrides_present,
                )
            )
