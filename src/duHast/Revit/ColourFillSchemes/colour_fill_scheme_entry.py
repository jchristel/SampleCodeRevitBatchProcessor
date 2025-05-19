# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from Autodesk.Revit.DB import  ColorFillSchemeEntry, ElementId, StorageType

def get_entry_value_storage_type(entry):
    """
    Get the value and storage type of a given colour fill scheme entry.

    :param entry: The colour fill scheme entry from which to retrieve the value and storage type.
    :type entry: Autodesk.Revit.DB.ColorFillSchemeEntry
    
    :return: A tuple containing the value and storage type.
    :rtype: tuple
    """

    if isinstance(entry, ColorFillSchemeEntry) == False:
        raise TypeError("entry must be of type ColorFillSchemeEntry. Got {}".format(type(entry)))

    if entry.StorageType == StorageType.None:
        return (None,0)
    elif entry.StorageType == StorageType.Integer:
        return (entry.GetIntegerValue(), 1)
    elif entry.StorageType == StorageType.Double:
        return (entry.GetDoubleValue(),2)
    elif entry.StorageType == StorageType.String:
        return(entry.GetStringValue(),3)
    elif entry.StorageType == StorageType.ElementId:
       return( entry.GetElementIdValue(),4)


def get_entry_value_as_string(entry):
    """
    Get the value of a given colour fill scheme entry as a string.
    
    :param entry: The colour fill scheme entry from which to retrieve the value.
    :type entry: Autodesk.Revit.DB.ColorFillSchemeEntry
    :return: The value as a string.
    :rtype: str
    """

    value_type = get_entry_value_storage_type(entry)

    if value_type[0] == None: 
        return "None"
    elif value_type[1] == 1:
        return str(value_type[0])
    elif value_type[1] == 2:
        return str(value_type[0])
    elif value_type[1] == 3:
        return value_type[0]
    elif value_type[1] == 4:
        return str(value_type[0].IntegerValue)


def set_entry_value (entry, value):
    """
    Set the value of a given colour fill scheme entry depending on its storage type.
    
    :param entry: The colour fill scheme entry to set the value for.
    :type entry: Autodesk.Revit.DB.ColorFillSchemeEntry
    :param value: The value to set.
    :type value: str
    :return: None
    """
    
    if isinstance(entry, ColorFillSchemeEntry) == False:
        raise TypeError("entry must be of type ColorFillSchemeEntry. Got {}".format(type(entry)))

    if entry.StorageType == StorageType.None:
        raise TypeError("entry has no storage type. Got {}".format(type(entry)))
    elif entry.StorageType == StorageType.Integer:
        if isinstance(value, int):
            entry.SetIntegerValue(value)
        else:
            entry.SetIntegerValue(int(value))
    elif entry.StorageType == StorageType.Double:
        if isinstance(value, float):
            entry.SetDoubleValue(value)
        else:
            entry.SetDoubleValue(float(value))
    elif entry.StorageType ==  StorageType.String:
        if isinstance(value, str):
            entry.SetStringValue(value)
        else:
            entry.SetStringValue(str(value))
    elif entry.StorageType == StorageType.ElementId:
        if isinstance(value, ElementId):
            entry.SetElementIdValue(value)
        else:
            entry.SetElementIdValue(ElementId(int(value)))
    
    return entry