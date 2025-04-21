
from duHast.Revit.DetailItems.curve_create import draw_2D_lines_on_bounding_box, draw_2D_lines_on_bounding_box_and_separate_point


def draw_bounding_box_around_filled_region(doc, active_view, filled_region):
    # get the bounding box of the filled region
    bounding_box = filled_region.get_BoundingBox(active_view)
    result_draw = draw_2D_lines_on_bounding_box(doc, bounding_box, active_view)
    

