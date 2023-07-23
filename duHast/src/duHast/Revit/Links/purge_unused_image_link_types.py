"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging unused image links.
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

from duHast.Revit.Common import common as com
from duHast.Revit.Links.image_links import (
    get_image_instances_in_model,
    get_image_types_in_model,
)


def get_all_unused_image_type_ids_in_model(doc):
    """
    Gets all image types with no instances placed in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    unused_images = com.get_not_placed_types(
        doc, get_image_types_in_model, get_image_instances_in_model
    )
    unused_type_ids = []
    for i in unused_images:
        unused_type_ids.append(i.Id)
    return unused_type_ids


def get_all_unused_image_type_ids_in_model_with_group_check(doc):
    """
    Gets all image types with no instance placed in a model but includes group definition check.
    This only returns valid data if at least one instance of the group is placed in the model!!
    Otherwise images in groups which are not placed will not be flagged by this filter!
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    unused_type_ids = get_all_unused_image_type_ids_in_model(doc)
    # and filter by any type id's in groups which may not be placed and hence no instance present in the model
    unused_type_ids = com.get_unused_type_ids_from_detail_groups(doc, unused_type_ids)
    return unused_type_ids
