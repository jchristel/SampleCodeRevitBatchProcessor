"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the view property data filter.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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


def filter_data_by_properties(data, headers, properties, default_headers):
    """
    Filters view data by supplied property names.
    Data gets filtered twice: property needs to exist in headers list as well as in properties list.

    :param data: List of sheet properties to be kept.
    :type data: list of list of str
    :param headers: Filter: list of headers representing property names.
    :type headers: list of str
    :param properties: list of optional properties to be extracted from data
    :type properties: list of str
    :param default_headers: list of view properties always extracted from data
    :type default_headers: list of str
    :return: List of sheet properties matching filters.
    :rtype: list of list of str
    """

    # filter data out
    new_data = []
    for d in data:
        data_row = {}
        for default_head in default_headers:
            if default_head in d:
                data_row[default_head] = d[default_head]
            else:
                data_row[default_head] = "default property does not exist on element"
        for prop in properties:
            if prop in d:
                data_row[prop] = d[prop]
            else:
                data_row[prop] = "property does not exist on element"
        new_data.append(data_row)
    return new_data
