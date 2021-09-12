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

# a class used to store purge actions and associated values
class PurgeAction: 
    def __init__(
        self, 
        purgeTransactionName, # the function which returns all element ids to be purged
        purgeIdsGetter, # the function which returns all element ids to be purged
        purgeReportHeader, # human readable repport header for each test action
        testReportHeader, # human readable repport header for each test action
        testIdsGetter # functions which returns all availble type ids in model of same category as purge action. To be used to compare ids before and after coded purge with ids before and after revit built in purge
    ): 
        self.purgeTransactionName = purgeTransactionName
        self.purgeIdsGetter = purgeIdsGetter
        self.purgeReportHeader = purgeReportHeader
        self.testReportHeader = testReportHeader
        self.testIdsGetter = testIdsGetter