"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions used to revit elements to data storage classes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




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

from duHast.Revit.Common.Objects.Data.colour_base import ColourBase

from Autodesk.Revit.DB import ViewDetailLevel

# dictionary conversion for view detail level to int
VIEW_DETAIL_LEVEL_NAME_MAPPING = {
    ViewDetailLevel.Undefined: -1,
    ViewDetailLevel.Coarse: 0,
    ViewDetailLevel.Medium: 1,
    ViewDetailLevel.Fine: 2,
}

# Create a reverse mapping of view detail enum values by swapping keys and values
VIEW_DETAIL_LEVEL_NAME_MAPPING_REVERSE = {
    v: k for k, v in VIEW_DETAIL_LEVEL_NAME_MAPPING.items()
}


def to_colour(revit_colour):
    """
    Convertes a Revit colour instance to a ColourBase storage instance

    :param revit_colour: A revit Colour object instance
    :type revit_colour: Autodesk.Revit.DB.Color

    :return: A ColourBase storage instance
    :rtype: :class:`.ColourBase`
    """

    c = ColourBase()
    try:
        # convert byte values to integers!
        c.red = int(revit_colour.Red)
        c.green = int(revit_colour.Green)
        c.blue = int(revit_colour.Blue)
    except Exception as e:
        c.red = -1
        c.green = -1
        c.blue = -1
    return c
