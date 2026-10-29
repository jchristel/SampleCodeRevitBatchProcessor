"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to place views on sheets as viewports.
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

from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import Viewport


def create_viewport_without_transaction_wrapper(doc, sheet, view, centre, viewport_type_id=None):
    """
    Places a view on a sheet.

    Changing the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: The sheet to place the view on.
    :type sheet: Autodesk.Revit.DB.ViewSheet
    :param view: The view to place.
    :type view: Autodesk.Revit.DB.View
    :param centre: Where the centre of the viewport goes on the sheet, in feet (z is ignored).
    :type centre: Autodesk.Revit.DB.XYZ
    :param viewport_type_id: The viewport type to apply, defaults to None (the default type).
    :type viewport_type_id: Autodesk.Revit.DB.ElementId, optional

    :return: Result class instance. .result holds the viewport when it was created.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        if not Viewport.CanAddViewToSheet(doc, sheet.Id, view.Id):
            return_value.update_sep(
                False,
                "View {} can not be placed on sheet {} (it is on a sheet already?).".format(view.Name, sheet.SheetNumber),
            )
            return return_value
        viewport = Viewport.Create(doc, sheet.Id, view.Id, centre)
        if viewport_type_id is not None:
            viewport.ChangeTypeId(viewport_type_id)
        return_value.append_message("View {} placed on sheet {}.".format(view.Name, sheet.SheetNumber))
        return_value.result.append(viewport)
    except Exception as e:
        return_value.update_sep(False, "Failed to place view on sheet with exception: {}".format(e))
    return return_value


def get_viewport_outline_size(viewport):
    """
    Returns the size of a viewport on its sheet.

    :param viewport: The viewport.
    :type viewport: Autodesk.Revit.DB.Viewport

    :return: Width and height in feet.
    :rtype: tuple (float, float)
    """

    outline = viewport.GetBoxOutline()
    return (
        outline.MaximumPoint.X - outline.MinimumPoint.X,
        outline.MaximumPoint.Y - outline.MinimumPoint.Y,
    )
