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

#import clr
#import System
from duHast.Utilities.timer import Timer

from duHast.Utilities import Result as res
#from duHast.Utilities import Utility as util
from duHast.APISamples.Family.Reporting import RevitFamilyBaseDataUtils as rFamBaseDataUtils
from duHast.APISamples.Family import RevitFamilyRenameFilesUtils as rFamRenameUtils

#---------------------------------------------------------------------------------------------------------------
#                      find families containing nested families needing to be renamed
#---------------------------------------------------------------------------------------------------------------

def _find_host_families(overallFamilyBaseNestedData, fileRenameList):
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
        hosts = rFamBaseDataUtils.find_direct_host_families(fileRenameFamily, overallFamilyBaseNestedData)
        # update dictionary with new hosts only
        for h in hosts:
            if( h not in hostFamilies):
                hostFamilies[h] = hosts[h]
    return hostFamilies

def find_host_families_with_nested_families_requiring_rename(inputDirectoryPath):
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
        overallFamilyBaseRootData, overallFamilyBaseNestedData = rFamBaseDataUtils.read_overall_family_data_list_from_directory(inputDirectoryPath)
        returnValue.append_message('{} Read overall family base data report. {} root entries found and {} nested entries found.'.format(tProcess.stop(),len(overallFamilyBaseRootData), len(overallFamilyBaseNestedData)))
        # check if input file existed and contained data
        if(len(overallFamilyBaseRootData) > 0):
            tProcess.start()
            fileRenameListStatus = rFamRenameUtils.get_rename_directives(inputDirectoryPath)
            returnValue.append_message('{} Read data from file! Rename family entries [{} ] found.'.format(tProcess.stop(),len(fileRenameListStatus.result)))
            # check if any rename directives
            if(len(fileRenameListStatus.result) > 0):
                before = len(overallFamilyBaseNestedData)
                tProcess.start()
                # reduce workload by culling not needed nested family data
                overallFamilyBaseNestedData =  rFamBaseDataUtils.cull_nested_base_data_blocks(overallFamilyBaseNestedData)
                returnValue.append_message('{} Culled nested family base data from : {} to: {} families.'.format(tProcess.stop(),before),len(overallFamilyBaseNestedData))

                tProcess.start()
                # get a list of simplified root data families extracted from nested family path data
                rootFamSimple = rFamBaseDataUtils.find_all_direct_host_families(fileRenameListStatus.result, overallFamilyBaseNestedData)
                returnValue.append_message('{} Found simplified root families: {}'.format(tProcess.stop(),len(rootFamSimple)))

                tProcess.start()
                # identify actual root families with nested families at top level which require renaming.
                rootFamilies = rFamBaseDataUtils.find_root_families_from_hosts(rootFamSimple, overallFamilyBaseRootData)
                returnValue.append_message('{} Found {} root families.'.format(tProcess.stop(),len(rootFamilies)))
                returnValue.result = rootFamilies
            else:
                returnValue.update_sep(False, 'No rename directives found. Aborted operation!')
        else:
            returnValue.update_sep(False, 'No base family data found. Aborted operation!')
    except Exception as e:
        returnValue.update_sep(False, 'Failed to find host families with exception: '.format(e))
    return returnValue