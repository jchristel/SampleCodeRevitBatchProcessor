"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class used to store view filters.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Stores view filters ( ParameterFilterElement in Revit)



ParameterFilterElement contains: 
    - ElementFilters ( a base class for filters)
    those in turn contain ElementLogicalFilter ( a base class for ) logical filters There are two types:
        - LogicalAndFilter
        - LogicalOrFilter
        and those in turn contain ElementParameterFilter ( a base class for parameter filters)
            - most often in view filters we seem to use ElementParameterFilter which consists of list of  FilterRule


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
from duHast.Revit.Views.Objects.Data.view_filter_logic_container import ViewFilterLogicContainer

class ViewFilter(base.Base):
    def __init__(self, data_type="view filter", j=None, **kwargs):
        """
        Class constructor.

        """

        super(ViewFilter, self).__init__(**kwargs)

        self.data_type = data_type
        self.category_ids = []  # list of category ids the filter applies to
        self.logic_containers = [] #is just one but be consistent with ViewFilterLogicContainer class
        self.name = ""
       
        

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

            #print("In ViewFilter init, j: {}".format(j))
            # load values and throw exception if something is missing!
            try:
                # debug print
                # for key, value in j.items():
                #     print("key: {}, value: {}".format(key, value))

                # get category ids
                self.category_ids = j["category_ids"]

                # get name
                self.name = j["name"]  

                # get containers
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
        Equality comparison
        :param other: other object to compare with
        :type other: ViewFilter

        :return: True if equal, False if not
        :rtype: bool
        """

        if not isinstance(other, ViewFilter):
            # don't attempt to compare against unrelated types
            return False

        if self.category_ids != other.category_ids:
            return False

        if self.name != other.name:
            return False

        if len(self.logic_containers) != len(other.logic_containers):
            return False
        else:
            for container in self.logic_containers:
                if container not in other.logic_containers:
                    return False

        return True
    

    def __ne__(self, other):
        """
        Inequality comparison
        :param other: other object to compare with
        :type other: ViewFilter

        :return: True if not equal, False if equal
        :rtype: bool
        """

        return not self.__eq__(other)


    def __hash__(self):
        """
        Override the default hash behavior (that returns the id or the object)
        :return: Hash value of the object
        :rtype: int
        """
        
        return hash((tuple(self.category_ids), self.name, tuple(self.logic_containers)))