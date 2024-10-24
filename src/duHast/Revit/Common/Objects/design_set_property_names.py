"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Design set property names enum class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


from enum import Enum


class DesignSetPropertyNames(Enum):
    """
    Contains property names used in data set dictionary
    """
    
    DESIGN_SET_NAME = "designSetName"
    DESIGN_OPTION_NAME = "designOptionName"
    DESIGN_OPTION_IS_PRIMARY = "isPrimary"

    DESIGN_SET_DEFAULT_NAME = "Main Model"
    DESIGN_OPTION_DEFAULT_NAME = "-"

    @classmethod
    def combine_set_and_option_name(cls,set_name, option_name):
        """
        Combines the set and option name is fixed format

        :param set_name: The option set name
        :type set_name: str
        :param option_name: The option name
        :type option_name: str
        :return: Combination of set and option name
        :rtype: str
        """
        return  "{}_{}".format(set_name,option_name)