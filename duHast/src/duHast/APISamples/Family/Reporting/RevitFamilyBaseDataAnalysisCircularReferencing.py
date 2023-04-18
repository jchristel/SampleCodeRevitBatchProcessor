'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data analysis module containing functions to find circular family referencing in extracted data.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A circular reference is when a family A has a family B nested but family B has also family A nested.

Algorithm description:

- read base data file processing list (created by RevitFamilyBaseDataProcessor module)
- extract all root families (no ' :: ' in root path)
- extract all nested families (' :: 'in root path)

- loop over root families
    - loop over nested families 
        - check if root family is in nested family root path
            - yes
            - get all families higher in root path and add to parents prop of root family (if not there already)
            - get all families lower in root path of nested family and add to child property of root family if not already
            -   TODO: Check this theory: families always have the same children...once children are identified there is no need to check over and over again!

- loop over root family 
    -   check whether any family exist in parent and child family
        - YES: found circular reference

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

import threading
import os

from duHast.APISamples.Family.Reporting import RevitFamilyBaseDataUtils as rFamBaseDataUtils
from duHast.Utilities.timer import Timer
from duHast.Utilities import Result as res

def _extract_parent_families(currentParent, treePath):
    '''
    Find the index of the match in the root tree, any entries in the root tree list with a lower index are parents

    Note: Changes currentParent.parent property of the currentParent variable!

    :param currentParent: A tuple containing family root data
    :type currentParent: named tuple rootFamily
    :param treePath: list of family names describing the nesting tree of a family
    :type treePath: [str]
    :return: Nothing
    :rtype: None
    '''
   
    indexMatch = treePath.index(currentParent.name)
    # double check...it exists and it is not root itself
    if(indexMatch > 0):
        # add all parents
        for i in range (indexMatch):
            if(treePath[i] not in currentParent.parent):
                currentParent.parent.append(treePath[i])


def _extract_child_families(currentParent, treePath):
    '''
    Find the index of the match in the root tree, any entries in the root tree list with a lower index are children

    Note: Changes currentParent.child property of the currentParent variable!

    :param currentParent: A tuple containing family root data
    :type currentParent: named tuple rootFamily
    :param treePath: list of family names describing the nesting tree of a family
    :type treePath: [str]
    :return: Nothing
    :rtype: None
    '''

    indexMatch = treePath.index(currentParent.name)
    # double check...it exists and it is not root itself and its not the last item in tree path
    if(indexMatch > 0 and indexMatch != len(treePath)):
        # add all children
        for i in range (indexMatch + 1, len(treePath)):
            if(treePath[i] not in currentParent.child):
                currentParent.child.append(treePath[i])


def _check_data_blocks_for_overLap(blockOne, blockTwo):
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

def _cull_data_block(familyBaseNestedDataBlock):
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
            uniqueNodes = _check_data_blocks_for_overLap(dataBlocksByLength[i], dataBlocksByLength[i + 1])
            # only add non overlapping blocks
            culledFamilyBaseNestedDataBlocks = culledFamilyBaseNestedDataBlocks + uniqueNodes
    return culledFamilyBaseNestedDataBlocks

def _cull_nested_base_data_blocks(overallFamilyBaseNestedData):
    '''
    Reduce base data families for parent / child finding purposes. Keep the nodes with the root path longest branch only.

    Sample:
    
    famA :: famB :: famC
    famA :: famB

    The second of the above examples can be culled since the first contains the same information.

    :param overallFamilyBaseNestedData: A list containing all nested families with the longest nesting levels per branch per host family.
    :type overallFamilyBaseNestedData: [nestedFamily]
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
        d = _cull_data_block(familyBlock)
        retainedFamilyBaseNestedData = retainedFamilyBaseNestedData + d
        
    return retainedFamilyBaseNestedData


def find_parents_and_children(overallFamilyBaseRootData, overallFamilyBaseNestedData):
    '''
    Loop over all root families and check if they exist in root path of any nested families.
    if so extract families higher up the root path tree as parents and families further down the root path tree as children

    :param overallFamilyBaseRootData: List of tuples containing root family data.
    :type overallFamilyBaseRootData: [rootFamily]
    :param overallFamilyBaseNestedData: List of tuples containing nested family data.
    :type overallFamilyBaseNestedData: [nestedFamily]

    :return: List of tuples containing root family data.
    :rtype: [rootFamily]
    '''
    
    for i in range(len(overallFamilyBaseRootData)):
        #print ('checking family :' , i, ' ', overallFamilyBaseRootData[i].name)
        for nestedFam in overallFamilyBaseNestedData:
            try:
                # get the index of the match
                indexMatch = nestedFam.rootPath.index(overallFamilyBaseRootData[i].name)
                if(indexMatch > 0):
                    
                    #print('found ', overallFamilyBaseRootData[i].name ,' in ', nestedFam.rootPath)
                    _extract_parent_families(overallFamilyBaseRootData[i], nestedFam.rootPath)
                    
                    _extract_child_families(overallFamilyBaseRootData[i], nestedFam.rootPath)

                    #print('after: ', overallFamilyBaseRootData[i].child)
            except:
                pass
    return overallFamilyBaseRootData

def find_circular_references(overallFamilyBaseRootData):
    '''
    Loops over family data and returns any families which appear in circular references.
    (A family appears in their parent and child collection)

    :param overallFamilyBaseRootData: List of tuples containing root family data.
    :type overallFamilyBaseRootData: [rootFamily]
    
    :return: List of tuples containing root family data.
    :rtype: [rootFamily]
    '''

    circularReferences = []
    # loop over all families and check whether there are any families in both the parent as well as child collection
    for family in overallFamilyBaseRootData:
        for parentFamily in family.parent:
            if (parentFamily in family.child):
                circularReferences.append(family)
    return circularReferences

def check_families_have_circular_references(familyBaseDataReportFilePath):
    '''
    Processes a family base data report and identifies any families which contain circular reference.

    Makes use of multithreading when more then 2 cores are present.

    :param familyBaseDataReportFilePath: Fully qualified file path to family base data report file. 
    :type familyBaseDataReportFilePath: str

    :return: 
        Result class instance.

        - result.status. True if circular referencing file was written successfully, otherwise False.
        - result.message will contain the summary messages of the process including time stamps.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    # set up a timer
    tProcess = Timer()
    tProcess.start()

    returnValue = res.Result()
    # read overall family base data and nested data from file 
    overallFamilyBaseRootData, overallFamilyBaseNestedData = rFamBaseDataUtils.read_overall_family_data_list(familyBaseDataReportFilePath)
    returnValue.append_message('{} Read overall family base data report. {} root entries found and {} nested entries found.'.format(tProcess.stop(),len(overallFamilyBaseRootData,len(overallFamilyBaseNestedData))))
    tProcess.start()

    before = len(overallFamilyBaseNestedData)
    # reduce workload by culling not needed nested family data
    overallFamilyBaseNestedData = _cull_nested_base_data_blocks(overallFamilyBaseNestedData)
    returnValue.append_message(' {} culled nested family base data from : {} to: {} families.'.format(tProcess.stop(), before),len(overallFamilyBaseNestedData))
    tProcess.start()

    # set up some multithreading
    coreCount = int(os.environ['NUMBER_OF_PROCESSORS'])
    if (coreCount > 2):
        returnValue.append_message('cores: '.format(coreCount))
        # leave some room for other processes
        coreCount = coreCount - 1
        chunkSize = len(overallFamilyBaseRootData)/coreCount
        threads = []
        # set up threads
        for i in range(coreCount):
            t = threading.Thread(target=find_parents_and_children, args=(overallFamilyBaseRootData[i*chunkSize:(i+1) * chunkSize],overallFamilyBaseNestedData))
            threads.append(t)
        # start up threads
        for t in threads:
            t.start()
        # wait for results
        for t in threads:
            t.join()
    else:
        # find parents and children
        overallFamilyBaseRootData = find_parents_and_children(overallFamilyBaseRootData, overallFamilyBaseNestedData)
    
    returnValue.append_message('{} Populated parents and children properties of: {} root families'.format(tProcess.stop(), len(overallFamilyBaseRootData)))
    tProcess.start()

    # identify circular references
    circularReferences = find_circular_references(overallFamilyBaseRootData)
    returnValue.append_message('{} Found: {} circular references in families.'.format(tProcess.stop(), len(circularReferences)))
    if(len(circularReferences) > 0):
        returnValue.result = circularReferences
    return returnValue
