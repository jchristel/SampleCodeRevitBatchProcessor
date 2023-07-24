"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Category override data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

import json
from duHast.Revit.Views.Objects.override_by_category import OverrideByCategory
from duHast.Revit.Views.Objects.override_by_filter import OverrideByFilter
from duHast.Revit.Views.Objects.view_graphics_settings import ViewGraphicsSettings


def _get_model_overrides(view):
    pass


def _get_filter_overrides(view):
    pass


def convert_revit_view_to_data(doc, view):
    """
    Convertes a Revit view element into an instance of class ViewGraphicsSettings

    :param view: A Revit view instance.
    :type view: Autodesk.Revit.DB.View
    :return: A storage class which contains graphics settings
    :rtype: :class:`.ViewGraphicsSettings`
    """

    data_dic = {}

    data_dic[OverrideByCategory.data_type] = _get_model_overrides(view)
    data_dic[OverrideByFilter.data_type] = _get_filter_overrides(view)

    return_value = ViewGraphicsSettings(
        view_name=view.Name,
        view_id=view.Id.IntegerValue,
        j=data_dic,
    )

    return return_value
 