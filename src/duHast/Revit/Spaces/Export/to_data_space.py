"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit spaces export to DATA class functions. Modeled after to_data_room.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from Autodesk.Revit.DB import BuiltInParameter, Element

from duHast.Revit.Common import (
    parameter_get_utils as rParaGet,
    phases as rPhase,
)
from duHast.Data.Objects.Collectors import data_space as dSpace
from duHast.Revit.Common.Geometry import to_data_conversion as rGeo
from duHast.Revit.Spaces.spaces import get_all_spaces
from duHast.Revit.Rooms.Geometry.geometry import get_2d_points_from_revit_room
from duHast.Revit.Exports.export_data import (
    get_model_data,
    get_instance_properties,
    get_design_set_data,
)

from duHast.Utilities.utility import encode_utf8


def populate_data_space_object(doc, revit_space):
    """
    Returns a custom space data objects populated with some data from the revit model space passed in.
    Fields mirror DataRoom where applicable.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_space: The space element.
    :type revit_space: Autodesk.Revit.DB.SpatialElement (Space)

    :return: A space data instance.
    :rtype: :class:`.DataSpace`
    """

    # set up data class object
    data_s = dSpace.DataSpace()
    # get space geometry (boundary points)
    try:
        revit_geometry_point_groups = get_2d_points_from_revit_room(revit_space)
    except Exception:
        revit_geometry_point_groups = []

    if len(revit_geometry_point_groups) > 0:
        space_point_groups_as_doubles = []
        for space_point_group_by_poly in revit_geometry_point_groups:
            data_geometry_converted = rGeo.convert_xyz_in_data_geometry_polygons(
                doc, space_point_group_by_poly
            )
            space_point_groups_as_doubles.append(data_geometry_converted)
        data_s.polygon = space_point_groups_as_doubles

        # get design set data
        design_set = get_design_set_data(doc=doc, element=revit_space)
        data_s.design_set_and_option = design_set

        # get instance properties
        instance_props = get_instance_properties(revit_space)
        data_s.instance_properties = instance_props

        # get the model name
        model = get_model_data(doc=doc)
        data_s.revit_model = model

        # get phase name
        try:
            data_s.phasing.created = encode_utf8(
                rPhase.get_phase_name_by_id(
                    doc,
                    rParaGet.get_built_in_parameter_value(
                        revit_space,
                        BuiltInParameter.ROOM_PHASE,
                        rParaGet.get_parameter_value_as_element_id,
                    ),
                )
            )
        except Exception:
            data_s.phasing.created = ""
        data_s.phasing.demolished = -1

        # get level data
        try:
            data_s.level.name = encode_utf8(Element.Name.GetValue(revit_space.Level))
            data_s.level.id = revit_space.Level.Id.Value
        except Exception:
            data_s.level.name = "no level"
            data_s.level.id = -1
        return data_s

    else:
        return None


def get_all_space_data(doc):
    """
    Returns a list of space data objects for each space in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of space data instances.
    :rtype: list of  :class:`.DataSpace`
    """

    all_space_data = []
    spaces = get_all_spaces(doc)
    for space in spaces:
        sd = populate_data_space_object(doc, space)
        if sd is not None:
            all_space_data.append(sd)
    return all_space_data
