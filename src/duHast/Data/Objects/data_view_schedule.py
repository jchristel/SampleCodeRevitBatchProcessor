"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage base class used for Revit views.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains 

    - the view bounding box in model coordinates

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

import json

from duHast.Data.Objects.data_view_base import DataViewBase

from duHast.Data.Objects.Properties.data_property_names import DataPropertyNames
from duHast.Data.Objects.Properties.Geometry.geometry_bounding_box_2 import (
    DataBoundingBox2,
)
from duHast.Data.Objects.Properties.data_schedule_segement import DataScheduleSegment

class DataViewSchedule(DataViewBase):

    data_type = "view_schedule"

    def __init__(self, j=None):
        """
        Class constructor for a view_schedule.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # initialise parent classes with values
        super(DataViewSchedule, self).__init__(
            data_type=DataViewSchedule.data_type, j=j
        )

        # set default values
        self.bounding_box = DataBoundingBox2()
        self.total_number_of_rows = 0
        self.segments = []

        # check if any data was past in with constructor!
        if j != None and len(j) > 0:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                j = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                pass
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                self.bounding_box = DataBoundingBox2(
                    j.get(DataPropertyNames.BOUNDING_BOX.value, {})
                )
                self.total_number_of_rows = j.get(DataPropertyNames.TOTAL_NUMBER_OF_ROWS.value, self.total_number_of_rows)
                segment_data = j.get(DataPropertyNames.SEGMENTS,[])
                for seg_d in segment_data:
                    seg = DataScheduleSegment(j=seg_d)
                    self.segments.append(seg)
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
