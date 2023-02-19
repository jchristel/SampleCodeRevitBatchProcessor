'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data utility module containing functions to read the data from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reads family base data into two list of named tuples.

rootFamily:

- name 
- category 
- filePath 
- parent 
- child

nestedFamily:

- name 
- category 
- filePath 
- rootPath  [str]
- categoryPath [str]

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

from duHast.Utilities import Utility as util

# tuples containing base family data read from file
rootFamily = namedtuple('rootFamily', 'name category filePath parent child')
nestedFamily = namedtuple('nestedFamily', 'name category filePath rootPath categoryPath hostFamily')

# row structure of family base data file
_BASE_DATA_LIST_INDEX_FAMILY_NAME = 2
_BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH = 3
_BASE_DATA_LIST_INDEX_CATEGORY = 4
_BASE_DATA_LIST_INDEX_ROOT_PATH = 0
_BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH = 1

# file name identifiers for family base data
_FAMILY_BASE_DATA_FILE_NAME_PREFIX = 'FamilyBase'
_FAMILY_BASE_DATA_FILE_EXTENSION = '.csv'

# exceptions
_EXCEPTION_NO_FAMILY_BASE_DATA_FILES = 'Families base data list files do not exist.'
_EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES = 'Empty Families base data list file!'


def _getBaseDataFileName(directoryPath):
    '''
    Gets the first family base data file in provided directory or any of it's sub directories.

    :param directoryPath: Fully qualified directory path.
    :type directoryPath: str
    :raises Exception: EXCEPTION_NO_FAMILY_BASE_DATA_FILES

    :return: Fully qualified file path to family base data file.
    :rtype: str
    '''

    # get all base data files in folder
    files = util.GetFilesFromDirectoryWalkerWithFilters(
        directoryPath,
        _FAMILY_BASE_DATA_FILE_NAME_PREFIX,
        '',
        _FAMILY_BASE_DATA_FILE_EXTENSION
    )
    if( len(files) > 0):
        return files[0]
    else:
        raise Exception(_EXCEPTION_NO_FAMILY_BASE_DATA_FILES)

def ReadOverallFamilyDataList(filePath):
    '''
    Reads list of families from family base data report file into named tuples.

    :param filePath: Fully qualified file path to family base data report file.
    :type filePath: str
    :raises Exception: "Families base data list files does not exist."
    :raises Exception: "Empty Families base data list file!"
    :return: Two lists: first list of named tuples contain family root data, second list contains family nested data.
    :rtype: [rootFamily], [nestedFamily]
    '''

    rows = []
    if(util.FileExist(filePath)):
        rows = util.ReadCSVfile(filePath)
    else:
        raise Exception(_EXCEPTION_NO_FAMILY_BASE_DATA_FILES)
    if(len(rows) > 0):
        pass
    else:
        raise Exception(_EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES)
    
    returnValueRootFamily = []
    returnValueNestedFamily = []
    for i in range(1, len(rows)):
        # check if root family
        if( '::' not in rows[i][_BASE_DATA_LIST_INDEX_ROOT_PATH]):
            data = rootFamily(
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_NAME], 
                rows[i][_BASE_DATA_LIST_INDEX_CATEGORY], 
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH],
                [], # set up an empty list for parent families
                []  # set up an empty list for child families
            )
            returnValueRootFamily.append(data)
        else:
            # found a child family
            data = nestedFamily(
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_NAME], 
                rows[i][_BASE_DATA_LIST_INDEX_CATEGORY], 
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH],
                rows[i][_BASE_DATA_LIST_INDEX_ROOT_PATH].split(' :: '), # split root path into list for ease of searching
                rows[i][_BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH].split(' :: '), # split category path into list for ease of searching
                []
            )
            returnValueNestedFamily.append(data)
    return returnValueRootFamily, returnValueNestedFamily

def ReadOverallFamilyDataListFromDirectory(directoryPath):
    '''
    Reads the first family base data file it finds in a folder.
    Note: This method calls ReadOverallFamilyDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directoryPath: A fully qualified directory path containing family base data file(s)
    :type directoryPath: _str

    :return: Two lists: first list of named tuples contain family root data, second list contains family nested data.
    :rtype: [rootFamily], [nestedFamily]
    '''

    fileName = _getBaseDataFileName(directoryPath)
    return ReadOverallFamilyDataList(fileName)

def ReadOverallFamilyDataListIntoNested(filePath):
    '''
    Reads list of families from family base data report file into named tuples.

    :param filePath: Fully qualified file path to family base data report file.
    :type filePath: str
    :raises Exception: "Families base data list files does not exist."
    :raises Exception: "Empty Families base data list file!"
    :return: A list contains family nested data.
    :rtype: [nestedFamily]
    '''

    rows = []
    if(util.FileExist(filePath)):
        rows = util.ReadCSVfile(filePath)
    else:
        raise Exception(_EXCEPTION_NO_FAMILY_BASE_DATA_FILES)
    if(len(rows) > 0):
        pass
    else:
        raise Exception(_EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES)
    
    returnValueNestedFamily = []
    for i in range(1, len(rows)):
        # found a child family
        data = nestedFamily(
            rows[i][_BASE_DATA_LIST_INDEX_FAMILY_NAME], 
            rows[i][_BASE_DATA_LIST_INDEX_CATEGORY], 
            rows[i][_BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH],
            rows[i][_BASE_DATA_LIST_INDEX_ROOT_PATH].split(' :: '), # split root path into list for ease of searching
            rows[i][_BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH].split(' :: '), # split category path into list for ease of searching
            []
        )
        returnValueNestedFamily.append(data)
    return returnValueNestedFamily

def ReadOverallFamilyDataListIntoNestedFromDirectory(directoryPath):
    '''
    Reads the first family base data file it finds in a folder.
    Note: This method calls ReadOverallFamilyIntoNestedDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directoryPath: A fully qualified directory path containing family base data file(s)
    :type directoryPath: _str

    :return: A list contains family nested data.
    :rtype: [nestedFamily]
    '''

    fileName = _getBaseDataFileName(directoryPath)
    return ReadOverallFamilyDataListIntoNested(fileName)

# -------------------------------- simplify data set ----------------------------------------------------------------

def _CheckDataBlocksForOverLap(blockOne, blockTwo):
    '''
    Checks whether the root path of families in the first block overlaps with the root path of any family in the second block.
    Overlap is checked from the start of the root path. Any families from block one which are not overlapping any family in\
        block two are returned.

    :param blockOne: List of family tuples of type nestedFamily
    :type blockOne: [nestedFamily]
    :param blockTwo: List of family tuples of type nestedFamily
    :type blockTwo: [nestedFamily]
    
    :return: List of family tuples of type nestedFamily
    :rtype: [nestedFamily]
    '''

    uniqueTreeNodes = []
    for fam in blockOne:
        match = False
        for famUp in blockTwo:
            if(' :: '.join(famUp.rootPath).startswith(' :: '.join(fam.rootPath))):
                match = True
                break
        if(match == False):
            uniqueTreeNodes.append(fam)
    return uniqueTreeNodes

def _CullDataBlock(familyBaseNestedDataBlock):
    '''
    Sorts family data blocks into a dictionary where key, from 1 onwards, is the level of nesting indicated by number of '::' in root path string.

    After sorting it compares adjacent blocks in the dictionary (key and key + 1) for overlaps in the root path string. Only unique families will be returned.

    :param familyBaseNestedDataBlock: A list containing all nested families belonging to a single root host family.
    :type familyBaseNestedDataBlock: [nestedFamily]
    
    :return: A list of unique families in terms of root path.
    :rtype: [nestedFamily]
    '''

    culledFamilyBaseNestedDataBlocks = []
    dataBlocksByLength = {}
    # build dic by root path length
    # start at 1 because for nesting level ( 1 based rather then 0 based )
    for family in familyBaseNestedDataBlock:
        if(len(family.rootPath) -1 in dataBlocksByLength):
            dataBlocksByLength[len(family.rootPath) -1 ].append(family)
        else:
            dataBlocksByLength[len(family.rootPath)- 1 ] = [family]
    
    # loop over dictionary and check block entries against next entry up blocks
    for i in range(1, len(dataBlocksByLength) + 1):
        # last block get automatically added
        if(i == len(dataBlocksByLength)):
            culledFamilyBaseNestedDataBlocks = culledFamilyBaseNestedDataBlocks + dataBlocksByLength[i]
        else:
            # check for matches in next one up
            uniqueNodes = _CheckDataBlocksForOverLap(dataBlocksByLength[i], dataBlocksByLength[i + 1])
            # only add non overlapping blocks
            culledFamilyBaseNestedDataBlocks = culledFamilyBaseNestedDataBlocks + uniqueNodes
    return culledFamilyBaseNestedDataBlocks

def CullNestedBaseDataBlocks(overallFamilyBaseNestedData):
    '''
    Reduce base data families for parent / child finding purposes. Keep the nodes with the root path longes branch only.

    Sample:
    
    famA :: famB :: famC
    famA :: famB

    The second of the above examples can be culled since the first contains the same information.

    :param overallFamilyBaseNestedData: _description_
    :type overallFamilyBaseNestedData: _type_
    '''

    currentRootFamName = ''
    familyBlocks = []
    block = []
    # read families into blocks
    for nested in overallFamilyBaseNestedData:
        if(nested.rootPath[0] != currentRootFamName):
            # read family block
            if(len(block) > 0):
                familyBlocks.append(block)
                # reset block
                block = []
                block.append(nested)
                currentRootFamName = nested.rootPath[0]
            else:
                block.append(nested)
                currentRootFamName = nested.rootPath[0]
        else:
            block.append(nested)
    
    retainedFamilyBaseNestedData = []
    # cull data per block
    for familyBlock in familyBlocks:
        d = _CullDataBlock(familyBlock)
        retainedFamilyBaseNestedData = retainedFamilyBaseNestedData + d
        
    return retainedFamilyBaseNestedData

# --------------------------------------------  find families in nesting tree data ------------------------------------

def FindDirectHostFamilies(nestedFam, overallFamilyBaseNestedData):
    '''
    Finds the direct hosts of the past in family in the base nested family data set.

    :param nestedFam: A tuple containing nested family data.
    :type nestedFam: nestedFamily
    :param overallFamilyBaseNestedData: List of tuples containing nested family data.
    :type overallFamilyBaseNestedData: [nestedFamily]
    
    :return: A dictionary where:
        
        - key is the family name and category concatenated and 
        - value is a tuple in format 0: family name, 1: family category
    
    :rtype: {str: (str,str)}
    '''
    
    hostFamilies = {}
    # check each base family data whether it contains the missing family in its nesting tree
    for baseNestedFam in overallFamilyBaseNestedData:
        if nestedFam.name in baseNestedFam.rootPath:
            indexMatch = util.IndexOf(baseNestedFam.rootPath, nestedFam.name)
            # make sure we have a match and it is not the first entry in list (does not have a parent...)
            if indexMatch > 0:
                # confirm category is the same
                if(baseNestedFam.categoryPath[indexMatch] == nestedFam.category):
                    # got a direct parent! (index - 1)
                     keyNew = baseNestedFam.rootPath[indexMatch - 1] + baseNestedFam.categoryPath[indexMatch - 1]
                     if(keyNew not in hostFamilies):
                        hostFamilies[keyNew] = (baseNestedFam.rootPath[indexMatch - 1],baseNestedFam.categoryPath[indexMatch - 1])
    return hostFamilies

def FindAllDirectHostFamilies(families, overallFamilyBaseNestedData):
    '''
    Returns a dictionary of all direct host families of families past in.

    :param families: A list of tuples containing nested family data.
    :type families: [nestedFamily]
    :param overallFamilyBaseNestedData: List of tuples containing nested family data.
    :type overallFamilyBaseNestedData: [nestedFamily]
    
    :return: A dictionary.
    :rtype: {str: (str,str)}
    '''

    hostFamilies = {}
    for fam in families:
        hosts = FindDirectHostFamilies(fam, overallFamilyBaseNestedData)
        # update dictionary with new hosts only
        for h in hosts:
            if( h not in hostFamilies):
                hostFamilies[h] = hosts[h]
    return hostFamilies

def FindRootFamsFromHosts(hostFamilies, overallFamilyBaseRootData):
    '''
    Returns a list of tuples of type rootFamily matching the past in host families. 

    :param hostFamilies: A dictionary where:
        
        - key is the family name and category concatenated and 
        - value is a tuple in format 0: family name, 1: family category

    :type hostFamilies: {str: (str,str)}
    :param overallFamilyBaseRootData: List of tuples containing root family data.
    :type overallFamilyBaseRootData: [rootFamily]
    
    :return: List of root family tuples.
    :rtype: [rootFamily]
    '''

    baseHostFamilies = []
    for nestedId, nestedFam in hostFamilies.items():
        for baseRootFam in overallFamilyBaseRootData:
            if (nestedFam[0] == baseRootFam.name and nestedFam[1] == baseRootFam.category):
                baseHostFamilies.append(baseRootFam)
    return baseHostFamilies
