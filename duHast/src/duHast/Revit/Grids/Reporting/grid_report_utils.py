"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for grid reports. 
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

import Autodesk.Revit.DB as rdb
from duHast.Revit.Common import worksets as rWork
from duHast.Utilities import utility as util
from duHast.Revit.Grids import grids as rGrid


def get_grid_report_data(doc, revit_file_path):
    """
    Gets grid data ready for being printed to file
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: fully qualified file path of Revit file
    :type revit_file_path: str
    :return: list of list of revit grid properties.
    :rtype: [[str]]
    """

    data = []
    for grid in rdb.FilteredElementCollector(doc).OfClass(rdb.Grid):
        data.append(
            [
                revit_file_path,
                str(grid.Id.IntegerValue),
                util.encode_ascii(grid.Name),
                rWork.get_workset_name_by_id(doc, grid.WorksetId.IntegerValue),
                rGrid.get_max_extent_as_string(grid),
                rGrid.get_min_extent_as_string(grid),
            ]
        )
    return data
