'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to sort task evenly into workload buckets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A bucket contains a number of files which will eventually be written into task files to be processed by batch processor.
The below function attempt to fill these buckets evenly measured on file size.
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

import clr
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

from duHast.UI import WorkloadBucket as wb

def DistributeWorkload (numberOfBuckets, items, getWorkloadSize):
    '''
    Distributes a given number of items evenly by workload size into workload buckets.

    :param numberOfBuckets: The number of buckets items are to be distributed to
    :type numberOfBuckets: int
    :param items: A list of items.
    :type items: [foo]
    :param getWorkloadSize: A function returning the workload size from an item.
    :type getWorkloadSize: func(foo) -> int
    
    :return: A list of workload bucket objects containing items.
    :rtype: list[ :class:`.WorkloadBucket`]
    '''
    
    workloadBuckets = []
    try:
        # ini bucket list
        for x in range(numberOfBuckets):
            workloadBuckets.append(wb.WorkloadBucket())
        itemToWorkLoadValues = []
        
        # build key value list of items and their workload value
        for item in items:
            itemToWorkLoadValues.append([item, getWorkloadSize(item)])
        
        # sort list by workload size in descending order (biggest item first)
        itemToWorkLoadValues = Sort(itemToWorkLoadValues)
        
        # load up with buckets
        for bucket in itemToWorkLoadValues:
            # find bucket with smallest work load value
            lowBucket = min(workloadBuckets, key=lambda wbucket: wbucket.workLoadValue)
            # add new item to bucket list
            lowBucket.AddItem(bucket[0])
            # increase work bucket size by size of item added
            lowBucket.SetWorkLoadValue(lowBucket.workLoadValue + bucket[1])

    except Exception as e:
        print(e)
        pass
    # send loaded buckets back
    return workloadBuckets

def Sort(sub_li): 
    '''
    Python code to sort the tuples using second element of sublist. Inplace way to sort using sort().

    Note: not sure a one liner warrants a method...?

    :param sub_li: _description_
    :type sub_li: _type_
    :return: _description_
    :rtype: _type_
    '''
    # reverse = None (Sorts in Ascending order) 
    # key is set to sort using second element of  
    # sublist lambda has been used 
    sub_li.sort(key = lambda x: x[1], reverse = True) 
    return sub_li 