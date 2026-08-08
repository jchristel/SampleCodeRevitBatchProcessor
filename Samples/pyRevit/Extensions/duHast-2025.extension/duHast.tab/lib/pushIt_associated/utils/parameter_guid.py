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


def normalise_guid(guid):
    """
    Returns a parameter guid in a shape which can safely be compared with another guid.

    Revit always reports a shared parameter guid in lower case and without braces, however
    guids coming from a data source ( CSV file, drofus property mappings ) are authored by
    hand and may be upper case and / or wrapped in braces. Comparing those as is fails
    silently and no parameter data gets transferred.

    :param guid: The guid to normalise. Can be a string or a System.Guid.
    :type guid: str or System.Guid or None
    :return: The guid as a lower case string without braces or surrounding white space. An
        empty string if None was passed in.
    :rtype: str
    """

    if guid is None:
        return ""

    return str(guid).strip().strip("{}").strip().lower()
