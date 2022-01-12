#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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

import json

class DataRoom():
    def __init__(self):
        self.dataType = 'room'
        self.id = -1
        self.name = '-'
        self.number = '-'
        self.levelName = '-'
        self.levelId = '-'
        self.geometry = [[]]
        self.functionNumber = '-'
        self.associatedElements = []

    def to_json(self):
        '''
        convert the instance of this class to json
        '''
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)