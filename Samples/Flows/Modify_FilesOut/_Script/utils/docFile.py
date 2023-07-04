#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# a class used to store file date for renaming
class docFile: 
    def __init__(self, data): 
        try:
            self.existingFileName = data[0]
            self.fileExtension = data[4]
            self.fileNameNewParts = []
            self.fileNameNewParts.append(data[1])
            if(len(data[3]) > 0):
                self.fileNameNewParts.append(data[3])
            if(len(data[2]) > 0):
                self.revision = data[2]
            else:
                self.revision = '-'
            self.AconexDocNumber = data[5]
            self.AconexDocName = data[6]
            self.NewRevision = False
        except Exception as e:
            print (str(e))
            pass

    def getNewFileName(self):
        suffix =''
        if(len(self.fileNameNewParts)>1):
            suffix = self.fileNameNewParts[1]
        return self.fileNameNewParts[0] + self.revision + suffix # ignore revision brackets

    # returns a list of all property values of this class
    def getData(self):
        returnvalue = []
        returnvalue.append(self.existingFileName)
        returnvalue.append(self.fileNameNewParts[0])
        returnvalue.append(self.revision)
        if(len(self.fileNameNewParts)>1):
            returnvalue.append(self.fileNameNewParts[1])
        else:
            returnvalue.append('')
        returnvalue.append(self.fileExtension)
        returnvalue.append(self.AconexDocNumber)
        returnvalue.append(self.AconexDocName)
        return returnvalue

    def upDateNumericalRev(self):
        try:
            # default start value
            rev = 1
            # check if start value is to be applied
            if(self.revision != '-'):
                rev = int(self.revision)
                rev = rev + 1
            # apply new rev value as string
            self.revision = str(rev)
        except Exception as e:
            # no need to do anything
            self.revision = self.revision