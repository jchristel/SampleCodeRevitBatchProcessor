"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit grids workset modifier functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from Autodesk.Revit.DB import FilteredElementCollector, Grid

from duHast.Utilities.Objects import result as res
from duHast.Revit.Common import worksets as rWork
from duHast.Revit.Grids import grids as rGrid


def modify_grid_worksets_default(doc, worksetRules):
    """
    Workset modifier method. Moves all grids to one workset.

    Rules format:

    ['Model name', [[workset modifier method,[worksetName]]]]

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :param worksetRules: The workset rules in the specified format.
    :type worksetRules: List

    :return: A result object.
    :rtype: Type
    """

    gridsResults = res.Result()
    collectorGrids = FilteredElementCollector(doc).OfClass(Grid)
    for rule in worksetRules:
        for defaultWorksetName in rule:
            grids = rWork.modify_element_workset(
                doc, defaultWorksetName, collectorGrids, "grids"
            )
            gridsResults.update(grids)
    return gridsResults


def modify_grid_worksets_by_type_name(doc, worksetRules):
    """
    Workset modifier method. Moves grids matching a type condition to a particular workset.

    Default workset type rules example:

    [['model name', [[ModifyGridWorkSetsByTypeName, [['workset name', util.ConDoesNotEqual, 'grid type name'],['workset name', util.ConDoesEqual, 'grid type name']]]]]]

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :param worksetRules: The workset rules in the specified format.
    :type worksetRules: List

    :return: A result object.
    :rtype: Type
    """

    gridsResults = res.Result()
    # loop over grid type filter and address one at the time
    # get all grids matching type name filter
    for (
        defaultWorksetName,
        typeNameCondition,
        typeName,
    ) in worksetRules:
        # get the grid type id from the type name
        typeId = rGrid.get_grid_type_id_by_name(doc, typeName)
        collectorGrids = (
            FilteredElementCollector(doc)
            .OfClass(Grid)
            .Where(lambda e: typeNameCondition(e.GetTypeId(), typeId))
        )
        grids = rWork.modify_element_workset(
            doc, defaultWorksetName, collectorGrids, "grids"
        )
        gridsResults.update(grids)
    return gridsResults


def modify_grid_worksets_by_parameter_value(doc, worksetRules):
    """
    Workset modifier method. Moves grids matching parameter condition to a particular workset

    Default workset type rules example:

    [['model name', [[ModifyGridWorkSetsByParameterValue, [['workset name', util.ConTwoStartWithOne, 'Name', 'name starts with value']]]]]]

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param worksetRules: _description_
    :type worksetRules: _type_

    :return: returns a result object
    :rtype: _type_
    """

    gridsResults = res.Result()
    # loop over grid parameter filter and address one at the time
    # get all grids matching filter
    for defaultWorksetName, paraCondition, paraName, conditionValue in worksetRules:
        collectorGrids = (
            FilteredElementCollector(doc)
            .OfClass(Grid)
            .Where(
                lambda e: rGrid.grid_check_parameter_value(
                    e, paraName, paraCondition, conditionValue
                )
            )
        )
        grids = rWork.modify_element_workset(
            doc, defaultWorksetName, collectorGrids, "grids"
        )
        gridsResults.update(grids)
    return gridsResults


def modify_grids_worksets(doc, revitFileName, worksetRules):
    """
    Modifies worksets of grids as per workset rules format.

    Default workset type rules example:

    [['model name', [[ModifyGridWorkSetsDefault, [['default workset name']  # There should only be one per model]]]]]

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFileName: _description_
    :type revitFileName: _type_
    :param worksetRules: _description_
    :type worksetRules: _type_

    :return: returns a result object
    :return: Result class instance.

        - result.status: View deletion status returned in result.status. False if an exception occurred, otherwise True.
        - result.message: will contain the fully qualified file path of the exported file
        - result.result: will be an empty list

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    """

    gridsResults = res.Result()
    foundMatch = False
    for fileName, worksetModifierList in worksetRules:
        if revitFileName.startswith(fileName):
            foundMatch = True
            for worksetModifier, rules in worksetModifierList:
                grids = worksetModifier(doc, rules)
                gridsResults.update(grids)
            break
    if foundMatch == False:
        gridsResults.update_sep(False, "No grid rules found for file: " + revitFileName)
    return gridsResults
