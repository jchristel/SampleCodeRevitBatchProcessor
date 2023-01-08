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

def AdjustSessionIdForFileName(id):
    '''
    Removes chevrons and replace colons with underscores in session id supplied by revit batch processor so it\
        can be used in a file name.

    :param id: Session id supplied by revit batch processor.
    :type id: str

    :return: Re-formatted session id.
    :rtype: str
    '''

    # remove colons
    sessionIdChanged = id.replace(':','_')
    # remove chevrons
    sessionIdChanged = sessionIdChanged[1:-1]
    return sessionIdChanged

def AdjustSessionIdFileNameBack(fileNameId):
    '''
    Re-introduces chevrons and replaces underscores with colons to match session Id format used in batch processor to a\
        file name using a batch processor supplied id.

    :param fileNameId: A file name containing a session id with all illegal characters replaced.
    :type fileNameId: str

    :return: A session id.
    :rtype: str
    '''

    # re-instate colons
    sessionIdChanged = fileNameId.replace('_',':')
    # remove chevrons
    sessionIdChanged = '<' + sessionIdChanged + '>'
    return sessionIdChanged

def AdjustSessionIdForFolderName(id):
    '''
    Removes chevrons and replace colons, full stops, dashes with underscores in session id supplied by revit batch processor so it\
        can be used in a folder name.

    :param id: Session id supplied by revit batch processor.
    :type id: str

    :return: Re-formatted session id.
    :rtype: str
    '''

    # remove colons
    sessionIdChanged = id.replace(':','_')
    # remove spaces
    sessionIdChanged = sessionIdChanged.replace(' ','_')
    # remove full stops
    sessionIdChanged = sessionIdChanged.replace('.','_')
    # remove dashes
    sessionIdChanged = sessionIdChanged.replace('-','_')
    # remove chevrons
    sessionIdChanged = sessionIdChanged.replace('<','')
    sessionIdChanged = sessionIdChanged.replace('>','')
    return sessionIdChanged