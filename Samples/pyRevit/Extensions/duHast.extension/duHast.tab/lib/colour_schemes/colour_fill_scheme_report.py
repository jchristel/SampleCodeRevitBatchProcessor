

from Autodesk.Revit.DB import ElementId


from colour_schemes.Objects.colour_fill_storage import ColourFillStorage

def get_report_data_of_colour_fill_scheme(doc, colour_fill_scheme):

    """
    Retrieves the report data from a given colour fill scheme.

    :param colour_fill_scheme: The colour fill scheme element from which to retrieve report data.
    :type colour_fill_scheme: Autodesk.Revit.DB.ColorFillScheme
    :return: A dictionary containing the report data.
    :rtype: dict
    """

    # get the report data
    report_data = []


    # get the area scheme id
    area_scheme_id = colour_fill_scheme.AreaSchemeId
    
    area_scheme_name = "unknown"
    if area_scheme_id is not ElementId.InvalidElementId:
        # get the area scheme name
        area_scheme = doc.GetElement(area_scheme_id)
        area_scheme_name = area_scheme.Name 
    

    # get all entries in the colour fill scheme
    entries = colour_fill_scheme.GetEntries()

    # loop over the entries and get the report data
    for entry in entries:
        entry_data = ColourFillStorage()
        entry_data.fill_scheme_name = colour_fill_scheme.Name
        entry_data.area_scheme_name = area_scheme_name
        entry_data.parameter_value = entry.GetStringValue()
        entry_data.fill_pattern_id = entry.FillPatternId.IntegerValue
        entry_data.is_in_use = entry.IsInUse
        entry_data.is_visible = entry.IsVisible
        entry_data.colour_red = entry.Color.Red
        entry_data.colour_green = entry.Color.Green
        entry_data.colour_blue = entry.Color.Blue
        report_data.append(entry_data)
        
    return report_data