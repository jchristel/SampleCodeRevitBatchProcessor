"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Category data utility module containing functions to read category data from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reads family category data into  list of named tuples.

root_family:

- name 
- category 
- filePath 
- parent 
- child
- subcategories

nested_family:

- name 
- category
- filePath
- rootPath
- categoryPath
- hostFamily
- subcategories

reads change category directives into list of named tuples:

change_family_category:

- filePath
- newCategoryName

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

from collections import namedtuple

from duHast.Utilities import (
    files_csv as fileCSV,
    files_get as fileGet,
    files_io as fileIO,
)

# tuples containing change family category data read from file
change_family_category = namedtuple(
    "change_family_category", "filePath newCategoryName"
)

# tuples containing change family subcategory data read from file
change_family_sub_category = namedtuple(
    "change_family_sub_category", "familyCategory oldSubCategoryName newSubCategoryName"
)

# tuples used to build category data
graphic_property_rgb = namedtuple("graphic_property_rgb", "red green blue")
graphic_property_line_weight = namedtuple(
    "graphic_property_line_weight", "cut projection"
)
graphic_property_material = namedtuple("graphic_property_material", "id name")
graphic_property_three_d_cut_projection = namedtuple(
    "graphicProperty", "threeD cut projection"
)
# container for category properties
sub_category_properties_container = namedtuple(
    "subCategoryProperties", "rgb lineWeight material graphic"
)
# the actual subcategory representing single row in report
sub_category = namedtuple(
    "sub_category",
    "parentCategoryName subCategoryName subCategoryId usageCounter usedBy subCategoryProperties ",
)

# a root family
root_family = namedtuple(
    "root_family", "name category filePath parent child subcategories"
)
# a nested family
nested_family = namedtuple(
    "nested_family",
    "name category filePath rootPath categoryPath hostFamily subcategories",
)

# row structure of family change category directive file
CATEGORY_CHANGE_DATA_LIST_INDEX_FAMILY_FILE_PATH = 0
CATEGORY_CHANGE_DATA_LIST_INDEX_NEW_FAMILY_CATEGORY = 1

# row structure of family change subcategory directive file
SUBCATEGORY_CHANGE_DATA_LIST_INDEX_FAMILY_CATEGORY = 0
SUBCATEGORY_CHANGE_DATA_LIST_INDEX_OLD_SUBCATEGORY_NAME = 1
SUBCATEGORY_CHANGE_DATA_LIST_INDEX_NEW_SUBCATEGORY_NAME = 2

# row structure of family category data file
CATEGORY_DATA_LIST_INDEX_ROOT_PATH = 0
CATEGORY_DATA_LIST_INDEX_ROOT_CATEGORY_PATH = 1
CATEGORY_DATA_LIST_INDEX_FAMILY_NAME = 2
CATEGORY_DATA_LIST_INDEX_FAMILY_FILE_PATH = 3
CATEGORY_DATA_LIST_INDEX_USAGE_COUNTER = 4
CATEGORY_DATA_LIST_INDEX_USED_BY = 5
CATEGORY_DATA_LIST_INDEX_CATEGORY_NAME = 6
CATEGORY_DATA_LIST_INDEX_SUBCATEGORY_NAME = 7
CATEGORY_DATA_LIST_INDEX_SUBCATEGORY_ID = 8
category_data_list_index_graphic_property_3_d = 9
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_CUT = 10
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_PROJECTION = 11
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_MATERIAL_NAME = 12
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_MATERIAL_ID = 13
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_LINE_WEIGHT_CUT = 14
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_LINE_WEIGHT_PROJECTION = 15
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_RGB_RED = 16
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_RGB_GREEN = 17
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_RGB_BLUE = 18

# file name identifiers for family base data
FAMILY_CATEGORY_DATA_FILE_NAME_PREFIX = "FamilyCategories"
FAMILY_CATEGORY_DATA_FILE_EXTENSION = ".csv"

# file name identifiers for category change directives
CATEGORY_CHANGE_DIRECTIVE_FILE_NAME_PREFIX = "CategoryChangeDirective"
CATEGORY_CHANGE_DIRECTIVE_FILE_EXTENSION = ".csv"

# file name identifiers for subcategory change directives
SUBCATEGORY_CHANGE_DIRECTIVE_FILE_NAME_PREFIX = "SubCategoryChangeDirective"
SUBCATEGORY_CHANGE_DIRECTIVE_FILE_EXTENSION = ".csv"

# exceptions
EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES = (
    "Families change directive list files do not exist."
)
EXCEPTION_EMPTY_CHANGE_DIRECTIVE_DATA_FILES = (
    "Empty Families change directive data file(s)!"
)

EXCEPTION_NO_FAMILY_CATEGORY_DATA_FILES = (
    "Families category data list files do not exist."
)
EXCEPTION_EMPTY_FAMILY_CATEGORY_DATA_FILES = "Empty Families category data list file!"
EXCEPTION_NO_FAMILY_SUBCATEGORY_DATA_FILES = (
    "Families subcategory data list files do not exist."
)
EXCEPTION_EMPTY_FAMILY_SUBCATEGORY_DATA_FILES = (
    "Empty Families subcategory data list file!"
)


# -------------------------------- read category data set ----------------------------------------------------------------

# sample root and nested family tuple usage / set up
# set up subcategory properties
"""
dataRGB = graphic_property_rgb(120,120,120)
dataLineWeight = graphic_property_line_weight(3,6)
dataMaterial = graphic_property_material(-1,'')
dataGraphic = graphic_property_three_d_cut_projection(None,None,None)
# combine into a container
dataSubPropertiesContainer = sub_category_properties_container (dataRGB, dataLineWeight, dataMaterial, dataGraphic)
# set up the actual sub category ( single row in report )
dataSubCatSample = sub_category('Parent Cat Name', 'subCat name', 1234, dataSubPropertiesContainer)
# set up a root family tuple
dataRootFam = root_family('root family name', 'root family category', 'file path', [], [], [dataSubCatSample])
# set up a nested family tuple
dataNestedFam = nested_family('nested family name', 'nested family category', 'file path', 'root Path', 'category Path','host Family data', [dataSubCatSample])
"""
# end samples


def _create_root_family_from_data(data_row):
    """
    Sets up a root family tuple from data row past in.

    :param data_row: A row from the category report.
    :type data_row: [str]

    :return: a root_family tuple
    :rtype: named tuple :root_family
    """
    # need to check if this is a category belonging to the current family or a new family??
    fam = root_family(
        data_row[CATEGORY_DATA_LIST_INDEX_FAMILY_NAME],
        data_row[CATEGORY_DATA_LIST_INDEX_CATEGORY_NAME],
        data_row[CATEGORY_DATA_LIST_INDEX_FAMILY_FILE_PATH],
        [],  # set up an empty list for parent families
        [],  # set up an empty list for child families
        [],  # set up empty list for sub-categories
    )
    return fam


def _create_nested_family_from_data(data_row):
    """
    Sets up a nested family tuple from data row past in.

    :param data_row: A row from the category report.
    :type data_row: [str]

    :return: a nested family tuple
    :rtype: named tuple :nested_family
    """

    # found a child family
    fam = nested_family(
        data_row[CATEGORY_DATA_LIST_INDEX_FAMILY_NAME],
        data_row[CATEGORY_DATA_LIST_INDEX_CATEGORY_NAME],
        data_row[CATEGORY_DATA_LIST_INDEX_FAMILY_FILE_PATH],
        data_row[CATEGORY_DATA_LIST_INDEX_ROOT_PATH].split(
            " :: "
        ),  # split root path into list for ease of searching
        data_row[CATEGORY_DATA_LIST_INDEX_ROOT_CATEGORY_PATH].split(
            " :: "
        ),  # split category path into list for ease of searching
        [],  # set up an empty list for host families
        [],  # set up empty list for sub-categories
    )
    return fam


def _setup_family_from_data(data_row):
    """
    Creates a nested family or root family tuple from data row past in.

    :param data_row: A row from the category report.
    :type data_row: [str]

    :return: A nested or root family tuple.
    :rtype: named tuple
    """

    fam = None
    if "::" not in data_row[CATEGORY_DATA_LIST_INDEX_ROOT_PATH]:
        fam = _create_root_family_from_data(data_row)
    else:
        # found a child family
        fam = _create_nested_family_from_data(data_row)
    return fam


def _build_sub_category_properties_from_data(data_row):
    """
    Generates a subcategory tuple based on data row past in.

    :param data_row: A row from the category report.
    :type data_row: [str]

    :return: A sub_category tuple.
    :rtype: named tuple
    """

    # read category data first
    # get colour RGB values
    data_rgb = graphic_property_rgb(
        data_row[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_RGB_RED],
        data_row[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_RGB_GREEN],
        data_row[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_RGB_BLUE],
    )
    # get line weight values
    data_line_weight = graphic_property_line_weight(
        data_row[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_LINE_WEIGHT_CUT],
        data_row[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_LINE_WEIGHT_PROJECTION],
    )
    # get material values
    data_material = graphic_property_material(
        data_row[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_MATERIAL_ID],
        data_row[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_MATERIAL_NAME],
    )
    # get graphic properties
    data_graphic = graphic_property_three_d_cut_projection(
        data_row[category_data_list_index_graphic_property_3_d],
        data_row[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_CUT],
        data_row[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_PROJECTION],
    )
    # put all of the above together
    data_sub_properties_container = sub_category_properties_container(
        data_rgb, data_line_weight, data_material, data_graphic
    )
    # set up the actual sub category ( single row in report )
    data_sub_cat_sample = sub_category(
        data_row[CATEGORY_DATA_LIST_INDEX_CATEGORY_NAME],
        data_row[CATEGORY_DATA_LIST_INDEX_SUBCATEGORY_NAME],
        data_row[CATEGORY_DATA_LIST_INDEX_SUBCATEGORY_ID],
        data_row[CATEGORY_DATA_LIST_INDEX_USAGE_COUNTER],
        data_row[CATEGORY_DATA_LIST_INDEX_USED_BY],
        data_sub_properties_container,
    )
    return data_sub_cat_sample


def _get_category_data_file_name(directory_path):
    """
    Gets the first family base data file in provided directory or any of it's sub directories.

    :param directory_path: Fully qualified directory path.
    :type directory_path: str
    :raises Exception: EXCEPTION_NO_FAMILY_BASE_DATA_FILES

    :return: Fully qualified file path to family base data file.
    :rtype: str
    """

    # get all base data files in folder
    files = fileGet.get_files_from_directory_walker_with_filters(
        directory_path,
        FAMILY_CATEGORY_DATA_FILE_NAME_PREFIX,
        "",
        FAMILY_CATEGORY_DATA_FILE_EXTENSION,
    )

    if len(files) > 0:
        return files[0]
    else:
        raise Exception(EXCEPTION_NO_FAMILY_CATEGORY_DATA_FILES)


def read_overall_family_data_list(file_path):
    """
    Reads list of families from family category data report file into named tuples.

    :param file_path: Fully qualified file path to family category data report file.
    :type file_path: str
    :raises Exception: "Families category data list files does not exist."
    :raises Exception: "Empty Families category data list file!"
    :return: Two lists: first list of named tuples contain family root data, second list contains family nested data.
    :rtype: [root_family], [nested_family]
    """

    rows = []
    if fileIO.file_exist(file_path):
        rows = fileCSV.read_csv_file(file_path)
    else:
        raise Exception(EXCEPTION_NO_FAMILY_CATEGORY_DATA_FILES)
    if len(rows) > 0:
        pass
    else:
        raise Exception(EXCEPTION_EMPTY_FAMILY_CATEGORY_DATA_FILES)

    return_value_root_family = []
    return_value_nested_family = []
    # pointer to the current family
    current_fam = None
    for i in range(1, len(rows)):
        # set up the actual sub category ( single row in report )
        data_sub_cat_sample = _build_sub_category_properties_from_data(rows[i])
        # get name and category as unique identifier
        fam_id = (
            rows[i][CATEGORY_DATA_LIST_INDEX_FAMILY_NAME]
            + rows[i][CATEGORY_DATA_LIST_INDEX_CATEGORY_NAME]
        )
        # check if this is the current family ...
        # this assumes family category data in report file is ordered by family!!!
        if current_fam == None:
            # and set up a new one:
            current_fam = _setup_family_from_data(rows[i])
            # append category data to new family
            current_fam.subcategories.append(data_sub_cat_sample)
        elif current_fam.name + current_fam.category == fam_id:
            # append category data to existing family
            current_fam.subcategories.append(data_sub_cat_sample)
        else:
            # if not:
            # append family to one of the list to be returned
            if isinstance(current_fam, root_family):
                return_value_root_family.append(current_fam)
            else:
                return_value_nested_family.append(current_fam)
            # and set up a new one:
            current_fam = _setup_family_from_data(rows[i])
            # append category data to new family
            current_fam.subcategories.append(data_sub_cat_sample)
    return return_value_root_family, return_value_nested_family


def read_overall_family_category_data_from_directory(directory_path):
    """
    Reads the first family category data file it finds in a folder.
    Note: This method calls ReadOverallFamilyDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directory_path: A fully qualified directory path containing family category data file(s)
    :type directory_path: _str

    :return: Two lists: first list of named tuples contain family root data, second list contains family nested data.
    :rtype: [root_family], [nested_family]
    """

    file_name = _get_category_data_file_name(directory_path)
    return read_overall_family_data_list(file_name)


# -------------------------------- read family category change directives ----------------------------------------------------------------


def read_overall_change_category_directives_list(file_paths):
    """
    Reads list of family change category directives from files into named tuples.

    :param file_path: List of fully qualified file path to family change category directive file.
    :type file_path: [str]
    :raises Exception: "Families change directive list files do not exist."
    :raises Exception: "Empty Families category data list file!"

    :return: List of named tuples contain family category change directive.
    :rtype: [change_family_category]
    """

    rows = []
    match_any_file = False
    for file_path in file_paths:
        if fileIO.file_exist(file_path):
            # set flag that we at least found one file
            match_any_file = True
            rows_file = fileCSV.read_csv_file(file_path)
            result = list(rows)
            result.extend(item for item in rows_file if item not in result)
            rows = result

    # check if any files found
    if match_any_file == False:
        raise Exception(EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES)

    # check if files contained any data
    if len(rows) > 0:
        # populate change directive tuples
        return_value_change_directives = []
        for row in rows:
            change_directive = change_family_category(
                row[CATEGORY_CHANGE_DATA_LIST_INDEX_FAMILY_FILE_PATH],
                row[CATEGORY_CHANGE_DATA_LIST_INDEX_NEW_FAMILY_CATEGORY],
            )
            return_value_change_directives.append(change_directive)
    else:
        raise Exception(EXCEPTION_EMPTY_CHANGE_DIRECTIVE_DATA_FILES)

    return return_value_change_directives


def _get_category_change_directive_file_names(directory_path):
    """
    Gets change category directive file in provided directory or any of it's sub directories.

    :param directory_path: Fully qualified directory path.
    :type directory_path: str
    :raises Exception: _EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES

    :return: List of fully qualified file path to family change category directive files.
    :rtype: [str]
    """

    # get all base data files in folder
    files = fileGet.get_files_from_directory_walker_with_filters(
        directory_path,
        CATEGORY_CHANGE_DIRECTIVE_FILE_NAME_PREFIX,
        "",
        CATEGORY_CHANGE_DIRECTIVE_FILE_EXTENSION,
    )
    if len(files) > 0:
        return files
    else:
        raise Exception(EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES)


def read_overall_family_category_change_directives_from_directory(directory_path):
    """
    Reads all category change directive file it finds in a folder.
    Note: This method calls ReadOverallFamilyDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directory_path: A fully qualified directory path containing family category change directive file(s)
    :type directory_path: _str

    :return: list of named tuples contain family category change directives.
    :rtype: [change_family_category]
    """

    file_names = _get_category_change_directive_file_names(directory_path)
    return read_overall_change_category_directives_list(file_names)


# -------------------------------- read family subcategory change directives ----------------------------------------------------------------


def read_overall_family_sub_category_change_directives_from_directory(directory_path):
    """
    Reads all subcategory change directive file it finds in a folder.
    Note: This method calls ReadOverallFamilyDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directory_path: A fully qualified directory path containing family category change directive file(s)
    :type directory_path: _str

    :return: list of named tuples contain family sub category change directives.
    :rtype: [change_family_sub_category]
    """

    file_names = _get_sub_category_change_directive_file_names(directory_path)
    return read_overall_change_sub_category_directives_list(file_names)


def _get_sub_category_change_directive_file_names(directory_path):
    """
    Gets change subcategory directive file in provided directory or any of it's sub directories.

    :param directory_path: Fully qualified directory path.
    :type directory_path: str
    :raises Exception: _EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES

    :return: List of fully qualified file path to family change sub category directive files.
    :rtype: [str]
    """

    # get all base data files in folder
    files = fileGet.get_files_from_directory_walker_with_filters(
        directory_path,
        SUBCATEGORY_CHANGE_DIRECTIVE_FILE_NAME_PREFIX,
        "",
        SUBCATEGORY_CHANGE_DIRECTIVE_FILE_EXTENSION,
    )
    if len(files) > 0:
        return files
    else:
        raise Exception(EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES)


def read_overall_change_sub_category_directives_list(file_paths):
    """
    Reads list of family change subcategory directives from files into named tuples.

    :param file_path: List of fully qualified file path to family change category directive file.
    :type file_path: [str]
    :raises Exception: _EXCEPTION_NO_FAMILY_SUBCATEGORY_DATA_FILES
    :raises Exception: _EXCEPTION_EMPTY_FAMILY_SUBCATEGORY_DATA_FILES

    :return: List of named tuples containing family subcategory change directive.
    :rtype: [change_family_sub_category]
    """

    rows = []
    match_any_file = False
    for file_path in file_paths:
        if fileIO.file_exist(file_path):
            # set flag that we at least found one file
            match_any_file = True
            rows_file = fileCSV.read_csv_file(file_path)
            result = list(rows)
            result.extend(item for item in rows_file if item not in result)
            rows = result

    # check if any files found
    if match_any_file == False:
        raise Exception(EXCEPTION_NO_FAMILY_SUBCATEGORY_DATA_FILES)

    # check if files contained any data
    if len(rows) > 0:
        # populate change directive tuples
        return_value_change_directives = []
        for row in rows:
            change_directive = change_family_sub_category(
                row[SUBCATEGORY_CHANGE_DATA_LIST_INDEX_FAMILY_CATEGORY],
                row[SUBCATEGORY_CHANGE_DATA_LIST_INDEX_OLD_SUBCATEGORY_NAME],
                row[SUBCATEGORY_CHANGE_DATA_LIST_INDEX_NEW_SUBCATEGORY_NAME],
            )
            return_value_change_directives.append(change_directive)
    else:
        raise Exception(EXCEPTION_EMPTY_FAMILY_SUBCATEGORY_DATA_FILES)

    return return_value_change_directives


def get_families_requiring_sub_category_change(
    root_families, sub_cat_change_directives
):
    """
    Returns a list of file path of root families containing subcategories requiring a rename.

    Note: list of file path returned is unique: i.e.  if a family has multiple matches for rename subcategory directives it will still only appear once in the list.

    :param root_families: List of tuples of root families.
    :type root_families: [root_family]
    :param sub_cat_change_directives: List of subcategory change directives.
    :type sub_cat_change_directives: [change_family_sub_category]

    :return: List of family file path.
    :rtype: [str]
    """

    root_families_needing_change = []
    # check each root family
    for root_fam in root_families:
        # against each subcategory change directive
        for change_d in sub_cat_change_directives:
            # check if match family category
            if root_fam.category == change_d.familyCategory:
                # loop over subcategories in family and check if any of them needs renaming
                for sub_cat_root in root_fam.subcategories:
                    if sub_cat_root.subCategoryName == change_d.oldSubCategoryName:
                        # found a match
                        if root_fam.filePath not in root_families_needing_change:
                            root_families_needing_change.append(root_fam.filePath)
                        break
    return root_families_needing_change
