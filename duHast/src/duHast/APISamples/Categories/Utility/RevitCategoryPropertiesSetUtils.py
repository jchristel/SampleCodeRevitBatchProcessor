'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit sub-category property set functions .
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

from duHast.APISamples.LinePattern import RevitLineStylesPatterns as rPat
from duHast.APISamples.Common import RevitTransaction as rTran
from duHast.Utilities import Result as res
from duHast.APISamples.Categories.Utility.RevitCategoryPropertyNames import PROPERTY_LINE_COLOUR_BLUE_NAME, PROPERTY_LINE_COLOUR_GREEN_NAME, PROPERTY_LINE_COLOUR_RED_NAME, PROPERTY_LINE_WEIGHT_CUT_NAME, PROPERTY_LINE_WEIGHT_PROJECTION_NAME, PROPERTY_MATERIAL_ID
from duHast.APISamples.Categories.Utility.RevitCategoryPropertiesGetUtils import get_saved_category_property_by_name


def set_category_material(doc, cat, materialId):
    '''
    Updates material property of a given category.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param materialId: The new material element id.
    :type materialId: Autodesk.Revit.DB.ElementId
    :return: True if material property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        mat = doc.GetElement(materialId)
        def action():
            actionReturnValue = res.Result()
            try:
                cat.Material = mat
                actionReturnValue.UpdateSep(True, 'Successfully set material value of subcategory')
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to set material value of subcategory with exception: {}'.format(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,'Updating subcategory material: ' + str(rdb.Element.Name.GetValue(mat)))
        updateMat = rTran.in_transaction(transaction, action)
        flag = updateMat.status
    except Exception as e:
        flag = False
    return flag


def set_category_line_pattern(doc, cat, linePatternId, ignoreMissingCutStyle):
    '''
    Updates line pattern property of a given category.
    Note: in cases where the 'cut' property does not exist on a sub category this will return false even though the 'projection' property will most
    likely have been updated without a problem...
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param materialId: The new material element id.
    :type materialId: Autodesk.Revit.DB.ElementId
    :param ignoreMissingCutStyle: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignoreMissingCutStyle: bool
    :return: True if line pattern property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        def action():
            actionReturnValue = res.Result()
            try:
                cat.SetLinePatternId(linePatternId, rdb.GraphicsStyleType.Cut)
                actionReturnValue.UpdateSep(True, 'Successfully set cut line pattern of subcategory')
            except Exception as e:
                if(ignoreMissingCutStyle):
                    actionReturnValue.UpdateSep(True, 'Failed to set cut line pattern of subcategory with exception: {}. Exception ignored!'.format(e))
                else:
                    actionReturnValue.UpdateSep(False, 'Failed to set cut line pattern of subcategory with exception: {}'.format(e))
            try:
                cat.SetLinePatternId(linePatternId, rdb.GraphicsStyleType.Projection)
                actionReturnValue.UpdateSep(True, 'Successfully set projection line pattern of subcategory')
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to set projection line pattern of subcategory with exception: {}'.format(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,'Updating subcategory line pattern')
        updateLinePattern = rTran.in_transaction(transaction, action)
        flag = updateLinePattern.status
    except Exception as e:
        flag = False
    return flag


def set_category_line_weights(doc, cat, lineThickNessCut, lineThicknessProjection, ignoreMissingCutStyle):
    '''
    Updates line weight properties of a given category.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param lineThickNessCut: The cut line weight.
    :type lineThickNessCut: int
    :param lineThicknessProjection: The projection line weight.
    :type lineThicknessProjection: int
    :param ignoreMissingCutStyle: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignoreMissingCutStyle: bool
    :return: True if line weight property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        def action():
            actionReturnValue = res.Result()
            try:
                cat.SetLineWeight(lineThickNessCut, rdb.GraphicsStyleType.Cut)
                actionReturnValue.UpdateSep(True, 'Successfully set cut line weight of subcategory')
            except Exception as e:
                if(ignoreMissingCutStyle):
                    actionReturnValue.UpdateSep(True, 'Failed to set cut line weight of subcategory with exception: {}. Exception ignored!'.format(e))
                else:
                    actionReturnValue.UpdateSep(False, 'Failed to set cut line weight of subcategory with exception: {}'.format(e))
            try:
                cat.SetLineWeight(lineThicknessProjection, rdb.GraphicsStyleType.Projection)
                actionReturnValue.UpdateSep(True, 'Successfully set projection line weight of subcategory')
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to set projection line weight of subcategory with exception: {}'.format(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,'Updating subcategory line weights')
        updateLineWeights = rTran.in_transaction(transaction, action)
        flag = updateLineWeights.status
    except Exception as e:
        flag = False
    return flag


def set_category_colour(doc, cat, red, green, blue):
    '''
    Updates colour properties of a given category.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param red: The colour red channel.
    :type red: byte
    :param green: The colour green channel.
    :type green: byte
    :param blue: The colour blue channel.
    :type blue: byte
    :return: True if colour property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        def action():
            actionReturnValue = res.Result()
            try:
                newColour = rdb.Color(red, green, blue)
                cat.LineColor = newColour
                actionReturnValue.UpdateSep(True, 'Successfully set colour value of subcategory')
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to set colour value of subcategory with exception: {}'.format(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,'Updating subcategory colour')
        updateColour = rTran.in_transaction(transaction, action)
        flag = updateColour.status
    except Exception as e:
        flag = False
    return flag


def set_category_properties(doc, cat, properties, ignoreMissingCutStyle):
    '''
    Updates varies property values of a given category.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param properties: List of property values to be applied to category.
    :type properties: list of dictionaries in format as per GetCategoryProperties(cat) method.
    :param ignoreMissingCutStyle: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignoreMissingCutStyle: bool
    :return: True if all properties where updated successfully, otherwise False.
    :rtype: bool
    '''

    # material
    matId = get_saved_category_property_by_name(properties, [PROPERTY_MATERIAL_ID])
    flagMat = set_category_material(doc, cat, matId[0])

    # line pattern
    linePatternId = get_saved_category_property_by_name(properties, [rPat.PROPERTY_PATTERN_ID])
    flagPattern = set_category_line_pattern(doc, cat, linePatternId[0], ignoreMissingCutStyle)

    # line weights
    lineWeights = get_saved_category_property_by_name(properties, [PROPERTY_LINE_WEIGHT_CUT_NAME, PROPERTY_LINE_WEIGHT_PROJECTION_NAME])
    flagLineWeights = set_category_line_weights(doc, cat, lineWeights[0], lineWeights[1], ignoreMissingCutStyle)

    # category colour
    colourRGB = get_saved_category_property_by_name(properties, [PROPERTY_LINE_COLOUR_RED_NAME, PROPERTY_LINE_COLOUR_GREEN_NAME, PROPERTY_LINE_COLOUR_BLUE_NAME])
    flagColours = set_category_colour(doc, cat, colourRGB[0], colourRGB[1], colourRGB[2])

    return flagMat & flagPattern & flagLineWeights & flagColours