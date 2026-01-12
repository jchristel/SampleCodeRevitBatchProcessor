


from Autodesk.Revit.DB import (BuiltInCategory, ElementCategoryFilter, FamilyInstance, FilteredElementCollector)

from duHast.Revit.Common.parameter_get_utils import get_parameter_value_by_name, getter_double_as_double
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm


def get_window_families_by_host_id(doc, filter_by_family_name=None):
    """
    Retrieves all window family symbols in the given Revit document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of window family symbols.
    :rtype: list of Autodesk.Revit.DB.FamilySymbol
    """
    
    
    filter = ElementCategoryFilter(BuiltInCategory.OST_Windows)
    col = (
        FilteredElementCollector(doc)
        .OfClass(FamilyInstance)
        .WherePasses(filter)
    )
    col_list =[]
    if filter_by_family_name:
        col_list = [f for f in col if f.Symbol.Family.Name in filter_by_family_name]
    else:
        col_list = [f for f in col]

    windows_by_host = {}

    for window in col_list:
        host_id = window.Host.Id.Value
        if host_id not in windows_by_host:
            windows_by_host[host_id] = []
        windows_by_host[host_id].append(window)
    
    return windows_by_host





def window_area_instance(doc, family_instance):
    """
    Calculates the area of a window instance where the width is instance but the height is type

    :param window_instance: The window family instance.
    :type window_instance: Autodesk.Revit.DB.FamilyInstance

    :return: Area of the window in square m.
    :rtype: float
    """

    try:
       
        window_width= get_parameter_value_by_name(family_instance, "HSL_WIDTH", getter_double_as_double)
        window_height= get_parameter_value_by_name(family_instance, "HSL_HEIGHT", getter_double_as_double)

        #print("Width: {}, Height: {}".format(window_width, window_height))
        
        if window_width and window_height:
            area = convert_imperial_feet_to_metric_mm(window_width) * convert_imperial_feet_to_metric_mm(window_height)
            
            # return in square meters
            area_in_sqm = area/1000000.0
            #print("Area in sqm: {}".format(area_in_sqm))

            return area_in_sqm
       
       
    except Exception as e:
        print("Error: window instance: {}".format(e))
        return 0.0

def window_area_type (doc, family_instance):
    """
    Calculates the area of a window type where the width and height are type parameters
    :param window_instance: The window family instance.
    :type window_instance: Autodesk.Revit.DB.FamilyInstance
    :return: Area of the window in square m.
    :rtype: float
    """

    try:
        window_width= get_parameter_value_by_name(family_instance.Symbol, "HSL_WIDTH", getter_double_as_double)
        window_height= get_parameter_value_by_name(family_instance.Symbol, "HSL_HEIGHT", getter_double_as_double)

        #print("Width: {}, Height: {}".format(window_width, window_height))
        
        if window_width and window_height:
            area = convert_imperial_feet_to_metric_mm(window_width) * convert_imperial_feet_to_metric_mm(window_height)
            
            # return in square meters
            area_in_sqm = area/1000000.0
            #print("Area in sqm: {}".format(area_in_sqm))

            return area_in_sqm
    except Exception as e:
        print("Error: window type: {}".format(e))
        return 0.0