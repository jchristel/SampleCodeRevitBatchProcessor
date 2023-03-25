'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit API utility functions to set parameter values.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# class used for stats reporting
from duHast.Utilities import Result as res

# import everything from Autodesk Revit DataBase namespace (Revit API)
import Autodesk.Revit.DB as rdb
# utilities
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitTransaction as rTran

# type checker
#from typing import List, Callable

#----------------------------------------parameters value setters -----------------------------------------------

def set_parameter_value(
    para, 
    value_as_string, # type: str
    doc,
    in_transaction = rTran.in_transaction
    ):
    '''
    Sets the parameter value by trying to convert the past in string representing the value into the appropriate value type.

    Changing a parameter value requires this action to run inside a transaction.

    :param para: Parameter of which the value is to be set.
    :type para: Autodesk.Revit.DB.Parameter
    :param value_as_string: The new parameter value.
    :type value_as_string: str
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param in_transaction: The transaction wrapper function to be used.
    :type in_transaction: func(Autodesk.Revit.DB.Transaction, action(), Autodesk.Revit.DB.Document)

    :raise: Any exception will need to be managed by the function caller.

    ToDo: This needs updating for Revit 2022+ to take into account changes in Revit API: Forge Parameters

    :return: 
        Result class instance.

        - Set parameter status (bool) returned in result.status. False if an exception occurred, otherwise True.
        - Result.message property updated in format: Changed parameter value of type x ['parameter name'] : 'old value' to: 'new value'.
        
        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    old_value = rParaGet.get_parameter_value(para)
    transaction_name = 'Update to parameter value'
    # different parameter storage types will require different actions due to value type past in is a string which will need converting
    # first before applied to the parameter
    if(para.StorageType == rdb.StorageType.ElementId):
        new_id = rdb.ElementId(int(value_as_string))
        # changing parameter value is required to run inside a transaction
        def action():
            # set up a result instance to be returned to caller with transaction outcome
            action_return_value = res.Result()
            try:
                para.Set(new_id)
                action_return_value.message = 'Changed parameter value of type Id.[ {} ] from: {} to: {}'.format(para.Definition.Name ,old_value ,value_as_string)
            except Exception as e:
                action_return_value.UpdateSep(False, 'Failed with exception: ' + str(e))
            return action_return_value
        transaction = rdb.Transaction(doc,transaction_name)
        return_value = in_transaction(transaction, action)
    elif(para.StorageType == rdb.StorageType.Double):
        # THIS IS THE KEY:  Use SetValueString instead of Set.  Set requires your data to be in
        # whatever internal units of measure Revit uses. SetValueString expects your value to 
        # be in whatever the current DisplayUnitType (units of measure) the document is set to 
        # for the UnitType associated with the parameter.
        #
        # So SetValueString is basically how the Revit GUI works.
        def action():
            action_return_value = res.Result()
            try:
                para.SetValueString(value_as_string)
                action_return_value.message = 'Changed parameter value of type double.[ {} ] from: {} to: {}'.format(para.Definition.Name ,old_value ,value_as_string)
            except Exception as e:
                action_return_value.UpdateSep(False, 'Failed with exception: {}'.format(e))
            return action_return_value
        transaction = rdb.Transaction(doc,transaction_name)
        return_value = in_transaction(transaction, action)
    elif (para.StorageType == rdb.StorageType.Integer):
        def action():
            action_return_value = res.Result()
            try:
                para.Set(int(value_as_string))
                action_return_value.message = 'Changed parameter value of type integer.[ {} ] from: {} to: {}'.format(para.Definition.Name ,old_value ,value_as_string)
            except Exception as e:
                action_return_value.UpdateSep(False, 'Failed with exception: {}'.format(e))
            return action_return_value
        transaction = rdb.Transaction(doc,transaction_name)
        return_value = in_transaction(transaction, action)
    elif (para.StorageType == rdb.StorageType.String):
        def action():
            action_return_value = res.Result()
            try:
                para.Set(value_as_string)
                action_return_value.message = 'Changed parameter value of type string.[ {} ] from: {} to: {}'.format(para.Definition.Name ,old_value ,value_as_string)
            except Exception as e:
                action_return_value.UpdateSep(False, 'Failed with exception: {}'.format(e))
            return action_return_value
        transaction = rdb.Transaction(doc,transaction_name)
        return_value = in_transaction(transaction, action, doc)
    else:  
        # dead end
        return_value.UpdateSep(False, 'Dont know what to do with this storage type: {}'.format(para.StorageType))
    return return_value

def set_built_in_parameter_value(
    doc, 
    element, 
    built_in_parameter_def, 
    value_as_string, # type: str
    parameter_value_setter = set_parameter_value
    ):
    '''
    Sets the built-in parameter value by trying to convert the past in string representing the value into the appropriate value type.

    Changing a parameter value requires this action to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: Element to which the built-in parameter belongs.
    :type element: Autodesk.Revit.DB.Element
    :param built_in_parameter_def: The parameters built-in definition of which the value is to be returned.
    :type built_in_parameter_def: Autodesk.Revit.DB.Definition
    :param value_as_string: The new parameter value.
    :type value_as_string: str
    :param parameter_value_setter:
        The function which takes the parameter as an argument and changes it's value to.
        The function needs to accept these args: parameter, new parameter value as string, document
    :type parameter_value_setter: function 
    :raise: As per value setter method.
    
    ToDo: This needs updating for Revit 2022+ to take into account changes in Revit API: Forge Parameters

    :return: 
        Result class instance.

        - Set parameter status (bool) returned in result.status. False if an exception occurred, or parameter does not exist on element, otherwise True.
        - Result.message property updated in format: Changed parameter value of type x ['parameter name'] : 'old value' to: 'new value'.
        
        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.
        
    :rtype: :class:`.Result`
    '''
    
    return_value = res.Result()
    return_value.UpdateSep(False, 'Parameter not found')
    paras = element.GetOrderedParameters()
    for para in paras:
        if(para.Definition.BuiltInParameter == built_in_parameter_def):
            return_value = parameter_value_setter(para, value_as_string, doc)
            break
    return return_value