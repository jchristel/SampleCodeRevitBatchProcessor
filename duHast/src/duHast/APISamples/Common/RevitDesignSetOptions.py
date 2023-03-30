'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit Design Sets and Design Options.
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

import clr
import System

# import common library modules
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet


# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_DESIGNSET_HEADER = ['HOSTFILE','ID', 'NAME', 'PRIMARY OPTION', 'OTHER OPTIONS']

# --------------------------------------------- utility functions ------------------

def GetDesignOptions(doc):
    '''
    Gets all design options in a model,

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Design options in current model
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.DesignOption)
    return collector

def GetDesignSets(doc):
    '''
    Gets all the design sets in a model,

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Design sets in the current model
    :rtype: list of Autodesk.Revit.DB.Element
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.DesignOption)
    designSets = []
    designSetNames = []
    for do in collector:
        e = doc.GetElement(do.get_Parameter(rdb.BuiltInParameter.OPTION_SET_ID).AsElementId())
        designSetName = rdb.Element.Name.GetValue(e)
        if(designSetName not in designSetNames):
            designSets.append(e)
            designSetNames.append(designSetName)
    return designSets

def IsDesignOptionPrimary(doc, designSetName, designOptionName):
    '''
    Checks whether a design option is the primary option within a design set.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param designSetName: The name of the design set the option belongs to,
    :type designSetName: str
    :param designOptionName: The name of the design option to be checked,
    :type designOptionName: str
    :return: True if this option is primary otherwise False
    :rtype: bool
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.DesignOption)
    isPrimary = False
    # loop over all design options in model, get the set they belong to and check for matches on both, set and option, by name
    for do in collector:
        designOName = rdb.Element.Name.GetValue(do)
        # check if '< 'in name indicating a primary option, if so remove from name
        index_chevron = designOName.find('<')
        if (index_chevron > 0):
            designOName = designOName[:index_chevron-2]
        # design set
        design_set = doc.GetElement(do.get_Parameter(rdb.BuiltInParameter.OPTION_SET_ID).AsElementId())
        design_set_name = rdb.Element.Name.GetValue(design_set)
        # check for match on both set and option
        if(design_set_name == designSetName and designOName == designOptionName):
            # get isPrimary property on design option
            isPrimary = do.IsPrimary
            break
    return isPrimary

def GetDesignSetOptionInfo(doc, element):
    '''
    Get the design set, design option information of an element.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: The element of which the design set/option data is to be returned.
    :type element: Autodesk.Revit.DB.Element
    :return: Dictionary
        Design Set Name: (can be either Main Model or the design set name)
        designOptionName:    Design Option Name (empty string if Main Model
        isPrimary:           Indicating whether design option is primary (true also if Main Model)
    :rtype: Dictionary
        designSetName:str
        designOptionName:str
        isPrimary:bool
    '''

    # keys match properties in DataDesignSetOption class!!
    new_key= ['designSetName','designOptionName','isPrimary']
    new_value= ['Main Model','-',True]
    dic = dict(zip(new_key,new_value))
    # get design option data from element
    pValue = rParaGet.get_built_in_parameter_value(element, rdb.BuiltInParameter.DESIGN_OPTION_PARAM)
    if(pValue != None):
        designOptionData = pValue.split(':')
        # check if main model ( length is 1! )
        if(len(designOptionData) > 1):
            dic['designSetName'] = designOptionData[0].Trim()
            dic['designOptionName'] = designOptionData[1].Trim()
            dic['isPrimary'] = IsDesignOptionPrimary(doc, dic['designSetName'], dic['designOptionName'])
        else:
            # use default values
            pass
    return dic
