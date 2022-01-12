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

from Autodesk.Revit.DB import *

# ---------------------------- debug ----------------------------
def GetPointAsString (point):
    return str(point.X) + ' : ' + str(point.Y) + ' : ' + str(point.Z)
    
def GetEdgeAsString(edge):
    returnValue = ''
    for p in edge.Tessellate():
        returnValue = returnValue + '\n' + GetPointAsString (p)
    return returnValue

# ---------------------------- math utility ----------------------------

# a     float
# b     float
def IsClose(a, b, rel_tol=1e-09, abs_tol=0.0):
    '''
    compares two floats with a tolerance. Returns True if they are close enough, otherwise False
    refer to: https://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python
    '''
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# p1         Revit XYZ point
# p2         Revit XYZ point
def ArePointsIdentical(p1, p2):
    ''' 
    compares the X,Y,Z values of a revit point and returns True if they are the same
    returns False if they are not the same
    '''
    if (IsClose(p1.X,p2.X) and IsClose(p1.Y, p2.Y) and IsClose(p1.Z,p2.Z)):
        return True
    else:
        return False

# points        collection of Revit  XYZ points
# point         Revit XYZ point
def CheckDuplicatePoint(points, point):
    '''
    Checks whether a collection contains a given point and returns True if that is the case
    '''
    for p1 in points:
        if(ArePointsIdentical(p1, point)):
            return True
    return False

# edge          Revit Edge objectS
def GetEdgePoints(edge):
    '''
    returns the two Revit XYZ points defining an edge
    '''
    points = []
    for p in  edge.Tessellate():
        points.append(p)
    return points

# edges         list of Revit Edge objects
# edge          Revit Edge objectS
def CheckDuplicateEdge(edges, edge):
    '''
    Checks whether a collection contains a given edge and returns True if that is the case
    '''
    flagOverAll = False
    compPoints = GetEdgePoints(edge)
    if(len(edges) > 0):
        for e in edges:
            listPoints = GetEdgePoints(e)
            if (len(compPoints) == len(listPoints)):
                edgeSameFlag = True
                for p1 in compPoints:
                    if(CheckDuplicatePoint(listPoints, p1) == False):
                        edgeSameFlag = False
                if(edgeSameFlag):
                    flagOverAll = True
                    break
            else:
              pass
    else:
        pass # flag is already False
    return flagOverAll
        
# solid         a Revit Solid object
def CheckSolidIsZeroHeight(solid):
    ''' 
    returns False if points collection of a solid has multiple z values, 
    returns True if only one Z value in points collection (2D solid...??)
    '''
    return  CheckEdgesAreZeroHeight(solid.Edges)

# edges         a list of Revit edge elements
def CheckEdgesAreZeroHeight(edges):
    ''' 
    returns False if points collection of a edges has multiple z values, 
    returns True if only one Z value in points collection (2D solid...??)
    '''
    lowestZ = 0.0
    counter = 0
    for edge in edges:
        for p in edge.Tessellate():
            if (counter == 0):
                lowestZ = p.Z
            else:
                if(IsClose(p.Z, lowestZ) == False):
                    # found multiple z
                    return False
            counter = counter + 1
    return True

# solid         a Revit Solid element
def GetLowestZFromSolidsPointCollection(solid):
    ''' 
    returns the lowest Z value in a solids point collection
    '''
    return GetLowestZFromSolidsPointCollection(solid.Edges)

# edges         a list of Revit edge elements
def GetLowestZFromEdgesPointCollection(edges):
    ''' 
    returns the lowest Z value in a solids point collection
    '''
    lowestZ = 0.0
    counter = 0
    for edge in edges:
        for p in edge.Tessellate():
            # make sure lowest z is initialist with the first point z values
            if (counter == 0):
                lowestZ = p.Z
            else:
                if(IsClose(p.Z, lowestZ) == False and p.Z < lowestZ):
                    lowestZ = p.Z
            counter = counter + 1 
    return lowestZ

# edge1         Revit edge element
# edge2         Recit edge element
def EdgesAreConnected(edge1, edge2):
    '''
    returns true if the two edges passt in share at least one point
    '''
    for p1 in edge1.Tessellate():
        for p2 in edge2.Tessellate():
            if (ArePointsIdentical(p1, p2)):
                return True
    return False

# edge      reference Revit edge element
# edges     list of Revit edge elements to check  whether any of them is connected to reference edge
def FindConnectedEdges(edge, edges):
    '''
    checks a list of edges for any edge connected to the passt in reference edge and returns list od connected edges
    initial list needs to contain the reference edge!
    '''
    copyEdges = list(edges)
    # check not accounted edge only
    if (CheckDuplicateEdge(edges, edge) == False):
        # check if edge is connected to some of the existing edges
        for checkEdge in copyEdges:
            if(EdgesAreConnected(checkEdge, edge)):
                edges.append(edge)
                break
    else:
        pass # duplicate edge, no need to check again
    return edges

# edges     list of Revit edge elements to build edge group from
def BuildEdgeGroup(edges):
    '''
    builds a list of edges which are connected to form a volumne. It will take the first edge form the list passt in and will
    look for any edges connected to the initial edge and any further edges (building a tree)
    '''
    edgeGroup = []
    if(len(edges) > 0):
        edgeGroup = [edges[0]]
        # iterate mutliple times over edge list to mkae sure to catch all possible connections
        for x in range(len(edges)):
            for edge in edges:
                edgeGroup = FindConnectedEdges(edge, edgeGroup)
                # check if all edges are accounted for..may not always be the the case i.e. : if multiple volumnes
                if(len(edgeGroup) == len(edges)):
                    break
    return edgeGroup

# edges     list of Revit edge elements to build edge groups from
def SortEdges(edges):
    '''
    Some solids are made up of multiple volumnes...to group points by volumnes I need to sort edges by volume first
    Returns list of list of edges describing individual volumnes
    '''
    # copy original array so it can be modified
    edgesCopy = list(edges)
    # store the original edge array size for reference
    originalSize = edges.Size
    # to hold any edge groups identified
    edgeGroups = []
    # counter of edges assigned to a edge group
    lenOverAll = 0
    # fail safe: how many edges where identified in previous loop iteration
    previousLenOverAll = 0
    # while loop flag. False when all edges are assigned to a edge group or safety kicks in
    flag = True
    # loop over balance of edges and check whether any of them is connected
    while flag:
        # build an edge group
        edgeGroup = BuildEdgeGroup(edgesCopy)
        lenOverAll = lenOverAll + len(edgeGroup)
        # check if anything usefull came back
        if(len(edgeGroup) > 0):
            edgeGroups.append(edgeGroup)
        # check if all edges are accounted for in edge groups
        if(lenOverAll < originalSize ):
            # remove edges which are accounted for from overall list and go again
            for edgeRemove in edgeGroup:
                edgesCopy.remove(edgeRemove)
            # check whether there are any edges to check left
            if(len(edgesCopy) == 0):
                flag = False
        else:
            # all edges are accounted for
            flag = False

         # avoid infinite loop by checking for changes
        if(lenOverAll == previousLenOverAll):
            flag = False
        else:
            previousLenOverAll = lenOverAll
    return edgeGroups

# solid         a Revit Solid element
def ConvertSolidToFlattened2DPoints(solid):
    '''
    returns a list of list of Revit XYZ points describing the outline of a solid projected onto a plane
    arcs, circles will be tesselated to polygons
    '''
    pointsGroups = []
    if(solid != None and solid.Edges.Size > 0):
        edgeGroups = SortEdges(solid.Edges)
        for eg in edgeGroups:
            points = []
            # check if zero height ceiling (Basic ceiling)
            if(CheckEdgesAreZeroHeight(eg)):
                # need to avoid duplicate points!
                for edge in eg:
                    for p in edge.Tessellate():
                        if(CheckDuplicatePoint(points, p) == False):
                            points.append(p)
                pointsGroups.append(points)
            else:
                # Compound ceiling
                lowestZ = GetLowestZFromEdgesPointCollection(eg)
                for edge in eg:
                    # tessalate edge to avoid arcs
                    for p in edge.Tessellate():
                        # make sure only points from the lowest plane are taken
                        # remove any duplicate points (vertical and horizontal edges share points!)
                        if(IsClose(p.Z, lowestZ) and CheckDuplicatePoint(points, p) == False):
                            points.append(p)
                pointsGroups.append(points)
    return pointsGroups