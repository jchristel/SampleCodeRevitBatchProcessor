'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit grids workset modifier functions.
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

from duHast.Utilities import Result as res
from duHast.APISamples.Common import RevitWorksets as rWork
from duHast.APISamples.Grids import RevitGrids as rGrid


def ModifyGridWorkSetsDefault (doc, worksetRules):
    '''
    Workset modifier method. Moves all grids to one workset
    rules format:
    ['Model name',[
           [workset modifier method,
               [worksetName]
               ]
           ]
    :param doc: _description_
    :type doc: _type_
    :param worksetRules: _description_
    :type worksetRules: _type_
    :return: returns a result object
    :rtype: _type_
    '''
    gridsResults = res.Result()
    collectorGrids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid)
    for rule in worksetRules:
        for defaultWorksetName in rule:
            grids = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorGrids, 'grids')
            gridsResults.Update(grids)
    return gridsResults


def ModifyGridWorkSetsByTypeName(doc, worksetRules):
    '''
    Workset modifier method. Moves grids matching type condition to a particular workset
    defaultWorksetTypeRules_ = [
        ['model name',[
            [ModifyGridWorkSetsByTypeName,[
                ['workset name', util.ConDoesNotEqual, 'grid type name'],
                ['workset name', util.ConDoesEqual, 'grid type name']
                ]
            ]
            ]
        ]
    ]
    :param doc: _description_
    :type doc: _type_
    :param worksetRules: _description_
    :type worksetRules: _type_
    :return: returns a result object
    :rtype: _type_
    '''

    gridsResults = res.Result()
    # loop over grid type filter and address one at the time
    # get all grids matching type name filter
    for defaultWorksetName, typeNameCondition, typeName,  in worksetRules:
        # get the grid type id from the type name
        typeId = rGrid.GetGridTypeIdByName(doc, typeName)
        collectorGrids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid).Where(lambda e: typeNameCondition(e.GetTypeId(), typeId))
        grids = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorGrids, 'grids')
        gridsResults.Update(grids)
    return gridsResults


def ModifyGridWorkSetsByParameterValue(doc, worksetRules):
    '''
    Workset modifier method. Moves grids matching parameter condition to a particular workset
    #defaultWorksetRulesNames_ = [
        ['model name',[
            [ModifyGridWorkSetsByParameterValue,[
                ['workset name', util.ConTwoStartWithOne, 'Name' ,'name starts with value']
                ]
            ]
            ]
        ]
    ]
    :param doc: _description_
    :type doc: _type_
    :param worksetRules: _description_
    :type worksetRules: _type_
    :return: returns a result object
    :rtype: _type_
    '''

    gridsResults = res.Result()
    # loop over grid parameter filter and address one at the time
    # get all grids matching filter
    for defaultWorksetName, paraCondition, paraName, conditionValue  in worksetRules:
        collectorGrids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid).Where(lambda e: rGrid.GridCheckParameterValue(e, paraName, paraCondition, conditionValue))
        grids = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorGrids, 'grids')
        gridsResults.Update(grids)
    return gridsResults


def ModifyGridsWorksets(doc, revitFileName, worksetRules):
    '''
    Modifies worksets of grids as per workset rules
    rules format:
    defaultWorksetRulesAll_ = [
        ['model name',[
            [ModifyGridWorkSetsDefault,[
                ['default workset name'] # there should only be one per model
                ]
            ]
            ]
        ]
    ]
    :param doc: _description_
    :type doc: _type_
    :param revitFileName: _description_
    :type revitFileName: _type_
    :param worksetRules: _description_
    :type worksetRules: _type_
    :return: returns a result object
    :rtype: _type_
    '''

    gridsResults = res.Result()
    foundMatch = False
    for fileName, worksetModifierList in worksetRules:
        if (revitFileName.startswith(fileName)):
            foundMatch = True
            for worksetModifier, rules in worksetModifierList:
                grids = worksetModifier(doc, rules)
                gridsResults.Update(grids)
            break
    if foundMatch == False:
        gridsResults.UpdateSep(False, 'No grid rules found for file: ' + revitFileName)
    return gridsResults