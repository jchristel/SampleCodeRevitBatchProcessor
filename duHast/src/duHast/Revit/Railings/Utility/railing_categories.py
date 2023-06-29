"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit railings built-in categories. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- useful for filtering out families which can be used in MEP system types

"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

#: category filter for all railing element filters by category
import Autodesk.Revit.DB as rdb
from System.Collections.Generic import List


RAILING_CATEGORY_FILTER = List[rdb.BuiltInCategory](
    [
        rdb.BuiltInCategory.OST_Railings,
        rdb.BuiltInCategory.OST_RailingBalusterRail,
        rdb.BuiltInCategory.OST_RailingHandRail,
        rdb.BuiltInCategory.OST_RailingSupport,
        rdb.BuiltInCategory.OST_RailingSystem,
        rdb.BuiltInCategory.OST_RailingTermination,
        rdb.BuiltInCategory.OST_RailingTopRail,
    ]
)
