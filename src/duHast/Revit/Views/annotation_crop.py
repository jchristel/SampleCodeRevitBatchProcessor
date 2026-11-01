"""
Helper functions to switch a view's annotation crop on or off and place its edges.
"""

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.unit_conversion import convert_mm_to_imperial_feet

from Autodesk.Revit.DB import BuiltInParameter


def set_annotation_crop_without_transaction_wrapper(view, active, offsets=None):
    """
    Switches the annotation crop of a view on or off and, when on, places its four edges.

    The offsets are from the edges of the view crop and in view units, which is paper: Revit keeps them in
    feet on paper, so they hold at any view scale. The annotation crop can not be smaller than the view crop
    (the least offset is 1/8 inch on paper); a smaller offset is raised to it by Revit's own check, which this
    reports.

    Changing the model: this needs to run inside a transaction.

    :param view: The plan or elevation view.
    :type view: Autodesk.Revit.DB.View
    :param active: Whether the annotation crop is on.
    :type active: bool
    :param offsets: The edges as {"left", "right", "top", "bottom"} in mm on paper; only used when active.
    :type offsets: dict, optional

    :return: Result class instance.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        manager = view.GetCropRegionShapeManager()
        if not manager.CanHaveAnnotationCrop:
            return_value.append_message("View {} can not have an annotation crop.".format(view.Name))
            return return_value
        parameter = view.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE)
        if parameter is None or parameter.IsReadOnly:
            return_value.update_sep(False, "The annotation crop of view {} can not be set.".format(view.Name))
            return return_value
        parameter.Set(1 if active else 0)
        if active and offsets:
            manager.LeftAnnotationCropOffset = convert_mm_to_imperial_feet(offsets["left"])
            manager.RightAnnotationCropOffset = convert_mm_to_imperial_feet(offsets["right"])
            manager.TopAnnotationCropOffset = convert_mm_to_imperial_feet(offsets["top"])
            manager.BottomAnnotationCropOffset = convert_mm_to_imperial_feet(offsets["bottom"])
        return_value.append_message("Annotation crop of {} set.".format(view.Name))
    except Exception as e:
        return_value.update_sep(False, "Failed to set the annotation crop of view {} with exception: {}".format(view.Name, e))
    return return_value
