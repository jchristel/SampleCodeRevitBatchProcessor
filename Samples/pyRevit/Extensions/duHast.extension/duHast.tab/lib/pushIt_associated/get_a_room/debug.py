from System.Collections.Generic import List

from duHast.Revit.DetailItems.curve_create import draw_2D_lines_on_bounding_box, draw_2D_lines_on_bounding_box_and_separate_point
from duHast.Revit.DetailItems.filled_regions import  get_filled_region_curve_loops
from duHast.Utilities.unit_conversion import  convert_mm_to_imperial_feet
from duHast.Revit.DetailItems.filled_regions_create import create_filled_region_by_view

from duHast.Revit.Common.Geometry.curve_loops import get_curve_loop_centroid, create_curve_loop_through_offset

from Autodesk.Revit.DB import CurveLoop

def draw_bounding_box_around_filled_region(doc, active_view, filled_region):
    # get the bounding box of the filled region
    bounding_box = filled_region.get_BoundingBox(active_view)
    result_draw = draw_2D_lines_on_bounding_box(doc, bounding_box, active_view)
    

def offset_curve_loop_and_draw_bounding_box_around_filled_region(doc, filled_region):

    filled_region_loops = get_filled_region_curve_loops(filled_region)

    loop_of_interest = filled_region_loops[0] if len(filled_region_loops) == 1 else filled_region_loops[1]
    
    offset_distance = 120  #convert_mm_to_imperial_feet(120)  
    centroid = get_curve_loop_centroid(loop_of_interest)
    try:

        print("offset_distance: ", offset_distance)
        print("centroid: ", centroid)
        print("loop_of_interest: ", loop_of_interest)

        new_loop = create_curve_loop_through_offset( loop_of_interest, offset_distance)
      
        
        curve_loop_net_list = List[CurveLoop]()
        curve_loop_net_list.Add(new_loop)
        
        filled_region_offset_result = create_filled_region_by_view(doc,  doc.ActiveView, curve_loop_net_list, filled_region.GetTypeId())
        print(filled_region_offset_result)
    except Exception as e:
        print(e)
        return False
    