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
#: report file name suffix : view filters
PARAM_ACTIONS_FILENAME_NO_OF_VIEW_FILTERS = "_NumberOfViewFilters"
#: report file name suffix : view filters unused
PARAM_ACTIONS_FILENAME_NO_OF_VIEW_FILTERS_UNUSED = "_NumberOfViewFiltersUnused"
#: report file name suffix : text styles
PARAM_ACTIONS_FILENAME_NO_OF_TEXT_STYLES = "_NumberOfTextStyles"
#: report file name suffix : view filters unused
PARAM_ACTIONS_FILENAME_NO_OF_TEXT_STYLES_UNUSED = "_NumberOfTextStylesUnused"
#: report file name suffix : dimension styles
PARAM_ACTIONS_FILENAME_NO_OF_DIMENSION_STYLES = "_NumberOfDimStyles"
#: report file name suffix : dimension unused
PARAM_ACTIONS_FILENAME_NO_OF_DIMENSION_STYLES_UNUSED = "_NumberOfDimStylesUnused"
#: report file name suffix : arrow head styles
PARAM_ACTIONS_FILENAME_NO_OF_ARROW_HEAD_STYLES = "_NumberOfArrowHeadStyles"
#: report file name suffix : arrow head styles unused
PARAM_ACTIONS_FILENAME_NO_OF_ARROW_HEAD_STYLES_UNUSED = "_NumberOfArrowHeadStylesUnused"
#: report file name suffix : view templates
PARAM_ACTIONS_FILENAME_NO_OF_VIEW_TEMPLATES = "_NumberOfViewTemplates"
#: report file name suffix : view template unused
PARAM_ACTIONS_FILENAME_NO_OF_VIEW_TEMPLATES_UNUSED = "_NumberOfViewTemplatesUnused"
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
    PARAM_ACTIONS_FILENAME_NO_OF_VIEW_FILTERS,
    PARAM_ACTIONS_FILENAME_NO_OF_VIEW_FILTERS_UNUSED,
    PARAM_ACTIONS_FILENAME_NO_OF_VIEW_TEMPLATES,
    PARAM_ACTIONS_FILENAME_NO_OF_VIEW_TEMPLATES_UNUSED,
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
    PARAM_ACTIONS_FILENAME_NO_OF_ARROW_HEAD_STYLES,
    PARAM_ACTIONS_FILENAME_NO_OF_ARROW_HEAD_STYLES_UNUSED,
    PARAM_ACTIONS_FILENAME_NO_OF_TEXT_STYLES,
    PARAM_ACTIONS_FILENAME_NO_OF_TEXT_STYLES_UNUSED,
    PARAM_ACTIONS_FILENAME_NO_OF_DIMENSION_STYLES,
    PARAM_ACTIONS_FILENAME_NO_OF_DIMENSION_STYLES_UNUSED,
}
