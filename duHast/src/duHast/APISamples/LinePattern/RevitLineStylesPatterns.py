'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit line styles and line patterns helper functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
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

import clr
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)
import System

# import common library modules
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities import Result as res


# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------------PATTERN PROPERTIES ------------

#: pattern name
PROPERTY_PATTERN_NAME = 'PatternName'
#: pattern name default value, hard coded solid line pattern name
PROPERTY_PATTERN_NAME_VALUE_DEFAULT = 'Solid'
#: pattern id
PROPERTY_PATTERN_ID = 'PatternId'

def GetLinePatternFromCategory(cat, doc):
    '''
    Returns the line pattern properties as a dictionary\
         where keys are pattern name and pattern id.

    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: str, str: Autodesk.Revit.DB.ElementId}
    '''

    dicPattern = {}
    dicPattern[PROPERTY_PATTERN_NAME] = PROPERTY_PATTERN_NAME_VALUE_DEFAULT
    dicPattern[PROPERTY_PATTERN_ID] = patternId = cat.GetLinePatternId(rdb.GraphicsStyleType.Projection)
    '''check for 'solid' pattern which apparently is not a pattern at all
    *The RevitAPI.chm documents says: Note that Solid is special. It isn't a line pattern at all -- 
    * it is a special code that tells drawing and export code to use solid lines rather than patterned lines. 
    * Solid is visible to the user when selecting line patterns. 
    '''
    if(patternId != rdb.LinePatternElement.GetSolidPatternId()):
        # not a solid line pattern
        collector = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement)
        linePatternElement = None
        for c in collector:
            if(patternId == c.Id):
                dicPattern[PROPERTY_PATTERN_NAME] = rdb.Element.Name.GetValue(c)         
    return dicPattern

def GetLinePatternFromLevelElement(doc, level):
    '''
    Returns the line pattern properties as a dictionary\
         where keys are pattern name and pattern id.

    :param doc: Current Revit family document.
    :type doc: Current Revit family document.
    :param level: a level element
    :type level: Autodesk.Revit.DB.Level

    :return: A dictionary.
    :rtype: dictionary {str: str, str: Autodesk.Revit.DB.ElementId}
    '''

    dicPattern = {}
    dicPattern[PROPERTY_PATTERN_NAME] = PROPERTY_PATTERN_NAME_VALUE_DEFAULT
    dicPattern[PROPERTY_PATTERN_ID] = rdb.ElementId.InvalidElementId
    try:
        lTypeId = level.GetTypeId()
        levelType = doc.GetElement(lTypeId)
        linePatternIdString = rParaGet.get_built_in_parameter_value(levelType, rdb.BuiltInParameter.LINE_PATTERN)
        dicPattern[PROPERTY_PATTERN_ID] = rdb.ElementId(int(linePatternIdString))
        dicPattern[PROPERTY_PATTERN_NAME] = rdb.Element.Name.GetValue(levelType)
    except Exception as ex:
        dicPattern[PROPERTY_PATTERN_NAME] = str(ex)
    return dicPattern

# ------------------------------------------------ DELETE LINE PATTERNS ----------------------------------------------

def DeleteLinePatternsContains(doc, contains):
    '''
    Deletes all line patterns where the names contains a provided string

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param contains: Filter: pattern name needs to contain this string to be deleted.
    :type contains: str

    :return: 
        Result class instance.
           
        - .result = True if line pattern where deleted successfully. Otherwise False.
        - .message will contain delete status per pattern.

    :rtype: :class:`.Result`
    '''

    lps = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement).ToList()
    ids = list(lp.Id for lp in lps if lp.GetLinePattern().Name.Contains(contains)).ToList[rdb.ElementId]()
    result = com.DeleteByElementIds(doc,ids, 'Deleting line patterns where name contains: ' + str(contains),'line patterns containing: ' + str(contains))
    return result

def DeleteLinePatternStartsWith(doc, startsWith):
    '''
    Deletes all line patterns where the name starts with provided string.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param startsWith: Filter: pattern name needs to start with this string to be deleted.
    :type startsWith: str

    :return: 
        Result class instance.

        - .result = True if line pattern where deleted successfully. Otherwise False.
        - .message will contain delete status per pattern.

    :rtype: :class:`.Result`
    '''

    lps = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement).ToList()
    ids = list(lp.Id for lp in lps if lp.GetLinePattern().Name.StartsWith(startsWith)).ToList[rdb.ElementId]()
    result = com.DeleteByElementIds(doc,ids, 'Delete line patterns where name starts with: ' + str(startsWith),'line patterns starting with: ' + str(startsWith))
    return result

def DeleteLinePatternsWithout(doc, contains):
    '''
    Deletes all line patterns where the name does not contain the provided string.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param contains: Filter: pattern name needs not to contain this string to be deleted.
    :type contains: str

    :return: 
        Result class instance.

        - .result = True if line pattern where deleted successfully. Otherwise False.
        - .message will contain delete status per pattern.

    :rtype: :class:`.Result`
    '''

    lps = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement).ToList()
    ids = list(lp.Id for lp in lps).ToList[rdb.ElementId]()
    idsContain = list(lp.Id for lp in lps if lp.GetLinePattern().Name.Contains(contains)).ToList[rdb.ElementId]()
    deleteIds = list(set(ids)-set(idsContain))
    result = com.DeleteByElementIds(doc,deleteIds, 'Delete line patterns where name does not contain: ' + str(contains),'line patterns without: ' + str(contains))
    return result

def GetAllLinePatterns(doc):
    '''
    Gets all line patterns in the model.

    :param doc: _description_
    :type doc: _type_

    :return: List of all line pattern elements in model.
    :rtype: list of Autodesk.Revit.DB.LinePatternElement
    '''
    return rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement).ToList()

def BuildPatternsDictionaryByName(doc):
    '''
    Returns a dictionary where line pattern name is key, values are all ids of line patterns with the exact same name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where line pattern name is key, values are all ids of line patterns with the exact same name
    :rtype: dictionary(key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    lpDic = {}
    lps = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement)
    for lp in lps:
        if(lpDic.has_key(lp.GetLinePattern().Name)):
            lpDic[lp.GetLinePattern().Name].append(lp.Id)
        else:
            lpDic[lp.GetLinePattern().Name] = [lp.Id]
    return lpDic

def DeleteDuplicatLinePatterNames(doc):
    '''
    Deletes all but the first line pattern by Id with the exact same name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - .result = True if all views where deleted. Otherwise False.
        - .message will contain deletion status.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    returnValue.AppendMessage('Deletes all but the first line pattern by Id with the exact same name...start')
    # get a dictionary: Key pattern name, value all ids of line patterns with the same name
    # anything where the value list is greater then 1 means duplicates of the same name...
    linePatterns = BuildPatternsDictionaryByName(doc)
    for key, value in linePatterns.items():
        if(len(value) > 1):
            # keep the first one (original)
            value.remove(value[0])
            flagDelete = com.DeleteByElementIds(doc,value, 'Deleting duplicate line patterns names: ' + str(key),'line patterns duplicates: ' + str(key))
            returnValue.Update (flagDelete)
    return returnValue

# ------------------------------------------------ DELETE LINE STYLES ----------------------------------------------

def DeleteLineStylesStartsWith(doc, startsWith):
    '''
    Deletes all line styles where the name starts with provided string

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param startsWith: Filter: style name needs to start with this string to be deleted.
    :type startsWith: str

    :return: 
        Result class instance.

        - .result = True if all views where deleted. Otherwise False.
        - .message will contain deletion status.

    :rtype: :class:`.Result`
    '''

    lc = doc.Settings.Categories[rdb.BuiltInCategory.OST_Lines]
    ids = list(c.Id for c in lc.SubCategories if c.Name.StartsWith(startsWith)).ToList[rdb.ElementId]()
    result = com.DeleteByElementIds(doc,ids, 'Delete line styles where name starts with: ' + str(startsWith),'line styles starting with: ' + str(startsWith))
    return result

def GetAllLineStyleIds(doc):
    '''
    Gets all line styles ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of all line style ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    lc = doc.Settings.Categories[rdb.BuiltInCategory.OST_Lines]
    ids = list(c.Id for c in lc.SubCategories).ToList[rdb.ElementId]()
    return ids

# ------------------------------------------------ Fill Patterns ----------------------------------------------

def GetAllFillPattern(doc):
    '''
    Gets all fill pattern element ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of all fill pattern elements.
    :rtype: list of Autodesk.Revit.DB.FillPatternElement
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.FillPatternElement).ToList()
