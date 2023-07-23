"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Purge action storage class for Revit purge unused.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


# import System
# import clr

from duHast.Utilities.Objects import base


class PurgeAction(base.Base):
    def __init__(
        self,
        purgeTransactionName,  # the function which returns all element ids to be purged
        purgeIdsGetter,  # the function which returns all element ids to be purged
        purgeReportHeader,  # human readable report header for each test action
        testReportHeader,  # human readable report header for each test action
        testIdsGetter,  # functions which returns all available type ids in model of same category as purge action. To be used to compare ids before and after coded purge with ids before and after revit built in purge
    ):
        """
        Class constructor.

        :param purgeTransactionName: The name of the transaction to purge elements under.
        :type purgeTransactionName: str
        :param purgeIdsGetter: The function which returns all element ids to be purged
        :type purgeIdsGetter: func
        :param purgeReportHeader: Human readable report header for each purge action
        :type purgeReportHeader: str
        :param testReportHeader: Human readable report header for each test action
        :type testReportHeader: str
        :param testIdsGetter: functions which returns all available type ids in model of same category as purge action.\
            To be used to compare ids before and after code purge with ids before and after revit built in purge
        :type testIdsGetter: func
        """

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(PurgeAction, self).__init__()

        self.purge_transaction_name = purgeTransactionName
        self.purge_ids_getter = purgeIdsGetter
        self.purge_report_header = purgeReportHeader
        self.test_report_header = testReportHeader
        self.test_ids_getter = testIdsGetter
