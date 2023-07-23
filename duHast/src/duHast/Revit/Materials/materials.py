"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit materials helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

import clr
import System

# import common library modules

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------------------------- utility functions ------------------


def get_all_materials(doc):
    """
    Gets all materials in a model.

    Filter by class.

    :param doc: _description_
    :type doc: _type_

    :return: A filtered element collector of materials
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.Material)
    return collector


def get_material_by_id(doc, id):
    """
    Gets a material element based on a material id.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param id: The id of material to be returned.
    :type id: Autodesk.Revit.DB.ElementId

    :return: A material if matching id was found. Otherwise nothing gets returned!
    :rtype: Autodesk.Revit.DB.Material
    """

    mats = get_all_materials(doc)
    for m in mats:
        if m.Id.IntegerValue == id.IntegerValue:
            return m


def get_material_name_by_id(doc, id):
    """
    Gets a material name based on a material id.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param id: Id of material of which the name is to be returned.
    :type id: Autodesk.Revit.DB.ElementId

    :return: The material name if matching id was found or the default value: '<By Category>'
    :rtype: str
    """

    name = "<By Category>"
    mats = get_all_materials(doc)
    for m in mats:
        if m.Id.IntegerValue == id.IntegerValue:
            m_name = rdb.Element.Name.GetValue(m)
            name = "" if m_name == None else m_name
    return name
