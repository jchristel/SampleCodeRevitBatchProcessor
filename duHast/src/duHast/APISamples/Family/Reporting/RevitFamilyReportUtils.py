'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family report data utility module containing functions to read the data from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reads family base data into two list of named tuples.

rootFamily:

- name 
- category 
- filePath 


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
from duHast.Utilities import Result as res

# tuples containing base family data read from file
rootFamily = namedtuple('rootFamily', 'name category filePath')
nestedFamily = namedtuple('nestedFamily', 'name category filePath rootPath categoryPath')

# row structure of report data file
_BASE_DATA_LIST_INDEX_ROOT_PATH = 0
_BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH = 1
_BASE_DATA_LIST_INDEX_FAMILY_NAME = 2
_BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH = 3

# exceptions
_EXCEPTION_NO_FAMILY_BASE_DATA_FILES = 'Report data list files do not exist.'
_EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES = 'Empty report data list file!'

def ReadUniqueFamiliesFromReport(filePath):
    '''
    Reads list of families from any report file into list of unique named tuples. 
    Reports needs:
    
    - to contain the following columns (in this order):  root path, category path , family name, family file path
    - a tab separated file

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
                rows[i][_BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH], 
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH]
            )
            # only add unique occurrences
            if (data not in returnValueRootFamily):
                returnValueRootFamily.append(data)
        else:
            # the category is the last entry in the category root path
            categories = rows[i][_BASE_DATA_LIST_INDEX_ROOT_PATH].split(' :: ')
            category = categories[len(categories) - 1]
            # found a child family
            data = nestedFamily(
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_NAME], 
                category, 
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH],
                rows[i][_BASE_DATA_LIST_INDEX_ROOT_PATH].split(' :: '), # split root path into list for ease of searching
                rows[i][_BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH].split(' :: '), # split category path into list for ease of searching
            )
            # only add unique occurrences
            if (data not in returnValueNestedFamily):
                returnValueNestedFamily.append(data)
    return returnValueRootFamily, returnValueNestedFamily

def ReadUniqueFamiliesWithRowDataFromReport(filePath):
    '''
    Reads list of families from any report file into dictionaries where key is a named tuple and values are the rows associated with that family
    Reports needs:
    
    - to contain the following columns (in this order):  root path, category path , family name, family file path
    - a tab separated file

    :param filePath: Fully qualified file path to family base data report file.
    :type filePath: str
    :raises Exception: "Families base data list files does not exist."
    :raises Exception: "Empty Families base data list file!"
    :return: Two dictionaries: first dictionary contain family root data, second dictionary contains family nested data.
    :rtype: {rootFamily:[[str]]}, {nestedFamily:[[str]]}
    '''

    rows = []
    if(util.FileExist(filePath)):
        rows = util.ReadCSVfile(filePath, True)
    else:
        raise Exception(_EXCEPTION_NO_FAMILY_BASE_DATA_FILES)
    if(len(rows) > 0):
        pass
    else:
        raise Exception(_EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES)
    
    returnValueRootFamily = {}
    returnValueNestedFamily = {}
    for i in range(1, len(rows)):
        # check if root family
        if( '::' not in rows[i][_BASE_DATA_LIST_INDEX_ROOT_PATH]):
            data = rootFamily(
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_NAME], 
                rows[i][_BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH], 
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH]
            )
            # add row to dictionary
            if (data not in returnValueRootFamily):
                returnValueRootFamily[data] = [rows[i]]
            else:
                returnValueRootFamily[data].append(rows[i])
        else:
            # the category is the last entry in the category root path
            categories = rows[i][_BASE_DATA_LIST_INDEX_ROOT_PATH].split(' :: ')
            category = categories[len(categories) - 1]
            # found a child family
            data = nestedFamily(
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_NAME], 
                category, 
                rows[i][_BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH],
                rows[i][_BASE_DATA_LIST_INDEX_ROOT_PATH], 
                rows[i][_BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH], 
            )
            returnValueNestedFamily[data] = [rows[i]]
    return returnValueRootFamily, returnValueNestedFamily

# ------------------------------------- combining reports --------------------------------------------

def _getDataRowsFromDictionary(dic):
    '''
    Builds list of data rows from dictionary past in

    :param dic: Dictionary where key is a tuple and values is a list of list of strings
    :type dic: {named tuple: [[str]]}
    :param dataList: List of list of strings
    :type dataList: [[str]]
    
    :return: List of list of strings
    :rtype: [[str]]
    '''

    dataList = []
    # get rows from dictionary
    for k,v in dic.items():
        # get data rows for root family
        for rootData in v[0]:
            dataList.append(rootData)
        # get data rows for any nested families
        for nestedFamRowValue in v[1]:
            dataList.append(nestedFamRowValue)
    return dataList


def _compareFamilyDictionaries(previousAgData, newAgData):
    '''
    Compares two aggregate data dictionaries. Any new root family from newAgData ( root family occurring in newAgData only) will be add to the previousAgData dictionary. 
    Any existing root family (root family occurring in previous and new aggregate data dictionaries) will be updated in the previousAgData dictionary with row data from the newAgData data dictionary.

    
    :param previousAgData: A dictionary containing aggregated family data from the previous report.
    :type previousAgData: {key:str, value ([str],[str])}
    :param newAgData: A dictionary containing aggregated family data from the new report.
    :type newAgData: {key:str, value ([str],[str])}
    :return:

        If previousAgData is empty and newAgData contains data, newAgData will be returned unchanged.
        If newAgData is empty and previousAgData contains data, previousAgData will be returned unchanged.
        if both dictionary are empty an empty dictionary will be returned.

    :rtype: {key:str, value ([str],[str])}
    '''
    
    returnValue = res.Result()
    # check corner cases:
    if(len(newAgData) == 0 and len(previousAgData) > 0):
        # new is empty, but previous has data
        returnValue.UpdateSep(True, 'New report data is empty, using previous report data only')
        returnValue.result.append(previousAgData)
    elif(len(newAgData) > 0 and len(previousAgData) == 0):
        # new has data, but previous is empty
        returnValue.UpdateSep(True, 'Previous report data is empty, using new report data only')
        returnValue.result.append(newAgData)
    elif(len(newAgData) == 0 and len (previousAgData) == 0):
        # new is empty, previous is empty
        returnValue.UpdateSep(True, 'Previous report data and new report data are empty!')
        returnValue.result.append({})
    else:
        # other and current have data
        for newData in newAgData:
            if(newData in previousAgData):
                returnValue.AppendMessage('Substituting family data: ' + newData)
            else:
                returnValue.AppendMessage('Adding new family data: ' + newData)
            previousAgData[newData] = newAgData[newData]
        returnValue.result.append(previousAgData)
    return returnValue

def _getNestedFamiliesBelongingToRootFamilies(rootFam, nestedFamilies):
    '''
    Returns a list of all row data of nested families belonging to a given root family.

    :param rootFam: A tuple of a root family from a report.
    :type rootFam: tuple of type 'rootFamily'
    :param nestedFamilies: A list of tuples of all nested families in a report
    :type nestedFamilies: [tuple of type 'nestedFamily']

    :return: _description_
    :rtype: _type_
    '''

    nestedFamiliesBelongingToRootFamRowData = []
    for nf in nestedFamilies:
        # split path in order to get to top most root family
        nestedFamRootPath = nf.rootPath.split(' :: ')
        nestedFamCatPath = nf.categoryPath.split(' :: ')
        if(rootFam.name == nestedFamRootPath[0] and rootFam.category == nestedFamCatPath[0]):
            nestedFamiliesBelongingToRootFamRowData.append(nestedFamilies[nf][0])
    return nestedFamiliesBelongingToRootFamRowData

def _aggregateFamilyData(rootFamilies, nestedFamilies):
    '''
    Returns a dictionary where key are all the root family file path from a report and value is a tuple of two list of strings containing
    the row data read from report file for the root family itself (first list) and the row data read from report file for any nested families (second list).

    :param rootFamilies: A list containing tuples of all root families in a report.
    :type rootFamilies: [tuple of type 'rootFamily']
    :param nestedFamilies: A list of tuples of all nested families in a report
    :type nestedFamilies: [tuple of type 'nestedFamily']
    
    :return: Returns a dictionary where key is the root family file path and value is a tuple of two list of strings containing the row data for root family itself (first list) and the row data for any nested families (second list)
    :rtype: {key:str, value ([str],[str])}
    '''

    # key is root family, value is tuple of csv row representing the root family data and list of rows each representing a nested family data
    aggregatedFamilyData = {}
    for rf in rootFamilies:
        nestedFamiliesOfRootFamilyRowData = _getNestedFamiliesBelongingToRootFamilies(rf, nestedFamilies)
        # key is the unique family file path of the root family
        # value is a tuple of two lists : root data rows at index 0, nested fam data rows at index 1
        aggregatedFamilyData[rf.filePath] = (rootFamilies[rf], nestedFamiliesOfRootFamilyRowData)
    return aggregatedFamilyData

def _checkFamiliesStillExist(famData):
    '''
    Checks whether families still exist on file server.

    Reason why families no longer exist:

    - family got deleted or moved
    - family got renamed

    :param famData: A dictionary containing aggregated family data from the a report.
    :type famData: {key:str, value ([str],[str])}

    :return: 
        Result class instance.
        
        - .result = True if successfully removed any outdated family data or None needed removing. Otherwise False.
        - .message will contain list of families removed or message nothing needed to be removed.
        - . result will contain past in dictionary at index 0

        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        removeKeys = []
        # get keys from dic as a list
        # check which ones do not exist anymore
        for filePath in famData.keys():
            if (util.FileExist(filePath) == False):
                removeKeys.append(filePath)
        
        # check if any family requires to be removed from the data set
        if(len(removeKeys) > 0):
            # remove those keys from dictionary
            for dKey in removeKeys:
                removeSingleKey = famData.pop(dKey, None)
                if (removeSingleKey != None):
                    returnValue.AppendMessage('Removed family from data: {}'.format(dKey))
                else:
                    returnValue.AppendMessage('Failed to removed family from data: {}'.format(dKey))
        else:
            returnValue.AppendMessage('No family required removing from data.')

        # update return data
        returnValue.UpdateSep(True, 'Successfully updated family data.')
        returnValue.result.append(famData)

    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to check whether families still exist with exception: ' + str(e))
    return returnValue

def CombineReports (previousReportPath, newReportPath):
    '''
    This combines two reports by:

    - building an aggregate data dictionary of each report (key root family file path, values lists containing the row data read from file for the root family as well as any nested families)
    - comparing the previous report dictionary with the new report dictionary and
        - adding any new families found in the new report dictionary
        - updating any previous report families found with data matching the root family in the new report dictionary

    All reports start with the following 2 columns:
    root	rootCategory

    First entry (after split at separator) in each of these columns identifies root family uniquely.
    Assume that new report only ever adds or substitutes entries in previous report but does not delete from it!

    :param previousReportPath: A fully qualified file path to the previous report file.
    :type previousReportPath: str
    :param newReportPath: A fully qualified file path to the new report file.
    :type newReportPath: str

    :return: list of lists of report rows
    :rtype: [[str]]
    '''

    returnValue = res.Result()
    # read families from both reports
    # ...compare them:
    # take all families from current report and all none matching families from the other report

    previousAggregatedFamilies = {}
    newAggregatedFamilies = {}

    # previous report
    try:
        previousRoot, previousNested = ReadUniqueFamiliesWithRowDataFromReport(previousReportPath)
        returnValue.AppendMessage('Previous report: found ' + str(len(previousRoot)) + ' root families.')
        returnValue.AppendMessage('Previous report: found ' + str(len(previousNested)) + ' nested families.')
        # build dictionary containing all family data per root family
        previousAggregatedFamilies = _aggregateFamilyData(previousRoot, previousNested)
    except Exception as e:
        # check whether empty file exception
        if (str(e) != _EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES):
            raise e
    
    # new report
    try:
        newRoot, newNested = ReadUniqueFamiliesWithRowDataFromReport(newReportPath)
        # build dictionary containing all family data per root family
        newAggregatedFamilies = _aggregateFamilyData(newRoot, newNested)
        returnValue.AppendMessage('New report: found ' + str(len(newRoot)) + ' root families.')
        returnValue.AppendMessage('New report: found ' + str(len(newNested)) + ' nested families.')
    except Exception as e:
        # check whether empty file exception
        if (str(e) != _EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES):
            raise e

    # compare dictionaries: build unique list of families
    uniqueFamDataStatus = _compareFamilyDictionaries(previousAggregatedFamilies, newAggregatedFamilies)
    returnValue.Update(uniqueFamDataStatus)
    uniqueFamData = uniqueFamDataStatus.result[0]

    # check whether families still exist on file server
    removeNoneExistingFamilies = _checkFamiliesStillExist(uniqueFamData)
    returnValue.Update(removeNoneExistingFamilies)
    # only update family data if culling occurred without any exceptions
    if(removeNoneExistingFamilies.status):
        uniqueFamData = removeNoneExistingFamilies.result[0]

    # get report header row (there should be a previous report file...otherwise this will write an empty header row)
    header = util.GetFirstRowInCSVFile(previousReportPath)
    headerRow = header.split(',')
    
    # build list of data rows
    rowsCurrent = _getDataRowsFromDictionary(uniqueFamData)
    # sort rows by root ( first entry ) since other code (circ reference checker for instance) expects data sorted
    rowsCurrent.sort()
    # start with header row
    rowsCurrent.insert(0, headerRow)
    # overwrite return result value since it is already containing data from previous operations
    returnValue.result = rowsCurrent
    return returnValue