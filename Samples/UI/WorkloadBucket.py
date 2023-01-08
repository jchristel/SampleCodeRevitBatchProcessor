'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A work load bucket.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Workload buckets are used to distribute file processing evenly between parallel running batch processor\
    sessions based on Revit file size.

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


# a class used to store work load items
class WorkloadBucket: 
    def __init__(self): 
        '''
        Class constructor.

        Initializes this class with:

        - .workLoadValue = 0
        - .items = []

        '''
        
        self.workLoadValue = 0
        self.items = []
    
    def SetWorkLoadValue(self, value):
        '''
        Sets the buckets overall workload value.

        :param value: An integer representing the workload value of this bucket.
        :type value: int
        '''

        try:
            self.workLoadValue = value
        except Exception as e:
            print (str(e))
            pass
    
    def AddItem(self, value):
        '''
        Adds an item to the workload list.

        :param value: Adds an item to the workload list.
        :type value: foo
        '''
        try:
            self.items.append(value)
        except Exception as e:
            print (str(e))
            pass