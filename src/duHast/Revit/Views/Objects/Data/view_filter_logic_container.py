"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A container class used to group ElementParameterFilters.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Stores view filters rules


"""


#
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


import json

from duHast.Utilities.Objects import base
from duHast.Revit.Views.Objects.Data.view_filter_rule import ViewFilterRule

class ViewFilterLogicContainer(base.Base):
    def __init__(self, data_type="view filter logic container", j=None, **kwargs):
        """
        Class constructor.
        """

        super(ViewFilterLogicContainer, self).__init__(**kwargs)

        self.data_type = data_type
        self.view_filter_rules = []
        self.logic_containers = []
        self.logic_container_type = ""

        # print("here in ViewFilterLogicContainer init...")
        # print("j: {}".format(j))
        # check if any data was past in with constructor!
        if j is not None:
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
                # get the container type
                self.logic_container_type = j["logic_container_type"]

                # get rules
                rules = j["view_filter_rules"]
                for r in rules:
                    self.view_filter_rules.append(ViewFilterRule(j=r))

                # get containers
                containers = j["logic_containers"]
                for c in containers:
                    self.logic_containers.append(ViewFilterLogicContainer(j=c))

            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        data_type, e
                    )
                )
    

    def __eq__(self, other):
        """
        Equality method to compare two objects of this class.

        :param other: Other object to compare with.
        :type other: ViewFilterLogicContainer

        :return: True if both objects are equal, False otherwise.
        :rtype: bool
        """

        if not isinstance(other, ViewFilterLogicContainer):
            # don't attempt to compare against unrelated types
            return False

        # compare the logic container type
        if self.logic_container_type != other.logic_container_type:
            return False

        if self.data_type != other.data_type:
            return False

        if len(self.view_filter_rules) != len(other.view_filter_rules):
            return False
        else:
            for rule in self.view_filter_rules:
                if rule not in other.view_filter_rules:
                    return False

        if len(self.logic_containers) != len(other.logic_containers):
            return False
        else:
            for container in self.logic_containers:
                if container not in other.logic_containers:
                    return False

        # all tests passed, must be equal
        return True
    

    def __ne__(self, other):
        """
        Inequality method to compare two objects of this class.

        :param other: Other object to compare with.
        :type other: ViewFilterLogicContainer

        :return: True if both objects are not equal, False otherwise.
        :rtype: bool
        """

        return not self.__eq__(other)
    
    def __hash__(self):
        """
        Override the default hash behavior (that returns the id or the object)
        """

        return hash((self.logic_container_type, tuple(self.view_filter_rules), tuple(self.logic_containers)))