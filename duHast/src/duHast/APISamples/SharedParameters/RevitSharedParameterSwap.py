'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a function to swap out one shard parameter for another.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The swap is done by:
- changing current shared parameter to a family parameter (dummy)
- deleting the old shared parameter definition
- swapping the family parameter (dummy) to the new shared parameter.

Note: storage types of old and new shared parameter need to be identical.

Parameter change directives are read from a .csv file:

- header row: yes
- column 1: current shared parameter name
- column 2: new shared parameter name
- column 3: fully qualified file path of shared parameter file
- column 4: Is parameter instance (True / False)
- column 5: parameter grouping name ( refer to module: RevitParameterGrouping)

'''

#
#License:
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

import clr
import System

# import common library modules
#from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.Utilities import Result as res
from duHast.Utilities import FilesCSV as fileCSV
from duHast.APISamples.SharedParameters import RevitSharedParameterAdd as rSharedPAdd
from duHast.APISamples.SharedParameters import RevitSharedParametersTuple as rSharedT
from duHast.APISamples.Common import RevitParameterGrouping as rPG
from duHast.APISamples.SharedParameters import RevitSharedParameters as rSharedPara
from duHast.APISamples.SharedParameters import RevitSharedParametersDelete as rSharedParaDelete
from duHast.APISamples.SharedParameters import RevitSharedParameterTypeChange as rSharedTypeChange

from collections import namedtuple


'''
Tuple containing settings data on how to swap a shared parameter retrieved from a file.
'''

PARAMETER_SETTINGS_DATA = namedtuple('parameterSettingsData', 'oldParameterName newParameterData sharedParameterPath')

def _load_shared_parameter_data_from_file(filePath):
    '''
    _summary_

    :param filePath: Fully qualified file path to shared parameter change directive file.
    :type filePath: str

    :return: A dictionary in format; key: current parameter name, value: named tuple of type parameterSettingsData
    :rtype: {str:named tuple}
    '''

    parameterMapper = {}
    fileData = fileCSV.read_csv_file(filePath)
    for i in range (1, len(fileData)):
        row = fileData[i]
        if(len(row) == 5):
            flag = False
            if(row[3].upper() == "TRUE"):
                flag = True
            t = rSharedT.PARAMETER_DATA (row[1], flag, rPG.PRAMETER_GROPUING_TO_BUILD_IN_PARAMETER_GROUPS[row[4]])
            parameterMapper[row[0]] = PARAMETER_SETTINGS_DATA(row[0], t, row[2])
    return parameterMapper

def swap_shared_parameters(doc, changeDirectiveFilePath):
    '''
    Swaps out a shared parameter for another. (refer to module header for details)

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param changeDirectiveFilePath: Fully qualified file path to shared parameter change directive.
    :type changeDirectiveFilePath: str

    :return: 
        Result class instance.

        - False if an exception occurred, otherwise True.
        - result.message will contain the names of the changed shared parameter(s).
        - result status will contain lists of new shared parameters
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    _parameterPrefix_ = "_dummy_"
    # load change directive
    parameterDirectives = _load_shared_parameter_data_from_file(changeDirectiveFilePath)
    if(len(parameterDirectives) > 0):
        # loop over directive and
        for pDirective in parameterDirectives:
            # load shared para file
            sharedParaDefFile = rSharedPAdd.load_shared_parameter_file(doc, parameterDirectives[pDirective].sharedParameterPath)
            returnValue.append_message('Read shared parameter file: ' + parameterDirectives[pDirective].sharedParameterPath)
            if(sharedParaDefFile != None):
                #   - swap shared parameter to family parameter
                statusChangeToFamPara = rSharedTypeChange.change_shared_parameter_to_family_parameter(doc, pDirective, _parameterPrefix_)
                returnValue.update(statusChangeToFamPara)
                if(statusChangeToFamPara.status):
                    #   - delete all shared parameter definition
                    statusDeleteOldSharedParaDef = rSharedParaDelete.delete_shared_parameter_by_name(doc, pDirective)
                    returnValue.update(statusDeleteOldSharedParaDef)
                    if(statusDeleteOldSharedParaDef.status):
                        # get shared parameter definition
                        sParaDef = rSharedPara.get_shared_parameter_definition(parameterDirectives[pDirective].newParameterData.name, sharedParaDefFile)
                        #   - add new shared parameter
                        if(sParaDef != None):
                            returnValue.append_message('Retrieved shared parameter definition for: ' + parameterDirectives[pDirective].newParameterData.name) 
                            #   - swap family parameter to shared parameter
                            statusSwapFamToSharedP = rSharedTypeChange.change_family_parameter_to_shared_parameter(
                                doc, 
                                _parameterPrefix_ + pDirective, # add prefix
                                parameterDirectives[pDirective].newParameterData, 
                                sParaDef
                                )
                            returnValue.update(statusSwapFamToSharedP)
                        else:
                            returnValue.update_sep(False, 'Failed to get shared parameter definition from file.')
                    else:
                        returnValue.update(statusDeleteOldSharedParaDef)
                else:
                    returnValue.update(statusChangeToFamPara)
            else:
                returnValue.update_sep(False, 'Failed to load shared parameter def file from: ' + parameterDirectives[pDirective].sharedParameterPath)
    else:
        returnValue.status = False
        returnValue.message = 'No change directives in file.'
    return returnValue