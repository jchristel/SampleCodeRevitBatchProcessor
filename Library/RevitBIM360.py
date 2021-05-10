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
import glob
import Result as res

#from System.IO import Path
from Autodesk.Revit.DB import *
import os.path as path

# return human readable BIM 360 path
def GetBim360Path(doc):
    # get bim 360 path
    revitFilePath = ''
    try:
        path = doc.GetCloudModelPath()
        revitFilePath = ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    except Exception as e:
        revitFilePath = ''
    return revitFilePath

# pretend this is a file server path rather than cloud model path
def ConvertBIM360FilePath(path):
    # hack.. pretend path points to C:\\ rather than BIM 360://
    path = path.replace(r'BIM 360://', r'C:/')
    return path
