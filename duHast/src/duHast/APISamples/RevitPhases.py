'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model phase functions.
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


def GetAllPhases(doc):
    '''
    Returns a dictionary where key is the id and value is the name of the phase.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A dictionary where key is the id and value is the name of the phase. Dictionary will be empty if no phases exist (family doc?)
    :rtype: dic{key Autodesk.Revit.DB.ElementId: value str}
    '''

    returnValue = {}
    phases = doc.Phases
    if (phases.Size > 0):
        for phase in phases:
            returnValue[phase.Id] = phase.Name
    return returnValue

def GetPhaseNameById(doc, phaseId):
    '''
    Returns the name of a phase by Id

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param phaseId: The phase element id.
    :type phaseId: Autodesk.Revit.DB.ElementId
    
    :return: Name of the phase, otherwise 'No phase in document' if no phase exists or 'Invalid phase id.' if no phase matching the id was found.
    :rtype: str
    '''

    returnValue = 'No phase in document'
    phases = GetAllPhases(doc)
    if(len(phases) > 0):
        if phaseId in phases:
            returnValue = phases[phaseId]
        else:
            returnValue = 'Invalid phase id.'
    return returnValue