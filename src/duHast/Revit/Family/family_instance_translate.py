"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit family instance translation functions.
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


from math import pi

# class used for stats reporting
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import Element, ElementTransformUtils, Line, Transaction

# Constants
RADIAN_ANGLE_45DEGREES = pi / 4
RADIAN_ANGLE_90DEGREES = pi / 2

def rotate_around_origin(element, angle, transaction_manager =None):
    """
    Rotates an element around its origin.

    :param element: The element to rotate.
    :type element: Autodesk.Revit.DB.Element
    :param angle: The angle to rotate the element by in radians.
    :type angle: float
    """

    return_value = res.Result()

    # Get the element's transform
    transform = element.GetTotalTransform()

    # Create a line from the transform's origin and basis Z
    line = Line.CreateUnbound(transform.Origin, transform.BasisZ)

    try:
        def action():
            try:
                action_return_value = res.Result()
                ElementTransformUtils.RotateElement(element.Document, element.Id, line, angle)
                return_value.append_message( "Element rotated around origin.") 
            except Exception as e:
                action_return_value.update_sep(False, "Failed to rotate element around origin. {}".format(e))
            return action_return_value
       
        if transaction_manager is None:
            # assume there is an transaction already going on
            return_value = action()
        else:
            # create a transaction
            transaction = Transaction(element.Document, "rotated element around origin: {}".format(Element.Name.GetValue(element)))
            return_value = in_transaction(transaction, action)

    except Exception as e:
        return_value.update_sep(False, "Failed to rotate element around origin. {}".format(e))


    return return_value
