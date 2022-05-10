'''
This module contains a class used to return status, messages and objects back to a caller. 
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
        _summary_
        '''
        self.message = '-'
        self.status = True
        self.result = []
    
    def AppendMessage(self, message):
        '''
        _summary_

        :param message: _description_
        :type message: _type_
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
        _summary_

        :param otherResult: _description_
        :type otherResult: _type_
        '''
        try:
            # check if default message string, if so do not update
            if(otherResult.message is not '-'):
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
        _summary_

        :param status: _description_
        :type status: _type_
        :param message: _description_
        :type message: _type_
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
        _summary_

        :param status: _description_
        :type status: _type_
        '''
        try:
            self.status = self.status & status
        except Exception as e:
            print (str(e))
            pass
