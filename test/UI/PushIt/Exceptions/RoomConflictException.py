#License:
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

# Define a custom exception by subclassing Exception
from PushIt.Models.Room import Room

class RoomsConflictException(Exception):
    def __init__(self, message, existing_room, new_room):
        """
        Constructor for the RoomsConflictException class.

        :param message: The error message
        :type message: str
        :param existing_room: The existing room
        :type existing_room: Room
        :param new_room: The new room
        :type new_room: Room
        """

        if(isinstance(existing_room, Room)==False):
            raise TypeError ("existing_room need to be of type Room. Got {} instead.".format(type(existing_room)))
        self.existing_room = existing_room
        
        if(isinstance(new_room, Room)==False):
            raise TypeError ("new_room need to be of type Room. Got {} instead.".format(type(new_room)))
        self.new_room = new_room
        
        # Call the base class constructor with the message
        super(RoomsConflictException, self).__init__(message, existing_room, new_room)
        

    def __str__(self):
        # Custom string representation of the exception
        return "RoomsConflictException: {}".format(self.args[0])