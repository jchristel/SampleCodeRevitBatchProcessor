'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data analysis module containing functions to find missing families.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A missing family is a family which is not present in the family base data report as a root family but present as a nested family.

Algorithm description:

- read base data file processing list (created by RevitFamilyBaseDataProcessor module)
- extract all root families (no :: in root path)
- extract all nested families ( :: in root path)

- cull nested family so each nested family appears only once

- loop over nested families
    - loop over root families 
        - check if nested family exists in root families ( by name and category)
            - no
            - add to missing families list
            - stop processing since one match is enough per missing family
- write out missing families data ( host family filepath,)

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
#

#from collections import namedtuple

from duHast.Revit.Family.Data import family_base_data_utils as rFamBaseDataUtils
from duHast.Utilities.timer import Timer
from duHast.Utilities import result as res

def _build_unique_nested_family_dic(overallFamilyBaseNestedData):
    '''
    Builds a dictionary containing unique nested families only. Key is the family name and category concatenated.

    :param overallFamilyBaseNestedData: List of tuples containing nested family data.
    :type overallFamilyBaseNestedData: [nestedFamily]
    
    :return: A dictionary where:
    
        - Key is the family name and category concatenated.
        - value is a tuple representing one instance of the nested family data.
    :rtype:{ str : nestedFamily }
    '''
    
    uniqueDic = {}

    for nested in overallFamilyBaseNestedData:
        keyNew = nested.name + nested.category
        if(keyNew not in uniqueDic):
            uniqueDic[keyNew] = nested
    
    return uniqueDic

def _check_nested_against_root_families(uniqNestedDictionary, overallFamilyBaseRootData):
    '''
    Compared a dictionary containing tuples containing nested family data against list of root family data.
    Any nested family without a match in the root family data list will be returned (missing from list).

    :param uniqNestedDictionary: A dictionary where:
    
        - Key is the family name and category concatenated.
        - value is a tuple representing one instance of the nested family data.

    :type uniqNestedDictionary: { str : nestedFamily }
    :param overallFamilyBaseRootData: List of tuples containing root family data.
    :type overallFamilyBaseRootData: [rootFamily]
    
    :return: List of tuples containing nested family data.
    :rtype: [nestedFamily]
    '''

    missingFamilies = []
    for nestedId, nestedFam in uniqNestedDictionary.items():
        match = False
        for baseRootFam in overallFamilyBaseRootData:
            if (nestedFam.name == baseRootFam.name and nestedFam.category == baseRootFam.category):
                match = True
                break
        if (match == False):
            missingFamilies.append(nestedFam)
    return missingFamilies

def _get_unique_nested_families(overallFamilyBaseNestedData):
    '''
    Loops over family nested base data and creates a unique list of nested families based on name and category.
    This is done to make search faster (reduce the to be searched data set)

    :param overallFamilyBaseNestedData: List of tuples containing nested family data.
    :type overallFamilyBaseNestedData: [nestedFamily]
    :return: Unique list of tuples containing nested family data.
    :rtype: [nestedFamily]
    '''

    uniqueNestedFamiliesCompare = []
    uniqueNestedFamilies = []
    for nestedFam in overallFamilyBaseNestedData:
        if (nestedFam.name + nestedFam.category not in uniqueNestedFamiliesCompare):
            uniqueNestedFamilies.append(nestedFam)
            uniqueNestedFamiliesCompare.append(nestedFam.name + nestedFam.category)

    return uniqueNestedFamilies

def check_families_missing_from_library(familyBaseDataReportFilePath):
    '''
    Processes a family base data report and identifies any nested families which have not been processed as a root family\
        and therefore do not exist in the library.
    
    :param familyBaseDataReportFilePath: Fully qualified file path to family base data report file. 
    :type familyBaseDataReportFilePath: str
    
    :return: 
        Result class instance.

        - result.status. True if missing families where found without an exception occurring.
        - result.message will contain the summary messages of the process including time stamps.
        - result.result [nestedFamily]
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''
    returnValue = res.Result()
    try:
        # set up a timer
        tProcess = Timer()
        tProcess.start()

    
        # read overall family base data from file 
        overallFamilyBaseRootData, overallFamilyBaseNestedData = rFamBaseDataUtils.read_overall_family_data_list(familyBaseDataReportFilePath)
        returnValue.append_message('{} Read overall family base data report. {} root entries found and {} nested entries found.'.format(tProcess.stop(),len(overallFamilyBaseRootData),len(overallFamilyBaseNestedData)))
    
        tProcess.start()
        # get a list of unique families from the nested family data
        uniqueFamilyBaseNestedData = _get_unique_nested_families(overallFamilyBaseNestedData)
        returnValue.append_message('{} Culled nested family base data from : {} to: {} families'.format(tProcess.stop(),len(overallFamilyBaseNestedData)),len(uniqueFamilyBaseNestedData ))

        tProcess.start()
        # read over nested data and built a list of unique families ( name + category )
        uniqueDic = _build_unique_nested_family_dic(uniqueFamilyBaseNestedData)
        returnValue.append_message('{} Found unique nested families [{}]'.format(tProcess.stop(),len(uniqueDic)))

        tProcess.start()
        # identify missing families in unique list of nested families
        missingFamilies = _check_nested_against_root_families(uniqueDic, overallFamilyBaseRootData)
        returnValue.append_message('{} Found: {} missing families.'.format(tProcess.stop(),len(missingFamilies)))
        if(len(missingFamilies) > 0):
            returnValue.result = missingFamilies
    except Exception as e:
        returnValue.update_sep(False, 'Failed to retrieve missing families with exception: {}'.format(e))
    return returnValue

# ----------------------------missing families: direct host files -----------------------------------------

def find_missing_families_direct_host_families (familyBaseDataReportFilePath, missingFamilies):
    '''
    Returns a list of root family tuples which represent the direct parents (host families) of the missing families.

    :param missingFamilies: A list of tuple containing nested family data representing missing families(no base root family entry)
    :type missingFamilies: [nestedFamily]
    :param familyBaseDataReportFilePath: Fully qualified file path to family base data report file. 
    :type familyBaseDataReportFilePath: str
    
    :return: 
        Result class instance.

        - result.status. True if host families of missing families where found without an exception occurring.
        - result.message will contain the summary messages of the process including time stamps.
        - result.result [rootFamily]
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    # loop over missing families
    # loop over base nested data
    #   - check if missing fam is in root path (name and category) if so:
    #   - get the direct parent (make sure missing family isn't first entry!)
    #   - check if direct parent is already in dictionary (key is name + category) ? if not:
    #       - add direct parent to dictionary
    #
    # loop over direct host data:
    #   - loop over root fam data and check for match in name and category; If so:
    #       - add to root family data to be returned. 

    returnValue = res.Result()
    try:
        # set up a timer
        tProcess = Timer()
        tProcess.start()

        returnValue = res.Result()
        # read overall family base data from file 
        overallFamilyBaseRootData, overallFamilyBaseNestedData = rFamBaseDataUtils.read_overall_family_data_list(familyBaseDataReportFilePath)
        returnValue.append_message('{} Read overall family base data report. {} root entries found and {} nested entries found.'.format(tProcess.stop(),len(overallFamilyBaseRootData)),len(overallFamilyBaseNestedData))
    
        tProcess.start()
        hostFamilies = rFamBaseDataUtils.find_all_direct_host_families(missingFamilies, overallFamilyBaseNestedData)
        # get the root families from host family data
        rootHosts = rFamBaseDataUtils.find_root_families_from_hosts(hostFamilies, overallFamilyBaseRootData)
        returnValue.result = rootHosts
        returnValue.append_message('{} Found direct host families of missing families: {}'.format(tProcess.stop(),len(rootHosts)))
    except  Exception as e:
        returnValue.update_sep(False, 'Failed to retrieve host families of missing families with exception: '.format(e))
    return returnValue