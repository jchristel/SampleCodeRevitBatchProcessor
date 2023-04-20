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
from duHast.APISamples.Common import transaction as rTran
# class used for stats reporting
from duHast.Utilities import Result as res

# import Autodesk Revit DataBase namespace
import Autodesk.Revit.DB as rdb

def set_family_parameter_value_by_storage_type(param_w, manager, value):
    return_value = res.Result()
    try:
        if(param_w.StorageType == rdb.StorageType.Double):
            # THIS IS THE KEY:  Use SetValueString instead of Set.  Set requires your data to be in
            # whatever internal units of measure Revit uses. SetValueString expects your value to 
            # be in whatever the current DisplayUnitType (units of measure) the document is set to 
            # for the UnitType associated with the parameter.
            #
            # So SetValueString is basically how the Revit GUI works.
            manager.SetValueString(param_w, value)
            return_value.update_sep(True, 'Updated {} to value: {}'.format(param_w.Definition.Name ,value))
        elif(param_w.StorageType == rdb.StorageType.ElementId):
            manager.Set(param_w, value)
            return_value.update_sep(True, 'Updated {} to value: {}'.format(param_w.Definition.Name, value))
        elif(param_w.StorageType == rdb.StorageType.Integer):
            manager.Set(param_w, value)
            return_value.update_sep(True, 'Updated {} to value: {}'.format(param_w.Definition.Name ,value))
        elif(param_w.StorageType == rdb.StorageType.String):
            manager.Set(param_w, value)
            return_value.update_sep(True, 'Updated {} to value: {}'.format(param_w.Definition.Name ,value))
        else:
            return_value.update_sep(False, 'Parameter storage type is not supported!')
        
    except Exception as e:
        return_value.update_sep(False, 'failed to set parameter value with exception: {}'.format(e))
    return return_value

def set_family_parameter_value(doc, manager, fam_para, value):
    #get the parameter
    param_w = manager.get_Parameter(fam_para.Definition.Name)
    # set-up action to be executed in transaction
    def action():
        action_return_value = res.Result()
        try:
            # attempt to change parameter value
            action_return_value = set_family_parameter_value_by_storage_type(param_w, manager, value)
        except Exception as e:
            action_return_value.status = False
            action_return_value.message = fam_para.Definition.Name + ' : Failed to set parameter value: with exception: ' + str(e)
        return action_return_value
    transaction = rdb.Transaction(doc, "Setting parameter value")
    return_value = rTran.in_transaction(transaction, action)
    return return_value

def set_parameter_formula(doc, manager, fam_para, formula):
    def action():
        action_return_value = res.Result()
        try:
            # set parameter formula
            manager.SetFormula(fam_para, formula)
            action_return_value.message = fam_para.Definition.Name + ' : parameter formulas successfully set.'
            action_return_value.result.append(fam_para)
        except Exception as e:
            action_return_value.status = False
            action_return_value.message = fam_para.Definition.Name + ' : Failed to set parameter formula: with exception: ' + str(e)
        return action_return_value
    transaction = rdb.Transaction(doc, "Setting parameter formula")
    return_value = rTran.in_transaction(transaction, action)
    return return_value
