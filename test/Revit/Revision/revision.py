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
# BSD License
# Copyright 2023, Jan Christel
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
