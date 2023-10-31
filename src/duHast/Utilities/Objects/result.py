"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class used to return status, messages and objects back to a caller.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `Result` class is a subclass of the `base.Base` class and is used to store and manipulate the results of a process. It has fields for `message`, `status`, and `result`, and provides methods to update these fields.

Example Usage:
    result = Result()  # Create a new instance of the Result class
    result.append_message("An error occurred")  # Append a new message to the existing message
    result.update_status(False)  # Update the status to False
    result.update_sep(True, "Process completed successfully")  # Update the status and append a new message
    print(result)  # Print the result object

Methods:
    __init__(self):
        Initializes the Result object with default values for `message`, `status`, and `result`

    __repr__(self):
        Returns a string representation of the Result object, including the formatted message, status, and result

    append_message(self, message):
        Appends a new line and new message string to the existing message

    update(self, otherResult):
        Updates the Result object using another Result object, updating the message, status, and result

    update_sep(self, status, message):
        Updates the status and message properties of the Result object

    update_status(self, status):
        Updates the status property of the Result object

Fields:
    message: A string representing the message of the result
    status: A boolean representing the status of the result
    result: A list to store the result items
   
"""


#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

    def __repr__(self):
        # Split the message string into individual lines
        lines = self.message.splitlines()

        # Use str.format() to add indentation and line breaks
        formatted_string = "\n".join(["...{}".format(line) for line in lines])

        return "message: \n{} \nstatus: [{}] \nresult: {}".format(
            formatted_string, self.status, self.result
        )

    def append_message(self, message):
        """
        Appends a new line and new message string to the existing message.

        First message appended will replace the default value of -

        :param message: The new message to be appended.
        :type message: str
        """

        try:
            if self.message == "-":
                self.message = "{}".format(message)
            else:
                self.message = "{}\n{}".format(self.message, message)
        except Exception as e:
            self.message = "{} \nAn exception in result class occurred!!! {}".format(
                self.message, e
            )

    def update(self, otherResult):
        """
        Will use the past in result instance to update the instance.

        - .status is using a logical AND
        - .message is using append (unless other message is default '-')
        - .result is looping over past in result and adding it one by one to this .result list (ignores None)

        :param otherResult: Another result class instance.
        :type otherResult: SampleBatchProcessorCode.Result
        """

        if not isinstance(otherResult, Result):
            raise TypeError("otherResult must be an instance of Result")

        try:
            # check if default message string, if so do not update
            if otherResult.message != "-":
                self.append_message(otherResult.message)
            self.status = self.status & otherResult.status
            # check if result property that was passed in has values
            if any(otherResult.result):
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

        if not isinstance(status, bool):
            raise TypeError("status must be an instance of boolean")

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
