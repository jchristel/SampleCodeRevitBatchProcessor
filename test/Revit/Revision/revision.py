"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit revision data . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


For Revit versions

- 2022
- 2023

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

from duHast.Revit.Revisions.revisions import (
    REVISION_DATA,
)

# import Autodesk
import Autodesk.Revit.DB as rdb

#: set up revision data for Revit up to version 2022
TEST_DATA_2022 = REVISION_DATA(
    description="unit test",
    issued_by="tester",
    issued_to="testy",
    revision_number_type=rdb.RevisionNumberType.Numeric,
    revision_date="23/12/23",
    tag_cloud_visibility=rdb.RevisionVisibility.Hidden,
)

#: set up revision data for Revit from version 2023 onwards
TEST_DATA_2023 = REVISION_DATA(
    description="unit test",
    issued_by="tester",
    issued_to="testy",
    revision_number_type="Numeric",  # sequence name, which in turn defines the number type
    revision_date="23/12/23",
    tag_cloud_visibility=rdb.RevisionVisibility.Hidden,
)
