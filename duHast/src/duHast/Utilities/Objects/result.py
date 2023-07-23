"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class used to return status, messages and objects back to a caller.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


A class used to return the value if any, a message and the status of a method (true if everything is ok or false if something went wrong).

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

from duHast.Utilities.Objects import base


class Result(base.Base):
    def __init__(self):
        """
        Class constructor.

        - message default value is -
        - status default value is True
        - result default value is []

        """

        super(Result, self).__init__()

        self.message = "-"
        self.status = True
        self.result = []

    def append_message(self, message):
        """
        Appends a new line and new message string to the existing message.

        First message appended will replace the default value of -

        :param message: The new message to be appended.
        :type message: str
        """

        try:
            if self.message == "-":
                self.message = message
            else:
                self.message = self.message + "\n" + message
        except Exception as e:
            print(str(e))
            pass

    def update(self, otherResult):
        """
        Will use the past in result instance to update the instance.

        - .status is using a logical AND
        - .message is using append (unless other message is default '-')
        - .result is looping over past in result and adding it one by one to this .result list (ignores None)

        :param otherResult: Another result class instance.
        :type otherResult: SampleBatchProcessorCode.Result
        """

        try:
            # check if default message string, if so do not update
            if otherResult.message != "-":
                self.append_message(otherResult.message)
            self.status = self.status & otherResult.status
            # check if result property that was passed in has values
            if otherResult.result is not None and len(otherResult.result) > 0:
                for item in otherResult.result:
                    self.result.append(item)
        except Exception as e:
            print(str(e))
            pass

    def update_sep(self, status, message):
        """
        Updates the .status and .message property only.

        - .status is using a logical AND
        - .message is using append (unless other message is default '-')

        :param status: The status to be added.
        :type status: bool
        :param message: The message to be appended.
        :type message: str
        """

        try:
            self.append_message(message)
            # self.message = self.message + '\n' + message
            self.status = self.status & status
        except Exception as e:
            print(str(e))
            pass

    def update_status(self, status):
        """
        Update .status only.

        - .status is using a logical AND

        :param status: The status to be added.
        :type status: bool
        """

        try:
            self.status = self.status & status
        except Exception as e:
            print(str(e))
            pass
