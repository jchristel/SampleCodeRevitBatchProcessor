#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

import clr
import System

# import common library modules
import RevitCommonAPI as com
import Result as res
import Utility as util

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_DESIGNSET_HEADER = ['HOSTFILE','ID', 'NAME', 'PRIMARY OPTION', 'OTHER OPTIONS']

# --------------------------------------------- utility functions ------------------

# returns a collector containing all design options in a model
# doc   current document
def GetDesignOptions(doc):
    collector = FilteredElementCollector(doc).OfClass(DesignOption)
    return collector


# returns a list of all the design sets in a model
# doc   current document
def GetDesignSets(doc):
    collector = FilteredElementCollector(doc).OfClass(DesignOption)
    designSets = []
    designSetNames = []
    for do in collector:
        e = doc.GetElement(do.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId())
        designSetName = Element.Name.GetValue(e)
        if(designSetName not in designSetNames):
            designSets.append(do)
            designSetNames.append(designSetName)
    return designSets
