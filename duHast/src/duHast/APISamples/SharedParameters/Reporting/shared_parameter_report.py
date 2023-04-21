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
from duHast.APISamples.SharedParameters.shared_parameters import get_all_shared_parameters, param_binding_exists


def get_shared_parameter_report_data(doc, revit_file_path):
    '''
    Gets shared parameter data ready for being printed to file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The file hostname, which is added to data returned.
    :type revit_file_path: str
    :return: list of list of parameter properties.
    :rtype: list of list of str
    '''

    data = []
    paras = get_all_shared_parameters(doc)
    for p in paras:
        parameter_definition = p.GetDefinition()
        parameter_bindings = []
        # parameter bindings do not exist in a family document
        if(doc.IsFamilyDocument == False):
            parameter_bindings = param_binding_exists(doc, rdb.Element.Name.GetValue(p), parameter_definition.ParameterType)

        # just in case parameter name is not unicode
        parameter_name = 'unknown'
        try:
            parameter_name = util.EncodeAscii(rdb.Element.Name.GetValue(p))
        except Exception as ex:
            parameter_name = 'Exception: ' + str(ex)
        # build data
        data.append([
            revit_file_path,
            p.GuidValue.ToString(),
            str(p.Id.IntegerValue),
            parameter_name,
            str(parameter_bindings)
            ])
    return data