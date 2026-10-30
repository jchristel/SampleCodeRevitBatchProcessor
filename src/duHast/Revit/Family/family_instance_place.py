"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around data storage in Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data storage can be used to project wide settings not associated with a specific element. 

Obsolete in Revit 2025 ... 
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

"""
Placing family instances inside a transaction the caller already holds: on a level (rotated), on the nearest wall, with the
created phase set and the facing flipped to match a direction.

The functions of :mod:`duHast.Revit.Family.family_instance_create` open a transaction per instance; these are for placing many
instances in one.
"""

from duHast.Revit.Common.element_id import get_el_id_int
from duHast.Revit.Family.family_symbol_lookup import activate_symbol_without_transaction_wrapper

from Autodesk.Revit.DB import (
    BuiltInParameter,
    ElementTransformUtils,
    FilteredElementCollector,
    Line,
    Wall,
    XYZ,
)
from Autodesk.Revit.DB.Structure import StructuralType


def get_nearest_wall_on_level(doc, level, point, reach):
    """
    Returns the wall on a level whose location curve is nearest to a point, within a reach.

    The distance is measured in plan.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The level the wall is on.
    :type level: Autodesk.Revit.DB.Level
    :param point: The point (feet).
    :type point: Autodesk.Revit.DB.XYZ
    :param reach: The largest distance accepted (feet).
    :type reach: float

    :return: The wall, None if there is none within the reach.
    :rtype: Autodesk.Revit.DB.Wall or None
    """

    best = None
    best_distance = reach
    level_value = get_el_id_int(level.Id)
    for wall in FilteredElementCollector(doc).OfClass(Wall):
        try:
            if get_el_id_int(wall.LevelId) != level_value:
                continue
            curve = wall.Location.Curve
            flat = XYZ(point.X, point.Y, curve.GetEndPoint(0).Z)
            distance = curve.Project(flat).Distance
        except Exception:
            continue
        if distance < best_distance:
            best, best_distance = wall, distance
    return best


def place_instance_on_level_without_transaction_wrapper(doc, symbol, point, level, rotation=0.0):
    """
    Places a level based family instance and turns it about the vertical axis through its location.

    Needs to be called within an open transaction. The symbol is activated if it is not.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param symbol: The family symbol.
    :type symbol: Autodesk.Revit.DB.FamilySymbol
    :param point: The location (feet).
    :type point: Autodesk.Revit.DB.XYZ
    :param level: The level.
    :type level: Autodesk.Revit.DB.Level
    :param rotation: Counter clockwise angle in radians; 0 does not rotate.
    :type rotation: float

    :return: The new instance.
    :rtype: Autodesk.Revit.DB.FamilyInstance
    """

    activate_symbol_without_transaction_wrapper(doc, symbol)
    instance = doc.Create.NewFamilyInstance(point, symbol, level, StructuralType.NonStructural)
    if rotation:
        axis = Line.CreateBound(point, XYZ(point.X, point.Y, point.Z + 1.0))
        ElementTransformUtils.RotateElement(doc, instance.Id, axis, rotation)
    return instance


def place_instance_on_nearest_wall_without_transaction_wrapper(doc, symbol, point, level, reach):
    """
    Places a wall hosted family instance on the wall nearest to a point.

    Needs to be called within an open transaction. The symbol is activated if it is not.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param symbol: The family symbol.
    :type symbol: Autodesk.Revit.DB.FamilySymbol
    :param point: The location (feet).
    :type point: Autodesk.Revit.DB.XYZ
    :param level: The level.
    :type level: Autodesk.Revit.DB.Level
    :param reach: How far from the point a wall may be (feet).
    :type reach: float

    :raises ValueError: when there is no wall within the reach.

    :return: The new instance.
    :rtype: Autodesk.Revit.DB.FamilyInstance
    """

    wall = get_nearest_wall_on_level(doc, level, point, reach)
    if wall is None:
        raise ValueError("no wall within reach to host the instance")
    activate_symbol_without_transaction_wrapper(doc, symbol)
    return doc.Create.NewFamilyInstance(point, symbol, wall, level, StructuralType.NonStructural)


def flip_facing_towards_without_transaction_wrapper(instance, direction_x, direction_y):
    """
    Flips a hosted instance whose facing points away from a plan direction. Does nothing if it can not be flipped.

    Needs to be called within an open transaction.

    :param instance: The family instance.
    :type instance: Autodesk.Revit.DB.FamilyInstance
    :param direction_x: X component of the wanted direction.
    :type direction_x: float
    :param direction_y: Y component of the wanted direction.
    :type direction_y: float

    :return: True if the instance was flipped.
    :rtype: bool
    """

    try:
        x_axis = instance.GetTransform().BasisX
        if x_axis.X * direction_x + x_axis.Y * direction_y < 0 and instance.CanFlipFacing:
            instance.flipFacing()
            return True
    except Exception:
        pass
    return False


def set_created_phase_without_transaction_wrapper(instance, phase):
    """
    Sets the phase an element is created in.

    Needs to be called within an open transaction.

    :param instance: The element.
    :type instance: Autodesk.Revit.DB.Element
    :param phase: The phase.
    :type phase: Autodesk.Revit.DB.Phase

    :return: True if the phase was set.
    :rtype: bool
    """

    created = instance.get_Parameter(BuiltInParameter.PHASE_CREATED)
    if created is not None and not created.IsReadOnly:
        return created.Set(phase.Id)
    return False
