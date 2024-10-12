"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Model health report metrics can either be displayed in a family where each parameter is assigned to a metric 
and or data can be exported to text files which can be used to visualize key metrics over time.

"""
#
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

import clr
import os
import System

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

from System.Collections.Generic import List
from collections import namedtuple

from Autodesk.Revit.DB import (
    ParameterValueProvider,
    BuiltInParameter,
    ElementId,
    ElementParameterFilter,
    FamilyInstance,
    FilteredElementCollector,
    FilterStringEquals,
    FilterStringRule,
)

from duHast.Utilities.Objects import result as res
from duHast.Revit.ModelHealth.Reporting import report_file_names as rFns
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.date_stamps import (
    get_file_date_stamp,
    get_date_stamp,
    FILE_DATE_STAMP_YYYYMMDD_SPACE,
    TIME_STAMP_HHMMSEC_COLON,
)

from duHast.Revit.ModelHealth.Reporting.Properties.view import (
    get_number_of_sheets,
    get_number_of_unused_view_filters,
    get_number_of_unplaced_views,
    get_number_of_unused_view_templates,
    get_number_of_view_filters,
    get_number_of_view_templates,
    get_number_of_views,
)

from duHast.Revit.ModelHealth.Reporting.Properties.rooms import (
    get_number_of_not_enclosed_rooms,
    get_number_of_redundant_rooms,
    get_number_of_rooms,
    get_number_of_unplaced_rooms,
)

from duHast.Revit.ModelHealth.Reporting.Properties.constants import (
    FAILED_TO_RETRIEVE_VALUE,
    MODEL_HEALTH_TRACKER_FAMILY,
)

from duHast.Revit.ModelHealth.Reporting.Properties.design_set_options import (
    get_number_of_design_options,
    get_number_of_design_sets,
)

from duHast.Revit.ModelHealth.Reporting.Properties.line_styles_types import (
    get_number_of_line_styles,
    get_number_of_fill_patterns,
    get_number_of_line_patterns,
)

from duHast.Revit.ModelHealth.Reporting.Properties.links_cad import (
    get_number_of_cad_imports,
    get_number_of_cad_links_to_model,
    get_number_of_cad_links_to_view,
)

from duHast.Revit.ModelHealth.Reporting.Properties.groups import (
    get_number_of_detail_groups,
    get_number_of_model_groups,
    get_number_of_unplaced_detail_groups,
    get_number_of_unplaced_model_groups,
)

from duHast.Revit.ModelHealth.Reporting.Properties.annotations import (
    get_number_of_dimension_types,
    get_number_of_unused_dimension_types,
    get_number_of_text_types,
    get_number_of_unused_text_types,
    get_number_of_arrow_head_types,
    get_number_of_unused_arrow_head_types,
)

from duHast.Revit.ModelHealth.Reporting.Properties.links_images import (
    get_number_of_image_imports,
    get_number_of_image_links,
)

from duHast.Revit.ModelHealth.Reporting.Properties.general import (
    get_number_of_warnings,
    get_current_date,
    get_workset_number,
    get_current_file_size,
)

from duHast.Revit.ModelHealth.Reporting.Properties.families import (
    get_number_of_families,
    get_number_of_in_place_families,
)

from duHast.Revit.ModelHealth.Reporting.Properties.detail_items import (
    get_number_of_filled_regions,
)


from duHast.Revit.Common.parameter_set_utils import set_parameter_value
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Revit.Common.revit_version import get_revit_version_number


def _cast_parameter_value(p_value):
    """
    Check if parameter is of type string ( currently the date only)
    and only cast to string if not...

    :param p_value: The parameter value
    :type p_value: unknown
    :return: The parameter value as a string
    :rtype: str
    """

    new_para_value = ""
    if p_value.GetType() != System.String:
        new_para_value = str(p_value)
    else:
        new_para_value = p_value
    return new_para_value


def get_instances_of_model_health(doc):
    """
    Gets all instances of the model health tracker family in a model.

    Built in parameter containing family name when filtering familyInstance elements:
    BuiltInParameter.ELEM_FAMILY_PARAM
    This is a faster filter in terms of performance then LINQ query refer to:
    https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list containing all model health tracker families in the model.
    :rtype: list of Autodesk.Revit.DB.FamilyInstance
    """

    provider = ParameterValueProvider(ElementId(BuiltInParameter.ELEM_FAMILY_PARAM))
    evaluator = FilterStringEquals()

    revit_version = get_revit_version_number(doc=doc)
    # define rule with a placeholder
    rule = None
    # ge the rule depending on Revit version
    if revit_version <= 2022:
        # use case sensitive flag
        rule = FilterStringRule(provider, evaluator, MODEL_HEALTH_TRACKER_FAMILY, True)
    else:
        # case sensitive flag has been removed in Revit 2023 onwards
        rule = FilterStringRule(provider, evaluator, MODEL_HEALTH_TRACKER_FAMILY)

    filter = ElementParameterFilter(rule)
    return (
        FilteredElementCollector(doc)
        .OfClass(FamilyInstance)
        .WherePasses(filter)
        .ToList()
    )


def get_parameters_of_instance(fam_instance, doc):
    """
    Updates parameter values of model tracker family instance.

    :param fam_instance: An instance of the model health tracker family.
    :type fam_instance: Autodesk.Revit.DB.FamilyInstance
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - .status True if all parameters where found on the family and got updated successfully or no update at all was required. Otherwise False.
        - .message will be 'Failed to get value for'

    :rtype: :class:`.Result`
    """

    result_value = res.Result()
    flag_update = False
    for p in fam_instance.GetOrderedParameters():
        # check if parameter is read only
        if p.IsReadOnly == False:
            # check an action to update this parameter value exists
            if PARAM_ACTIONS.ContainsKey(p.Definition.Name):
                try:
                    parameter_value = PARAM_ACTIONS[p.Definition.Name].get_data(doc)
                    if parameter_value != FAILED_TO_RETRIEVE_VALUE:
                        flag = set_parameter_value(
                            p, _cast_parameter_value(parameter_value), doc
                        )
                        result_value.update(flag)
                        flag_update = True
                    else:
                        result_value.update_sep(
                            False, "Failed to get value for " + p.Definition.Name
                        )
                except Exception as e:
                    result_value.update_sep(
                        False,
                        "Failed to update {} with exception: {}".format(
                            p.Definition.Name, e
                        ),
                    )
    if flag_update == False:
        result_value.message = "No family parameters where updated"
        result_value.status = True
    return result_value


# ----------------------------------------------
# main
# ----------------------------------------------

# set up a named tuple to store data in it
health_data_action = namedtuple("healthDataAction", "get_data report_file_name")

#: List of actions reporting model health metrics and their associated parameter name
PARAM_ACTIONS = {
    "ValueWorksets": health_data_action(
        get_workset_number, rFns.PARAM_ACTIONS_FILENAME_NO_OF_WORKSETS
    ),
    "ValueFileSize": health_data_action(
        get_current_file_size, rFns.PARAM_ACTIONS_FILENAME_FILE_SIZE
    ),
    "ValueWarnings": health_data_action(
        get_number_of_warnings, rFns.PARAM_ACTIONS_FILENAME_NO_OF_WARNINGS
    ),
    "ValueDesignSets": health_data_action(
        get_number_of_design_sets, rFns.PARAM_ACTIONS_FILENAME_NO_OF_DESIGN_SETS
    ),
    "ValueDesignOptions": health_data_action(
        get_number_of_design_options, rFns.PARAM_ACTIONS_FILENAME_NO_OF_DESIGN_OPTIONS
    ),
    "ValueSheets": health_data_action(
        get_number_of_sheets, rFns.PARAM_ACTIONS_FILENAME_NO_OF_SHEETS
    ),
    "ValueViews": health_data_action(
        get_number_of_views, rFns.PARAM_ACTIONS_FILENAME_NO_OF_VIEWS
    ),
    "ValueViewsNotPlaced": health_data_action(
        get_number_of_unplaced_views, rFns.PARAM_ACTIONS_FILENAME_NO_OF_VIEWS_NOT_PLACED
    ),
    "ValueViewFilters": health_data_action(
        get_number_of_view_filters, rFns.PARAM_ACTIONS_FILENAME_NO_OF_VIEW_FILTERS
    ),
    "ValueViewFiltersUnused": health_data_action(
        get_number_of_unused_view_filters,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_VIEW_FILTERS_UNUSED,
    ),
    "ValueViewTemplates": health_data_action(
        get_number_of_view_templates, rFns.PARAM_ACTIONS_FILENAME_NO_OF_VIEW_TEMPLATES
    ),
    "ValueViewTemplatesUnused": health_data_action(
        get_number_of_unused_view_templates,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_VIEW_TEMPLATES_UNUSED,
    ),
    "ValueLineStyles": health_data_action(
        get_number_of_line_styles, rFns.PARAM_ACTIONS_FILENAME_NO_OF_LINE_STYLES
    ),
    "ValueLinePatterns": health_data_action(
        get_number_of_line_patterns, rFns.PARAM_ACTIONS_FILENAME_NO_OF_LINE_PATTERNS
    ),
    "ValueFillPatterns": health_data_action(
        get_number_of_fill_patterns, rFns.PARAM_ACTIONS_FILENAME_NO_OF_FILL_PATTERNS
    ),
    "ValueCADImports": health_data_action(
        get_number_of_cad_imports, rFns.PARAM_ACTIONS_FILENAME_NO_OF_CAD_IMPORTS
    ),
    "ValueCADLinksToModel": health_data_action(
        get_number_of_cad_links_to_model,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_CAD_LINKS_MODEL,
    ),
    "ValueCADLinksToView": health_data_action(
        get_number_of_cad_links_to_view,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_CAD_LINKS_VIEW,
    ),
    "ValueImageImports": health_data_action(
        get_number_of_image_imports, rFns.PARAM_ACTIONS_FILENAME_NO_OF_IMAGE_IMPORTS
    ),
    "ValueImageLinks": health_data_action(
        get_number_of_image_links, rFns.PARAM_ACTIONS_FILENAME_NO_OF_IMAGE_LINKS
    ),
    "ValueFamilies": health_data_action(
        get_number_of_families, rFns.PARAM_ACTIONS_FILENAME_NO_OF_FAMILIES
    ),
    "ValueFamiliesInPlace": health_data_action(
        get_number_of_in_place_families,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_FAMILIES_IN_PLACE,
    ),
    "ValueModelGroups": health_data_action(
        get_number_of_model_groups, rFns.PARAM_ACTIONS_FILENAME_NO_OF_MODEL_GROUPS
    ),
    "ValueModelGroupsUnplaced": health_data_action(
        get_number_of_unplaced_model_groups,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_MODEL_GROUPS_UNPLACED,
    ),
    "ValueDetailGroups": health_data_action(
        get_number_of_detail_groups, rFns.PARAM_ACTIONS_FILENAME_NO_OF_DETAIL_GROUPS
    ),
    "ValueDetailGroupsUnplaced": health_data_action(
        get_number_of_unplaced_detail_groups,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_DETAIL_GROUPS_UNPLACED,
    ),
    "ValueRooms": health_data_action(
        get_number_of_rooms, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS
    ),
    "ValueRoomsUnplaced": health_data_action(
        get_number_of_unplaced_rooms, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNPLACED
    ),
    "ValueRoomsNotEnclosed": health_data_action(
        get_number_of_not_enclosed_rooms,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNENCLOSED,
    ),
    "ValueRoomsRedundant": health_data_action(
        get_number_of_redundant_rooms, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_REDUNDANT
    ),
    "ValueFilledRegions": health_data_action(
        get_number_of_filled_regions, rFns.PARAM_ACTIONS_FILENAME_NO_OF_FILLED_REGIONS
    ),
    "ValueDimensionStyles": health_data_action(
        get_number_of_dimension_types,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_DIMENSION_STYLES,
    ),
    "ValueDimensionStylesUnused": health_data_action(
        get_number_of_unused_dimension_types,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_DIMENSION_STYLES_UNUSED,
    ),
    "ValueTextStyles": health_data_action(
        get_number_of_text_types, rFns.PARAM_ACTIONS_FILENAME_NO_OF_TEXT_STYLES
    ),
    "ValueTextStylesUnused": health_data_action(
        get_number_of_unused_text_types,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_TEXT_STYLES_UNUSED,
    ),
    "ValueArrowHeadStyles": health_data_action(
        get_number_of_arrow_head_types,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_ARROW_HEAD_STYLES,
    ),
    "ValueArrowHeadStylesUnused": health_data_action(
        get_number_of_unused_arrow_head_types,
        rFns.PARAM_ACTIONS_FILENAME_NO_OF_ARROW_HEAD_STYLES_UNUSED,
    ),
    "ValueDateLastUpdated": health_data_action(
        get_current_date, rFns.PARAM_ACTIONS_FILENAME_DATE_LAST_UPDATED
    ),
}


def update_model_health_tracer_family(doc, revit_file_path):
    """
    Updates instances of model health tracker family in project.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: Fully qualified revit model file path.
    :type revit_file_path: str

    :return:
        Result class instance.

        - .status True if all model key health metric where updated successfully. Otherwise False.
        - .message will be listing each parameter update: old value to new value

    :rtype: :class:`.Result`
    """

    revit_file_name = get_file_name_without_ext(revit_file_path)
    result_value = res.Result()
    instances = get_instances_of_model_health(doc)
    if len(instances) > 0:
        for instance in instances:
            try:
                update_flag = get_parameters_of_instance(instance, doc)
                result_value.update(update_flag)
            except Exception as e:
                result_value.update_sep(False, "{}".format(e))
    else:
        result_value.update_sep(
            False,
            "Family to update: {} was not found in model: {}".format(
                MODEL_HEALTH_TRACKER_FAMILY, revit_file_name
            ),
        )
    return result_value


# doc   current document
# revitFilePath     path of the current document
def write_model_health_report(doc, revit_file_path, output_directory):
    """
    Write out health tracker data to file.

    Each value gets written to a separate file. The file name is made up of time stamp and the revit file name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: Fully qualified revit model file path.
    :type revit_file_path: str
    :param output_directory: The directory path of where to write the data to.
    :type output_directory: str

    :return:
        Result class instance.

        - .status True if data was written to files successfully. Otherwise False.
        - .message will be contain data file path for each file.

    :rtype: :class:`.Result`
    """

    revit_file_name = get_file_name_without_ext(revit_file_path)
    result_value = res.Result()
    # get values and write them out
    for key, value in PARAM_ACTIONS.items():
        # parameter value get may throw an exception
        # record -1 in that case!
        try:
            parameter_value = PARAM_ACTIONS[key].get_data(doc)
        except Exception as e:
            parameter_value = FAILED_TO_RETRIEVE_VALUE
        file_name = (
            get_file_date_stamp()
            + revit_file_name
            + PARAM_ACTIONS[key].report_file_name
            + ".temp"
        )
        res_export = res.Result()
        try:
            write_report_data_as_csv(
                os.path.join(output_directory, file_name),
                rFns.LOG_FILE_HEADER,
                [
                    [
                        revit_file_name,
                        key,
                        get_date_stamp(FILE_DATE_STAMP_YYYYMMDD_SPACE),
                        get_date_stamp(TIME_STAMP_HHMMSEC_COLON),
                        _cast_parameter_value(parameter_value),
                    ]
                ],
            )

            res_export.update_sep(True, "Exported: {}".format(key))
        except Exception as e:
            res_export.update_sep(
                False, "Export failed: {} with exception: {}".format(key, e)
            )
        result_value.update(res_export)
    return result_value
