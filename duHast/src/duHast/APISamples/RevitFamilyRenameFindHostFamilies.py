'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Finds host families of nested families requiring to be renamed.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- read file rename change list:
-   text file (tab separated) with columns: currentFamilyName   currentFamilyFilePath	categoryName newFamilyName
-   note: current family file path could be blank in situations where just a rename of a nested family is required...
- read base data file processing list (created by RevitFamilyBaseDataProcessor module)
- extract all root families (no :: in root path)
- extract all nested families ( :: in root path)
- loop over nested families and find any family where:
    - family at first nesting level is in rename list by name and category
    - extract root family name and add to identified host family list

- loop over root families
-   find match in identified host families
- write out root family date: family file path, family name, category

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

import clr
import System
from duHast.Utilities.timer import Timer

from duHast.Utilities import Result as res
#from duHast.Utilities import Utility as util
from duHast.APISamples import RevitFamilyBaseDataUtils as rFamBaseDataUtils
from duHast.APISamples import RevitFamilyRenameFilesUtils as rFamRenameUtils

#---------------------------------------------------------------------------------------------------------------
#                      find families containing nested families needing to be renamed
#---------------------------------------------------------------------------------------------------------------

def _FindHostFamilies(overallFamilyBaseNestedData, fileRenameList):
    '''
    Finds all root family names and categories where the first level nested family is one which needs to be renamed.

    :param overallFamilyBaseNestedData: A list containing all root families.
    :type overallFamilyBaseNestedData: [rootFamily]
    :param fileRenameList: A list containing all families needing to be renamed.
    :type fileRenameList: [renameFamily]
    
    :return: A dictionary where:
        
        - key is the family name and category concatenated and 
        - value is a tuple in format 0: family name, 1: family category
    
    :rtype: {str: (str,str)}
    '''

    hostFamilies = {}
    for fileRenameFamily in fileRenameList:
        hosts = rFamBaseDataUtils.FindDirectHostFamilies(fileRenameFamily, overallFamilyBaseNestedData)
        # update dictionary with new hosts only
        for h in hosts:
            if( h not in hostFamilies):
                hostFamilies[h] = hosts[h]
    return hostFamilies

def FindHostFamiliesWithNestedFamsRequiringRename(inputDirectoryPath):
    '''
    Finds all host families in data set containing nested families needing to be renamed.

    :param inputDirectoryPath: Fully qualified directory path containing rename directives and family base data report.
    :type inputDirectoryPath: str

    :return: 
        Result class instance.

        - result.status: True if any host families are found with nested families needing renaming, otherwise False.
        - result.message: processing steps with time stamps
        - result.result: [rootFamily]
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    # set up a timer
    tProcess = Timer()
    tProcess.start()

    returnValue = res.Result()
    # read overall family base data from file
    try:
        overallFamilyBaseRootData, overallFamilyBaseNestedData = rFamBaseDataUtils.ReadOverallFamilyDataListFromDirectory(inputDirectoryPath)
        returnValue.AppendMessage(tProcess.stop() +  ' Read overall family base data report. ' + str(len(overallFamilyBaseRootData)) + ' root entries found and '\
            + str(len(overallFamilyBaseNestedData)) + ' nested entries found.')
        # check if input file existed and contained data
        if(len(overallFamilyBaseRootData) > 0):
            tProcess.start()
            fileRenameListStatus = rFamRenameUtils.GetRenameDirectives(inputDirectoryPath)
            returnValue.AppendMessage(tProcess.stop() + ' Read data from file! Rename family entries ['+ str(len(fileRenameListStatus.result)) + ' ] found.')
            # check if any rename directives
            if(len(fileRenameListStatus.result) > 0):
                before = len(overallFamilyBaseNestedData)
                tProcess.start()
                # reduce workload by culling not needed nested family data
                overallFamilyBaseNestedData =  rFamBaseDataUtils.CullNestedBaseDataBlocks(overallFamilyBaseNestedData)
                returnValue.AppendMessage(tProcess.stop() +  ' Culled nested family base data from : ' + str(before) +' to: ' + str(len(overallFamilyBaseNestedData)) + ' families.' )

                tProcess.start()
                # get a list of simplified root data families extracted from nested family path data
                rootFamSimple = rFamBaseDataUtils.FindAllDirectHostFamilies(fileRenameListStatus.result, overallFamilyBaseNestedData)
                returnValue.AppendMessage(tProcess.stop() +  ' Found simplified root families: ' + str(len(rootFamSimple)))

                tProcess.start()
                # identify actual root families with nested families at top level which require renaming.
                rootFamilies = rFamBaseDataUtils.FindRootFamsFromHosts(rootFamSimple, overallFamilyBaseRootData)
                returnValue.AppendMessage(tProcess.stop() +  ' Found ' + str(len(rootFamilies)) +' root families.' )
                returnValue.result = rootFamilies
            else:
                returnValue.UpdateSep(False, 'No rename directives found. Aborted operation!')
        else:
            returnValue.UpdateSep(False, 'No base family data found. Aborted operation!')
    except Exception as e:
        returnValue.UpdateSep(False, str(e))
    return returnValue