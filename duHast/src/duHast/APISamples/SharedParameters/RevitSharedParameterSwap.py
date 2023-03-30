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
from duHast.APISamples import RevitCommonAPI as com
from duHast.Utilities import Result as res
from duHast.Utilities import Utility as util
from duHast.APISamples import RevitSharedParameterAdd as rSharedPAdd
from duHast.APISamples import RevitSharedParametersTuple as rSharedT
from duHast.APISamples import RevitParameterGrouping as rPG
from duHast.APISamples import RevitSharedParameters as rSharedPara

from collections import namedtuple

'''
Tuple containing settings data on how to swap a shared parameter retrieved from a file.
'''

parameterSettingsData = namedtuple('parameterSettingsData', 'oldParameterName newParameterData sharedParameterPath')

def _loadSharedParameterDataFromFile(filePath):
    '''
    _summary_

    :param filePath: Fully qualified file path to shared parameter change directive file.
    :type filePath: str

    :return: A dictionary in format; key: current parameter name, value: named tuple of type parameterSettingsData
    :rtype: {str:named tuple}
    '''

    parameterMapper = {}
    fileData = util.ReadCSVfile(filePath)
    for i in range (1, len(fileData)):
        row = fileData[i]
        if(len(row) == 5):
            flag = False
            if(row[3].upper() == "TRUE"):
                flag = True
            t = rSharedT.parameterData (row[1], flag, rPG.ParameterGroupingToBuiltInParameterGroups[row[4]])
            parameterMapper[row[0]] = parameterSettingsData(row[0], t, row[2])
    return parameterMapper

def SwapSharedParameters(doc, changeDirectiveFilePath):
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
    parameterDirectives = _loadSharedParameterDataFromFile(changeDirectiveFilePath)
    if(len(parameterDirectives) > 0):
        # loop over directive and
        for pDirective in parameterDirectives:
            # load shared para file
            sharedParaDefFile = rSharedPAdd.LoadSharedParameterFile(doc, parameterDirectives[pDirective].sharedParameterPath)
            returnValue.AppendMessage('Read shared parameter file: ' + parameterDirectives[pDirective].sharedParameterPath)
            if(sharedParaDefFile != None):
                #   - swap shared parameter to family parameter
                statusChangeToFamPara = rSharedPara.ChangeSharedParameterToFamilyParameter(doc, pDirective, _parameterPrefix_)
                returnValue.Update(statusChangeToFamPara)
                if(statusChangeToFamPara.status):
                    #   - delete all shared parameter definition
                    statusDeleteOldSharedParaDef = rSharedPara.DeleteSharedParameterByName(doc, pDirective)
                    returnValue.Update(statusDeleteOldSharedParaDef)
                    if(statusDeleteOldSharedParaDef.status):
                        # get shared parameter definition
                        sParaDef = rSharedPara.GetSharedParameterDefinition(parameterDirectives[pDirective].newParameterData.name, sharedParaDefFile)
                        #   - add new shared parameter
                        if(sParaDef != None):
                            returnValue.AppendMessage('Retrieved shared parameter definition for: ' + parameterDirectives[pDirective].newParameterData.name) 
                            #   - swap family parameter to shared parameter
                            statusSwapFamToSharedP = rSharedPara.ChangeFamilyParameterToSharedParameter(
                                doc, 
                                _parameterPrefix_ + pDirective, # add prefix
                                parameterDirectives[pDirective].newParameterData, 
                                sParaDef
                                )
                            returnValue.Update(statusSwapFamToSharedP)
                        else:
                            returnValue.UpdateSep(False, 'Failed to get shared parameter definition from file.')
                    else:
                        returnValue.Update(statusDeleteOldSharedParaDef)
                else:
                    returnValue.Update(statusChangeToFamPara)
            else:
                returnValue.UpdateSep(False, 'Failed to load shared parameter def file from: ' + parameterDirectives[pDirective].sharedParameterPath)
    else:
        returnValue.status = False
        returnValue.message = 'No change directives in file.'
    return returnValue