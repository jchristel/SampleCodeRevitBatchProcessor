"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions exporting revit geometry to data objects.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Revit.Ceilings.Export import to_data_ceiling as rCeil
from duHast.Revit.Rooms.Export import to_data_room as rRoom

from duHast.Data.Objects import data_ceiling as dc
from duHast.Data.Objects import data_room as dr


# -------------------------------- write data to file -------------------------------------------------------


def get_data_from_model(doc):
    """
    Gets element data from the model. This is currently limited to

    - rooms
    - ceilings

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary in format {file name: str, date processed : str, room:[], ceiling:[]}
    :rtype: {}
    """

    # get data
    allRoomData = rRoom.get_all_room_data(doc)
    allCeilingData = rCeil.get_all_ceiling_data(doc)

    dic = {
        dr.DataRoom.data_type: allRoomData,
        dc.DataCeiling.data_type: allCeilingData,
    }

    return dic
