"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit line line styles helper functions. 
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

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

import Autodesk.Revit.DB as rdb
from duHast.Revit.Common import delete as rDel


def delete_line_styles_starts_with(doc, starts_with):
    """
    Deletes all line styles where the name starts with provided string
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param starts_with: Filter: style name needs to start with this string to be deleted.
    :type starts_with: str
    :return:
        Result class instance.
        - .result = True if all views where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    """

    lc = doc.Settings.Categories[rdb.BuiltInCategory.OST_Lines]
    ids = list(c.Id for c in lc.SubCategories if c.Name.StartsWith(starts_with)).ToList[
        rdb.ElementId
    ]()
    result = rDel.delete_by_element_ids(
        doc,
        ids,
        "Delete line styles where name starts with: " + str(starts_with),
        "line styles starting with: " + str(starts_with),
    )
    return result


def get_all_line_style_ids(doc):
    """
    Gets all line styles ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of all line style ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    lc = doc.Settings.Categories[rdb.BuiltInCategory.OST_Lines]
    ids = list(c.Id for c in lc.SubCategories).ToList[rdb.ElementId]()
    return ids
