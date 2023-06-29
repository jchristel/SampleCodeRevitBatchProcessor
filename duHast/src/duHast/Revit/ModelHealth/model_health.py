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
# Copyright (c) 2021  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import clr
import os

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)
import System

from duHast.Revit.BIM360 import bim_360 as b360

# from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.Utilities.Objects import result as res
from duHast.Utilities import date_stamps as dateStamp, files_io as fileIO
from duHast.Revit.Common import design_set_options as rDoS
from duHast.Revit.Warnings import warnings as rWarn
from duHast.Revit.Common import worksets as rWork
from duHast.Revit.Views import sheets as rViewSheets
from duHast.Revit.Views import views as rViews
from duHast.Revit.LinePattern import line_patterns as rLinePat
from duHast.Revit.LinePattern import fill_patterns as rFill
from duHast.Revit.LinePattern import line_styles as rLineStyle
from duHast.Revit.Links import cad_links as rCadLink
from duHast.Revit.Links import image_links as rImageLink
from duHast.Revit.ModelHealth.Reporting import report_file_names as rFns
from duHast.Revit.Family import family_utils as rFams
from duHast.Revit.Common import groups as rGrp
from duHast.Revit.Rooms import rooms as rRooms
from duHast.Revit.DetailItems import detail_items as rDetItems
from duHast.Revit.Common import parameter_set_utils as rParaSet
from duHast.Utilities.files_csv import write_report_data_as_csv

import Autodesk.Revit.DB as rdb
from System.Collections.Generic import List
from collections import namedtuple

# constants

#: A revit family displaying the health metrics retrieved by this code.
MODEL_HEALTH_TRACKER_FAMILY = "Symbol_GraphicModelHealth_ANN"
#: Default value if unable to retrieve a health metric value from model
FAILED_TO_RETRIEVE_VALUE = -1


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

    provider = rdb.ParameterValueProvider(
        rdb.ElementId(rdb.BuiltInParameter.ELEM_FAMILY_PARAM)
    )
    evaluator = rdb.FilterStringEquals()
    rule = rdb.FilterStringRule(provider, evaluator, MODEL_HEALTH_TRACKER_FAMILY, True)
    filter = rdb.ElementParameterFilter(rule)
    return (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdb.FamilyInstance)
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

        - .result = True if all parameters where found on the family and got updated successfully or no update at all was required. Otherwise False.
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
                parameter_value = PARAM_ACTIONS[p.Definition.Name].get_data(doc)
                if parameter_value != FAILED_TO_RETRIEVE_VALUE:
                    flag = rParaSet.set_parameter_value(
                        p, _cast_parameter_value(parameter_value), doc
                    )
                    result_value.update(flag)
                    flag_update = True
                else:
                    result_value.update_sep(
                        False, "Failed to get value for " + p.Definition.Name
                    )
    if flag_update == False:
        result_value.message = "No family parameters where updated"
        result_value.status = True
    return result_value


# ----------------------------------------------
# model properties
# ----------------------------------------------

# --------------------------------------------- GENERAL ---------------------------------------------


def get_current_date(doc):
    """
    Get the current date

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: The current date in format YYYY_MM_DD.
    :rtype: str

    """
    return dateStamp.get_file_date_stamp(dateStamp.FILE_DATE_STAMP_YYYY_MM_DD)


def get_workset_number(doc):
    """
    Gets the number of worksets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: The number of worksets in a model.
    :rtype: int
    """

    return len(rWork.get_worksets(doc))


def get_file_size(doc):
    """
    Gets the file size in MB.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: File size in MB. On exception it will return -1
    :rtype: int
    """

    size = FAILED_TO_RETRIEVE_VALUE
    try:
        # get the path from the document
        # this will fail if not a file based doc or the document is detached
        revit_file_path = doc.PathName
        # check if bim 360 file
        if revit_file_path.StartsWith("BIM 360"):
            size = b360.get_model_file_size(doc)
        else:
            if fileIO.file_exist(revit_file_path):
                # get file size in MB
                size = fileIO.get_file_size(revit_file_path)
    except:
        pass
    return size


def get_number_of_warnings(doc):
    """
    Gets the number of warnings in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of warnings in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rWarn.get_warnings(doc))
    except:
        pass
    return number


def get_number_of_design_sets(doc):
    """
    Gets the number of design sets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of design sets in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rDoS.get_design_sets(doc))
    except:
        pass
    return number


def get_number_of_design_options(doc):
    """
    Gets the number of design options in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of design option in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rDoS.get_design_options(doc).ToList())
    except:
        pass
    return number


# --------------------------------------------- VIEWS ---------------------------------------------


def get_number_of_sheets(doc):
    """
    Gets the number of sheets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of sheets in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rViewSheets.get_all_sheets(doc).ToList())
    except:
        pass
    return number


def _view_filter(view):
    """
    generic view filter allowing all views to be selected

    :param view: not used!
    :type view: Autodesk.Revit.DB.View

    :return: returns always True
    :rtype: bool
    """
    return True


def get_number_of_views(doc):
    """
    Gets the number of views in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of views in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rViews.get_views_in_model(doc, _view_filter))
    except:
        pass
    return number


def get_number_of_unplaced_views(doc):
    """
    Gets the number of unplaced views in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced views in model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rViews.get_views_not_on_sheet(doc))
    except:
        pass
    return number


# --------------------------------------------- LINE STYLES / TYPES  ---------------------------------------------


def get_number_of_line_styles(doc):
    """
    Gets the number of line styles in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of line styles in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLineStyle.get_all_line_style_ids(doc))
    except:
        pass
    return number


def get_number_of_line_patterns(doc):
    """
    Gets the number of line patterns in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of line patterns in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinePat.get_all_line_patterns(doc))
    except:
        pass
    return number


def get_number_of_fill_patterns(doc):
    """
    Gets the number of fill pattern in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of fill pattern in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rFill.get_all_fill_pattern(doc))
    except Exception as e:
        pass
    return number


# --------------------------------------------- CAD links  ---------------------------------------------


def get_number_of_cad_imports(doc):
    """
    Gets the number of CAD imports in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of CAD imports in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rCadLink.get_cad_type_imports_only(doc))
    except:
        pass
    return number


def get_number_of_cad_links_to_model(doc):
    """
    Gets the number of CAD links by model in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of CAD links by model in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rCadLink.get_all_cad_link_type_in_model_only(doc))
    except:
        pass
    return number


def get_number_of_cad_links_to_view(doc):
    """
    Gets the number of CAD links by view in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of CAD links by view in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rCadLink.get_all_cad_link_type_by_view_only(doc))
    except:
        pass
    return number


# ---------------------------------------------  images  ---------------------------------------------


def get_number_of_image_imports(doc):
    """
    Gets the number of image imports in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of image imports in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rImageLink.get_all_image_link_type_imported_in_model(doc))
    except:
        pass
    return number


def get_number_of_image_links(doc):
    """
    Gets the number of image links in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of image links in model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rImageLink.get_all_image_link_type_linked_in_model(doc))
    except:
        pass
    return number


# ---------------------------------------------  Families  ---------------------------------------------


def get_number_of_families(doc):
    """
    Gets the number of families loaded into the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of families loaded into model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rFams.get_all_loadable_families(doc))
    except:
        pass
    return number


def get_number_of_in_place_families(doc):
    """
    Gets the number of in-place families the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of in-place in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rFams.get_all_in_place_families(doc))
    except:
        pass
    return number


# ---------------------------------------------  Groups  ---------------------------------------------


def get_number_of_detail_groups(doc):
    """
    Gets the number of detail group definitions the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of detail group definitions in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.get_detail_groups(doc))
    except:
        pass
    return number


def get_number_of_model_groups(doc):
    """
    Gets the number of model group definitions in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of model group definitions in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.get_model_groups(doc))
    except:
        pass
    return number


def get_number_of_unplaced_detail_groups(doc):
    """
    Gets the number of unplaced detail group definitions in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced detail group definitions in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.get_unplaced_detail_groups(doc))
    except:
        pass
    return number


def get_number_of_unplaced_model_groups(doc):
    """
    Gets the number of unplaced model group definitions in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced model group definitions in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.get_unplaced_model_groups(doc))
    except:
        pass
    return number


# ---------------------------------------------  Rooms  ---------------------------------------------


def get_number_of_rooms(doc):
    """
    Gets the number of rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of rooms in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.get_all_rooms(doc))
    except:
        pass
    return number


def get_number_of_unplaced_rooms(doc):
    """
    Gets the number of unplaced rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced rooms in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.get_unplaced_rooms(doc))
    except:
        pass
    return number


def get_number_of_redundant_rooms(doc):
    """
    Gets the number of redundant rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of redundant rooms in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.get_redundant_rooms(doc))
    except:
        pass
    return number


def get_number_of_not_enclosed_rooms(doc):
    """
    Gets the not enclosed number of rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of not enclosed rooms in the model. On exception it will return -1
    :rtype: int
    """

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.get_not_enclosed_rooms(doc))
    except:
        pass
    return number


# ---------------------------------------------  Detail Items  ---------------------------------------------


def get_number_of_filled_regions(doc):
    """
    Gets the number of filled region instances in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of filled region instances in the model. On exception it will return -1
    :rtype: int
    """
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rDetItems.get_filled_regions_in_model(doc))
    except:
        pass
    return number


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
        get_file_size, rFns.PARAM_ACTIONS_FILENAME_FILE_SIZE
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

        - .result = True if all model key health metric where updated successfully. Otherwise False.
        - .message will be listing each parameter update: old value to new value

    :rtype: :class:`.Result`
    """

    revit_file_name = fileIO.get_file_name_without_ext(revit_file_path)
    result_value = res.Result()
    instances = get_instances_of_model_health(doc)
    if len(instances) > 0:
        for instance in instances:
            update_flag = get_parameters_of_instance(instance, doc)
            result_value.update(update_flag)
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

        - .result = True if data was written to files successfully. Otherwise False.
        - .message will be contain data file path for each file.

    :rtype: :class:`.Result`
    """

    revit_file_name = fileIO.get_file_name_without_ext(revit_file_path)
    result_value = res.Result()
    # get values and write them out
    for key, value in PARAM_ACTIONS.items():
        parameter_value = PARAM_ACTIONS[key].get_data(doc)
        file_name = (
            dateStamp.get_file_date_stamp()
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
                        dateStamp.get_date_stamp(
                            dateStamp.FILE_DATE_STAMP_YYYYMMDD_SPACE
                        ),
                        dateStamp.get_date_stamp(dateStamp.TIME_STAMP_HHMMSEC_COLON),
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
