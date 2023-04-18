'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to comparing:. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- two values
- whether a text value starts or does not start with a given text value

'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

def does_not_equal (valueOne, valueTwo):
    '''
    Returns True if valueOne does not match valueTwo.
    :param valueOne: a value
    :type valueOne: var
    :param valueTwo: another value
    :type valueTwo: var
    :return: True if valueOne does not match valueTwo, otherwise False
    :rtype: bool
    '''

    if (valueOne != valueTwo):
        return True
    else:
        return False


def does_equal (valueOne, valueTwo):
    '''
    Returns True if valueOne does match valueTwo.
    :param valueOne: a value
    :type valueOne: var
    :param valueTwo: another value
    :type valueTwo: var
    :return: True if valueOne does match valueTwo, otherwise False
    :rtype: bool
    '''

    if (valueOne == valueTwo):
        return True
    else:
        return False


def one_start_with_two (valueOne, valueTwo):
    '''
    Returns True if valueOne starts with valueTwo.
    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    :return: True if valueOne starts with valueTwo, otherwise False
    :rtype: bool
    '''

    if (valueOne.startswith(valueTwo)):
        return True
    else:
        return False


def two_does_not_start_with_one (valueOne, valueTwo):
    '''
    Returns True if valueTwo does not starts with valueOne.
    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    :return: True if valueTwo does not starts with valueOne, otherwise False
    :rtype: bool
    '''

    if (valueTwo.startswith(valueOne)):
        return False
    else:
        return True