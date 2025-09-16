"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class used to store view filter rules.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Stores view filters rules

The paraemeter id
the Evaluation type
the rule value


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

class ViewFilterRule(base.Base):
    def __init__(self, data_type="view filter rule", j=None, **kwargs):
        """
        Class constructor.
        """

        super(ViewFilterRule, self).__init__(**kwargs)

        self.data_type = data_type
        self.parameter_id = -1
        self.parameter_name = ""
        self.parameter_guid = ""
        self.evaluation_type = ""
        self.value_provider = ""
        self.rule_value = ""
        self.rule_type = ""
        self.is_inversed = False
        self.epsilon = None
       
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
                # get category ids
                self.parameter_id = j["parameter_id"]
                self.evaluation_type = j["evaluation_type"]
                self.rule_value = j["rule_value"]
                self.is_inversed = j["is_inversed"]
                self.parameter_name = j["parameter_name"]
                self.parameter_guid = j["parameter_guid"]
                self.rule_type = j["rule_type"]
                self.value_provider = j["value_provider"]
                self.epsilon = j.get("epsilon", None)

            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                       data_type, e
                    )
                )
    

    def __eq__(self, other):
        """
        Override the default Equals behavior.

        Will take into account that shared parameters can have different ids in different documents

        """
        if isinstance(other, ViewFilterRule):
            # check if this is comparing a shared parameter based rule
            if self.parameter_guid != "" and other.parameter_guid != "":
                return self.parameter_guid == other.parameter_guid and \
                    self.evaluation_type == other.evaluation_type and \
                    self.rule_value == other.rule_value and \
                    self.is_inversed == other.is_inversed and \
                    self.parameter_name == other.parameter_name and \
                    self.rule_type == other.rule_type and \
                    self.value_provider == other.value_provider and \
                    self.epsilon == other.epsilon
            else:
                return self.parameter_id == other.parameter_id and \
                    self.evaluation_type == other.evaluation_type and \
                    self.rule_value == other.rule_value and \
                    self.is_inversed == other.is_inversed and \
                    self.parameter_name == other.parameter_name and \
                    self.parameter_guid == other.parameter_guid and \
                    self.rule_type == other.rule_type and \
                    self.value_provider == other.value_provider and \
                    self.epsilon == other.epsilon
        return False
    

    def __ne__(self, other):
        """
        Define a non-equality test
        """
        return not self.__eq__(other)
    

    def __hash__(self):
        """
        Override the default hash behavior (that returns the id or the object)
        """
        return hash((
            self.parameter_id, 
            self.evaluation_type, 
            self.rule_value, 
            self.is_inversed, 
            self.parameter_name, 
            self.parameter_guid,
            self.rule_type,
            self.value_provider,
            self.epsilon
            )
        )