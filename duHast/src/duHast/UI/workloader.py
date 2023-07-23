"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to sort task evenly into workload buckets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A bucket contains a number of files which will eventually be written into task files to be processed by batch processor.
The below function attempt to fill these buckets evenly measured on file size.
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

import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

from duHast.UI import workload_bucket as wb


def distribute_workload(number_of_buckets, items, getWorkloadSize):
    """
    Distributes a given number of items evenly by workload size into workload buckets.

    :param numberOfBuckets: The number of buckets items are to be distributed to
    :type numberOfBuckets: int
    :param items: A list of items.
    :type items: [foo]
    :param getWorkloadSize: A function returning the workload size from an item.
    :type getWorkloadSize: func(foo) -> int

    :return: A list of workload bucket objects containing items.
    :rtype: list[ :class:`.WorkloadBucket`]
    """

    workload_buckets = []
    try:
        # ini bucket list
        for x in range(number_of_buckets):
            workload_buckets.append(wb.WorkloadBucket())
        itemToWorkLoadValues = []

        # build key value list of items and their workload value
        for item in items:
            itemToWorkLoadValues.append([item, getWorkloadSize(item)])

        # sort list by workload size in descending order (biggest item first)
        itemToWorkLoadValues = sort(itemToWorkLoadValues)

        # load up with buckets
        for bucket in itemToWorkLoadValues:
            # find bucket with smallest work load value
            lowBucket = min(
                workload_buckets, key=lambda work_bucket: work_bucket.workload_value
            )
            # add new item to bucket list
            lowBucket.add_item(bucket[0])
            # increase work bucket size by size of item added
            lowBucket.set_workload_value(lowBucket.workload_value + bucket[1])

    except Exception as e:
        print(e)
        pass
    # send loaded buckets back
    return workload_buckets


def sort(sub_li):
    """
    Python code to sort the tuples using second element of sublist. Inplace way to sort using sort().

    Note: not sure a one liner warrants a method...?

    :param sub_li: _description_
    :type sub_li: _type_
    :return: _description_
    :rtype: _type_
    """
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    sub_li.sort(key=lambda x: x[1], reverse=True)
    return sub_li
