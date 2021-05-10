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

import System
import clr

#a class used to return the value  if any, a message and the status of a method (true if everything is ok or false if something went wrong)
class Result: 
    def __init__(self): 
        self.message = '-'
        self.status = True
        self.result = []
    
    def Update(self, otherResult):
        try:
            # check if default message string, if so do not update
            if(otherResult.message is not '-'):
                self.message = self.message + '\n' + otherResult.message
            self.status = self.status & otherResult.status
            # check if result property that was passed in has values
            if(otherResult.result is not None and len(otherResult.result)>0):
                self.result.append(otherResult.result)
        except Exception as e:
            print (str(e))
            pass
    
    def UpdateSep (self, status, message):
        try:
            self.message = self.message + '\n' + message
            self.status = self.status & status
        except Exception as e:
            print (str(e))
            pass

    def AppendMessage(self, message):
        try:
            self.message = self.message + '\n' + message
        except Exception as e:
            print (str(e))
            pass

    def UpdateStatus(self, status):
        try:
            self.status = self.status & status
        except Exception as e:
            print (str(e))
            pass
