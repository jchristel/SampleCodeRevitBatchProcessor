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

import System
import clr
import WorkloadBucket as wb


# distributes a given number evenly to workload buckets
# number of buckets : the nubmer of buckets items are to be distributed to
# items: list of items
# getWorkloadSize: function returning the indivisual items workload size
def DistributeWorkload (numerOfBuckets, items, getWorkloadSize):
    workloadBuckets = []
    try:
        # ini bucket list
        for x in range(numerOfBuckets):
            workloadBuckets.append(wb.WorkloadBucket())
        itemToWorkLoadValues = []
        
        # build key value list of items and their workload value
        for item in items:
            itemToWorkLoadValues.append([item, getWorkloadSize(item)])
        
        # sort list by workload size in descending order
        itemToWorkLoadValues = Sort(itemToWorkLoadValues)
        
        # load up with buckets
        for bucket in itemToWorkLoadValues:
            # find bucket with smallest work load value
            lowBucket = min(workloadBuckets, key=lambda wbucket: wbucket.workLoadValue)
            # add new item to bucket list
            lowBucket.AddItem(bucket[0])
            # increase workbucket size by size of item added
            lowBucket.SetWorkLoadValue(lowBucket.workLoadValue + bucket[1])

    except Exception as e:
        print(e)
        pass
    # send loaded buckets back
    return workloadBuckets

# Python code to sort the tuples using second element  
# of sublist Inplace way to sort using sort() 
def Sort(sub_li): 
  
    # reverse = None (Sorts in Ascending order) 
    # key is set to sort using second element of  
    # sublist lambda has been used 
    sub_li.sort(key = lambda x: x[1]) 
    return sub_li 