'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit API utility functions to get parameter values.
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

import System
import clr
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

# import everything from Autodesk Revit DataBase namespace (Revit API)
import Autodesk.Revit.DB as rdb

# utilities
from duHast.Utilities import Utility as util

# type checker
#from typing import List, Callable


#----------------------------------------parameters-----------------------------------------------

def check_parameter_value(
    para, 
    para_condition, # type: Callable[[str,str],bool]
    condition_value):
    # type: (...) -> bool
    '''
    Checks a parameter value based on passed in condition function.

    This extracts the value of the past in parameter and compares it against a past in value using 
    the also past in compare function. 
    Note that values will be past into compare function as ASCII encoded.

    :param para: Parameter of which the value is to be checked.
    :type para: Autodesk.Revit.DB.Parameter 
    :param para_condition:
        Function taking 2 arguments:
        First argument is the value to be checked against
        Second argument is the actual parameter value
        Needs to return a bool!
        Both arguments will be ASCII encoded at passing in.
    :type para_condition: function
    :param condition_value: The value to be checked for
    :type condition_value: var 
    :raise: Any exception will need to be managed by the function caller.

    :return:
        True if condition value is evaluated to be True by past in function paraCondition.
        Will return False if compare function returns None or a False.
    :rtype: bool
    
    '''
    # set default return value
    is_match = False
    parameter_value = get_parameter_value(para)
    # evaluate parameter value with past in value using past in function
    compare_outcome = para_condition(util.EncodeAscii(condition_value), util.EncodeAscii(parameter_value))
    # check the return value for a bool (True) only. Everything else will return False
    if (compare_outcome == True):
        is_match = True
    return is_match

#----------------------------------------parameters value getter over loads-----------------------------------------------

def getter_none(para):
    '''
    Used for parameters where the storage type is None
    
    :param para: _description_
    :type para: _type_
    '''

    return 'Invalid storage type: (NONE)'

def getter_double_or_int_as_string(para):
    '''
    Returns a parameter value of type double or integer as string.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: String representation of double or integer value. If value is empty it will return None
    :rtype: str or None
    '''

    parameter_value = None
    if(para.AsValueString() != None and para.AsValueString() != ''):
        parameter_value = para.AsValueString()
    return parameter_value

def getter_double_as_double(para):
    '''
    Returns a parameter value of type double as a double.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Double value. If value is empty it will return None
    :rtype: Double or None
    '''

    parameter_value = None
    if(para.AsValueString() != None and para.AsValueString() != ''):
        parameter_value = para.AsDouble()
    return parameter_value

def getter_double_as_double_converted_to_millimeter(para):
    '''
    Returns a parameter value of type double as a double converted to mm (if required).
    Revit uses feet internally for any length value!

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Double value. If value is empty it will return None
    :rtype: Double or None
    '''

    parameter_value = None
    if(para.AsValueString() != None and para.AsValueString() != ''):
        if(para.Definition.ParameterType == rdb.ParameterType.Length):
            parameter_value = para.AsDouble() * 304.8
        else:
            parameter_value = para.AsDouble()
    return parameter_value

def getter_int_as_int(para):
    '''
    Returns a parameter value of type integer as a integer.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Integer value. If value is empty it will return None
    :rtype: Integer or None
    '''

    parameter_value = None
    if(para.AsValueString() != None and para.AsValueString() != ''):
        parameter_value = para.AsInteger()
    return parameter_value

def getter_string_as_UTF8_string(para):
    '''
    Returns a parameter value of type string as a utf-8 formatted string.
    
    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: String value. If value is empty it will return None
    :rtype: String or None
    '''

    parameter_value = None
    if(para.StorageType == rdb.StorageType.String):
        if(para.AsString() != None and para.AsString() != ''):
            parameter_value = para.AsString().encode('utf-8')
    return parameter_value

def getter_string_as_string(para):
    '''
    Returns a parameter value of type string as a string.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: String value. If value is empty it will return None
    :rtype: String or None
    '''

    parameter_value = None
    if(para.StorageType == rdb.StorageType.String):
        if(para.AsString() != None and para.AsString() != ''):
            parameter_value = para.AsString()
    return parameter_value

def getter_element_id_as_string(para):
    '''
    Returns a parameter value of type element id as a string.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: String value. If value is empty it will return None
    :rtype: String or None
    '''

    parameter_value = None
    if(para.StorageType == rdb.StorageType.ElementId):
        if(para.AsElementId() != None):
            parameter_value = str(para.AsElementId())
    return parameter_value     

def getter_element_id_as_element_id(para):
    '''
    Returns a parameter value of type element id as a element id.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Element id value. If value is empty it will return None
    :rtype: Element id or None
    '''

    parameter_value = None
    if(para.StorageType == rdb.StorageType.ElementId):
        if(para.AsElementId() != None):
            parameter_value = para.AsElementId()
    return parameter_value

def getter_element_id_as_element_int(para):
    '''
    Returns a parameter value of type element id as an integer.

    :param para: The parameter.
    :type para: Autodesk.Revit.DB.Parameter

    :return: Integer value. If value is empty it will return None
    :rtype: Integer or None
    '''

    parameter_value = None
    if(para.StorageType == rdb.StorageType.ElementId):
        if(para.AsElementId() != None):
            parameter_value = para.AsElementId().IntegerValue
    return parameter_value 

#----------------------------------------parameters value getters -----------------------------------------------

def get_parameter_value_with_over_load (para, parameter_value_getters):
    '''
    Returns a parameter value in format depending on storage type.
    
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
    parameter_value = None
    try:
        # extract parameter value depending on its storage type
        if(para.StorageType == rdb.StorageType.Double):
            if(para.AsValueString()!= None and para.AsValueString() != ''):
                if(rdb.StorageType.Double in parameter_value_getters):
                    parameter_value = parameter_value_getters[rdb.StorageType.Double](para)
                else:
                    raise ValueError('No parameter value getter for storage type Double provided')
        elif(para.StorageType == rdb.StorageType.Integer):
            if(para.AsValueString()!= None and para.AsValueString() != ''):
                if(rdb.StorageType.Integer in parameter_value_getters):
                    parameter_value = parameter_value_getters[rdb.StorageType.Integer](para)
                else:
                    raise ValueError('No parameter value getter for storage type Integer provided')
        elif(para.StorageType == rdb.StorageType.String):
            if(para.AsString() != None and para.AsString() != ''):
                if(rdb.StorageType.String in parameter_value_getters):
                    parameter_value = parameter_value_getters[rdb.StorageType.String](para)
                else:
                    raise ValueError('No parameter value getter for storage type String provided')
        elif(para.StorageType == rdb.StorageType.ElementId):
            if(para.AsElementId() != None):
                if(rdb.StorageType.ElementId in parameter_value_getters):
                    parameter_value = parameter_value_getters[rdb.StorageType.ElementId](para)
                else:
                    raise ValueError('No parameter value getter for storage type Element Id provided')
        else:
            # this should be invalid storage type only
            parameter_value = parameter_value_getters[str(None)](para)

    except  Exception as e:
        parameter_value = 'Exception: {}'.format(e)
    return parameter_value

def get_parameter_value(
    para
    ):
    # type: (...) -> str
    '''
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
    parameter_value = 'no Value'
    try:
        value_getter = {
            rdb.StorageType.Double : getter_double_or_int_as_string,
            rdb.StorageType.Integer : getter_double_or_int_as_string,
            rdb.StorageType.String : getter_string_as_string,
            rdb.StorageType.ElementId : getter_element_id_as_string,
            str(None) : getter_none
        }

        parameter_value = get_parameter_value_with_over_load (para, value_getter)

    except  Exception as e:
        parameter_value = 'Exception: '+str(e)
    
    return parameter_value

def get_parameter_value_utf8_string(
    para
    ):
    # type: (...) -> str
    '''
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
    parameter_value = 'no Value'

    value_getter = {
            rdb.StorageType.Double : getter_double_or_int_as_string, # no specific utf encoding required
            rdb.StorageType.Integer : getter_double_or_int_as_string, # no specific utf encoding required
            rdb.StorageType.String : getter_string_as_UTF8_string,
            rdb.StorageType.ElementId : getter_element_id_as_string, # no specific utf encoding required
            str(None) : getter_none
        }
    
    parameter_value = get_parameter_value_with_over_load (para, value_getter)

    return parameter_value

def get_parameter_value_as_integer(
    para
    ):
    # type: (...) -> int
    '''
    Returns the parameter value as integer only if the storage type is integer. Otherwise -1 will be returned.

    :param para: Parameter of which the value is to be returned.
    :type para: Autodesk.Revit.DB.Parameter 
    :raise: Any exception will need to be managed by the function caller.

    :return:
        Default value is -1 if parameter value is empty or storage type is not integer.
        Otherwise the actual parameter value.
    :rtype: int
    '''

    # set return value default
    parameter_value = -1

    value_getter = {
            rdb.StorageType.Integer : getter_int_as_int
        }
    
    # extract parameter value depending on whether its storage type is integer, otherwise default value
    if(para.StorageType == rdb.StorageType.Integer):
        parameter_value = get_parameter_value_with_over_load (para, value_getter)
    return parameter_value

def get_parameter_value_as_element_id(
    para
    ):
    '''
    Returns the parameter value as element Id only if the storage type is ElementId. Otherwise InvalidElementId (-1) will be returned.

    :param para: Parameter of which the value is to be returned.
    :type para: Autodesk.Revit.DB.Parameter 
    :raise: Any exception will need to be managed by the function caller.

    :return:
        Default value is -1 if parameter value is empty or storage type is not integer.
        Otherwise the actual parameter value.
    :rtype: int
    '''

    # set return value default
    parameter_value = rdb.ElementId.InvalidElementId

    value_getter = {
            rdb.StorageType.ElementId : getter_element_id_as_element_id
        }
    
    # check if element id...otherwise return the default value
    if(para.StorageType == rdb.StorageType.ElementId):
        parameter_value = get_parameter_value_with_over_load (para, value_getter)
    return parameter_value

def get_all_parameters_and_values_wit_custom_getters(element, parameter_value_getters):
    '''
    Returns all parameters and their values as using custom value getter associated with provided element in form of a dictionary.

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

def get_built_in_parameter_value(element, builtInParameterDef, parameterValueGetter = get_parameter_value_utf8_string):
    '''
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
    parameter_value = None
    paras = element.GetOrderedParameters()
    for para in paras:
        if(para.Definition.BuiltInParameter == builtInParameterDef):
            parameter_value = parameterValueGetter(para)
            break
    return parameter_value

def get_parameter_value_by_name(
    element, 
    parameterName, # type: str
    parameterValueGetter = get_parameter_value_utf8_string
    ):
    '''
    Returns the parameter value by parameter name.

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
    parameter_value = None
    paras = element.GetOrderedParameters()
    for para in paras:
        if(para.Definition.Name == parameterName):
            parameter_value = parameterValueGetter(para)
            break
    return parameter_value