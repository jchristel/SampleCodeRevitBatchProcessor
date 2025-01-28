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
)
from duHast.Revit.Areas.areas import get_views_by_area_scheme_name
from duHast.Revit.Areas.areas import get_area_schemes

from duHast.Revit.Rooms.Reporting.room_separation_lines import (
    room_lines_with_warnings_by_design_option_and_level,
)
from duHast.Revit.Rooms.room_lines import sort_room_separation_line_by_phase_created
from duHast.Revit.Common.phases import get_phase_name_by_id

from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import Element


def _print_area_line_table(
    output, table_name, column_names, table_data_lines, table_data_views
):
    """
    Print a pyRevit table showing area lines with warning by area scheme and the level they are placed on for ease of finding

    :param output: a pyRevit script output instance
    :type output: pyRevit output module
    :param table_name: The name of the table
    :type table_name: str
    :param column_names: A list of column names
    :type column_names: [str]
    :param table_data_lines: A dictionary containing the area line data by area scheme name and level name
    :type table_data_lines: {str:{str:[]}}
    :param table_data_views: A dictionary containing the view data by area scheme name and level name
    :type table_data_views: {str:{str:[]}}
    """
    # convert dictionary data to line data for table
    data = []
    for area_scheme_name, levels in table_data_lines.items():
        for level, lines in levels.items():
            row = [area_scheme_name, level]
            ids_str = []
            for line in lines:
                ids_str.append(str(line.Id.IntegerValue))
            row.append(";".join(ids_str))

            # get associated views if any:
            if area_scheme_name in table_data_views:
                views_by_level = table_data_views[area_scheme_name]
                if level in views_by_level:
                    views = views_by_level[level]
                    view_names = []
                    for view in views:
                        view_names.append(Element.Name.GetValue(view))
                    if len(view_names) == 0:
                        row.append("")
                    else:
                        row.append(";".join(view_names))
                else:
                    # add empty field for missing views
                    row.append("")
            else:
                # add empty field for missing views
                row.append("")

            # only display rows with data
            if len(ids_str) > 0:
                data.append(row)

    # check if there is any data
    if len(data) == 0:
        print("No area lines with warnings in model.")
        return

    format_by_columns = [""] * len(column_names)

    output.print_table(
        table_data=data,
        title=table_name,
        columns=column_names,
        formats=format_by_columns,
    )


def _views_by_area_scheme_and_level(doc):
    """
    Gets all views associated with area schemes by their associated level.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing views by area scheme name and level name
    :rtype: {str:{str:[]}}
    """
    views_by_area_scheme = {}

    # get all area schemes
    all_area_schemes = get_area_schemes(doc=doc)

    # get views by area scheme
    for scheme in all_area_schemes:
        views = get_views_by_area_scheme_name(doc=doc, area_scheme_name=scheme.Name)
        views_by_area_scheme[scheme.Name] = views

    views_by_area_scheme_and_level = {}
    # sort views by level name
    for area_scheme_name, views_by_area_scheme in views_by_area_scheme.items():
        views_by_level_name = {}
        for view in views_by_area_scheme:
            level = view.GenLevel
            level_name = "unknown"
            if level is not None:
                level_name = level.Name

            if level_name in views_by_level_name:
                views_by_level_name[level_name].append(view)
            else:
                views_by_level_name[level_name] = [view]

        views_by_area_scheme_and_level[area_scheme_name] = views_by_level_name

    return views_by_area_scheme_and_level


def report_area_lines_with_warnings_by_scheme_and_level(doc, output, forms):
    """
    Reports on area lines with warnings attached to them

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit progressbar
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if area lines with warnings where reported without an exception, otherwise False.
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
        # get report data
        lines_with_warnings = area_lines_with_warnings_by_schemes_and_by_levels(doc=doc)

        # check if anything is to visualize
        if len(lines_with_warnings) == 0:
            return_value.update_sep(True, "No area lines with warnings in the model.")
            print("No area lines with warnings in the model.")
            return return_value

        # get views associated by area scheme and level
        views_by_area_scheme_and_level = _views_by_area_scheme_and_level(doc=doc)

        # pyRevit table header names
        table_column_names = [
            "Area Scheme",
            "Level",
            "Ids of Area lines with warnings",
            "Area Views",
        ]

        # print table
        _print_area_line_table(
            output=output,
            table_name="Area lines with warnings by scheme and level",
            column_names=table_column_names,
            table_data_lines=lines_with_warnings,
            table_data_views=views_by_area_scheme_and_level,
        )

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


def _print_room_separation_lines_table(
    output, table_name, column_names, table_data_lines
):
    """
    Print room separation lines with warnings to a table.

    :param output: a pyRevit script output instance
    :type output: _type_
    :param table_name: The name of the table
    :type table_name: str
    :param column_names: A list of column names
    :type column_names: [str]
    :param table_data_lines: A dictionary containing the room separation line data by design set / option name, level name and phase created name
    :type table_data_lines: {str:{str:{str:[]}}}
    """

    # convert dictionary data to line data for table
    data = []

    for design_set_option, levels in table_data_lines.items():
        for level_name, lines_by_phase in levels.items():
            for phase, lines in lines_by_phase.items():
                row = [design_set_option, level_name, phase]
                ids_str = []
                for line in lines:
                    ids_str.append(str(line.Id.IntegerValue))
                row.append(";".join(ids_str))
                # only display rows with data
                if len(ids_str) > 0:
                    data.append(row)

    # check if there is any data
    if len(data) == 0:
        print("No room separation lines with warnings in model.")
        return

    format_by_columns = [""] * len(column_names)

    output.print_table(
        table_data=data,
        title=table_name,
        columns=column_names,
        formats=format_by_columns,
    )


def _sort_lines_by_phase_created(doc, rooms_separation_lines):
    """
    Sort lines by phase created.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param rooms_separation_lines: A dictionary where key is the option name, value is a nested dictionary where key is the level name and value is a list of room separation lines
    :type rooms_separation_lines: {str:{str:[Autodesk>Revit.DB.ModelCurve]}}

    :return:  A dictionary where key is the option name, value is a nested dictionary where key is the level name and value is another dictionary where key is the phase created and value is a list of room separation lines
    :rtype: {str:{str:{str:[Autodesk>Revit.DB.ModelCurve]}}}
    """

    room_sep_lines_by_design_set_level_phase_created = {}

    for design_set_option, levels in rooms_separation_lines.items():
        # add design set to return dictionary
        room_sep_lines_by_design_set_level_phase_created[design_set_option] = {}
        for level_name, lines_by_level in levels.items():
            # add level to return dictionary
            room_sep_lines_by_design_set_level_phase_created[design_set_option][
                level_name
            ] = {}
            # sort by phase created id:
            by_phase_id = sort_room_separation_line_by_phase_created(lines_by_level)
            for phase_id, lines_by_phase_created in by_phase_id.items():
                phase_name = get_phase_name_by_id(doc=doc, phase_id=phase_id)
                room_sep_lines_by_design_set_level_phase_created[design_set_option][
                    level_name
                ][phase_name] = lines_by_phase_created

    return room_sep_lines_by_design_set_level_phase_created


def report_room_lines_with_warnings_by_design_option_level_phase_created(
    doc, output, forms
):
    """
    Reports on room separation lines with warnings attached to them

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit progressbar
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if room separation lines with warnings where reported without an exception, otherwise False.
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

        # get report data
        lines_with_warnings_by_design_set_option_and_level = (
            room_lines_with_warnings_by_design_option_and_level(doc=doc)
        )

        # split report data further and add phase created into levels
        lines_with_warnings_by_design_set_option_level_phase_created = _sort_lines_by_phase_created(
            doc=doc,
            rooms_separation_lines=lines_with_warnings_by_design_set_option_and_level,
        )

        # pyRevit table header names
        table_column_names = [
            "Design Set & Option",
            "Level",
            "Phase Created",
            "Ids of Room separation lines with warnings",
        ]

        # print table
        _print_room_separation_lines_table(
            output=output,
            table_name="Room separation lines with warnings by design set / option, level and phase created",
            column_names=table_column_names,
            table_data_lines=lines_with_warnings_by_design_set_option_level_phase_created,
        )

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to get room separation lines with warnings with exception: {}".format(
                e
            ),
        )

    if return_value.status == False:
        print(return_value.message)
    print("Finished")

    return return_value
