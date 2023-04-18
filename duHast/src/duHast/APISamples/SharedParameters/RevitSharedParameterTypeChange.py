'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to changing Revit shared parameters to family parameters and vise versa.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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


import Autodesk.Revit.DB as rdb

from duHast.APISamples.Common import RevitTransaction as rTran
from duHast.Utilities import Result as res
from duHast.APISamples.SharedParameters.RevitSharedParameters import get_family_parameters


def change_shared_parameter_to_family_parameter(doc, parameterName, prefix = '_'):
    '''
    Changes a shared family parameter to a standard family parameter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameterName: The shared parameter name.
    :type parameterName: str
    :param prefix: Revit requires the new parameter to have a different name to the shard parameter, therefore a prefix to the name is applied, defaults to '_'
    :type prefix: str, optional
    :return: 
        Result class instance.
        - Parameter change status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter and the new family parameter name.
        - result.status will contain the new family parameter.
        On exception (handled by optimizer itself!):
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get the family manager
    manager = doc.FamilyManager
    # get family parameters
    paras = get_family_parameters(doc)
    # flag
    changedParameter = False
    # check whether any parameter in family requires changing
    for p in paras:
        if (p.Definition.Name == parameterName):
            paraOldName = p.Definition.Name
            def action():
                actionReturnValue = res.Result()
                try:

                    parameterNew = manager.ReplaceParameter(
                        p,
                        prefix + paraOldName,
                        p.Definition.ParameterGroup,
                        p.IsInstance
                        )

                    actionReturnValue.update_sep(True, paraOldName + ': Successfully changed shared parameter to family parameter: ' + prefix + paraOldName)
                    actionReturnValue.result.append(parameterNew)
                except Exception as e:
                    actionReturnValue.update_sep(False, paraOldName + ': Failed to change shared parameter to family parameter: ' + str(e))
                return actionReturnValue
            transaction = rdb.Transaction(doc, "change to family parameter")
            returnValue = rTran.in_transaction(transaction, action)
            changedParameter = returnValue.status
    if(changedParameter == False):
        returnValue.status = False
        returnValue.message = 'No parameter matching: ' + parameterName + ' was found. No shared parameter was changed.'
    return returnValue


def change_family_parameter_to_shared_parameter(doc, parameterName, parameterData, parameterDef):
    '''
    Changes a family parameter to a shared parameter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameterName: The family parameter name.
    :type parameterName: str
    :param parameterData: A named tup[le containing the shared parameter information
    :type parameterData: RevitSharedParametersTuple.parameterData
    :param parameterDef: The external definition of the shared parameter.
    :type parameterDef: Autodesk.Revit.DB.ExternalDefinition
    :return: 
        Result class instance.
        - Parameter change status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the family parameter and the new shared parameter name.
        - result.status will contain the new shared parameter.
        On exception (handled by optimizer itself!):
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get the family manager
    manager = doc.FamilyManager
    # get family parameters
    paras = get_family_parameters(doc)
    # flag
    changedParameter = False
    # check whether any parameter in family requires changing
    for p in paras:
        if (p.Definition.Name  == parameterName):
            def action():
                actionReturnValue = res.Result()
                try:

                    parameterNew = manager.ReplaceParameter(
                        p,
                        parameterDef,
                        parameterData.builtInParameterGroup,
                        parameterData.isInstance
                        )

                    actionReturnValue.update_sep(True, parameterName+': Changed family parameter to shared parameter: ' + parameterData.name)
                    actionReturnValue.result.append(parameterNew)
                except Exception as e:
                    actionReturnValue.update_sep(False, parameterName+': Failed to change family parameter to shared parameter.')
                return actionReturnValue
            transaction = rdb.Transaction(doc, "change to shared parameter")
            returnValue = rTran.in_transaction(transaction, action)
            changedParameter = returnValue.status
    if(changedParameter == False):
        returnValue.status = False
        returnValue.message = 'No parameter matching: ' + parameterName + ' was found. No family parameter was changed.'
    return returnValue