"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Contains file names used by model health report.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

#: header for each report file
LOG_FILE_HEADER = ["HOSTFILE", "REPORT", "DATE", "TIME", "VALUE"]


#: report file name suffix : date last updated
PARAM_ACTIONS_FILENAME_DATE_LAST_UPDATED = "_DateLastUpdated"
#: report file name suffix : worksets
PARAM_ACTIONS_FILENAME_NO_OF_WORKSETS = "_NumberOfWorksets"
#: report file name suffix : file size
PARAM_ACTIONS_FILENAME_FILE_SIZE = "_FileSize"
#: report file name suffix : warnings
PARAM_ACTIONS_FILENAME_NO_OF_WARNINGS = "_NumberOfWarnings"
#: report file name suffix : design sets
PARAM_ACTIONS_FILENAME_NO_OF_DESIGN_SETS = "_NumberOfDesignSets"
#: report file name suffix : design options
PARAM_ACTIONS_FILENAME_NO_OF_DESIGN_OPTIONS = "_NumberOfDesignOptions"
#: report file name suffix : sheet
PARAM_ACTIONS_FILENAME_NO_OF_SHEETS = "_NumberOfSheets"
#: report file name suffix : views
PARAM_ACTIONS_FILENAME_NO_OF_VIEWS = "_NumberOfViews"
#: report file name suffix : views not placed
PARAM_ACTIONS_FILENAME_NO_OF_VIEWS_NOT_PLACED = "_NumberOfViewsNotPlaced"
#: report file name suffix : line styles
PARAM_ACTIONS_FILENAME_NO_OF_LINE_STYLES = "_NumberOfLineStyles"
#: report file name suffix : line patterns
PARAM_ACTIONS_FILENAME_NO_OF_LINE_PATTERNS = "_NumberOfLinePatterns"
#: report file name suffix : fill patterns
PARAM_ACTIONS_FILENAME_NO_OF_FILL_PATTERNS = "_NumberOfFillPatterns"
#: report file name suffix : CAD imports
PARAM_ACTIONS_FILENAME_NO_OF_CAD_IMPORTS = "_NumberOfCadImports"
#: report file name suffix : CAD links in model
PARAM_ACTIONS_FILENAME_NO_OF_CAD_LINKS_MODEL = "_NumberOfCadLinksModel"
#: report file name suffix : CAD links in view
PARAM_ACTIONS_FILENAME_NO_OF_CAD_LINKS_VIEW = "_NumberOfCadLinksView"
#: report file name suffix : image imports
PARAM_ACTIONS_FILENAME_NO_OF_IMAGE_IMPORTS = "_NumberOfImageImports"
#: report file name suffix : image links
PARAM_ACTIONS_FILENAME_NO_OF_IMAGE_LINKS = "_NumberOfImageLinks"
#: report file name suffix : families in model
PARAM_ACTIONS_FILENAME_NO_OF_FAMILIES = "_NumberOfFamilies"
#: report file name suffix : in place families in model
PARAM_ACTIONS_FILENAME_NO_OF_FAMILIES_IN_PLACE = "_NumberOfInPlaceFamilies"
#: report file name suffix : model groups
PARAM_ACTIONS_FILENAME_NO_OF_MODEL_GROUPS = "_NumberOfModelGroups"
#: report file name suffix : model groups unplaced
PARAM_ACTIONS_FILENAME_NO_OF_MODEL_GROUPS_UNPLACED = "_NumberOfUnplacedModelGroups"
#: report file name suffix : detail groups
PARAM_ACTIONS_FILENAME_NO_OF_DETAIL_GROUPS = "_NumberOfDetailGroups"
#: report file name suffix : detail groups unplaced
PARAM_ACTIONS_FILENAME_NO_OF_DETAIL_GROUPS_UNPLACED = "_NumberOfUnplacedDetailGroups"
#: report file name suffix : rooms
PARAM_ACTIONS_FILENAME_NO_OF_ROOMS = "_NumberOfRooms"
#: report file name suffix : unplaced rooms
PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNPLACED = "_NumberOfUnplacedRooms"
#: report file name suffix : not enclosed rooms
PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNENCLOSED = "_NumberOfNotEnclosedRooms"
#: report file name suffix : redundant rooms
PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_REDUNDANT = "_NumberOfRedundantRooms"
#: report file name suffix : filled regions
PARAM_ACTIONS_FILENAME_NO_OF_FILLED_REGIONS = "_NumberOfRegions"

# combined log file for all reports
PARAM_ACTIONS_FILENAME_MOTHER = "_AllLogs"


#: list of report file name extensions
PARAM_ACTIONS_FILENAMES = {
    PARAM_ACTIONS_FILENAME_NO_OF_WORKSETS,
    PARAM_ACTIONS_FILENAME_FILE_SIZE,
    PARAM_ACTIONS_FILENAME_NO_OF_WARNINGS,
    PARAM_ACTIONS_FILENAME_NO_OF_DESIGN_SETS,
    PARAM_ACTIONS_FILENAME_NO_OF_DESIGN_OPTIONS,
    PARAM_ACTIONS_FILENAME_NO_OF_SHEETS,
    PARAM_ACTIONS_FILENAME_NO_OF_VIEWS,
    PARAM_ACTIONS_FILENAME_NO_OF_VIEWS_NOT_PLACED,
    PARAM_ACTIONS_FILENAME_NO_OF_LINE_STYLES,
    PARAM_ACTIONS_FILENAME_NO_OF_LINE_PATTERNS,
    PARAM_ACTIONS_FILENAME_NO_OF_FILL_PATTERNS,
    PARAM_ACTIONS_FILENAME_NO_OF_CAD_IMPORTS,
    PARAM_ACTIONS_FILENAME_NO_OF_CAD_LINKS_MODEL,
    PARAM_ACTIONS_FILENAME_NO_OF_CAD_LINKS_VIEW,
    PARAM_ACTIONS_FILENAME_NO_OF_IMAGE_IMPORTS,
    PARAM_ACTIONS_FILENAME_NO_OF_IMAGE_LINKS,
    PARAM_ACTIONS_FILENAME_NO_OF_FAMILIES,
    PARAM_ACTIONS_FILENAME_NO_OF_FAMILIES_IN_PLACE,
    PARAM_ACTIONS_FILENAME_NO_OF_MODEL_GROUPS,
    PARAM_ACTIONS_FILENAME_NO_OF_MODEL_GROUPS_UNPLACED,
    PARAM_ACTIONS_FILENAME_NO_OF_DETAIL_GROUPS,
    PARAM_ACTIONS_FILENAME_NO_OF_DETAIL_GROUPS_UNPLACED,
    PARAM_ACTIONS_FILENAME_NO_OF_ROOMS,
    PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNPLACED,
    PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNENCLOSED,
    PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_REDUNDANT,
    PARAM_ACTIONS_FILENAME_NO_OF_FILLED_REGIONS,
    PARAM_ACTIONS_FILENAME_DATE_LAST_UPDATED,
}
