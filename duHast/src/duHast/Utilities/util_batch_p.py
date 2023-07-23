"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to batch processor.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


def adjust_session_id_for_file_name(id):
    """
    Removes chevrons and replace colons with underscores in session id supplied by revit batch processor so it\
        can be used in a file name.

    :param id: Session id supplied by revit batch processor.
    :type id: str

    :return: Re-formatted session id.
    :rtype: str
    """

    # remove colons
    session_id_changed = id.replace(":", "_")
    # remove chevrons
    session_id_changed = session_id_changed[1:-1]
    return session_id_changed


def adjust_session_id_file_name_back(file_name_id):
    """
    Re-introduces chevrons and replaces underscores with colons to match session Id format used in batch processor to a\
        file name using a batch processor supplied id.

    :param file_name_id: A file name containing a session id with all illegal characters replaced.
    :type file_name_id: str

    :return: A session id.
    :rtype: str
    """

    # re-instate colons
    session_id_changed = file_name_id.replace("_", ":")
    # remove chevrons
    session_id_changed = "<" + session_id_changed + ">"
    return session_id_changed


def adjust_session_id_for_directory_name(id):
    """
    Removes chevrons and replace colons, full stops, dashes with underscores in session id supplied by revit batch processor so it\
        can be used in a folder name.

    :param id: Session id supplied by revit batch processor.
    :type id: str

    :return: Re-formatted session id.
    :rtype: str
    """

    # remove colons
    session_id_changed = id.replace(":", "_")
    # remove spaces
    session_id_changed = session_id_changed.replace(" ", "_")
    # remove full stops
    session_id_changed = session_id_changed.replace(".", "_")
    # remove dashes
    session_id_changed = session_id_changed.replace("-", "_")
    # remove chevrons
    session_id_changed = session_id_changed.replace("<", "")
    session_id_changed = session_id_changed.replace(">", "")
    return session_id_changed
