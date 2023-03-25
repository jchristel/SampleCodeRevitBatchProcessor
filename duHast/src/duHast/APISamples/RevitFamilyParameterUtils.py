'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families parameter helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

# import common library
# utility functions for most commonly used Revit API tasks
from duHast.APISamples import RevitTransaction as rTran
# class used for stats reporting
from duHast.Utilities import Result as res

# import Autodesk Revit DataBase namespace
import Autodesk.Revit.DB as rdb

def SetFamilyParameterValueByStorageType(paramW, manager, value):
    returnValue = res.Result()
    try:
        if(paramW.StorageType == rdb.StorageType.Double):
            # THIS IS THE KEY:  Use SetValueString instead of Set.  Set requires your data to be in
            # whatever internal units of measure Revit uses. SetValueString expects your value to 
            # be in whatever the current DisplayUnitType (units of measure) the document is set to 
            # for the UnitType associated with the parameter.
            #
            # So SetValueString is basically how the Revit GUI works.
            manager.SetValueString(paramW, value)
            returnValue.UpdateSep(True, 'Updated '+ paramW.Definition.Name + ' to value: ' + str(value))
        elif(paramW.StorageType == rdb.StorageType.ElementId):
            manager.Set(paramW, value)
            returnValue.UpdateSep(True, 'Updated '+ paramW.Definition.Name + ' to value: ' + str(value))
        elif(paramW.StorageType == rdb.StorageType.Integer):
            manager.Set(paramW, value)
            returnValue.UpdateSep(True, 'Updated '+ paramW.Definition.Name + ' to value: ' + str(value))
        elif(paramW.StorageType == rdb.StorageType.String):
            manager.Set(paramW, value)
            returnValue.UpdateSep(True, 'Updated '+ paramW.Definition.Name + ' to value: ' + value)
        else:
            returnValue.UpdateSep(False, 'Parameter storage type is not supported!')
        
    except Exception as e:
        returnValue.UpdateSep(False, 'failed to set parameter value with exception: '+ str(e))
    return returnValue

def SetFamilyParameterValue(doc, manager, famPara, value):
    #get the parameter
    paramW = manager.get_Parameter(famPara.Definition.Name)
    # set-up action to be executed in transaction
    def action():
        actionReturnValue = res.Result()
        try:
            # attempt to change parameter value
            actionReturnValue = SetFamilyParameterValueByStorageType(paramW, manager, value)
        except Exception as e:
            actionReturnValue.status = False
            actionReturnValue.message = famPara.Definition.Name + ' : Failed to set parameter value: with exception: ' + str(e)
        return actionReturnValue
    transaction = rdb.Transaction(doc, "Setting parameter value")
    returnValue = rTran.in_transaction(transaction, action)
    return returnValue

def SetParameterFormula(doc, manager, famPara, formula):
    def action():
        actionReturnValue = res.Result()
        try:
            # set parameter formula
            manager.SetFormula(famPara, formula)
            actionReturnValue.message = famPara.Definition.Name + ' : parameter formulas successfully set.'
            actionReturnValue.result.append(famPara)
        except Exception as e:
            actionReturnValue.status = False
            actionReturnValue.message = famPara.Definition.Name + ' : Failed to set parameter formula: with exception: ' + str(e)
        return actionReturnValue
    transaction = rdb.Transaction(doc, "Setting parameter formula")
    returnValue = rTran.in_transaction(transaction, action)
    return returnValue
