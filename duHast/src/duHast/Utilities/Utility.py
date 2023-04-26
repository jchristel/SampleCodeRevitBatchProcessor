'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

#import clr
#import System
#from numpy import empty
import os
import os.path
import collections

#import clr
#clr.AddReference("System.Core")
#from System import Linq
#clr.ImportExtensions(Linq)

def get_local_app_data_path():
    '''
    return directory path to local app data folder

    :return: Path to local app data
    :rtype: str
    '''

    return os.environ['LOCALAPPDATA']

def get_current_user_name():
    '''
    Returns the current user name

    :return: the user name
    :rtype: str
    '''
    
    return os.environ['USERNAME']


# ---------------------------------------------------------------------------------------------------------------------------------

def parse_string_to_bool(text):
    '''
    Converts a string to lower case and then to bool. Will throw an exception if it fails to do so.

    ( 'true' = True, 'false' = False)

    :param text: The string representing a bool.
    :type text: str
    :raises Exception: If string to bool conversion fails the 'String cant be converted to bool' exception will be raised.
    
    :return: True or False
    :rtype: bool
    '''

    if(text.lower() == 'true'):
        return True
    elif (text.lower() == 'false'):
        return False
    else:
         raise Exception('String cant be converted to bool')

# ---------------------------------------------------------------------------------------------------------------------------------

#: two digit padding
PAD_SINGLE_DIGIT_TO_TWO = '%02d'
#: three digit padding
PAD_SINGLE_DIGIT_TO_THREE = '%03d'


def pad_single_digit_numeric_string(numericString, format = PAD_SINGLE_DIGIT_TO_TWO):
    '''
    Pads a single digit integer (past in as a string) with a leading zero (default)

    :param numericString: Integer as string.
    :type numericString: str
    :param format: The integer padding format, defaults to PAD_SINGLE_DIGIT_TO_TWO
    :type format: str, optional
    
    :return: The padded integer as string.
    :rtype: str
    '''

    # attempt to convert string to int first
    try:
        value = int(numericString)
        return str(format%value)
    except Exception:
        #string was not an integer...
        return numericString

def encode_ascii (string):
    '''
    Encode a string as ascii and replaces all non ascii characters

    If a non string is past in the value will be returned unchanged.
    
    :param string: The string to be ascii encoded.
    :type string: str

    :return: ascii encoded string
    :rtype: str
    '''
    if (type(string) == str):
        return string.encode('ascii','replace')
    else:
        return string

def get_first(iterable, default, condition = lambda x: True):
    '''
    Returns the first value in a list matching condition. If no value found returns the specified default value.

    :param iterable: the list to be searched.
    :type iterable: iterable
    :param default: The default value
    :type default: var
    :param condition: The condition to be checked, defaults to lambda x:True
    :type condition: _type_, optional
    
    :return: First value matching condition, otherwise default value
    :rtype: var
    '''

    return next((x for x in iterable if condition(x)),default)

def index_of(list, item):
    '''
    Gets the index of item in list

    :param list: The list
    :type list: list
    :param item: The item of which to return the index.
    :type item: var

    :return: The index of the item in the list, if no match -1 will be returned
    :rtype: int
    '''
    try:
        return list.index(item)
    except:
        return -1

def remove_items_from_list(sourceList, removeIdsList):
    '''
    helper removes items from a source list

    :param sourceList: The list containing items
    :type sourceList: list var
    :param removeIdsList: the list containing items to be removed
    :type removeIdsList: list var
    
    :return: The filtered source list.
    :rtype: list var
    '''

    try:
        for item in removeIdsList:
            sourceList.remove(item)
    except:
        pass
    return sourceList


def flatten(d, parent_key='', sep='_'):
    '''
    Flattens a dictionary as per stack overflow

    https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys/6027615#6027615

    :param d: _description_
    :type d: _type_
    :param parent_key: _description_, defaults to ''
    :type parent_key: str, optional
    :param sep: _description_, defaults to '_'
    :type sep: str, optional
    :return: _description_
    :rtype: _type_
    '''
    
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)