"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing NWC export functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#

# --------------------------
# Imports
# --------------------------


from duHast.Revit.Exports.export_navis import (
    setup_nwc_default_export_option_shared_by_view,
    export_3d_views_to_nwc,
)
from duHast.Utilities.Objects import result as res


def set_up_nwc_default_export_option():
    """
    Return an NWC Export Options object with shared coordinates, export by View as provided in the generic library

    :return: _description_
    :rtype: _type_
    """
    return setup_nwc_default_export_option_shared_by_view()


def export_views_to_nwc(doc, export_view_prefix, export_directory, view_name_modifier):
    """
    Exports 3D views to nwc where the view name has a particular prefix.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: _description_
    :rtype: _type_
    """

    return_value = res.Result()
    nwc_export_option = set_up_nwc_default_export_option()
    return_value = export_3d_views_to_nwc(
        doc,
        export_view_prefix,
        nwc_export_option,
        export_directory,
        do_something_with_view_name=view_name_modifier,
    )
    return return_value
