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

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A custom exception raised when a family conflict occurs.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used by RevitFamiliesModel.

"""

# Define a custom exception by subclassing Exception
from families.reload.Models.RevitFamily import RevitFamily


class FamiliesConflictException(Exception):
    def __init__(self, message, existing_family, new_family):
        """
        A custom exception raised when a family conflict occurs.

        :param message: the message of the exception
        :type message: str
        :param existing_family: the existing family
        :type existing_family: :class:`.RevitFamily`
        :param new_family: the new family
        :type new_family: :class:`.RevitFamily`
        """

        if isinstance(existing_family, RevitFamily) == False:
            raise TypeError(
                "existing_reservation need to be of type RevitFamily. Got {} instead.".format(
                    type(existing_family)
                )
            )
        self.existing_reservation = existing_family

        if isinstance(new_family, RevitFamily) == False:
            raise TypeError(
                "new_reservation need to be of type RevitFamily. Got {} instead.".format(
                    type(new_family)
                )
            )
        self.new_reservation = new_family

        # Call the base class constructor with the message
        super(FamiliesConflictException, self).__init__(
            message, existing_family, new_family
        )

    def __str__(self):
        """
        Custom string representation of the exception
        """

        return "FamiliesConflictException: {}".format(self.args[0])
