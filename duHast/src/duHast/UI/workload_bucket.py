"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A work load bucket.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Workload buckets are used to distribute file processing evenly between parallel running batch processor\
    sessions based on Revit file size.

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
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from duHast.Utilities.Objects import base

# a class used to store work load items
class WorkloadBucket(base.Base):
    def __init__(self):
        """
        Class constructor.

        Initializes this class with:

        - .workload_value = 0
        - .items = []

        """

        # ini super class to allow multi inheritance in children!
        super(WorkloadBucket, self).__init__()

        self.workload_value = 0
        self.items = []

    def set_workload_value(self, value):
        """
        Sets the buckets overall workload value.

        :param value: An integer representing the workload value of this bucket.
        :type value: int
        """

        try:
            self.workload_value = value
        except Exception as e:
            print(
                "Failed to set workload value: {} with exception: {}".format(value, e)
            )
            pass

    def add_item(self, value):
        """
        Adds an item to the workload list.

        :param value: Adds an item to the workload list.
        :type value: foo
        """
        try:
            self.items.append(value)
        except Exception as e:
            print(
                "Failed to add item: {} to workload bucket with exception: {}".format(
                    value, e
                )
            )
            pass
