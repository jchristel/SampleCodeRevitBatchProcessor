'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Category data utility module containing functions to read category data from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reads family category data into  list of named tuples.

rootFamily:

- name 
- category 
- filePath 
- parent 
- child
- subcategories

nestedFamily:

- name 
- category
- filePath
- rootPath
- categoryPath
- hostFamily
- subcategories

reads change category directives into list of named tuples:

changeFamilyCategory:

- filePath
- newCategoryName

'''

#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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

from collections import namedtuple

from duHast.Utilities import FilesCSV as fileCSV, FilesGet as fileGet, FilesIO as util

# tuples containing change family category data read from file
changeFamilyCategory = namedtuple('changeFamilyCategory', 'filePath newCategoryName')

# tuples containing change family subcategory data read from file
changeFamilySubCategory = namedtuple('changeFamilySubCategory', 'familyCategory oldSubCategoryName newSubCategoryName')

# tuples used to build category data
graphicPropertyRGB = namedtuple('graphicPropertyRGB', 'red green blue')
graphicPropertyLineWeight = namedtuple('graphicPropertyLineWeight', 'cut projection')
graphicPropertyMaterial = namedtuple('graphicPropertyMaterial', 'id name')
graphicPropertyThreeDCutProjection = namedtuple('graphicProperty', 'threeD cut projection')
# container for category properties
subCategoryPropertiesContainer = namedtuple('subCategoryProperties', 'rgb lineWeight material graphic')
# the actual subcategory representing single row in report
subCategory = namedtuple('subCategory', 'parentCategoryName subCategoryName subCategoryId usageCounter usedBy subCategoryProperties ')

# a root family
rootFamily = namedtuple('rootFamily', 'name category filePath parent child subcategories')
# a nested family
nestedFamily = namedtuple('nestedFamily', 'name category filePath rootPath categoryPath hostFamily subcategories')

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
CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_3D = 9
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
FAMILY_CATEGORY_DATA_FILE_NAME_PREFIX = 'FamilyCategories'
FAMILY_CATEGORY_DATA_FILE_EXTENSION = '.csv'

# file name identifiers for category change directives
CATEGORY_CHANGE_DIRECTIVE_FILE_NAME_PREFIX = 'CategoryChangeDirective'
CATEGORY_CHANGE_DIRECTIVE_FILE_EXTENSION = '.csv'

# file name identifiers for subcategory change directives
SUBCATEGORY_CHANGE_DIRECTIVE_FILE_NAME_PREFIX = 'SubCategoryChangeDirective'
SUBCATEGORY_CHANGE_DIRECTIVE_FILE_EXTENSION = '.csv'

# exceptions
EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES = 'Families change directive list files do not exist.'
EXCEPTION_EMPTY_CHANGE_DIRECTIVE_DATA_FILES = 'Empty Families change directive data file(s)!'

EXCEPTION_NO_FAMILY_CATEGORY_DATA_FILES = 'Families category data list files do not exist.'
EXCEPTION_EMPTY_FAMILY_CATEGORY_DATA_FILES = 'Empty Families category data list file!'
EXCEPTION_NO_FAMILY_SUBCATEGORY_DATA_FILES = 'Families subcategory data list files do not exist.'
EXCEPTION_EMPTY_FAMILY_SUBCATEGORY_DATA_FILES = 'Empty Families subcategory data list file!'


# -------------------------------- read category data set ----------------------------------------------------------------

# sample root and nested family tuple usage / set up
# set up subcategory properties
'''
dataRGB = graphicPropertyRGB(120,120,120)
dataLineWeight = graphicPropertyLineWeight(3,6)
dataMaterial = graphicPropertyMaterial(-1,'')
dataGraphic = graphicPropertyThreeDCutProjection(None,None,None)
# combine into a container
dataSubPropertiesContainer = subCategoryPropertiesContainer (dataRGB, dataLineWeight, dataMaterial, dataGraphic)
# set up the actual sub category ( single row in report )
dataSubCatSample = subCategory('Parent Cat Name', 'subCat name', 1234, dataSubPropertiesContainer)
# set up a root family tuple
dataRootFam = rootFamily('root family name', 'root family category', 'file path', [], [], [dataSubCatSample])
# set up a nested family tuple
dataNestedFam = nestedFamily('nested family name', 'nested family category', 'file path', 'root Path', 'category Path','host Family data', [dataSubCatSample])
'''
#end samples

def _create_root_family_from_data(dataRow):
    '''
    Sets up a root family tuple from data row past in.

    :param dataRow: A row from the category report.
    :type dataRow: [str]

    :return: a rootFamily tuple
    :rtype: named tuple :rootFamily
    '''
    # need to check if this is a category belonging to the current family or a new family??
    fam = rootFamily(
        dataRow[CATEGORY_DATA_LIST_INDEX_FAMILY_NAME], 
        dataRow[CATEGORY_DATA_LIST_INDEX_CATEGORY_NAME], 
        dataRow[CATEGORY_DATA_LIST_INDEX_FAMILY_FILE_PATH],
        [], # set up an empty list for parent families
        [], # set up an empty list for child families
        [] # set up empty list for sub-categories
    )
    return fam

def _create_nested_family_from_data(dataRow):
    '''
    Sets up a nested family tuple from data row past in.

    :param dataRow: A row from the category report.
    :type dataRow: [str]

    :return: a nested family tuple
    :rtype: named tuple :nestedFamily
    '''

    # found a child family
    fam =  nestedFamily (
        dataRow[CATEGORY_DATA_LIST_INDEX_FAMILY_NAME], 
        dataRow[CATEGORY_DATA_LIST_INDEX_CATEGORY_NAME], 
        dataRow[CATEGORY_DATA_LIST_INDEX_FAMILY_FILE_PATH],
        dataRow[CATEGORY_DATA_LIST_INDEX_ROOT_PATH].split(' :: '), # split root path into list for ease of searching
        dataRow[CATEGORY_DATA_LIST_INDEX_ROOT_CATEGORY_PATH].split(' :: '), # split category path into list for ease of searching
        [], # set up an empty list for host families
        [] # set up empty list for sub-categories
    )
    return fam

def _setup_family_from_data(dataRow):
    '''
    Creates a nested family or root family tuple from data row past in.

    :param dataRow: A row from the category report.
    :type dataRow: [str]

    :return: A nested or root family tuple.
    :rtype: named tuple
    '''

    fam = None
    if( '::' not in dataRow[CATEGORY_DATA_LIST_INDEX_ROOT_PATH]):
        fam = _create_root_family_from_data(dataRow)
    else:
        # found a child family
        fam = _create_nested_family_from_data(dataRow)
    return fam

def _build_sub_category_properties_from_data(dataRow):
    '''
    Generates a subcategory tuple based on data row past in.

    :param dataRow: A row from the category report.
    :type dataRow: [str]

    :return: A subCategory tuple.
    :rtype: named tuple
    '''

    # read category data first
    # get colour RGB values
    dataRGB = graphicPropertyRGB(
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_RGB_RED],
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_RGB_GREEN],
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_RGB_BLUE]
    )
    # get line weight values
    dataLineWeight = graphicPropertyLineWeight(
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_LINE_WEIGHT_CUT],
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_LINE_WEIGHT_PROJECTION]
    )
    # get material values
    dataMaterial = graphicPropertyMaterial(
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_MATERIAL_ID],
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_MATERIAL_NAME]
    )
    # get graphic properties
    dataGraphic = graphicPropertyThreeDCutProjection(
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_3D],
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_CUT],
        dataRow[CATEGORY_DATA_LIST_INDEX_GRAPHIC_PROPERTY_PROJECTION]
    )
    # put all of the above together
    dataSubPropertiesContainer = subCategoryPropertiesContainer (
        dataRGB, 
        dataLineWeight, 
        dataMaterial, 
        dataGraphic
    )
    # set up the actual sub category ( single row in report )
    dataSubCatSample = subCategory(
        dataRow[CATEGORY_DATA_LIST_INDEX_CATEGORY_NAME], 
        dataRow[CATEGORY_DATA_LIST_INDEX_SUBCATEGORY_NAME], 
        dataRow[CATEGORY_DATA_LIST_INDEX_SUBCATEGORY_ID],
        dataRow[CATEGORY_DATA_LIST_INDEX_USAGE_COUNTER],
        dataRow[CATEGORY_DATA_LIST_INDEX_USED_BY],
        dataSubPropertiesContainer
    )
    return dataSubCatSample

def _get_category_data_file_name(directoryPath):
    '''
    Gets the first family base data file in provided directory or any of it's sub directories.

    :param directoryPath: Fully qualified directory path.
    :type directoryPath: str
    :raises Exception: EXCEPTION_NO_FAMILY_BASE_DATA_FILES

    :return: Fully qualified file path to family base data file.
    :rtype: str
    '''

    # get all base data files in folder
    files = fileGet.GetFilesFromDirectoryWalkerWithFilters(
        directoryPath,
        FAMILY_CATEGORY_DATA_FILE_NAME_PREFIX,
        '',
        FAMILY_CATEGORY_DATA_FILE_EXTENSION
    )

    if( len(files) > 0):
        return files[0]
    else:
        raise Exception(EXCEPTION_NO_FAMILY_CATEGORY_DATA_FILES)

def read_overall_family_data_list(filePath):
    '''
    Reads list of families from family category data report file into named tuples.

    :param filePath: Fully qualified file path to family category data report file.
    :type filePath: str
    :raises Exception: "Families category data list files does not exist."
    :raises Exception: "Empty Families category data list file!"
    :return: Two lists: first list of named tuples contain family root data, second list contains family nested data.
    :rtype: [rootFamily], [nestedFamily]
    '''

    rows = []
    if(util.FileExist(filePath)):
        rows = fileCSV.ReadCSVfile(filePath)
    else:
        raise Exception(EXCEPTION_NO_FAMILY_CATEGORY_DATA_FILES)
    if(len(rows) > 0):
        pass
    else:
        raise Exception(EXCEPTION_EMPTY_FAMILY_CATEGORY_DATA_FILES)
    
    returnValueRootFamily = []
    returnValueNestedFamily = []
    # pointer to the current family
    currentFam = None
    for i in range(1, len(rows)):
        # set up the actual sub category ( single row in report )
        dataSubCatSample = _build_sub_category_properties_from_data(rows[i])
        # get name and category as unique identifier
        famId = rows[i][CATEGORY_DATA_LIST_INDEX_FAMILY_NAME] + rows[i][CATEGORY_DATA_LIST_INDEX_CATEGORY_NAME]
        # check if this is the current family ... 
        # this assumes family category data in report file is ordered by family!!!
        if(currentFam == None):
            # and set up a new one:
            currentFam = _setup_family_from_data(rows[i])
            # append category data to new family
            currentFam.subcategories.append(dataSubCatSample)
        elif (currentFam.name + currentFam.category == famId):
            # append category data to existing family
            currentFam.subcategories.append(dataSubCatSample)
        else:
            # if not:
            # append family to one of the list to be returned
            if(isinstance(currentFam,rootFamily)):
                returnValueRootFamily.append(currentFam)
            else:
                returnValueNestedFamily.append(currentFam)
            # and set up a new one:
            currentFam = _setup_family_from_data(rows[i])
            # append category data to new family
            currentFam.subcategories.append(dataSubCatSample)
    return returnValueRootFamily, returnValueNestedFamily

def read_overall_family_category_data_from_directory(directoryPath):
    '''
    Reads the first family category data file it finds in a folder.
    Note: This method calls ReadOverallFamilyDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directoryPath: A fully qualified directory path containing family category data file(s)
    :type directoryPath: _str

    :return: Two lists: first list of named tuples contain family root data, second list contains family nested data.
    :rtype: [rootFamily], [nestedFamily]
    '''

    fileName = _get_category_data_file_name(directoryPath)
    return read_overall_family_data_list(fileName)

# -------------------------------- read family category change directives ----------------------------------------------------------------

def read_overall_change_category_directives_list(filePaths):
    '''
    Reads list of family change category directives from files into named tuples.

    :param filePath: List of fully qualified file path to family change category directive file.
    :type filePath: [str]
    :raises Exception: "Families change directive list files do not exist."
    :raises Exception: "Empty Families category data list file!"
    
    :return: List of named tuples contain family category change directive.
    :rtype: [changeFamilyCategory]
    '''

    rows = []
    matchAnyFile = False
    for filePath in filePaths:
        if(util.FileExist(filePath)):
            # set flag that we at least found one file
            matchAnyFile = True
            rowsFile = fileCSV.ReadCSVfile(filePath)
            result = list(rows)
            result.extend(item for item in rowsFile
              if item not in result)
            rows = result
    
    # check if any files found
    if(matchAnyFile == False):
        raise Exception(EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES)
    
    # check if files contained any data
    if(len(rows) > 0):
        # populate change directive tuples
        returnValueChangeDirectives = []
        for row in rows:
            changeDirective = changeFamilyCategory(
            row[CATEGORY_CHANGE_DATA_LIST_INDEX_FAMILY_FILE_PATH], 
            row[CATEGORY_CHANGE_DATA_LIST_INDEX_NEW_FAMILY_CATEGORY]
            )
            returnValueChangeDirectives.append(changeDirective)
    else:
        raise Exception(EXCEPTION_EMPTY_CHANGE_DIRECTIVE_DATA_FILES)
    
    return returnValueChangeDirectives
    
def _get_category_change_directive_file_names(directoryPath):
    '''
    Gets change category directive file in provided directory or any of it's sub directories.

    :param directoryPath: Fully qualified directory path.
    :type directoryPath: str
    :raises Exception: _EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES

    :return: List of fully qualified file path to family change category directive files.
    :rtype: [str]
    '''

    # get all base data files in folder
    files = fileGet.GetFilesFromDirectoryWalkerWithFilters(
        directoryPath,
        CATEGORY_CHANGE_DIRECTIVE_FILE_NAME_PREFIX,
        '',
        CATEGORY_CHANGE_DIRECTIVE_FILE_EXTENSION
    )
    if( len(files) > 0):
        return files
    else:
        raise Exception(EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES)

def read_overall_family_category_change_directives_from_directory(directoryPath):
    '''
    Reads all category change directive file it finds in a folder.
    Note: This method calls ReadOverallFamilyDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directoryPath: A fully qualified directory path containing family category change directive file(s)
    :type directoryPath: _str

    :return: list of named tuples contain family category change directives.
    :rtype: [changeFamilyCategory]
    '''

    fileNames = _get_category_change_directive_file_names(directoryPath)
    return read_overall_change_category_directives_list(fileNames)

# -------------------------------- read family subcategory change directives ----------------------------------------------------------------

def read_overall_family_sub_category_change_directives_from_directory(directoryPath):
    '''
    Reads all subcategory change directive file it finds in a folder.
    Note: This method calls ReadOverallFamilyDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directoryPath: A fully qualified directory path containing family category change directive file(s)
    :type directoryPath: _str

    :return: list of named tuples contain family sub category change directives.
    :rtype: [changeFamilySubCategory]
    '''

    fileNames = _get_sub_category_change_directive_file_names(directoryPath)
    return read_overall_change_sub_category_directives_list(fileNames)

def _get_sub_category_change_directive_file_names(directoryPath):
    '''
    Gets change subcategory directive file in provided directory or any of it's sub directories.

    :param directoryPath: Fully qualified directory path.
    :type directoryPath: str
    :raises Exception: _EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES

    :return: List of fully qualified file path to family change sub category directive files.
    :rtype: [str]
    '''

    # get all base data files in folder
    files = fileGet.GetFilesFromDirectoryWalkerWithFilters(
        directoryPath,
        SUBCATEGORY_CHANGE_DIRECTIVE_FILE_NAME_PREFIX,
        '',
        SUBCATEGORY_CHANGE_DIRECTIVE_FILE_EXTENSION
    )
    if( len(files) > 0):
        return files
    else:
        raise Exception(EXCEPTION_NO_FAMILY_CHANGE_DIRECTIVE_DATA_FILES)

def read_overall_change_sub_category_directives_list(filePaths):
    '''
    Reads list of family change subcategory directives from files into named tuples.

    :param filePath: List of fully qualified file path to family change category directive file.
    :type filePath: [str]
    :raises Exception: _EXCEPTION_NO_FAMILY_SUBCATEGORY_DATA_FILES
    :raises Exception: _EXCEPTION_EMPTY_FAMILY_SUBCATEGORY_DATA_FILES
    
    :return: List of named tuples containing family subcategory change directive.
    :rtype: [changeFamilySubCategory]
    '''

    rows = []
    matchAnyFile = False
    for filePath in filePaths:
        if(util.FileExist(filePath)):
            # set flag that we at least found one file
            matchAnyFile = True
            rowsFile = fileCSV.ReadCSVfile(filePath)
            result = list(rows)
            result.extend(item for item in rowsFile
              if item not in result)
            rows = result
    
    # check if any files found
    if(matchAnyFile == False):
        raise Exception(EXCEPTION_NO_FAMILY_SUBCATEGORY_DATA_FILES)
    
    # check if files contained any data
    if(len(rows) > 0):
        # populate change directive tuples
        returnValueChangeDirectives = []
        for row in rows:
            changeDirective = changeFamilySubCategory(
            row[SUBCATEGORY_CHANGE_DATA_LIST_INDEX_FAMILY_CATEGORY], 
            row[SUBCATEGORY_CHANGE_DATA_LIST_INDEX_OLD_SUBCATEGORY_NAME],
            row[SUBCATEGORY_CHANGE_DATA_LIST_INDEX_NEW_SUBCATEGORY_NAME],
            )
            returnValueChangeDirectives.append(changeDirective)
    else:
        raise Exception(EXCEPTION_EMPTY_FAMILY_SUBCATEGORY_DATA_FILES)
    
    return returnValueChangeDirectives

def get_families_requiring_sub_category_change(rootFamilies, subCatChangeDirectives):
    '''
    Returns a list of file path of root families containing subcategories requiring a rename.

    Note: list of file path returned is unique: i.e.  if a family has multiple matches for rename subcategory directives it will still only appear once in the list.

    :param rootFamilies: List of tuples of root families.
    :type rootFamilies: [rootFamily]
    :param subCatChangeDirectives: List of subcategory change directives.
    :type subCatChangeDirectives: [changeFamilySubCategory]

    :return: List of family file path.
    :rtype: [str]
    '''

    rootFamiliesNeedingChange = []
    # check each root family
    for rootFam in rootFamilies:
        # against each subcategory change directive
        for changeD in subCatChangeDirectives:
            # check if match family category
            if(rootFam.category == changeD.familyCategory):
                # loop over subcategories in family and check if any of them needs renaming
                for subCatRoot in rootFam.subcategories:
                    if(subCatRoot.subCategoryName == changeD.oldSubCategoryName):
                        # found a match
                        if (rootFam.filePath not in rootFamiliesNeedingChange):
                            rootFamiliesNeedingChange.append(rootFam.filePath)
                        break
    return rootFamiliesNeedingChange