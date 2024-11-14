"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions converting collector objects to blueprint objects.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Utilities.Objects.result import Result
from duHast.Data.Objects.Collectors.data_sheet import DataSheet

def sheets_group_by_instance_property(sheet_data, property_name):
    """
    Groups sheets by a given property

    :param sheet_data: A list od DataSheet instances
    :type sheet_data: [:class: `.DataSheet`]
    :param property_name: The name of the sheet instance property by its value to group the sheets by
    :type property_name: str
    :raises ValueError: property_name needs to be of type str
    :raises ValueError: sheet_data needs to be of type list
    :raises ValueError: sheet got multiple properties of the given name
    :raises ValueError: sheet no properties of the given name
    :raises ValueError: sheet_data list contained a none DataSheet object

    :return:
            Result class instance.
                - .status True if sheets where grouped successfully, otherwise False.
                - .message will be empty.
                - . result (a list with the grouped sheets as a dictionary)

                on exception:

                - .result Will be False
                - .message will contain exception message.
                - . result (empty list)
        :rtype: :class:`.Result`
    """

    return_value = Result()
    
    matches = {}

    try:

        # do some type checking
        if(isinstance(property_name, str)==False):
            raise ValueError("property_name needs to be a string, got {} instead.".format(type(property_name)))
        if(isinstance(sheet_data, list)==False):
            raise ValueError("sheet_data needs to be a list, got {} instead.".format(type(sheet_data)))
        
        # loop over sheets and attempt to group
        for sheet in sheet_data:
            if(isinstance(sheet, DataSheet)):
                # Finding objects with the specific property value using list comprehension
                result = [prop for prop in sheet.instance_properties.properties if prop.name == property_name]
                if(len(result)==1):
                    value = result[0].value 
                    if value in matches:
                        matches[value].append(sheet)
                    else:
                        matches[value] = [sheet]
                elif(len(result)>1):
                    # this really should never happen
                    raise ValueError ("Sheet got multiple instance properties of name: {}".format(property_name))
                else:
                    raise ValueError("Sheet has no property of name: {}".format(property_name))
            else:
                raise ValueError("Data list contained non sheet element!")
    except Exception as e:
        return_value.update_sep(False, "failed to group sheets by property: {} with exception: {}".format(property_name, e))
    
    # rteturn groupings to user
    return_value.result.append(matches)
    return return_value