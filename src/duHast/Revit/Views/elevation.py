"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit elevations. 
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

from Autodesk.Revit.DB import ElevationMarker, FilteredElementCollector,ViewSection

def get_view_index_on_marker(doc, view):
    """
    Get the index of the view on the elevation marker.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: Revit view.
    :type view: Autodesk.Revit.DB.View

    :return: Index of the view on the elevation marker. None if not found.
    :rtype: int or None
    """

    # check if we got an elevation view to start with
    if not isinstance(view, ViewSection):
        return None

    collector = FilteredElementCollector(doc).OfClass(ElevationMarker)

    found_marker = None
    for marker in collector:
        view_count = marker.MaximumViewCount
        for i in range(view_count):
            view_id = marker.GetViewId(i)
            if view_id == view.Id:
                found_marker = i
                break
        
        if found_marker is not None:
            break
    
    return found_marker