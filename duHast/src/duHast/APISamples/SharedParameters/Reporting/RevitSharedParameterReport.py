'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the hRevit shared parameter report functionality.
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
from duHast.APISamples.SharedParameters.RevitSharedParameters import GetAllSharedParameters, ParamBindingExists


def GetSharedParameterReportData(doc, revitFilePath):
    '''
    Gets shared parameter data ready for being printed to file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str
    :return: list of list of parameter properties.
    :rtype: list of list of str
    '''

    data = []
    paras = GetAllSharedParameters(doc)
    for p in paras:
        parameterDefinition = p.GetDefinition()
        parameterBindings = []
        # parameter bindings do not exist in a family document
        if(doc.IsFamilyDocument == False):
            parameterBindings = ParamBindingExists(doc, rdb.Element.Name.GetValue(p), parameterDefinition.ParameterType)

        # just in case parameter name is not unicode
        parameterName = 'unknown'
        try:
            parameterName = util.EncodeAscii(rdb.Element.Name.GetValue(p))
        except Exception as ex:
            parameterName = 'Exception: ' + str(ex)
        # build data
        data.append([
            revitFilePath,
            p.GuidValue.ToString(),
            str(p.Id.IntegerValue),
            parameterName,
            str(parameterBindings)
            ])
    return data