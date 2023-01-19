'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class used to return status, messages and objects back to a caller.
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


#a class used to return the value  if any, a message and the status of a method (true if everything is ok or false if something went wrong)
class Result: 
    def __init__(self):
        '''
        Class constructor.

        - message default value is -
        - status default value is True
        - result default value is []
        
        '''

        self.message = '-'
        self.status = True
        self.result = []
    
    def AppendMessage(self, message):
        '''
        Appends a new line and new message string to the existing message.

        First message appended will replace the default value of -

        :param message: The new message to be appended.
        :type message: str
        '''
        try:
            if(self.message == '-'):
                self.message = message
            else:
                self.message = self.message + '\n' + message
        except Exception as e:
            print (str(e))
            pass

    def Update(self, otherResult):
        '''
        Will use the past in result instance to update the instance.

        - .status is using a logical AND 
        - .message is using append (unless other message is default '-')
        - .result is looping over past in result and adding it one by one to this .result list (ignores None)

        :param otherResult: Another result class instance.
        :type otherResult: SampleBatchProcessorCode.Result
        '''
        try:
            # check if default message string, if so do not update
            if(otherResult.message != '-'):
                self.AppendMessage(otherResult.message)
            self.status = self.status & otherResult.status
            # check if result property that was passed in has values
            if(otherResult.result is not None and len(otherResult.result)>0):
                for item in otherResult.result:
                    self.result.append(item)
        except Exception as e:
            print (str(e))
            pass
    
    def UpdateSep (self, status, message):
        '''
        Updates the .status and .message property only.
        
        - .status is using a logical AND 
        - .message is using append (unless other message is default '-')
        
        :param status: The status to be added.
        :type status: bool
        :param message: The message to be appended.
        :type message: str
        '''
        
        try:
            self.AppendMessage(message)
            # self.message = self.message + '\n' + message
            self.status = self.status & status
        except Exception as e:
            print (str(e))
            pass

    def UpdateStatus(self, status):
        '''
        Update .status only.

        - .status is using a logical AND 

        :param status: The status to be added.
        :type status: bool
        '''
        try:
            self.status = self.status & status
        except Exception as e:
            print (str(e))
            pass
