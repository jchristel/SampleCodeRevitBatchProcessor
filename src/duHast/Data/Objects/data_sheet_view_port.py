"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage base class used for Revit sheets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains 

    - the title block
    - a list of view ports
    - a list of all sheet properties (instance and type)

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

from duHast.Data.Objects import data_base
from duHast.Data.Objects.Properties.Geometry.geometry_bounding_box import (
    DataBoundingBox,
)
from duHast.Data.Objects.data_view_plan import DataViewPlan
from duHast.Data.Objects.data_view_elevation import DataViewElevation
from duHast.Data.Objects.data_view_3d import DataViewThreeD
from duHast.Data.Objects.data_view_schedule import DataViewSchedule
from duHast.Data.Objects.Properties.data_view_port_type_names import (
    DataViewPortTypeNames,
)

from duHast.Data.Objects.Properties.data_property_names import DataPropertyNames


class DataSheetViewPort(data_base.DataBase):

    data_type = "sheet view port"

    def __init__(self, j=None):
        """
        Class constructor for a sheet view port.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # initialise parent classes with values
        super(DataSheetViewPort, self).__init__(
            data_type=DataSheetViewPort.data_type
        )

        # set default values
        self.bounding_box = DataBoundingBox()
        self.vp_type = DataViewPortTypeNames.FLOOR_PLAN.value
        self.view_id = -1
        self.view = DataViewPlan()

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

                self.bounding_box = DataBoundingBox(
                    j.get(DataPropertyNames.BOUNDING_BOX.value, {})
                )
                self.vp_type = j.get(DataPropertyNames.VIEW_PORT_TYPE.value, self.vp_type)
                self.view_id = j.get(DataPropertyNames.VIEW_ID,self.view_id)
                
                # set up the view depending on the view port type
                if self.vp_type == DataViewPortTypeNames.THREE_D.value:
                    self.view = DataViewThreeD(j.get(DataPropertyNames.VIEW.value,{}))
                elif self.vp_type == DataViewPortTypeNames.ELEVATION.value:
                    self.view = DataViewElevation(j.get(DataPropertyNames.VIEW.value,{}))
                elif self.vp_type == DataViewPortTypeNames.FLOOR_PLAN.value:
                    self.view = DataViewPlan(j.get(DataPropertyNames.VIEW.value,{}))
                elif self.vp_type == DataViewPortTypeNames.SCHEDULE.value:
                    self.view = DataViewSchedule(j.get(DataPropertyNames.VIEW.value,{}))
                else:
                    raise TypeError("Unsupported viewport type: {}".format(self.vp_type))

            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
