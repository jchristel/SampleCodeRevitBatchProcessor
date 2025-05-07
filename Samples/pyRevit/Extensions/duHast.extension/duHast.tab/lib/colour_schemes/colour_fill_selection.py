
from duHast.Utilities.Objects.result import Result

from colour_schemes.colour_fill_schemes import get_all_colour_schemes

def user_select_colour_scheme(doc, forms):
    
    return_value = Result()
    # get the colour schemes
    colour_schemes = get_all_colour_schemes(doc)

    # check if there are any colour schemes
    if not colour_schemes:
        return_value.update_sep(False, "No colour schemes found.")
        return return_value

    # get the area scheme name per colour fill scheme
    colour_schemes_by_area_scheme = {}

    for colour_scheme in colour_schemes:
        # get the area scheme id
        area_scheme_id = colour_scheme.AreaSchemeId

        # get the area scheme name
        area_scheme = doc.GetElement(area_scheme_id)

        # check if the area scheme is valid
        if not area_scheme:
            continue

        # get the area scheme name
        area_scheme_name = area_scheme.Name

        # add the colour scheme to the list of colour schemes for the area scheme
        colour_schemes_by_area_scheme["{} <{}>".format(colour_scheme.Name, area_scheme_name)] = colour_scheme


    # get the colour scheme to export
    colour_scheme_name_selected = forms.SelectFromList.show(
        [name for name, colour_schemes in colour_schemes_by_area_scheme.items()],
        title="Select Colour Scheme",
        multiselect=False,
        ok_text="Export",
        cancel_text="Cancel"
    )

    # check if the user cancelled the selection
    if not colour_scheme_name_selected :
        return return_value.update_sep(False, "User cancelled selection.")

    # get the selected colour scheme
    selected_colour_scheme = colour_schemes_by_area_scheme[colour_scheme_name_selected ]
    return_value.append_message("Colour scheme selected: {}".format(selected_colour_scheme.Name))
    return_value.result.append(selected_colour_scheme)

    return return_value