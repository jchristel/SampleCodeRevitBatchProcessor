"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around exporting from Revit to varies file formats.
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

#
# doSomethingWithViewName method will accept view name as arg only
def build_export_file_name_from_view(view_name, view_filter_rule, file_extension):
    """
    Function modifying the past in view name and returns a file name.

    :param view_name: The view name to be used as file name.
    :type view_name: str
    :param view_filter_rule: A prefix which will be removed from the view name.
    :type view_filter_rule: str
    :param file_extension: The file extension to be used. Format is '.something'
    :type file_extension: str
    :return: A file name.
    :rtype: str
    """

    # check if file extension is not none
    if file_extension is None:
        file_extension = ".tbc"
    # check the filter rule
    if view_filter_rule is None:
        new_file_name = view_name + file_extension
    else:
        new_file_name = view_name[len(view_filter_rule) :] + file_extension
        new_file_name = new_file_name.strip()
    return new_file_name
