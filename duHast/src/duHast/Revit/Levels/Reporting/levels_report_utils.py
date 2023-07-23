"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for level reports. 
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
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm


def get_level_report_data(doc, revitFilePath):
    """
    Gets level data ready for being printed to file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str
    :return: list of list of revit level properties.
    :rtype: list of list of str
    """

    data = []
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.Level):
        data.append(
            [
                revitFilePath,
                str(p.Id.IntegerValue),
                util.encode_ascii(p.Name),
                util.encode_ascii(
                    rWork.get_workset_name_by_id(doc, p.WorksetId.IntegerValue)
                ),
                str(convert_imperial_feet_to_metric_mm(p.Elevation)),
            ]
        )
    return data
