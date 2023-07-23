"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Customizable element filter class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class takes as constructor arguments

- a number of filter actions
- a boolean indicating whether filters are logical and or OR filters

Filter actions checks whether a property matches or does not match provided values. Refer to module: custom_element_filter_actions. The actual property test is undertaken by another function. Samples of those can be found in
module custom_element_filter_tests.

"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

# import Autodesk
# import Autodesk.Revit.DB as rdb

from duHast.Utilities.Objects import base


class RevitCustomElementFilter(base.Base):
    def __init__(self, element_filters=[], is_logical_and_filter=True, **kwargs):
        """
        Constructor: This takes a list of element filters and a flag whether this class instance is a logical AND filter (default)

        :param element_filters: List of element filter functions which will need to accept document and elementId as their arguments, defaults to []
        :type element_filters: list of functions, optional
        :param is_logical_and_filter: Flag indicating whether list of filters are logical AND filters or logical OR, defaults to True (logical AND)
        :type is_logical_and_filter: bool, optional
        """

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(RevitCustomElementFilter, self).__init__(**kwargs)

        self.element_filters = element_filters
        self.is_logical_and_filter = is_logical_and_filter

    def check_element(self, doc, element_id):
        """
        Filter checking whether element meets criteria.

        This function will loop over all the filters past in through the class constructor and test the element for each filter.
        Depending on whether these filters are logical and filters it will return True if all of them evaluate to True or, if logical or filter
        it will return True if one of them evaluates to True, otherwise False will be returned.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param element_id: The id of the element to be checked against the filter.
        :type element_id: Autodesk.Revit.DB.ElementId
        :return: True if it matches the filter(s), otherwise False
        :rtype: bool
        """

        if self.is_logical_and_filter:
            filter_over_all = True
        else:
            filter_over_all = False

        for filter in self.element_filters:
            filter_result = filter(doc, element_id)
            if self.is_logical_and_filter == False and filter_result == True:
                filter_over_all = True
                # can leave the loop at this point since only one of the tests need to result true in OR filter mode
                break
            elif self.is_logical_and_filter == True and filter_result == False:
                filter_over_all = False
                # can leave the loop at this point since only one of the tests need to result false in AND filter mode
                break
            else:
                filter_over_all = filter_over_all and filter_result
        return filter_over_all
