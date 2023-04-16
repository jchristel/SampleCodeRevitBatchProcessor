'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Customizable element filter class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

# import Autodesk
#import Autodesk.Revit.DB as rdb

from duHast.Utilities import Base

class RevitCustomElementFilter(Base.Base):

    def __init__(self, element_filters = [] , is_logical_and_filter = True,  **kwargs):
        '''
        Constructor: This takes a list of element filters and a flag whether this class instance is a logical AND filter (default)

        :param elementFilters: List of element filter functions which will need to accept document and elementId as their arguments, defaults to []
        :type elementFilters: list of functions, optional
        :param isLogicalANDFilter: Flag indicating whether list of filters are logical AND filters or logical OR, defaults to True (logical AND)
        :type isLogicalANDFilter: bool, optional
        '''

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(RevitCustomElementFilter, self).__init__(**kwargs)  

        self.element_filters = element_filters
        self.is_logical_and_filter = is_logical_and_filter
    
    def check_element(self, doc, element_id):
        '''
        Filter checking whether element meets criteria.

        This function will loop over all the filters past in through the class constructor and test the element for each filter.
        Depending on whether these filters are logical and filters it will return True if all of them evaluate to True or, if logical or filter
        it will return True if one of them evaluates to True, otherwise False will be returned.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param elementId: The id of the element to be checked against the filter.
        :type elementId: Autodesk.Revit.DB.ElementId
        :return: True if it matches the filter(s), otherwise False
        :rtype: bool
        '''

        if(self.is_logical_and_filter):
            filter_over_all = True
        else:
            filter_over_all = False
        
        for filter in self.element_filters:
            filter_result = filter(doc, element_id)
            if(self.is_logical_and_filter == False and filter_result == True):
                filter_over_all = True
                # can leave the loop at this point since only one of the tests need to result true in OR filter mode
                break
            elif(self.is_logical_and_filter == True and filter_result == False):
                filter_over_all = False
                # can leave the loop at this point since only one of the tests need to result false in AND filter mode
                break
            else:
                filter_over_all = filter_over_all and filter_result
        return filter_over_all
