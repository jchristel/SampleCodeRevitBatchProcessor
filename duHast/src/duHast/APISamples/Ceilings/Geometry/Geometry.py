'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit ceilings geometry extraction functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
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
import Autodesk.Revit.DB as rdb

from duHast.APISamples.Ceilings import RevitCeilings as rCeiling
from duHast.DataSamples.Objects.Properties.Geometry import FromRevitConversion as rCon


def get_2d_points_from_revit_ceiling(ceiling):
    '''
    Returns a list of lists of points representing the flattened(2D geometry) of the ceiling
    List of Lists because a ceiling can be made up of multiple sketches. Each nested list represents one ceiling sketch.
    Does not work with in place ceilings.

    :param ceiling: A revit ceiling instance.
    :type ceiling: Autodesk.Revit.DB.Ceiling

    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    '''

    allCeilingPoints = []
    # get geometry from ceiling
    opt = rdb.Options()
    fr1_geom = ceiling.get_Geometry(opt)
    solids = []
    # check geometry for Solid elements
    # todo check for FamilyInstance geometry ( in place families!)
    for item in fr1_geom:
        if(type(item) is rdb.Solid):
            solids.append(item)

    # process solids to points 
    # in place families may have more then one solid
    for s in solids:
        pointPerCeilings = rCon.convert_solid_to_flattened_2d_points(s)
        if(len(pointPerCeilings) > 0):
            for pLists in pointPerCeilings:
                allCeilingPoints.append(pLists)
    return allCeilingPoints


def get_2d_points_from_revit_ceilings_in_model(doc):
    '''
    Returns a list of lists of points representing the flattened(2D geometry) of the ceiling
    List of Lists because a ceiling can be made up of multiple sketches. Each nested list represents one ceiling sketch.
    Does not work with in place ceilings.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    '''

    ceilingInstances =  rCeiling.get_all_ceiling_instances_in_model_by_category(doc)
    allCeilingPoints = []
    for cI in ceilingInstances:
       ceilingPoints = get_2d_points_from_revit_ceiling(cI)
       if(len(ceilingPoints) > 0 ):
           allCeilingPoints.append (ceilingPoints)
    return allCeilingPoints