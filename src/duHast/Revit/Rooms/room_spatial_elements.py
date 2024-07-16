from Autodesk.Revit.DB import SpatialElementBoundaryOptions, CurveLoop, Wall, ModelLine


def get_room_segments(room):
    """
    Get a rooms boundary segments with the default spatial element boundary options.
    :param room: The room to get for
    :type room: Room
    :return: The boundary segments of the room
    :rtype: List[List[BoundarySegment]]
    """
    return room.GetBoundarySegments(SpatialElementBoundaryOptions())


def get_segment_host(rvt_doc, seg):
    """
    Get the element that the room boundary segment belongs to
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param seg: The boundary segment
    :type seg: BoundarySegment
    """

    # TODO: Add support for linked elements
    return rvt_doc.GetElement(seg.ElementId)


def get_curves_as_curve_loop(rm_crvs):
    """
    Get a list of curves as a CurveLoop object.
    :param rm_crvs: The curves to get for
    :type rm_crvs: List[Curve]
    :return: The curves as a CurveLoop object
    :rtype: CurveLoop
    """
    cl = CurveLoop()
    for crv in rm_crvs:
        cl.Append(crv)
    return cl


def get_segments_as_curves(rvt_doc, segments, filter_only=None):
    """
    Get a list of curves that represents the boundary segments of a room.

    Optional parameter to filter the segments by the host type (wall or
    room separation line).
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :param filter_only: Optional: The host type to filter for
    :type filter_only: Wall, ModelLine or both in a list
    :return: A list of curves
    :rtype: List[Curve]
    """
    curves = []

    if filter_only:
        filter_for = []

        if isinstance(filter_only, list):
            filter_for = filter_only
        else:
            filter_for = [filter_only]

        for closed_seg_set in segments:
            for seg in closed_seg_set:
                host = get_segment_host(rvt_doc, seg)
                if host.GetType() in filter_for:
                    curves.append(seg.GetCurve())

    else:
        for closed_seg_set in segments:
            for seg in closed_seg_set:
                curves.append(seg.GetCurve())

    return curves


def get_wall_segments_as_curves_only(rvt_doc, segments):
    """
    Get the wall segments of a room as curves.
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :return: A list of curves
    :rtype: List[Curve]
    """
    return get_segments_as_curves(rvt_doc, segments, filter_only=Wall)


def get_rm_sep_lines_as_curves_only(rvt_doc, segments):
    """
    Get the room separation line segments of a room as curves.
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :return: A list of curves
    :rtype: List[Curve]
    """
    return get_segments_as_curves(rvt_doc, segments, filter_only=ModelLine)
