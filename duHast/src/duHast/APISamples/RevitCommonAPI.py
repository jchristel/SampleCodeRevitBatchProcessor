'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Common Revit API utility functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

#import datetime
import System
import clr
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

#import glob
# class used for stats reporting
from duHast.Utilities import Result as res

# import everything from Autodesk Revit DataBase namespace (Revit API)
import Autodesk.Revit.DB as rdb
import os.path as path
# utilities
from duHast.Utilities import Utility as util
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitElementParameterSetUtils as rParaSet
from duHast.APISamples import RevitTransaction as rTran
# importing revit groups module
from duHast.APISamples import RevitGroups as rGroup

# type checker
#from typing import List, Callable

#--------------------------------------------Transactions-----------------------------------------

def InTransaction(
    tranny, # 
    action, # type: Callable[[], res.Result]
    doc = None    
    ):
    # type: (...) -> res.Result
    '''
    !DEPRECATED! Refer to module RevitTransaction. Revit transaction wrapper.

    This function is used to execute any actions requiring a transaction in the Revit api. On exception this will roll back the transaction.

    :param tranny: The transaction to be executed.
    :type tranny: Autodesk.Revit.DB.Transaction 
    :param action: The action to be nested within the transaction. This needs to return a Result class instance!
    :type action: action().
    
    :return: 
        Result class instance.
        
        - .result = True if successfully executed transaction, otherwise False.
        
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        tranny.Start()
        try:
            trannyResult = action()
            tranny.Commit()
            # check what came back
            if (trannyResult != None):
                # store false value 
                returnValue = trannyResult
        except Exception as e:
            tranny.RollBack()
            returnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnValue

#----------------------------------------parameters-----------------------------------------------

def CheckParameterValue(
    para, 
    paraCondition, # type: Callable[[str,str],bool]
    conditionValue):
    # type: (...) -> bool
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils:check_parameter_value 
    Checks a parameter value based on passed in condition function.

    This extracts the value of the past in parameter and compares it against a past in value using 
    the also past in compare function. 
    Note that values will be past into compare function as ASCII encoded.

    :param para: Parameter of which the value is to be checked.
    :type para: Autodesk.Revit.DB.Parameter 
    :param paraCondition:
        Function taking 2 arguments:
        First argument is the value to be checked against
        Second argument is the actual parameter value
        Needs to return a bool!
        Both arguments will be ASCII encoded at passing in.
    :type paraCondition: function
    :param conditionValue: The value to be checked for
    :type conditionValue: var 
    :raise: Any exception will need to be managed by the function caller.

    :return:
        True if condition value is evaluated to be True by past in function paraCondition.
        Will return False if compare function returns None or a False.
    :rtype: bool
    
    '''
    # set default return value
    isMatch = False
    pValue = rParaGet.get_parameter_value(para)
    # evaluate parameter value with past in value using past in function
    compareOutCome = paraCondition(util.EncodeAscii(conditionValue), util.EncodeAscii(pValue))
    # check the return value for a bool (True) only. Everything else will return False
    if (compareOutCome == True):
        isMatch = True
    return isMatch

#----------------------------------------parameters value getter over loads-----------------------------------------------

def getter_none(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Used for parameters where the storage type is None
    
    :param para: _description_
    :type para: _type_
    '''

    return 'Invalid storage type: (NONE)'

def getter_double_or_int_as_string(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value of type double or integer as string.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: String representation of double or integer value. If value is empty it will return None
    :rtype: str or None
    '''

    pValue = None
    if(para.AsValueString() != None and para.AsValueString() != ''):
        pValue = para.AsValueString()
    return pValue

def getter_double_as_double(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value of type double as a double.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Double value. If value is empty it will return None
    :rtype: Double or None
    '''

    pValue = None
    if(para.AsValueString() != None and para.AsValueString() != ''):
        pValue = para.AsDouble()
    return pValue

def getter_double_as_double_converted_to_millimeter(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value of type double as a double converted to mm (if required).
    Revit uses feet internally for any length value!

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Double value. If value is empty it will return None
    :rtype: Double or None
    '''

    pValue = None
    if(para.AsValueString() != None and para.AsValueString() != ''):
        if(para.Definition.ParameterType == rdb.ParameterType.Length):
            pValue = para.AsDouble() * 304.8
        else:
            pValue = para.AsDouble()
    return pValue

def getter_int_as_int(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value of type integer as a integer.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Integer value. If value is empty it will return None
    :rtype: Integer or None
    '''

    pValue = None
    if(para.AsValueString() != None and para.AsValueString() != ''):
        pValue = para.AsInteger()
    return pValue

def getter_string_as_UTF8_string(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value of type string as a utf-8 formatted string.
    
    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: String value. If value is empty it will return None
    :rtype: String or None
    '''

    pValue = None
    if(para.StorageType == rdb.StorageType.String):
        if(para.AsString() != None and para.AsString() != ''):
            pValue = para.AsString().encode('utf-8')
    return pValue

def getter_string_as_string(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value of type string as a string.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: String value. If value is empty it will return None
    :rtype: String or None
    '''

    pValue = None
    if(para.StorageType == rdb.StorageType.String):
        if(para.AsString() != None and para.AsString() != ''):
            pValue = para.AsString()
    return pValue

def getter_element_id_as_string(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value of type element id as a string.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: String value. If value is empty it will return None
    :rtype: String or None
    '''

    pValue = None
    if(para.StorageType == rdb.StorageType.ElementId):
        if(para.AsElementId() != None):
            pValue = str(para.AsElementId())
    return pValue     

def getter_element_id_as_element_id(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value of type element id as a element id.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Element id value. If value is empty it will return None
    :rtype: Element id or None
    '''

    pValue = None
    if(para.StorageType == rdb.StorageType.ElementId):
        if(para.AsElementId() != None):
            pValue = para.AsElementId()
    return pValue

def getter_element_id_as_element_int(para):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value of type element id as an integer.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Integer value. If value is empty it will return None
    :rtype: Integer or None
    '''

    pValue = None
    if(para.StorageType == rdb.StorageType.ElementId):
        if(para.AsElementId() != None):
            pValue = para.AsElementId().IntegerValue
    return pValue 

#----------------------------------------parameters value getters -----------------------------------------------

def get_parameter_value_with_over_load (para, parameter_value_getters):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value in format depending on storage type.
    
    Storage type can be:

    - Double
    - Integer
    - String
    - ElementId

    Will throw an exception if a storage type is not covered by parameter value getter functions.

    :param para: The Parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: The parameter value or if empty: None.
    :rtype: Depends on value getters functions
    '''

    # set return value default 
    pValue = None
    try:
        # extract parameter value depending on its storage type
        if(para.StorageType == rdb.StorageType.Double):
            if(para.AsValueString()!= None and para.AsValueString() != ''):
                if(rdb.StorageType.Double in parameter_value_getters):
                    pValue = parameter_value_getters[rdb.StorageType.Double](para)
                else:
                    raise ValueError('No parameter value getter for storage type Double provided')
        elif(para.StorageType == rdb.StorageType.Integer):
            if(para.AsValueString()!= None and para.AsValueString() != ''):
                if(rdb.StorageType.Integer in parameter_value_getters):
                    pValue = parameter_value_getters[rdb.StorageType.Integer](para)
                else:
                    raise ValueError('No parameter value getter for storage type Integer provided')
        elif(para.StorageType == rdb.StorageType.String):
            if(para.AsString() != None and para.AsString() != ''):
                if(rdb.StorageType.String in parameter_value_getters):
                    pValue = parameter_value_getters[rdb.StorageType.String](para)
                else:
                    raise ValueError('No parameter value getter for storage type String provided')
        elif(para.StorageType == rdb.StorageType.ElementId):
            if(para.AsElementId() != None):
                if(rdb.StorageType.ElementId in parameter_value_getters):
                    pValue = parameter_value_getters[rdb.StorageType.ElementId](para)
                else:
                    raise ValueError('No parameter value getter for storage type Element Id provided')
        else:
            # this should be invalid storage type only
            pValue = parameter_value_getters[str(None)](para)
    except  Exception as e:
        pValue = 'Exception: {}'.format(e)
    return pValue

def getParameterValue(
    para
    ):
    # type: (...) -> str
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns a parameter value as string.

    Returns a parameter value as string independent of its storage type.

    :param para: Parameter of which the value is to be returned.
    :type para: Autodesk.Revit.DB.Parameter
    :raise: If an exception occurs the exception message will be returned as the parameter value prefixed with 'Exception: '

    :return:
        Default value is 'no Value' if parameter value is empty.
        Otherwise the actual parameter value.
        Will return 'Exception: ' + exception message if an exception occurred.
    :rtype: str
    '''

    # set return value default 
    pValue = 'no Value'
    try:
        value_getter = {
            rdb.StorageType.Double : getter_double_or_int_as_string,
            rdb.StorageType.Integer : getter_double_or_int_as_string,
            rdb.StorageType.String : getter_string_as_string,
            rdb.StorageType.ElementId : getter_element_id_as_string,
            str(None) : getter_none
       }

        pValue = get_parameter_value_with_over_load (para, value_getter)

        '''
        # extract parameter value depending on its storage type
        if(para.StorageType == rdb.StorageType.Double or para.StorageType == rdb.StorageType.Integer):
            if(para.AsValueString()!= None and para.AsValueString() != ''):
                pValue = para.AsValueString()
        elif(para.StorageType == rdb.StorageType.String):
            if(para.AsString() != None and para.AsString() != ''):
                pValue = para.AsString()
        elif(para.StorageType == rdb.StorageType.ElementId):
            if(para.AsElementId() != None):
                pValue = str(para.AsElementId())
    '''
    except  Exception as e:
        pValue = 'Exception: '+str(e)
    
    return pValue

def GetParameterValueUTF8String(
    para
    ):
    # type: (...) -> str
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. 

    Returns the parameter value as utf-8 string independent of its storage type.

    :param para: Parameter of which the value is to be returned.
    :type para: Autodesk.Revit.DB.Parameter 
    :raise: If an exception occurs the exception message will be returned as the parameter value prefixed with 'Exception: '

    :return:
        Default value is 'no Value' if parameter value is empty.
        Otherwise the actual parameter value.
        Will return 'Exception: ' + exception message if an exception occurred.
    :rtype: str
    '''

    # set return value default 
    pValue = 'no Value'

    value_getter = {
            rdb.StorageType.Double : getter_double_or_int_as_string, # no specific utf encoding required
            rdb.StorageType.Integer : getter_double_or_int_as_string, # no specific utf encoding required
            rdb.StorageType.String : getter_string_as_UTF8_string,
            rdb.StorageType.ElementId : getter_element_id_as_string, # no specific utf encoding required
            str(None) : getter_none
       }
    
    pValue = get_parameter_value_with_over_load (para, value_getter)

    '''
    # extract parameter value depending on its storage type
    if(para.StorageType == rdb.StorageType.Double or para.StorageType == rdb.StorageType.Integer):
        if(para.AsValueString()!= None and para.AsValueString() != ''):
            pValue = para.AsValueString().encode('utf-8')
    elif(para.StorageType == rdb.StorageType.String):
        if(para.AsString() != None and para.AsString() != ''):
            pValue = para.AsString().encode('utf-8')
    elif(para.StorageType == rdb.StorageType.ElementId):
        if(para.AsElementId() != None):
            pValue = str(para.AsElementId()).encode('utf-8')
    '''
    return pValue

def GetParameterValueAsInteger(
    para
    ):
    # type: (...) -> int
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. 

    Returns the parameter value as integer only if the storage type is integer.

    :param para: Parameter of which the value is to be returned.
    :type para: Autodesk.Revit.DB.Parameter 
    :raise: Any exception will need to be managed by the function caller.

    :return:
        Default value is -1 if parameter value is empty or storage type is not integer.
        Otherwise the actual parameter value.
    :rtype: int
    '''

    # set return value default
    pValue = -1
    # extract parameter value depending on whether its storage type is integer, otherwise default value
    if(para.StorageType == rdb.StorageType.Integer):
        pValue = para.AsInteger()
    return pValue

def GetParameterValueAsElementId(
    para
    ):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. 

    Returns the parameter value as element Id only if the storage type is ElementId.

    :param para: Parameter of which the value is to be returned.
    :type para: Autodesk.Revit.DB.Parameter 
    :raise: Any exception will need to be managed by the function caller.

    :return:
        Default value is -1 if parameter value is empty or storage type is not integer.
        Otherwise the actual parameter value.
    :rtype: int
    '''

    # set return value default
    pValue = rdb.ElementId.InvalidElementId
    # extract parameter value depending on whether its storage type is integer, otherwise default value
    if(para.StorageType == rdb.StorageType.ElementId):
        pValue = para.AsElementId()
    return pValue

def get_all_parameters_and_values_wit_custom_getters(element, parameter_value_getters):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. Returns all parameters and their values as using custom value getter associated with provided element in form of a dictionary.

    :param element: The element
    :type element: var

    :return: Dictionary where key is the parameter name, and the value is the parameter value.
    :rtype: {str:var}
    '''
    return_value = {}
    paras = element.GetOrderedParameters()
    for p in paras:
        p_value =  get_parameter_value_with_over_load (p, parameter_value_getters)
        return_value[p.Definition.Name] = p_value
    return return_value

def GetBuiltInParameterValue(element, builtInParameterDef, parameterValueGetter = rParaGet.get_parameter_value_utf8_string):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. 

    Returns the built-in parameter value. Return value type depends on past in value getter function. Default is UTF-8 encoded string.

    :param element: Element to which the built-in parameter belongs.
    :type element: Autodesk.Revit.DB.Element 
    :param builtInParameterDef: The parameters built-in definition of which the value is to be returned.
    :type builtInParameterDef: Autodesk.Revit.DB.Definition 
    :param parameterValueGetter:
        The function which takes the parameter as an argument and returns it's value.
    :type parameterValueGetter: function
    :raise: As per value getter method.

    :return:
        Default value is None if parameter does not exist on element.
        Otherwise the actual parameter value as per value getter method.
    :rtype: var
    '''

    # set return value default
    parameterValue = None
    paras = element.GetOrderedParameters()
    for para in paras:
        if(para.Definition.BuiltInParameter == builtInParameterDef):
            parameterValue = parameterValueGetter(para)
            break
    return parameterValue

def GetParameterValueByName(
    element, 
    parameterName, # type: str
    parameterValueGetter = rParaGet.get_parameter_value_utf8_string
    ):
    '''
    !DEPRECATED! Refer to module RevitElementParameterGetUtils. 

    Return value type depends on past in value getter function. Default is UTF-8 encoded string.

    :param element: Element to which the built-in parameter belongs.
    :type element: Autodesk.Revit.DB.Element
    :param parameterName: The parameters name of which the value is to be returned.
    :type parameterName: str
    :param parameterValueGetter:
        The function which takes the parameter as an argument and returns it's value.
    :type parameterValueGetter: function
    :raise: As per value getter method.

    :return:
        Default value is None if parameter does not exist on element.
        Otherwise the actual parameter value as per value getter method.
    :rtype: var
    '''

    # set return value default
    parameterValue = None
    paras = element.GetOrderedParameters()
    for para in paras:
        if(para.Definition.Name == parameterName):
            parameterValue = parameterValueGetter(para)
            break
    return parameterValue

#----------------------------------------parameters value setters -----------------------------------------------

def setParameterValue(
    para, 
    valueAsString, # type: str
    doc,
    in_transaction = rTran.in_transaction
    ):
    '''
    !DEPRECATED! Refer to module RevitElementParameterSetUtils.

    Sets the parameter value by trying to convert the past in string representing the value into the appropriate value type.

    Changing a parameter value requires this action to run inside a transaction.

    :param para: Parameter of which the value is to be set.
    :type para: Autodesk.Revit.DB.Parameter
    :param valueAsString: The new parameter value.
    :type valueAsString: str
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

    returnValue = res.Result()
    oldValue = rParaGet.get_parameter_value(para)
    transactionName = 'Update to parameter value'
    # different parameter storage types will require different actions due to value type past in is a string which will need converting
    # first before applied to the parameter
    if(para.StorageType == rdb.StorageType.ElementId):
        newId = rdb.ElementId(int(valueAsString))
        # changing parameter value is required to run inside a transaction
        def action():
            # set up a result instance to be returned to caller with transaction outcome
            actionReturnValue = res.Result()
            try:
                para.Set(newId)
                actionReturnValue.message = 'Changed parameter value of type Id.[ {} ] from: {} to: {}'.format(para.Definition.Name ,oldValue ,valueAsString)
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,transactionName)
        returnValue = rTran.in_transaction(transaction, action)
    elif(para.StorageType == rdb.StorageType.Double):
        # THIS IS THE KEY:  Use SetValueString instead of Set.  Set requires your data to be in
        # whatever internal units of measure Revit uses. SetValueString expects your value to 
        # be in whatever the current DisplayUnitType (units of measure) the document is set to 
        # for the UnitType associated with the parameter.
        #
        # So SetValueString is basically how the Revit GUI works.
        def action():
            actionReturnValue = res.Result()
            try:
                para.SetValueString(valueAsString)
                actionReturnValue.message = 'Changed parameter value of type double.[ {} ] from: {} to: {}'.format(para.Definition.Name ,oldValue ,valueAsString)
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,transactionName)
        returnValue = rTran.in_transaction(transaction, action)
    elif (para.StorageType == rdb.StorageType.Integer):
        def action():
            actionReturnValue = res.Result()
            try:
                para.Set(int(valueAsString))
                actionReturnValue.message = 'Changed parameter value of type integer.[ {} ] from: {} to: {}'.format(para.Definition.Name ,oldValue ,valueAsString)
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,transactionName)
        returnValue = rTran.in_transaction(transaction, action)
    elif (para.StorageType == rdb.StorageType.String):
        def action():
            actionReturnValue = res.Result()
            try:
                para.Set(valueAsString)
                actionReturnValue.message = 'Changed parameter value of type string.[ {} ] from: {} to: {}'.format(para.Definition.Name ,oldValue ,valueAsString)
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,transactionName)
        returnValue = rTran.in_transaction(transaction, action, doc)
    else:  
        # dead end
        returnValue.UpdateSep(False,'Dont know what to do with this storage type: (NONE) '+ str(para.StorageType))
    return returnValue

def SetBuiltInParameterValue(
    doc, 
    element, 
    builtInParameterDef, 
    valueAsString, # type: str
    parameterValueSetter = rParaSet.set_parameter_value
    ):
    '''
    !DEPRECATED! Refer to module RevitElementParameterSetUtils.

    Sets the built-in parameter value by trying to convert the past in string representing the value into the appropriate value type.

    Changing a parameter value requires this action to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: Element to which the built-in parameter belongs.
    :type element: Autodesk.Revit.DB.Element
    :param builtInParameterDef: The parameters built-in definition of which the value is to be returned.
    :type builtInParameterDef: Autodesk.Revit.DB.Definition
    :param valueAsString: The new parameter value.
    :type valueAsString: str
    :param parameterValueSetter:
        The function which takes the parameter as an argument and changes it's value to.
        The function needs to accept these args: parameter, new parameter value as string, document
    :type parameterValueSetter: function 
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
    
    returnValue = res.Result()
    returnValue.UpdateSep(False, 'Parameter not found')
    paras = element.GetOrderedParameters()
    for para in paras:
        if(para.Definition.BuiltInParameter == builtInParameterDef):
            returnValue = parameterValueSetter(para, valueAsString, doc)
            break
    return returnValue

def GetElementMark(e):
    '''
    Returns the mark value of an element.

    :param e: The element.
    :type e: Autodesk.Revit.DB.Element

    :return:
        The element mark value.  
        If an exception occurred, the message will be 'Failed with exception: ' + the exception string.
    :rtype: str
    '''

    mark = ''
    try:
        paraMark = e.get_Parameter(rdb.BuiltInParameter.ALL_MODEL_MARK)
        mark = '' if paraMark == None else paraMark.AsString()
    except Exception as e:
        mark = 'Failed with exception: ' + str(e)
    return mark

#----------------------------- revisions ----------------

def GetSheetRevByName(
    doc, 
    sheetName # type: str
    ):

    '''
    Returns the revision of a sheet identified by its name. Default value is '-'.

    Since multiple sheets can have the same name it will return the revision of the first sheet matching the name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document 
    :param sheetName: The name of the sheet of which the revision is to be returned.
    :type sheetName: str
    :raise: Any exception will need to be managed by the function caller.

    :return:
        The sheets current revision value.  
        If no matching sheet is found, '-' is returned.
    :rtype: str
    '''

    revValue = '-'
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet).Where(lambda e: e.Name == sheetName)
    results = collector.ToList()
    if (len(results)>0):
        sheet = results[0]
        revP = sheet.get_Parameter(rdb.BuiltInParameter.SHEET_CURRENT_REVISION)
        revValue = util.PadSingleDigitNumericString(revP.AsString())
    return revValue

def GetSheetRevByNumber(
    doc, 
    sheetNumber # type: str
    ):

    '''
    Returns the revision of a sheet identified by its number. Default value is '-'.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheetNumber: The number of the sheet of which the revision is to be returned.
    :type sheetNumber: str
    :raise: Any exception will need to be managed by the function caller.

    :return:
        The sheets current revision value.  
        If no matching sheet is found, '-' is returned.
    :rtype: str
    '''

    revValue = '-'
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet).Where(lambda e: e.SheetNumber == sheetNumber)
    results = collector.ToList()
    if (len(results)>0):
        sheet = results[0]
        revP = sheet.get_Parameter(rdb.BuiltInParameter.SHEET_CURRENT_REVISION)
        revValue = revP.AsString()
    return revValue

#----------------------------------------Legend Components -----------------------------------------------

def GetLegendComponentsInModel(doc, typeIds):
    ''' 
    Returns all symbol (type) ids of families which have been placed as legend components and have match in list past in.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeIds: List of typeIds to check against.
    :type typeIds: list str
    :raise: Any exception will need to be managed by the function caller.

    :return: Values are representing symbol (type) ids of legend components in models filtered by ids past in.
    :rtype: list of str
    '''

    ids = []
    # get all legend components in the model to check against list past in
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_LegendComponents)
    for c in col:
        id = rParaGet.get_built_in_parameter_value (c, rdb.BuiltInParameter.LEGEND_COMPONENT, rParaGet.get_parameter_value)
        if (id in typeIds and id not in ids):
            ids.append(id)
            break
    return ids

#----------------------------------------types - Autodesk.Revit.DB ElementType -----------------------------------------------

def GetSimilarTypeFamiliesByType(doc, typeGetter):
    '''
    Returns a list of unique types its similar family (symbol) types.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param function typeGetter:
        The function which takes the document as an argument and returns a list of family symbols (types).
    :raise: Any exception will need to be managed by the function caller.
    
    :return: list of Autodesk.Revit.DB.Symbol and Autodesk.Revit.DB.ElementId:
    :rtype: List [[Autodesk.Revit.DB.ElementType, Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]
    '''

    simTypes=[]
    types = typeGetter(doc)
    for t in types:
        tData = [t]
        sims = t.GetSimilarTypes()
        simData = []
        for sim in sims:
            simData.append(sim)
        # simData.sort() # not sure a sort is actually doing anything
        tData.append(simData)
        if(CheckUniqueTypeData(simTypes, tData)):
            simTypes.append(tData)
    return simTypes

def CheckUniqueTypeData(existingTypes, newTypeData):
    '''
    Compares two lists of types and their similar types (ids).

    Assumes that second list past in has only one occurrence of type and its similar types
    Compares types by name and if match their similar types.

    :param existingTypes: Source list
    :type existingTypes: List of List in format [[Autodesk.Revit.DB.ElementType , Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]
    :param newTypeData: Comparison list
    :type newTypeData: List in format [Autodesk.Revit.DB.ElementType, Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...] 
    
    :return: 
        True, if new type is not in list existing Types passed in or
        if ids of similar family types do not match any similar types already in list
    :rtype: bool
    '''

    result = True
    for s in existingTypes:
        # check for matching family name
        if (s[0].FamilyName == newTypeData[0].FamilyName):
            # check if match has the same amount of similar family types
            # if not it is unique
            if (len(s[1]) == len(newTypeData[1])):
                # assume IDs do match
                matchIDs = True
                for i in range(len(s[1])):
                    if(s[1][i] != newTypeData[1][i]):
                          # id's dont match, this is unique
                          matchIDs = False
                          break
                if(matchIDs):
                    # data is not unique
                    result = False
                    break
    return result

def GetUnusedTypeIdsInModel(doc, typeGetter, instanceGetter):
    '''
    Returns ID of unused family types in the model.

    Used in purge code since it leaves at least one type behind (built in families require at least one type in the model)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeGetter: Function accepting current document as argument and returning a collector of types in model
    :type typeGetter: func
    :param instanceGetter: Function accepting current document as argument and returning a list of instances in model
    :type instanceGetter: func
    
    :return: List of type ids which can be purged from the model.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''
    
    # get all  types available and associated family types
    familyTypesAvailable = GetSimilarTypeFamiliesByType(doc, typeGetter)
    # get used type ids
    usedFamilyTypeIds = instanceGetter(doc)
    # flag indicating that at least one type was removed from list because it is in use
    # this flag used when checking how many items are left...
    removedAtLeastOne = []
    # set index to 0, type names might not be unique!!
    counter = 0
    # loop over available types and check which one is used
    for t in familyTypesAvailable:
        # remove all used family type Id's from the available list...
        # whatever is left can be deleted if not last available item in list for type
        # there should always be just one match
        for usedFamilyTypeId in usedFamilyTypeIds:
            # get the index of match
            index = util.IndexOf(t[1],usedFamilyTypeId)
            # remove used item from list
            if (index > -1):
                t[1].pop(index)
                if(t not in removedAtLeastOne):
                    removedAtLeastOne.append(counter)
        counter = counter + 1
    # filter these by family types where is only one left
    # make sure to leave at least one family type behind, since the last type cannot be deleted
    filteredUnusedTypeIds = []
    # reset index
    counter = 0
    for t in familyTypesAvailable:
        if (counter in removedAtLeastOne):
            # at least one item was already removed from list...so all left over ones can be purged
            for id in t[1]:
                # get the element
                tFam = doc.GetElement(id)
                if (tFam.CanBeDeleted):
                    filteredUnusedTypeIds.append(id)
        else:
            # need to keep at least one item
            if(len(t[1]) > 1):
                #maxLength = len(t[1])
                # make sure to leave the first one behind to match Revit purge behavior
                for x in range(1, len(t[1])):
                    id = t[1][x]
                    # get the element
                    tFam = doc.GetElement(id)
                    # check whether this can be deleted...
                    if (tFam.CanBeDeleted):
                        filteredUnusedTypeIds.append(id)
        counter = counter + 1 
    return filteredUnusedTypeIds

#----------------------------------------instances of types - Autodesk.Revit.DB ElementType -----------------------------------------------

def GetNotPlacedTypes(doc, getTypes, getInstances):
    '''
    
    returns a list of unused types foo by comparing type Ids of placed instances with types past in.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param getTypes: Types getter function. Needs to accept doc as argument and return a collector of type foo
    :type getTypes: func (doc)
    :param getInstances: Instances getter function. Needs to accept doc as argument and return a collector of instances foo
    :type getInstances: func(doc)
    
    :return: returns a list of unused types
    :rtype: list of type foo
    '''

    availTypes = getTypes(doc)
    placedInstances = getInstances(doc)
    notPlaced = []
    alreadyChecked = []
    # loop over all types and check for matching instances
    for at in availTypes:
        match = False
        for pi in placedInstances:
            # check if we had this type checked already, if so ignore and move to next
            if(pi.GetTypeId() not in alreadyChecked):
                #  check for type id match
                if(pi.GetTypeId() == at.Id):
                    # add to already checked and verified as match list
                    alreadyChecked.append(pi.GetTypeId())
                    match = True
                    break
        if(match == False):
            notPlaced.append(at)
    return notPlaced

# --------------------------------------------- check whether groups contain certain element types - Autodesk.Revit.DB ElementType  ------------------

def CheckGroupForTypeIds(doc, groupType, typeIds):
    '''
    
    Filters passed in list of type ids by type ids found in group and returns list of unmatched Id's
    
    This only returns valid data if at least one instance of the group is placed in the model, otherwise GetMemberIds() returns empty!!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param groupTypes: Group to be checked whether they contains elements of types past in.
    :type groupTypes: Autodesk.Revit.DB.GroupType
    :param typeIds: List of type ids to confirm whether they are in use a group
    :type typeIds: list of Autodesk.Revit.Db.ElementId
    
    :return: Returns all type ids not matched
    :rtype: list of Autodesk.Revit.Db.ElementId
    '''

    unusedTypeIds = []
    usedTypeIds = []
    # get the first group from the group type and get its members
    for g in groupType.Groups:
        # get ids of group elements:
        memberIds = g.GetMemberIds()
        # built list of used type ids
        for memberId in memberIds:
            member = doc.GetElement(memberId)
            usedTypeId = member.GetTypeId()
            if (usedTypeId not in usedTypeIds):
                usedTypeIds.append(usedTypeId)
    for checkId in typeIds:
        if(checkId not in usedTypeIds):
            unusedTypeIds.append(checkId)
    return unusedTypeIds

def CheckGroupsForMatchingTypeIds(doc, groupTypes, typeIds):
    '''
    Checks all elements in groups past in whether group includes element of which type Id is matching any type ids past in
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param groupTypes: Groups to be checked whether they contains elements of types past in.
    :type groupTypes: list of Autodesk.Revit.DB.GroupType
    :param typeIds: List of type ids to confirm whether they are in use a group
    :type typeIds: list of Autodesk.Revit.Db.ElementId
    
    :return: Returns all type ids not matched
    :rtype: list of Autodesk.Revit.Db.ElementId
    '''

    for groupType in groupTypes:
        typeIds = CheckGroupForTypeIds(doc, groupType, typeIds)
        # check if all type ids where matched up
        if (len(typeIds) == 0):
            break
    return typeIds

def GetUnusedTypeIdsFromDetailGroups(doc, typeIds):
    '''
    Checks elements in nested detail groups and detail groups whether their type ElementId is in the list past in.
    
    This only returns valid data if at least one instance of the group is placed in the model!!!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeIds: List of type ids to confirm whether they are in use a group
    :type typeIds: list of Autodesk.Revit.Db.ElementId
    
    :return: Returns all type Ids from list past in not found in group definitions
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    unusedTypeIds = []
    nestedDetailGroups = rGroup.GetNestedDetailGroups(doc)
    detailGroups = rGroup.GetDetailGroups(doc)
    unusedTypeIds = CheckGroupsForMatchingTypeIds(doc, nestedDetailGroups, typeIds)
    unusedTypeIds = CheckGroupsForMatchingTypeIds(doc, detailGroups, typeIds)
    return unusedTypeIds

#----------------------------------------elements-----------------------------------------------

def BuildCategoryDictionary(doc, elementIds):
    '''
    Builds a dictionary from elementId s past in.

    Dictionary key is the element category and values are all the elements of that category.
    If no category can be found the key 'invalid category' will be used.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param elementIds: List of element id of which to build the dictionary from.
    :type elementIds: list of AutoDesk.Revit.DB.ElementId
    
    :return: Dictionary key is the element category and values are all the elements of that category.
    :rtype: dictionary, key is string, value is list of AutoDesk.Revit.DB.Element
    '''

    dic = {}
    for elId in elementIds:
        try:
            el = doc.GetElement(elId)
            try:
                if(dic.has_key(el.Category.Name)):
                    dic[el.Category.Name].append(el)
                else:
                    dic[el.Category.Name] = [el]
            except:
                if(dic.has_key('invalid category')):
                    dic['invalid category'].append(el)
                else:
                    dic['invalid category'] = [el]
        except:
            if(dic.has_key('invalid element')):
                dic['invalid element'].append(el)
            else:
                dic['invalid element'] = [el]
    return dic

def CheckWhetherDependentElementsAreMultipleOrphanedLegendComponents (doc, elementIds):
    '''
    Check if element are orphaned legend components

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param elementIds: List of elements to check
    :type elementIds: list of AutoDesk.Revit.DB.ElementId
    
    :return: True if all but one element are orphaned legend components.
    :rtype: bool
    '''

    flag = True
    categoryName = 'Legend Components'
    # build dependent type dictionary
    # check whether dictionary is made of
    #   1 entry for type
    #   multiple entries for legend components
    #   no other entry
    # if so: check whether any of the legend component entry has a valid view id
    #   if none has return true, otherwise return false
    dic = BuildCategoryDictionary(doc,  elementIds)
    # check if dictionary has legend component key first up
    if(dic.has_key(categoryName) == True):
        # if so check number of keys and length of elements per key
        if(len(dic.keys()) == 2  and len(dic[categoryName]) == len(elementIds)-1):
            # this should be the only code path returning true...
            for value in dic[categoryName]:
                if value.OwnerViewId != rdb.ElementId.InvalidElementId:
                    flag = False
                    break
        else:
            flag = False
    else:
        flag = False
    return flag
           
def FilterOutWarnings(doc, dependentElements):
    '''
    Attempts to filter out any warnings from ids supplied by checking the workset name
    of each element for 'Reviewable Warnings'

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param dependentElements: List of elements to check.
    :type dependentElements: list of AutoDesk.Revit.DB.Element
    
    :return: A list of elements id where the workset name of the element is not 'Reviewable Warnings'
    :rtype: list of AutoDesk.Revit.DB.Element
    '''
    
    ids = []
    for id in dependentElements:
        el = doc.GetElement(id)
        pValue = rParaGet.get_built_in_parameter_value(el, rdb.BuiltInParameter.ELEM_PARTITION_PARAM, rParaGet.get_parameter_value)
        if(pValue != 'Reviewable Warnings'):
            ids.append(id)
    return ids

def HasDependentElements(
    doc,
    el, 
    filter = None, 
    threshold = 2 # type: int
    ):
    '''
    Checks whether an element has dependent elements.

    The dependent elements are collected via Element.GetDependentElements(filter).
    This also includes a check as to whether elements returned as dependent are orphaned. (for lack of better words)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param el: The element to be checked for dependent elements.
    :type el: AutoDesk.Revit.DB.Element
    :param filter: What type of dependent elements to filter, defaults to None which will return all dependent elements
    :type filter: Autodesk.Revit.DB.ElementFilter , optional
    :param threshold: The number of how many dependant elements an element can have but still be considered not used, defaults to 2
    :type threshold: int, optional
    
    :return: returns 0 for no dependent elements, 1, for other elements depend on it, -1 if an exception occurred
    :rtype: int
    '''

    value = 0 # 0: no dependent Elements, 1: has dependent elements, -1 an exception occurred
    try:
        dependentElements = el.GetDependentElements(filter)
        # remove any warnings from dependent elements
        dependentElements = FilterOutWarnings(doc, dependentElements)
        # check if dependent elements pass threshold value
        if(len(dependentElements)) > threshold :
            # there appear to be situations where dependent elements are multiple (orphaned?) legend components only
            # or warnings belonging to a type (same type mark ...)
            # these are legend components with an invalid OwnerViewId, check whether this is the case...
            if (CheckWhetherDependentElementsAreMultipleOrphanedLegendComponents(doc, dependentElements) == False):
                value = 1
    except Exception as e:
        value = -1
    return value

def GetUsedUnusedTypeIds(
    doc, 
    typeIdGetter, 
    useType = 0, # type: int
    threshold = 2 # type: int
    ):
    '''
    Gets either the used or not used type Ids provided by typeIdGetter.

    Whether the used or unused type ids depends on the useType value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeIdGetter: Function returning type ids
    :type typeIdGetter: list of Autodesk.Revit.DB.ElementId
    :param useType: 0, no dependent elements; 1: has dependent elements, defaults to 0
    :type useType: int, optional
    :param threshold: The number of how many dependant elements an element can have but still be considered not used, defaults to 2
    :type threshold: int, optional
    :return: A list of either all used or unused element ids. Depends on useType. 
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get all types elements available
    allTypeIds = typeIdGetter(doc)
    ids = []
    for typeId in allTypeIds:
        type = doc.GetElement(typeId)
        hasDependents = HasDependentElements(doc, type, None, threshold)
        if(hasDependents == useType):
            ids.append(typeId)
    return ids

def DeleteByElementIds(
    doc, 
    ids, 
    transactionName, # type: str
    elementName # type: str
    ):
    '''
    Deleting elements in list all at once.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List containing ids of all elements to be deleted.
    :type ids: list of Autodesk.Revit.DB.ElementId
    :param transactionName: The transaction name used for the deletion.
    :type transactionName: str
    :param elementName: The element name added to deletion status message.
    :type elementName: str
    
    :return: 
        Result class instance.
        
        - .result = True if successfully deleted all elements. Otherwise False.
        - .message will contain deletion status

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    def action():
        actionReturnValue = res.Result()
        try:
            doc.Delete(ids.ToList[rdb.ElementId]())
            actionReturnValue.message = 'Deleted ' + str(len(ids)) + ' ' + elementName
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Failed to delete ' + elementName + ' with exception: ' + str(e))
        return actionReturnValue
    transaction = rdb.Transaction(doc,transactionName)
    returnValue = rTran.in_transaction(transaction, action)
    return returnValue

def DeleteByElementIdsOneByOne(
    doc, 
    ids, 
    transactionName, # type: str
    elementName # type: str
    ):
    '''
    Deleting elements in list one at the time.

    Each element gets deleted in its own transaction. If the deletion fails the transaction is rolled back.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List containing ids of all elements to be deleted.
    :type ids: list of Autodesk.Revit.DB.ElementId
    :param transactionName: The transaction name used for the deletion.
    :type transactionName: str
    :param elementName: The name of the element (?) Not used!!
    :type elementName: str

    :return: 
        Result class instance.
        
        - .result = True if successfully deleted all elements. Otherwise False.
        - .message will contain each id and its deletion status

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    for id in ids:
        def action():
            actionReturnValue = res.Result()
            element = doc.GetElement(id)
            n = rdb.Element.Name.GetValue(element)
            try:
                doc.Delete(id)
                actionReturnValue.message = 'Deleted [' + str(id) + '] ' + n
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to delete ' + n + '[' +str(id) + '] with exception: ' + str(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,transactionName)
        returnValue.Update( rTran.in_transaction(transaction, action))
    return returnValue

def GetIdsFromElementCollector(col):
    '''
    This will return a list of all element ids in collector.

    Any element in collector which is invalid will be ignored.
    
    :param col: A filtered element collector.
    :type col: Autodesk.Revit.DB.FilteredElementCollector 
    
    :return: list of all element ids of valid elements in collector.
    :rtype: List of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for c in col:
        try:   
            ids.append(c.Id)
        except Exception as e:
            pass
    return ids

def IsElementOfBuiltInCategory(doc, elId, builtinCategories):
    '''
    Checks whether an element is of the built in categories past in.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param elId: The id of the element to be tested.
    :type elId: Autodesk.Revit.DB.ElementId
    :param builtinCategories: The builtin category the element does needs to match.
    :type builtinCategories: Autodesk.Revit.DB.Definition
    
    :return: True if element's builtin category does equals the test category, otherwise False.
    :rtype: bool
    '''

    match = False
    el = doc.GetElement(elId)
    enumCategoryId = el.Category.Id.IntegerValue.ToString()
    for bic in builtinCategories:
        if (enumCategoryId == bic.value__.ToString()):
            match = True
            break
    return match
         
def IsElementNotOfBuiltInCategory(doc, elId, builtinCategories):
    '''
    Checks whether an element is not of the built in categories past in.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param elId: The id of the element to be tested.
    :type elId: Autodesk.Revit.DB.ElementId
    :param builtinCategories: The builtin category the element does not needs to match.
    :type builtinCategories: Autodesk.Revit.DB.Definition
    
    :return: True if element's builtin category does not equals the test category, otherwise False.
    :rtype: bool
    '''

    match = True
    el = doc.GetElement(elId)
    enumCategoryId = el.Category.Id.IntegerValue.ToString()
    for bic in builtinCategories:
        if (enumCategoryId == bic.value__.ToString()):
            match = False
            break
    return match

def IsFamilyNameFromInstance(
    doc, 
    familyName, # type: str
    elementId
    ):

    '''
    Checks whether the family name of a given family instance matches filter value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param familyName: The string the name of the family needs to match.
    :type familyName: str
    :param elementId: The id of the element to be tested.
    :type elementId: Autodesk.Revit.DB.ElementId
    
    :return: True if family equals the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(rdb.Element.Name.GetValue(el.Symbol.Family) != familyName):
            flag = False
    except Exception:
        flag = False
    return flag

def IsFamilyNameFromInstanceContains(
    doc, 
    containsValue, # type: str
    elementId
    ):
    # type: (...) -> bool
    '''
    Checks whether the family name of a given family instance contains filter value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param containsValue: The string the name of the family instance is to be tested for.
    :type containsValue: str
    :param elementId: The id of the element to be tested.
    :type elementId:  Autodesk.Revit.DB.ElementId
    
    :return: True if family name does contain the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(containsValue not in rdb.Element.Name.GetValue(el.Symbol.Family)):
            flag = False
    except Exception:
        flag = False
    return flag

def IsFamilyNameFromInstanceDoesNotContains(
    doc, 
    containsValue, # type: str
    elementId
    ):
    # type: (...) -> bool
    '''
    Checks whether the family name of a given family instance does not contains filter value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param containsValue: The string the name of the family instance is to be tested for.
    :type containsValue: str
    :param elementId: The id of the element to be tested.
    :type elementId: Autodesk.Revit.DB.ElementId
    
    :return: True if family name does not contain the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(containsValue in rdb.Element.Name.GetValue(el.Symbol.Family)):
            flag = False
    except Exception:
        flag = False
    return flag

def IsSymbolNameFromInstanceContains(
    doc, 
    containsValue, # type: str
    elementId
    ):
    # type: (...) -> bool
    '''
    Checks whether the family symbol name of a given family instance contains filter value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param containsValue: The string the name of the family instance is to be tested for.
    :type containsValue: str
    :param elementId: The id of the element to be tested.
    :type elementId: Autodesk.Revit.DB.ElementId
    
    :return: : True if family name does contain the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(containsValue not in rdb.Element.Name.GetValue(el.Symbol)):
            flag = False
    except Exception:
        flag = False
    return flag

def IsSymbolNameFromInstanceDoesNotContains(
    doc, 
    containsValue, # type: str
    elementId
    ):
    # type: (...) -> bool

    '''
    Checks whether the family symbol name of a given family instance does not contains filter value.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param containsValue: The string the name of the family is to be tested for.
    :type containsValue: string
    :param elementId: The id of the element to be tested.
    :type elementId: Autodesk.Revit.DB.ElementId
    
    :return: True if symbol name does not contain the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(containsValue in rdb.Element.Name.GetValue(el.Symbol)):
            flag = False
    except Exception:
        flag = False
    return flag

#-------------------------------------------------------file IO --------------------------------------

def SyncFile (
    doc, 
    compactCentralFile = False # type: bool
    ):
    # type: (...) -> res.Result
    '''
    Synchronizes a Revit central file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param compactCentralFile: option to compact the central file, defaults to False
    :type compactCentralFile: bool, optional
    
    :return: 
        Result class instance.
        
        - .result = True if successfully synced file. Otherwise False.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # set up sync settings
    ro = rdb.RelinquishOptions(True)
    transActOptions = rdb.TransactWithCentralOptions()
    sync = rdb.SynchronizeWithCentralOptions()
    sync.Comment = 'Synchronized by Revit Batch Processor'
    sync.Compact = compactCentralFile
    sync.SetRelinquishOptions(ro)
    # Synch it
    try:
        # save local first ( this seems to prevent intermittent crash on sync(?))
        doc.Save()
        doc.SynchronizeWithCentral(transActOptions, sync)
        # relinquish all
        rdb.WorksharingUtils.RelinquishOwnership(doc, ro, transActOptions)
        returnValue.message = 'Successfully synched file.'
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnValue

def SaveAsWorksharedFile(
    doc, 
    fullFileName  # type: str
    ):
    # type: (...) -> res.Result
    '''
    Saves a Revit project file as a workshared file.

    Save as options are:
    Workset configuration is : Ask users on open to specify.
    Any existing file will be overwritten.
    Number of backups is 5
    File will bew compacted on save.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param fullFileName: The fully qualified file path of where to save the file.
    :type fullFileName: string
    
    :return: 
        Result class instance.
            
        - .result = True if successfully saved file, otherwise False.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        workSharingSaveAsOption = rdb.WorksharingSaveAsOptions()
        workSharingSaveAsOption.OpenWorksetsDefault = rdb.SimpleWorksetConfiguration.AskUserToSpecify
        workSharingSaveAsOption.SaveAsCentral = True
        saveOption = rdb.SaveAsOptions()
        saveOption.OverwriteExistingFile = True
        saveOption.SetWorksharingOptions(workSharingSaveAsOption)
        saveOption.MaximumBackups = 5
        saveOption.Compact = True
        doc.SaveAs(fullFileName, saveOption)
        returnValue.message = 'Successfully saved file: ' + str(fullFileName)
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnValue

def SaveAsFamily(
    doc, 
    targetFolderPath, # type: str
    currentFullFileName, # type: str
    nameData, # type: List[List[str]]
    fileExtension = '.rfa', # type: str
    compactFile = False # type: bool
    ):
    # type: (...) -> res.Result
    '''
    Saves a family file under new name in given location.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param targetFolderPath: The directory path of where to save the file.
    :type targetFolderPath: str
    :param currentFullFileName: The current (old) name of the file.
    :type currentFullFileName: str
    :param nameData:  Old name and new name are Revit file names without file extension. Used to rename the family on save from old name to new name.
    :type nameData: List of string arrays in format[[oldname, newName]]
    :param fileExtension: The file extension used for the new file, defaults to '.rfa'
    :type fileExtension: str, optional
    :param compactFile: Flag whether family is to be compacted on save, defaults to False
    :type compactFile: bool, optional
    
    :return: 
        Result class instance.
            
            - .result = True if successfully saved file, otherwise False.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    revitFileName = util.GetFileNameWithoutExt(currentFullFileName)
    newFileName= ''
    match = False
    # find new file name in list past in
    for oldName, newName in nameData:
        if (revitFileName.startswith(oldName)):
            match = True
            returnValue.message = ('Found file name match for: ' + revitFileName + ' new name: ' + newName)
            # save file under new name
            newFileName = targetFolderPath + '\\'+ newName + fileExtension
            break
    if(match == False):
        # save under same file name
        newFileName = targetFolderPath + '\\'+ revitFileName + fileExtension
        returnValue.message = 'Found no file name match for: ' + currentFullFileName
    try:
        # setup save as option
        so = rdb.SaveAsOptions()
        so.OverwriteExistingFile = True
        so.MaximumBackups = 5
        so.SetWorksharingOptions(None)
        so.Compact = compactFile
        doc.SaveAs(newFileName, so)
        returnValue.UpdateSep(True, 'Saved file: ' + newFileName)
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to save revit file to new location!' + ' exception: ' + str(e))
    return returnValue

def SaveAs(
    doc, 
    targetFolderPath, # type: str
    currentFullFileName, # type: str
    nameData, # type: List[List[str]]
    fileExtension = '.rvt' # type: str
    ):
    # type: (...) -> res.Result
    '''
    Saves a project file under new name in given location.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param targetFolderPath: The directory path of where to save the file.
    :type targetFolderPath: str
    :param currentFullFileName: The current (old) name of the file.
    :type currentFullFileName: str
    :param nameData: Old name and new name are revit file names without file extension. Used to rename the model on save from old name to new name.
    :type nameData: List of string arrays in format[[oldname, newName]]
    :param fileExtension: The file extension used for the new file, defaults to '.rvt'
    :type fileExtension: str, optional
    
    :return: 
        Result class instance.
        
        - .result = True if successfully saved file, otherwise False.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # added str() around this expression to satisfy sphinx auto code documentation
    # it will throw an exception when concatenating the string in the return statement
    revitFileName = str(util.GetFileNameWithoutExt(currentFullFileName))
    newFileName= ''
    match = False
    for oldName, newName in nameData:
        if (revitFileName.startswith(oldName)):
            match = True
            returnValue.message = ('Found file name match for: ' + revitFileName + ' new name: ' + newName)
            # save file under new name
            newFileName = targetFolderPath + '\\'+ newName + fileExtension
            break
    if(match == False):
        # save under same file name
        newFileName = targetFolderPath + '\\'+ revitFileName + fileExtension
        # added str.format around this expression to satisfy sphinx auto code documentation
        returnValue.message = 'Found no file name match for: {}'.format(currentFullFileName)
    try:
        returnValue.status = SaveAsWorksharedFile(doc, newFileName).status
        returnValue.AppendMessage('Saved file: ' + newFileName)
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to save revit file to new location!' + ' exception: ' + str(e))
    return returnValue

def SaveFile(
    doc, 
    compactFile = False # type: bool
    ):
    # type: (...) -> res.Result
    '''
    Saves a non workshared Revit file. To be used for families and non workshared revit files only.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param compactFile: True file will be compacted on save, defaults to False
    :type compactFile: bool, optional
    :return: 
            Result class instance.
            
            - .result = True if file was saved successfully. Otherwise False.
            - .message = 'Saved revit file!'
        
            On exception:
            
            - result.status (bool) will be False.
            - result.message will contain exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        so = rdb.SaveOptions()
        so.Compact = compactFile
        doc.Save(so)
        returnValue.UpdateSep(True, 'Saved revit file!')
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to save revit file!' + ' exception: ' + str(e))
    return returnValue
  
# enables work sharing
def EnableWorksharing(
    doc, #
    worksetNameGridLevel = 'Shared Levels and Grids', # type: str
    worksetName = 'Workset1' # type: str
    ):
    # type: (...) -> res.Result
    '''
    Enables worksharing in a non workshared revit project file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param worksetNameGridLevel: _description_, defaults to 'Shared Levels and Grids'
    :type worksetNameGridLevel: str, optional
    
    :return: 
            Result class instance.
            
            - .result = True if worksharing was enabled successfully. Otherwise False.
            - .message = 'Successfully enabled worksharing.'
        
            On exception:
            
            - result.status (bool) will be False.
            - result.message will contain exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        doc.EnableWorksharing('Shared Levels and Grids','Workset1')
        returnValue.message = 'Successfully enabled worksharing.'
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnValue