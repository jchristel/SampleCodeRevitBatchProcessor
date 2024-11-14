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

from duHast.Data.Objects.Collectors.data_view_base import DataViewBase

from duHast.Data.Objects.Collectors.Properties.data_property_names import (
    DataPropertyNames,
)
from duHast.Data.Objects.Collectors.Properties.Geometry.geometry_bounding_box_2 import (
    DataGeometryBoundingBox2,
)
from duHast.Data.Objects.Collectors.Properties.data_schedule_segement import (
    DataScheduleSegment,
)


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
        self.bounding_box = DataGeometryBoundingBox2()
        self.total_number_of_rows = 0
        self.segments = []

        json_var = None
        # check if any data was past in with constructor!
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                json_var = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                json_var = j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                self.bounding_box = DataGeometryBoundingBox2(
                    json_var.get(DataPropertyNames.BOUNDING_BOX, {})
                )

                self.total_number_of_rows = json_var.get(
                    DataPropertyNames.TOTAL_NUMBER_OF_ROWS,
                    self.total_number_of_rows,
                )
                if not isinstance(self.total_number_of_rows, int):
                    raise TypeError(
                        "Expected 'total_number_of_rows' to be an int, got {}".format(
                            type(self.total_number_of_rows)
                        )
                    )

                segment_data = json_var.get(DataPropertyNames.SEGMENTS, [])
                for seg_d in segment_data:
                    seg = DataScheduleSegment(j=seg_d)
                    self.segments.append(seg)

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        """
        equal compare

        Args:
            other (DataViewSchedule): another DataViewSchedule instance

        Returns:
            bool: True if equal, otherwise False
        """
        if not isinstance(other, DataViewSchedule):
            return NotImplemented
        return (
            self.bounding_box == other.bounding_box
            and self.total_number_of_rows == other.total_number_of_rows
            and self.segments == other.segments
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.bounding_box, self.total_number_of_rows, self.segments))
