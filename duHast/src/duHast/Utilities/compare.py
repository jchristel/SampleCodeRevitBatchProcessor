"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to comparing:. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- two values
- whether a text value starts or does not start with a given text value

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


def does_not_equal(valueOne, valueTwo):
    """
    Returns True if valueOne does not match valueTwo.
    :param valueOne: a value
    :type valueOne: var
    :param valueTwo: another value
    :type valueTwo: var
    :return: True if valueOne does not match valueTwo, otherwise False
    :rtype: bool
    """

    if valueOne != valueTwo:
        return True
    else:
        return False


def does_equal(valueOne, valueTwo):
    """
    Returns True if valueOne does match valueTwo.
    :param valueOne: a value
    :type valueOne: var
    :param valueTwo: another value
    :type valueTwo: var
    :return: True if valueOne does match valueTwo, otherwise False
    :rtype: bool
    """

    if valueOne == valueTwo:
        return True
    else:
        return False


def one_start_with_two(valueOne, valueTwo):
    """
    Returns True if valueOne starts with valueTwo.
    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    :return: True if valueOne starts with valueTwo, otherwise False
    :rtype: bool
    """

    if valueOne.startswith(valueTwo):
        return True
    else:
        return False


def two_does_not_start_with_one(valueOne, valueTwo):
    """
    Returns True if valueTwo does not starts with valueOne.
    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    :return: True if valueTwo does not starts with valueOne, otherwise False
    :rtype: bool
    """

    if valueTwo.startswith(valueOne):
        return False
    else:
        return True
