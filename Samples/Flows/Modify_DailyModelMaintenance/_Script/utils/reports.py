"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing reporting functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- sheets data
- sheets data short
- shared parameters
- levels
- grids
- families
- worksets

"""

# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

# required for .ToList() on FilteredElementCollector
import clr, os

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import Autodesk
import Autodesk.Revit.DB as rdb
from System.Collections.Generic import List

# import common library
import settings as settings  # sets up all commonly used variables and path locations!

import duHast.Utilities.Objects.result as res
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.files_csv import write_report_data_as_csv

from duHast.Revit.Views.Reporting.sheets_report import (
    write_sheet_data,
    write_sheet_data_by_property_names,
)
from duHast.Revit.SharedParameters.Reporting.shared_parameter_report import (
    get_shared_parameter_report_data,
)
from duHast.Revit.SharedParameters.Reporting.shared_parameter_report_header import (
    REPORT_SHARED_PARAMETERS_HEADER,
)
from duHast.Revit.Levels.Reporting.levels_report_utils import get_level_report_data
from duHast.Revit.Levels.Reporting.levels_report_header import REPORT_LEVELS_HEADER
from duHast.Revit.Grids.Reporting.grid_report_utils import get_grid_report_data
from duHast.Revit.Grids.Reporting.grids_report_header import REPORT_GRIDS_HEADER
from duHast.Revit.Family.Utility import loadable_family_categories as rFamUtilCats
from duHast.Revit.Family.family_utils import (
    get_family_symbols,
    get_family_instances_by_symbol_type_id,
)
from duHast.Revit.Common.parameter_get_utils import get_parameter_value_by_name
from duHast.Revit.Common.Reporting.worksets_report_utils import get_workset_report_data
from duHast.Revit.Common.Reporting.worksets_report_header import REPORT_WORKSETS_HEADER

from duHast.Revit.Views.Reporting.views_report import write_view_data_by_property_names
from duHast.Revit.Views.Reporting.views_data_report import (
    write_graphics_settings_report,
)
from duHast.Revit.Views.Utility.convert_revit_override_to_data import (
    get_views_graphic_settings_data,
)
from duHast.Revit.Views.templates import get_view_templates
from duHast.Revit.Walls.Reporting.walls_report import get_wall_report_data
from duHast.Revit.Walls.Reporting.walls_report_header import REPORT_WALLS_HEADER

from duHast.Revit.Warnings.Reporting.warnings_report import (
    get_warnings_report_data,
    write_warnings_data,
)

# tag reporting imports
from duHast.Revit.Annotation.Reporting.tags_independent_report import (
    get_tag_instances_report_data,
)
from duHast.Revit.Common import custom_element_filter_actions as elCustomFilterAction
from duHast.Revit.Common import custom_element_filter_tests as elCustomFilterTest
from duHast.Revit.Common import custom_element_filter as rCusFilter
from duHast.Utilities.files_json import write_json_to_file

from duHast.Revit.Links.Reporting import links_report_utils as rLinkRep
from duHast.Revit.Links.Reporting import links_report_header as rLinkHeader
from duHast.Revit.Links.Reporting import cad_links_report_utils as rLinkCadRep
from duHast.Revit.Links.Reporting import cad_links_report_header as rLinkCadHeader

from duHast.Utilities.utility import encode_utf8

def report_sheets(doc, revit_file_path, output):
    """
    Reports all sheet data in a file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting sheet data long...start")
    # build output file name
    file_name = (
        settings.OUTPUT_FOLDER
        + "\\"
        + get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_SHEETS
        + settings.REPORT_FILE_NAME_EXTENSION
    )
    task_value = write_sheet_data(
        doc, file_name, get_file_name_without_ext(revit_file_path)
    )
    return_value.update(task_value)
    return return_value


def report_sheets_short(doc, revit_file_path, output):
    """
    Reports all sheet data in a file short version

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting sheet data short...start")
    # build output file name
    file_name = (
        settings.OUTPUT_FOLDER
        + "\\"
        + get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_SHEETS_SHORT
        + settings.REPORT_FILE_NAME_EXTENSION
    )
    task_value = write_sheet_data_by_property_names(
        doc,
        file_name,
        get_file_name_without_ext(revit_file_path),
        settings.SHEET_DATA_PROPERTIES,
    )
    return_value.update(task_value)
    return return_value


def report_shared_paras(doc, revit_file_path, output):
    """
    Reports all shared paras in a project file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting shared parameters...start")
    # build output file name
    file_name = (
        settings.OUTPUT_FOLDER
        + "\\"
        + get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_SHARED_PARAMETERS
        + settings.REPORT_FILE_NAME_EXTENSION
    )
    data = get_shared_parameter_report_data(doc, revit_file_path)
    try:
        write_report_data_as_csv(file_name, REPORT_SHARED_PARAMETERS_HEADER, data, "w")
        return_value.update_sep(
            True, "Successfully wrote shared parameter data to file."
        )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write shared parameter data with exception: {}".format(e)
        )
    return return_value


def report_levels(doc, revit_file_path, output):
    """
    Report on levels in model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting levels...start")
    file_name = (
        settings.OUTPUT_FOLDER
        + "\\"
        + get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_LEVELS
        + settings.REPORT_FILE_NAME_EXTENSION
    )
    data = get_level_report_data(doc, revit_file_path)
    try:
        write_report_data_as_csv(file_name, REPORT_LEVELS_HEADER, data, "w")
        return_value.update_sep(True, "Successfully wrote level data to file.")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write level data with exception: {}".format(e)
        )
    return return_value


def report_grids(doc, revit_file_path, output):
    """
    Report on grids in model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting grids...start")
    file_name = (
        settings.OUTPUT_FOLDER
        + "\\"
        + get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_GRIDS
        + settings.REPORT_FILE_NAME_EXTENSION
    )
    data = get_grid_report_data(doc, revit_file_path)
    try:
        write_report_data_as_csv(file_name, REPORT_GRIDS_HEADER, data, "w")
        return_value.update_sep(True, "Successfully wrote grid data to file.")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write grid data with exception: {}".format(e)
        )
    return return_value


def report_families(doc, revit_file_path, output):
    """
    Get all loadable family ids in file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting families...start")
    file_name = (
        settings.OUTPUT_FOLDER
        + "\\"
        + get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_FAMILIES
        + settings.REPORT_FILE_NAME_EXTENSION
    )
    # build list of all categories we want families to be reloaded of
    famCats = List[rdb.BuiltInCategory](rFamUtilCats.CATEGORIES_LOADABLE_TAGS)
    famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_TAGS_OTHER)
    famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_3D)
    famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_3D_OTHER)

    # get all symbols in file
    family_symbols = get_family_symbols(doc, famCats)
    # get families from symbols and filter out in place families
    # get data in format:
    #   revit file name , family name, family symbol name, instances placed
    data = []
    revit_project_file_name = get_file_name_without_ext(revit_file_path)
    for family_symbol in family_symbols:
        row_data = []
        if family_symbol.Family.IsInPlace == False:
            custom_parameter_values = []
            for parameter_name in settings.FAMILY_PARAMETERS_TO_REPORT:
                parameter_value = get_parameter_value_by_name(
                    family_symbol, parameter_name
                )
                if parameter_value == None:
                    parameter_value = "NA"
                custom_parameter_values.append(parameter_value)

            family = doc.GetElement(family_symbol.Family.Id)
            collector_instances_placed = get_family_instances_by_symbol_type_id(
                doc, family_symbol.Id
            )
            count_instances = len(collector_instances_placed.ToList())
            category = family.FamilyCategory

            row_data = [
                revit_project_file_name,
                encode_utf8(rdb.Element.Name.GetValue(family)),
                category.Name,
                encode_utf8(rdb.Element.Name.GetValue(family_symbol)),
                str(count_instances),
            ]

            # insert parameter values at index 4
            if len(custom_parameter_values) > 0:
                row_data[4:4] = custom_parameter_values

            data.append(row_data)
    try:
        header = [
            "Project File Name",
            "Family Name",
            "Family Category",
            "Family Type Name",
            "Number of Instances Placed",
        ]
        # insert custom parameter names to headers if any
        if len(settings.FAMILY_PARAMETERS_TO_REPORT) > 0:
            header[4:4] = settings.FAMILY_PARAMETERS_TO_REPORT

        write_report_data_as_csv(
            file_name=file_name,
            header=header,
            data=data,
            write_type="w",
        )
        return_value.update_sep(True, "Successfully wrote family data to file.")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write family data with exception: {}".format(e)
        )
    return return_value


def report_worksets(doc, revit_file_path, output):
    """
    Report on worksets in model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`

    """

    return_value = res.Result()
    output("Reporting worksets...start")
    file_name = (
        settings.OUTPUT_FOLDER
        + "\\"
        + get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_WORKSETS
        + settings.REPORT_FILE_NAME_EXTENSION
    )
    data = get_workset_report_data(doc, revit_file_path)
    try:
        write_report_data_as_csv(file_name, REPORT_WORKSETS_HEADER, data, "w")
        return_value.update_sep(True, "Successfully wrote workset data to file.")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write workset data with exception: {}".format(e)
        )
    return return_value


def report_views_filtered(doc, revit_file_path, output):
    """
    Reports all views in the model with filtered properties.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)
    """

    return_value = res.Result()
    output("Reporting views...start")

    file_name = os.path.join(
        settings.OUTPUT_FOLDER,
        get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_VIEWS
        + settings.REPORT_FILE_NAME_EXTENSION,
    )
    try:
        # get sheet report headers
        task_value = write_view_data_by_property_names(
            doc,
            file_name,
            revit_file_path,
            settings.VIEW_DATA_FILTERS,
        )
        return_value.update(task_value)
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write view data with exception: {}".format(e)
        )
    return return_value


def report_wall_types(doc, revit_file_path, output):
    """
    Reports all wall types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting wall type data...start")
    file_name = os.path.join(
        settings.OUTPUT_FOLDER,
        get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_WALL_TYPES
        + settings.REPORT_FILE_NAME_EXTENSION,
    )
    # get wall report headers
    data = get_wall_report_data(doc, get_file_name_without_ext(revit_file_path))
    try:
        write_report_data_as_csv(file_name, REPORT_WALLS_HEADER, data, "w")
        return_value.update_sep(True, "Successfully wrote wall type data to file.")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write wall type data with exception: {}".format(e)
        )
    return return_value


def report_revit_link_data(doc, revit_file_path, output):
    """
    Reports all wall types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting revit link data...start")
    try:
        file_name = os.path.join(
            settings.OUTPUT_FOLDER,
            get_file_name_without_ext(revit_file_path)
            + settings.REPORT_EXTENSION_REVIT_LINKS,
            +settings.REPORT_FILE_NAME_EXTENSION,
        )
        write_report_data_as_csv(
            file_name,
            rLinkHeader.REPORT_REVIT_LINKS_HEADER,
            rLinkRep.get_revit_link_report_data(doc, revit_file_path),
        )
        return_value.update_sep(True, "Successfully wrote Revit link data to file.")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write Revit link data with exception: {}".format(e)
        )

    return return_value


def report_cad_link_data(doc, revit_file_path, output):
    """
    Reports all wall types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting CAD link data...start")
    try:
        file_name = os.path.join(
            settings.OUTPUT_FOLDER,
            get_file_name_without_ext(revit_file_path)
            + settings.REPORT_EXTENSION_CAD_LINKS,
            +settings.REPORT_FILE_NAME_EXTENSION,
        )
        write_report_data_as_csv(
            file_name,
            rLinkCadHeader.REPORT_CAD_LINKS_HEADER,
            rLinkCadRep.get_cad_report_data(doc, revit_file_path),
        )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write CAD link data with exception: {}".format(e)
        )

    return return_value


def _action_family_type_name_contains(doc, element_id, output):
    """
    Set up a function checking whether tag type name contains

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: id of element to be checked against condition
    :type element_id: Autodesk.Revit.DB.ElementId

    :return: True if element name contain 'tbc', otherwise False
    :rtype: bool
    """

    test = elCustomFilterAction.action_element_property_contains_any_of_values(
        [settings.MULTI_CATEGORY_TAG_TYPE_NAME],
        elCustomFilterTest.value_in_name,
        output,
    )

    flag = test(doc, element_id)
    return flag


def report_ffe_tags(doc, revit_file_path, output):
    """
    Reports ffe tag data. This should be called before families are reloaded in order to restore the original tag location after the family reload if required.
    A family reload may move the tag if the family origin has changed.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting ffe tag instance data...start")
    file_name = os.path.join(
        settings.OUTPUT_FOLDER,
        get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_FFE_TAG_INSTANCES
        + settings.TEMP_FILE_NAME_EXTENSION,
    )

    # define in line function to get access to output within filter
    def filter_action(doc, element_id):
        # set up a tag filter by name
        return _action_family_type_name_contains(doc, element_id, output)

    FILTER_TAGS = rCusFilter.RevitCustomElementFilter([filter_action])

    # get instance report data
    tag_data = get_tag_instances_report_data(
        doc=doc,
        revit_file_path=revit_file_path,
        custom_element_filter=FILTER_TAGS,
    )
    try:
        write_json_file_result = write_json_to_file(
            json_data=tag_data, data_output_file_path=file_name
        )
        return_value.update(write_json_file_result)
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write tag instance data with exception: {}".format(e)
        )
    return return_value


def report_template_overrides(doc, revit_file_path, output):
    """
    Reports category and filter overrides to all templates which support that.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting template data...start")

    revit_file_name = get_file_name_without_ext(revit_file_path)
    # check if document requires view templates to be exported
    export_vt = False
    for name in settings.VIEW_TEMPLATE_FILE_LIST:
        if revit_file_name in name:
            export_vt = True
            break

    if export_vt:
        file_name = os.path.join(
            settings.OUTPUT_FOLDER,
            revit_file_name
            + settings.REPORT_EXTENSION_VIEW_TEMPLATE_OVERRIDES
            + settings.REPORT_FILE_NAME_EXTENSION,
        )

        # get view templates which allow for graphical overrides
        view_templates_in_model = get_view_templates(doc)
        view_template_filtered = []
        for vt in view_templates_in_model:
            if vt.AreGraphicsOverridesAllowed():
                view_template_filtered.append(vt)

        # get view template data
        data = get_views_graphic_settings_data(doc, view_template_filtered)

        # write data to file
        try:
            write_json_file_result = write_graphics_settings_report(
                revit_file_name=revit_file_name,
                file_path=file_name,
                data=data,
            )
            return_value.update(write_json_file_result)
        except Exception as e:
            return_value.update_sep(
                False, "Failed to write view template data with exception: {}".format(e)
            )
    else:
        return_value.update_sep(
            True,
            "Document: {} is not marked for view template reporting".format(
                revit_file_name
            ),
        )

    return return_value


def report_warning_types(doc, revit_file_path, output):
    """
    Reports all warning types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model document file path
    :type revit_file_path: str
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Reporting warning types...start")
    file_name = os.path.join(
        settings.OUTPUT_FOLDER,
        get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_WARNING_TYPES
        + settings.REPORT_FILE_NAME_EXTENSION,
    )
    # get wall report headers
    data = get_warnings_report_data(doc, get_file_name_without_ext(revit_file_path))
    try:
        write_data = write_warnings_data(file_name, data)
        return_value.update(write_data)
    except Exception as e:
        return_value.update_sep(
            False, "Failed to write warning type data with exception: {}".format(e)
        )
    return return_value
