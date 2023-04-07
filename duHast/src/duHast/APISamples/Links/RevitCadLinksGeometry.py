'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to CAD link geometry.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.APISamples.Links.RevitCadLinks import GetAllCADLinkInstances


def GetCADImportInstanceGeometry(importInstance):
    '''
    Returns a list of geometry elements from an import instance
    :param importInstance: A import instance
    :type importInstance: AutoDesk.Revit.DB.ImportInstance
    :return: A list of geometry objects. Can return an empty list!
    :rtype: [Autodesk.Revit.DB GeometryObject]
    '''

    geo = []
    # default geometry option
    opt = rdb.Options()
    geoElemLevel1 = importInstance.get_Geometry(opt)
    if (geoElemLevel1 != None):
        for geoInstance in geoElemLevel1:
            if(geoInstance!= None):
                geoElemLevel2 = geoInstance.GetInstanceGeometry()
                if(geoElemLevel2 !=None):
                    for item in geoElemLevel2:
                        geo.append(item)
    return geo


def GetAllCADImportInstancesGeometry(doc):
    '''
    Returns a list of geometry elements from all import instances in the document.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of geometry objects. Can return an empty list!
    :rtype: [Autodesk.Revit.DB GeometryObject]
    '''
    instancesGeometry = []
    allImportInstances = GetAllCADLinkInstances(doc)
    for importInstance in allImportInstances:
        geometryInstances = GetCADImportInstanceGeometry(importInstance)
        if (len(geometryInstances) > 0):
            instancesGeometry += geometryInstances
    return instancesGeometry