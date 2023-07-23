"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit shared parameters.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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
from duHast.Revit.Common.revit_version import get_revit_version_number

# import Autodesk
import Autodesk.Revit.DB as rdb


# --------------------------------------------- utility functions ------------------


def get_all_shared_parameters(doc):
    """
    Gets all shared parameters in a model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing shared parameter elements
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.SharedParameterElement)
    return collector


def get_family_shared_parameters(doc):
    """
    Gets all family parameters which are shared parameters.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :raises Exception: "Document is not a family document." when a non family document is past in.

    :return: A list of family parameters
    :rtype: [Autodesk.Revit.DB.FamilyParameter]
    """

    if doc.IsFamilyDocument:
        fam_manager = doc.FamilyManager
        shared_fam_paras = []
        for fam_para in fam_manager.GetParameters():
            try:
                # only shared parameters hav .GUID property...
                if str(fam_para.GUID) != "":
                    shared_fam_paras.append(fam_para)
            except Exception as e:
                pass
    else:
        raise Exception("Document is not a family document.")
    return shared_fam_paras


def get_family_parameters(doc):
    """
    Gets all family parameters.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :raises Exception: "Document is not a family document." when a non family document is past in.

    :return: A list of family parameters
    :rtype: [Autodesk.Revit.DB.FamilyParameter]
    """

    if doc.IsFamilyDocument:
        fam_manager = doc.FamilyManager
        shared_fam_paras = []
        for fam_para in fam_manager.GetParameters():
            shared_fam_paras.append(fam_para)
    else:
        raise Exception("Document is not a family document.")
    return shared_fam_paras


# ------------------------------------------------------- parameter utilities --------------------------------------------------------------------


def check_whether_shared_parameters_are_in_file(doc, parameter_gui_ds):
    """
    Filters the past in list of shared parameter GUIDs by using the shared parameters in the document.
        Only parameter in both will be returned.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameter_gui_ds: list of shared parameter GUIDs as string values
    :type parameter_gui_ds: list str

    :return: list of shared parameter GUIDs as string values
    :rtype: list str
    """

    filtered_gui_ds = []
    paras = get_all_shared_parameters(doc)
    for p in paras:
        if p.GuidValue.ToString() in parameter_gui_ds:
            filtered_gui_ds.append(p.GuidValue.ToString())
    return filtered_gui_ds


def check_whether_shared_parameters_by_name_is_family_parameter(doc, parameter_name):
    """
    Checks, by name, whether a shared parameter exists as a family parameter in a family.

    param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameter_name: The name of the parameter.
    :type parameter_name: str

    :return: A family parameter if match was found, otherwise None
    :rtype: Autodesk.Revit.DB.FamilyParameter
    """

    para = None
    paras = get_family_parameters(doc)
    for fam_para in paras:
        if fam_para.Definition.Name == parameter_name:
            try:
                # only shared parameters hav .GUID property...
                if str(fam_para.GUID) != "":
                    para = fam_para
                    break
            except Exception as e:
                pass
    return para


def is_shared_parameter_definition_used(doc, shared_para):
    """
    Tests if a shared parameter GUID is used by a family parameter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param shared_para: A shared parameter
    :type shared_para: Autodesk.Revit.DB.SharedParameterElement

    :return: True is match is found, otherwise False
    :rtype: bool
    """

    fam_shared_paras = get_family_shared_parameters(doc)
    match = False
    for fam_shared_para in fam_shared_paras:
        if fam_shared_para.GUID == shared_para.GuidValue:
            match = True
            break
    return match


def get_unused_shared_parameter_definitions(doc):
    """
    Returns all unused shard parameter definitions in a family document.

    Note: These shared parameters might be used in any nested family!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of shared parameters
    :rtype: [Autodesk.Revit.DB.SharedParameterElement]
    """

    fam_shared_paras = get_family_shared_parameters(doc)
    shared_paras = get_all_shared_parameters(doc)
    unused_shared_parameter_definition = []
    for shared_para in shared_paras:
        match = False
        for fam_shared_para in fam_shared_paras:
            if fam_shared_para.GUID == shared_para.GuidValue:
                match = True
                break
        if match == False:
            unused_shared_parameter_definition.append(shared_para)
    return unused_shared_parameter_definition


def get_shared_parameter_definition(parameter_name, def_file):
    """
    Returns a shared parameter definition from a shared parameter file.

    :param parameter_name: The shared parameter name.
    :type parameter_name: str
    :param def_file: The shared parameter file definition.
    :type def_file: Autodesk.Revit.DB.DefinitionFile

    :return: The shared parameter definition. None if no parameter with a matching name was found.
    :rtype: Autodesk.Revit.DB.ExternalDefinition
    """

    parameter_definition = None
    try:
        # loop through parameters and try to find matching one
        # loop through all definition groups
        for group in def_file.Groups:
            # loop through para's within definition group
            for def_para in group.Definitions:
                # check whether this is the parameter we are after
                if def_para.Name == parameter_name:
                    # match and out
                    parameter_definition = def_para
                    break
            if parameter_definition != None:
                break
    except Exception as e:
        pass
    return parameter_definition


# ------------------------------------------------------- parameter reporting --------------------------------------------------------------------


def param_binding_exists(doc, param_name, param_type):
    """
    Gets all parameter bindings for a given parameter depending on revit version.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param param_name: The name of the parameter.
    :type param_name: str
    :param param_type: The parameter type. (Area, vs text vs... (deprecated in Revit 2022!)
    :type param_type: Autodesk.Revit.DB.ParameterType

    :return: List of categories a parameter is attached to.
    :rtype: list of str
    """

    revit_version = get_revit_version_number(doc)
    data = []
    if revit_version <= 2022:
        data = param_binding_exists_2022(
            doc=doc, param_name=param_name, param_type=param_type
        )
    else:
        data = param_binding_exists_2023(
            doc=doc, param_name=param_name, type_id=param_type
        )
    return data


def param_binding_exists_2022(doc, param_name, param_type):
    """
    Gets all parameter bindings for a given parameter fro Revit versions up to 2022.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param param_name: The name of the parameter.
    :type param_name: str
    :param param_type: The parameter type. (Area, vs text vs... (deprecated in Revit 2022!)
    :type param_type: Autodesk.Revit.DB.ParameterType

    :return: List of categories a parameter is attached to.
    :rtype: list of str
    """

    categories = []
    map = doc.ParameterBindings
    iterator = map.ForwardIterator()
    iterator.Reset()
    while iterator.MoveNext():
        if (
            iterator.Key != None
            and iterator.Key.Name == param_name
            and iterator.Key.ParameterType == param_type
        ):
            elem_bind = iterator.Current
            for cat in elem_bind.Categories:
                categories.append(cat.Name)
            break
    return categories


def param_binding_exists_2023(doc, param_name, type_id):
    """
    Gets all parameter bindings for a given parameter for Revit 2023 onwards

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param param_name: The name of the parameter.
    :type param_name: str
    :param type_id: Forge type id
    :type type_id: Autodesk.Revit.DB.ForgeTypeId

    :return: List of categories a parameter is attached to.
    :rtype: list of str
    """

    categories = []
    map = doc.ParameterBindings
    iterator = map.ForwardIterator()
    iterator.Reset()
    while iterator.MoveNext():
        if (
            iterator.Key != None
            and iterator.Key.Name == param_name
            and iterator.Key.GetDataType() == type_id
        ):
            elem_bind = iterator.Current
            for cat in elem_bind.Categories:
                categories.append(cat.Name)
            break
    return categories
