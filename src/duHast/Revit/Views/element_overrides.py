"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to by element in view overrides. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling

from Autodesk.Revit.DB import Document, OverrideGraphicSettings, Transaction, View


def overwrite_element_graphics_in_view(
    doc, view, elements, override_graphics_settings=None
):
    """
    Overwrite the graphics of elements in a view.

    Note:
    If None is passed as the override_graphics_settings parameter, the default settings will be used to remove any overrides on the elements.

    :param doc: The Revit document.
    :type doc: Document
    :param view: The view in which the elements are located.
    :type view: View
    :param elements: The elements to overwrite the graphics for.
    :type elements: list
    :param override_graphics_settings: The override settings to apply to the elements.
    :type override_graphics_settings: Autodesk.Revit.DB.OverrideGraphicSettings

    :return: A result object.
    :rtype: Result
    """

    # set up a default return value object
    return_value = Result()

    try:
        # do some type checking
        if (doc is None) or (view is None) or (elements is None):
            return_value.update_sep(
                False,
                "Failed to override elements in view. One or more required parameters are None.",
            )
            return return_value

        if len(elements) == 0:
            return_value.update_sep(
                False,
                "Failed to override elements in view. The elements list is empty.",
            )
            return return_value

        if not isinstance(elements, list):
            return_value.update_sep(
                False,
                "Failed to override elements in view. The elements parameter is not a list.",
            )
            return return_value

        if not isinstance(view, View):
            return_value.update_sep(
                False,
                "Failed to override elements in view. The view parameter is not a View.",
            )
            return return_value

        if not isinstance(doc, Document):
            return_value.update_sep(
                False,
                "Failed to override elements in view. The doc parameter is not a Document.",
            )
            return return_value

        if override_graphics_settings is not None and not isinstance(
            override_graphics_settings, OverrideGraphicSettings
        ):
            return_value.update_sep(
                False,
                "Failed to override elements in view. The override_graphics_settings parameter is not None and not  an OverrideGraphicSettings object.",
            )
            return return_value

        # set up a default override settings object
        override_settings = OverrideGraphicSettings()
        if override_graphics_settings is not None:
            # set up the override settings object with the provided settings
            override_settings = override_graphics_settings

        # override the graphics for each element
        for element in elements:

            def action():
                action_return_value = Result()
                try:
                    view.SetElementOverrides(element.Id, override_settings)
                    action_return_value.append_message(
                        "Successfully overrode graphics for element: {}.".format(
                            element.Id
                        )
                    )
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "Failed to override graphics for element: {}. Error: {}".format(
                            element.Id, e
                        ),
                    )
                return action_return_value

            tranny = Transaction(doc, "Override Graphics")
            tranny_result = in_transaction_with_failure_handling(
                transaction=tranny, action=action
            )
            return_value.update(tranny_result)
    except Exception as e:
        return_value.update_sep(
            False, "Failed to override elements in view with exception: {}".format(e)
        )
    return return_value
