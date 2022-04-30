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

# doc   current document
def GetDesignOptions(doc):
    '''
    returns a collector containing all design options in a model
    '''
    collector = FilteredElementCollector(doc).OfClass(DesignOption)
    return collector

# doc   current document
def GetDesignSets(doc):
    '''
    returns a list of all the design sets in a model
    '''
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

# doc                 current document
# designSetName       the name (string) of the design set the option belongs to
# designOptionName    the name (string) of the design option to be checked
def IsDesignOptionPrimary(doc, designSetName, designOptionName):
    '''
    returns bool if design option is primary
    '''
    collector = FilteredElementCollector(doc).OfClass(DesignOption)
    isPrimary = False
    # loop over all design options in model, get the set they belong to and check for matches on both, set and option, by name
    for do in collector:
        designOName = Element.Name.GetValue(do)
        # check if primray in name if so remove...( this is language agnostic!!!!!)
        if (designOName.endswith(' (primary)')):
            designOName = designOName[:-len(' (primary)')]
        # design set
        e = doc.GetElement(do.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId())
        designSName = Element.Name.GetValue(e)
        # check for match on both set and option
        if(designSName == designSetName and designOName == designOptionName):
            # get isPriamry property on design option
            isPrimary = do.IsPrimary
            break
    return isPrimary

# doc   current document
# element   the element of which thes desin set/option  data is to be returned
def GetDesignSetOptionInfo(doc, element):
    '''
    returns dictionary: 
    designSetName       Design Set Name (can be either Main Model or the design set name)
    designOptionName    Design Option Name (empty string if Main Model
    isPrimary           Bool indicating whether design option is primary (true also if Main Model)
    '''
    # keys match properties in DataDesignSetOption class!!
    new_key= ['designSetName','designOptionName','isPrimary']
    new_value= ['Main Model','-',True]
    dic = dict(zip(new_key,new_value))
    # get design option data from element
    pValue = com.GetBuiltInParameterValue(element, BuiltInParameter.DESIGN_OPTION_PARAM)
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
