"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit generic annotation helper functions.
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

from duHast.Revit.Common import parameter_get_utils as rParaGet

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------------------------- utility functions ------------------

# returns all  GenericAnnotation types in a model
# doc:   current model document
def get_all_generic_annotation_types_by_category(doc):
    """
    This will return a filtered element collector of all GenericAnnotation types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_GenericAnnotation)
        .WhereElementIsElementType()
    )
    return collector


# returns all  GenericAnnotation types in a model
# doc:   current model document
def get_all_generic_annotation_type_ids_by_category(doc):
    """
    This will return a list of all GenericAnnotation types (symbols) id's in the model excluding shared families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = get_all_generic_annotation_types_by_category(doc)
    for c in col:
        parameter_match = False
        # get the family object to check whether it is a shared family
        fam = c.Family
        id = rParaGet.get_built_in_parameter_value(
            fam, rdb.BuiltInParameter.FAMILY_SHARED
        )
        if id != None:
            parameter_match = True
            if id == "No" and c.Id not in ids:
                ids.append(c.Id)
        if parameter_match == False:
            # family cant be of type shared...
            ids.append(c.Id)
    return ids
