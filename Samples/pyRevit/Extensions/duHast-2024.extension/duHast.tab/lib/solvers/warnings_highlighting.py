# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

from duHast.Revit.Areas.Reporting.area_separation_lines import (
    area_lines_with_warnings_by_schemes_and_by_levels,
    area_lines_by_schemes_and_by_levels,
)
from duHast.Revit.Views.views import get_area_scheme_of_view, get_view_phase_id
from duHast.Revit.Views.element_overrides import overwrite_element_graphics_in_view
from duHast.Revit.Rooms.Reporting.room_separation_lines import (
    room_lines_with_warnings_by_design_option_and_level,
    room_lines_without_warnings_by_design_option_and_level,
)
from duHast.Revit.Rooms.room_lines import filter_room_separation_lines_by_phase_created
from duHast.Revit.Common.design_set_options import (
    get_active_design_option,
    get_design_set_from_option,
)
from duHast.Revit.Common.Objects.design_set_property_names import DesignSetPropertyNames
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.phases import get_all_phases_in_order

from Autodesk.Revit.DB import Color, OverrideGraphicSettings, ViewType


def highlight_area_lines_with_warnings_in_current_view(doc, output, forms):
    """
    Applies an override by view to area lines with warnings attached to them

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit progressbar
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if area lines with warnings where highlighted without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.

    :rtype: :class:`.Result`

    """

    # set up a status tracker
    return_value = Result()

    try:
        # check if the active view is of view type areaplan
        active_view = doc.ActiveView
        if active_view.ViewType != ViewType.AreaPlan:
            return_value.append_message("Active view is not an area plan view.")
            print("{} Exiting".format(return_value.message))
            return return_value

        # get the views active level
        associated_level = active_view.GenLevel
        associated_level_name = associated_level.Name

        # get the area scheme of the view
        view_area_scheme = get_area_scheme_of_view(doc=doc, view=active_view)
        print("Area scheme of active view: {}".format(view_area_scheme.Name))
        # get report data
        lines_with_warnings = area_lines_with_warnings_by_schemes_and_by_levels(doc=doc)

        # check if anything is to visualize
        if len(lines_with_warnings) == 0:
            return_value.update_sep(True, "No area lines with warnings in the model.")
            print("{} Exiting".format(return_value.message))
            return return_value

        # check if there are any area lines with warnings in view
        area_lines_with_warnings_in_view = lines_with_warnings.get(
            view_area_scheme.Name, {}
        ).get(associated_level_name, None)
        return_value.append_message(
            "Found {} area lines with warnings in view.".format(
                len(area_lines_with_warnings_in_view)
            )
        )
        if len(area_lines_with_warnings_in_view) == 0:
            print("{} Exiting".format(return_value.message))
            return return_value

        # set up default override settings ( which will remove any override if applied)
        override_graphics_settings = None

        # override lines in view in red
        override_graphics_settings = OverrideGraphicSettings()
        override_graphics_settings.SetProjectionLineColor(Color(255, 0, 0))

        # override or remove the overrides
        override_status = overwrite_element_graphics_in_view(
            doc=doc,
            view=active_view,
            elements=area_lines_with_warnings_in_view,
            override_graphics_settings=override_graphics_settings,
        )
        return_value.update(override_status)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to get area separation lines with warnings with exception: {}".format(
                e
            ),
        )

    print(return_value.message)
    print("Finished")
    return return_value


def remove_highlight_area_lines_with_warnings_in_current_view(doc, output, forms):
    """
    Removes any overrides by view to area lines without warnings attached to them

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit progressbar
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if area lines without warnings had their highlight removed without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    """

    # set up a status tracker
    return_value = Result()

    try:
        # check if the active view is of view type areaplan
        active_view = doc.ActiveView
        if active_view.ViewType != ViewType.AreaPlan:
            return_value.append_message("Active view is not an area plan view.")
            print("{} Exiting".format(return_value.message))
            return return_value

        # get the views active level
        associated_level = active_view.GenLevel
        associated_level_name = associated_level.Name

        # get the area scheme of the view
        view_area_scheme = get_area_scheme_of_view(doc=doc, view=active_view)

        # get area lines with warnings data
        lines_with_warnings = area_lines_with_warnings_by_schemes_and_by_levels(doc=doc)

        # get all area lines by scheme and level
        all_area_lines_by_scheme_and_level = area_lines_by_schemes_and_by_levels(
            doc=doc
        )

        # get lines associated by area scheme and level ( if nothing is found check for None or empty list)
        all_lines_on_level = all_area_lines_by_scheme_and_level.get(
            view_area_scheme.Name, {}
        ).get(associated_level_name, None)
        lines_with_warnings = lines_with_warnings.get(view_area_scheme.Name, {}).get(
            associated_level_name, None
        )

        if all_lines_on_level is None or len(all_lines_on_level) == 0:
            return_value.append_message(
                "Found 0 area lines without warnings in view.Exiting"
            )
            return return_value

        lines_to_remove_override = []
        # check if any area lines with warnings are about
        if lines_with_warnings is None or len(lines_with_warnings) == 0:
            lines_to_remove_override = all_lines_on_level
        else:
            # Check if any element from list1 is in list2 by Id property
            lines_to_remove_override = [
                item1
                for item1 in all_lines_on_level
                if not any(item1.Id == item2.Id for item2 in lines_with_warnings)
            ]

        if (lines_to_remove_override) == 0:
            return_value.append_message(
                "Found 0 area lines without warnings in view.Exiting"
            )
            return return_value

        # set up default override settings ( which will remove any override if applied)
        override_graphics_settings = None

        # override or remove the overrides
        override_status = overwrite_element_graphics_in_view(
            doc=doc,
            view=active_view,
            elements=lines_to_remove_override,
            override_graphics_settings=override_graphics_settings,
        )
        return_value.update(override_status)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to get area separation lines with warnings with exception: {}".format(
                e
            ),
        )

    print(return_value.message)
    print("Finished")
    return return_value


def filter_lines_by_all_phases_to_consider(doc, room_separation_lines, phase_names):
    """
    Filters past in list of room separation lines by phase created.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param room_separation_lines: A list of room separation lines to be filtered.
    :type room_separation_lines: [Autodesk.Revit.DB.ModelCurve]
    :param phase_names: A list of phase names to be filtered by
    :type phase_names: [str]

    :return: A list of room separation lines which where created in the phases provided
    :rtype: [Autodesk.Revit.DB.ModelCurve]
    """

    filtered_room_separation_lines = []

    # find all room separation lines which have been created in the phases of interest
    for phase_name in phase_names:
        room_sep_in_phase = filter_room_separation_lines_by_phase_created(
            doc=doc,
            room_separation_lines=room_separation_lines,
            phase_created_name=phase_name,
        )
        if len(room_sep_in_phase) > 0:
            filtered_room_separation_lines = (
                filtered_room_separation_lines + room_sep_in_phase
            )

    return filtered_room_separation_lines


def _get_phases_to_consider(doc, view_phase_id):
    """
    returns all phases in chronological order from oldest to newest up to and including the phase of which the id was provided

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_phase_id: The upper bound phase id
    :type view_phase_id: Autodesk.Revit.ElementId

    :return: A list of phase names
    :rtype: [str]
    """

    phase_names = []
    # get all phases in model:
    phases_in_model = get_all_phases_in_order(doc=doc)
    for phase in phases_in_model:
        phase_names.append(phase[1])
        if phase[0] == view_phase_id:
            # get out
            break

    return phase_names


def _print_phase_names(phase_names):
    """
    Output phase names to be considered when searching for lines with warnings

    :param phase_names: List of phase names
    :type phase_names: [str]
    """

    print("Considering room separation lines created in following phases only:")
    for phase_name in phase_names:
        print("...{}".format(phase_name))


def _modify_room_lines_graphics(
    doc, room_lines, override_graphics_settings, output, forms
):
    """
    Applies an override by view to room lines with warnings attached to them

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :param room_lines: Current Revit model document.
    :type room_lines: [Autodesk.Revit.DB.ModelCurve]
    :param override_graphics_settings: Revit override settings.
    :type override_graphics_settings: Autodesk.Revit.DB.OverrideGraphicSettings
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if room separation lines graphics was changed in view without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`

    """

    # set up a status tracker
    return_value = Result()

    try:
        # check if the active view is of view type area plan
        active_view = doc.ActiveView
        if active_view.ViewType != ViewType.FloorPlan:
            return_value.append_message("Active view is not an floor plan view.")
            print("{} Exiting".format(return_value.message))
            return return_value

        # get the views active level
        associated_level = active_view.GenLevel
        associated_level_name = associated_level.Name
        print(
            "Considering room separation lines created on level: {} only.".format(
                associated_level_name
            )
        )

        # get the views phase
        view_phase_id = get_view_phase_id(view=active_view)

        # get the active design option
        active_design_option = get_active_design_option(doc=doc)

        # get the lines in the active design option only (if none is active go for main model only)
        # set a default key ( main model only)
        key = DesignSetPropertyNames.combine_set_and_option_name(
            set_name=DesignSetPropertyNames.DESIGN_SET_DEFAULT_NAME,
            option_name=DesignSetPropertyNames.DESIGN_OPTION_DEFAULT_NAME,
        )

        # check if a design option is active and the key need changing
        if active_design_option:
            # just a design option...need to get the set as well to be able to filter dictionary of room lines
            # get the design set:
            design_set = get_design_set_from_option(
                doc=doc, design_option=active_design_option
            )
            key = DesignSetPropertyNames.combine_set_and_option_name(
                set_name=design_set.Name, option_name=active_design_option.Name
            )
        print(
            "Considering room separation lines created in  design option / set: {} only.".format(
                key
            )
        )

        # get lines with warnings in current design option
        lines_by_level_and_option = room_lines.get(key, [])
        if len(lines_by_level_and_option) == 0:
            return_value.append_message(
                "Active design option / set: {} has no room separation lines of interest.".format(
                    key
                )
            )
            print("{} Exiting".format(return_value.message))
            return return_value

        # get lines with warnings in current level
        lines_by_level = lines_by_level_and_option.get(associated_level_name, [])
        if len(lines_by_level) == 0:
            return_value.append_message(
                "Level: {} has no room separation lines of interest.".format(
                    associated_level_name
                )
            )
            print("{} Exiting".format(return_value.message))
            return return_value

        # filter room separation lines by phase of view and any prior phases
        # discard any lines in phase post view phase
        phases_to_consider = _get_phases_to_consider(doc, view_phase_id)
        # let the user know which phases are considered
        _print_phase_names(phase_names=phases_to_consider)
        room_separation_lines_of_interest = filter_lines_by_all_phases_to_consider(
            doc=doc,
            room_separation_lines=lines_by_level,
            phase_names=phases_to_consider,
        )
        if len(room_separation_lines_of_interest) == 0:
            return_value.append_message(
                "Active view phase {} has no room separation lines of interest.".format(
                    view_phase_id
                )
            )
            print("{} Exiting".format(return_value.message))
            return return_value

        # override or remove the overrides
        override_status = overwrite_element_graphics_in_view(
            doc=doc,
            view=active_view,
            elements=room_separation_lines_of_interest,
            override_graphics_settings=override_graphics_settings,
        )
        return_value.update(override_status)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to get area separation lines of interest with exception: {}".format(
                e
            ),
        )

    return return_value


def highlight_room_lines_with_warnings_in_current_view(doc, output, forms):
    """
    Applies an override by view to room lines with warnings attached to them.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit progressbar
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if room separation lines with warnings where highlighted without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    try:

        # all room lines with warnings:
        room_lines_with_warnings_by_design_op_and_level = (
            room_lines_with_warnings_by_design_option_and_level(doc=doc)
        )

        # set up default override settings ( which will remove any override if applied)
        override_graphics_settings = None

        # override lines in view in red
        override_graphics_settings = OverrideGraphicSettings()
        override_graphics_settings.SetProjectionLineColor(Color(255, 0, 0))

        # override or remove the overrides
        override_status = _modify_room_lines_graphics(
            doc=doc,
            room_lines=room_lines_with_warnings_by_design_op_and_level,
            override_graphics_settings=override_graphics_settings,
            output=output,
            forms=forms,
        )

        return_value.update(override_status)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to modify graphical appearance of room separation lines with warnings with exception: {}".format(
                e
            ),
        )

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value


def remove_highlight_from_room_lines_without_warnings_in_current_view(
    doc, output, forms
):
    """
    Removes any overrides by view to room lines without warnings attached to them.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit progressbar
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if room separation lines without warnings had highlighted removed without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    try:

        # all room lines with warnings:
        room_lines_without_warnings_by_design_op_and_level = (
            room_lines_without_warnings_by_design_option_and_level(doc=doc)
        )

        # set up default override settings ( which will remove any override if applied)
        override_graphics_settings = None

        # override or remove the overrides
        override_status = _modify_room_lines_graphics(
            doc=doc,
            room_lines=room_lines_without_warnings_by_design_op_and_level,
            override_graphics_settings=override_graphics_settings,
            output=output,
            forms=forms,
        )

        return_value.update(override_status)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to modify graphical appearance of room separation lines without warnings with exception: {}".format(
                e
            ),
        )

    print("\n{}".format(return_value.message))
    print("Finished")
    return return_value
