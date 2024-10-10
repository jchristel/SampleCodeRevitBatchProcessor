"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view port to data view port conversion. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


from duHast.Data.Objects.data_sheet_view_port import DataSheetViewPort
from duHast.Data.Objects.Properties.Geometry.geometry_bounding_box import DataBoundingBox

def convert_revit_viewport_to_data_instance(view_port):
    """
    Convertes a Revit ViewPort into a data viewport

    :param view_port: A Revit ViewPort
    :type view_port: Autodesk.Revit.DB.ViewPort
    :return: A populated data viewport instance
    :rtype: :class:`.DataSheetViewPort`
    """
    # set up data instances
    view_port_data = DataSheetViewPort()
    bbox = DataBoundingBox()

    # get an outline from the Revit view port
    view_port_outline = view_port.GetBoxOutline()
    # get the outlines min and max points
    max_point = view_port_outline.MaximumPoint
    min_point = view_port_outline.MinimumPoint

    # get the min and max point from the outline
    # TODO: convert into metric
    bbox.max = [max_point.X,max_point.Y,max_point.Z]
    bbox.min = [min_point.X,min_point.Y,min_point.Z]
    
    # update the bounding box property of the view port instance
    view_port_data.bounding_box = bbox

    return view_port_data