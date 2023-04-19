'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to batch processor.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
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
#

def adjust_session_id_for_file_name(id):
    '''
    Removes chevrons and replace colons with underscores in session id supplied by revit batch processor so it\
        can be used in a file name.

    :param id: Session id supplied by revit batch processor.
    :type id: str

    :return: Re-formatted session id.
    :rtype: str
    '''

    # remove colons
    session_id_changed = id.replace(':','_')
    # remove chevrons
    session_id_changed = session_id_changed[1:-1]
    return session_id_changed

def adjust_session_id_file_name_back(file_name_id):
    '''
    Re-introduces chevrons and replaces underscores with colons to match session Id format used in batch processor to a\
        file name using a batch processor supplied id.

    :param file_name_id: A file name containing a session id with all illegal characters replaced.
    :type file_name_id: str

    :return: A session id.
    :rtype: str
    '''

    # re-instate colons
    session_id_changed = file_name_id.replace('_',':')
    # remove chevrons
    session_id_changed = '<' + session_id_changed + '>'
    return session_id_changed

def adjust_session_id_for_directory_name(id):
    '''
    Removes chevrons and replace colons, full stops, dashes with underscores in session id supplied by revit batch processor so it\
        can be used in a folder name.

    :param id: Session id supplied by revit batch processor.
    :type id: str

    :return: Re-formatted session id.
    :rtype: str
    '''

    # remove colons
    session_id_changed = id.replace(':','_')
    # remove spaces
    session_id_changed = session_id_changed.replace(' ','_')
    # remove full stops
    session_id_changed = session_id_changed.replace('.','_')
    # remove dashes
    session_id_changed = session_id_changed.replace('-','_')
    # remove chevrons
    session_id_changed = session_id_changed.replace('<','')
    session_id_changed = session_id_changed.replace('>','')
    return session_id_changed