"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit filter overrides in views. 
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
import clr
import System

# import common library modules
from duHast.Revit.Views.Objects.filter_override_storage import RevitFilterOverride
from duHast.Revit.Views.filters import get_all_filters, is_filter_applied_to_view
from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Views.filters import VIEW_TYPE_WHICH_CAN_HAVE_FILTERS

# from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities.Objects import result as res

# import Autodesk
from Autodesk.Revit.DB import Transaction

# --------------------------- view filters --------------------------------


def get_filters_from_model(doc):
    """
    Retrieves all filters in a Revit model and stores them in a dictionary.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing the filters in the model as RevitFilterOverride objects. The keys of the dictionary are the filter names.
    :rtype: {str: :class:`.RevitFilterOverride`}
    """
    filters_dic = {}

    # get all filters in the model
    filters_in_model = get_all_filters(doc)
    for f in filters_in_model:
        filters_dic["{}".format(f.Name)] = RevitFilterOverride(
            filter_name=f.Name,
            filter=f,
            filter_id=f.Id,
            filter_override=None,
            is_filter_enabled=True,
            is_filter_visible=False,
        )

    return filters_dic


def update_filter_override_from_view(view, filter_storage_instance):
    """
    Populates the filter_override and is_filter_visible and is_filter_enabled field of a 'RevitFilterOverride' instance based on the view past in.

    :param view: The view from which the filter override is to be used.
    :type view: Autodesk.Revit.DB.View
    :param filter_storage_instance: An instances of revit filter storage containing no view specific information.
    :type filter_storage_instance: :class:`.RevitFilterOverride`

    :return: An updated instances of revit filter storage now containing the override, filter visibility and filter enabled flags.
    :rtype: :class:`.RevitFilterOverride`
    """

    filter_storage_instance.revit_override = view.GetFilterOverrides(
        filter_storage_instance.filter_id
    )
    filter_storage_instance.is_filter_visible = view.GetFilterVisibility(
        filter_storage_instance.filter_id
    )
    filter_storage_instance.is_filter_enabled = view.GetIsFilterEnabled(
        filter_storage_instance.filter_id
    )

    return filter_storage_instance


def get_filter_overrides_from_view(view, filter_storage_instances):
    """
    Populates the category_override and is_category_hidden fields of a list of 'category_storage' instances based on the view past in.

    :param view: The view from which the category override is to be used.
    :type view: Autodesk.Revit.DB.View
    :param filter_storage_instances: A list of instances of class 'RevitFilterOverride'
    :type filter_storage_instances: [:class:`.RevitFilterOverride`]

    :return: A list of instances of class 'RevitFilterOverride' where the override, filter visibility and filter enabled flags have been updated dependent on the view.
    :rtype: [:class:`.RevitFilterOverride`]
    """

    updated_filter_storage_instances = []
    for filter_storage_instance in filter_storage_instances:
        updated_filter_instance = update_filter_override_from_view(
            view, filter_storage_instance
        )
        updated_filter_storage_instances.append(updated_filter_instance)
    return updated_filter_storage_instances


def apply_filter_override_to_view(
    doc, view, filter_storage_instances, add_filter_if_not_present=True
):
    """
    Applies filter override(s) to a single view

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view on which the category override is to be used.
    :type view: Autodesk.Revit.DB.View
    :param filter_storage_instances: A list of storage class instances.
    :type filter_storage_instances: [:class:`.RevitFilterOverride`]

    :return:
        Result class instance.

        - Apply override status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message 'Successfully set category override...' for each override applied.
        - result.result will be an empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    for filter_storage_instance in filter_storage_instances:

        def action():
            action_return_value = res.Result()
            try:
                # check if filter is present
                if (
                    is_filter_applied_to_view(
                        view=view, filter=filter_storage_instance.filter
                    )
                    == False
                ):
                    # do we need to add it? ( if yes the below code will do that automatically)
                    if add_filter_if_not_present == False:
                        # nothing to do ... move on
                        action_return_value.update_sep(
                            True,
                            "Filter {} is not applied to view {}. Skipping".format(
                                filter_storage_instance.filter_name, view.Name
                            ),
                        )
                        return action_return_value

                # this appears to add the filter if not present...
                view.SetFilterOverrides(
                    filter_storage_instance.filter_id,
                    filter_storage_instance.revit_override,
                )
                action_return_value.update_sep(
                    True,
                    "Successfully set filter override {} in view {} ".format(
                        filter_storage_instance.filter_name,
                        view.Name,
                    ),
                )
                # filter visibility
                view.SetFilterVisibility(
                    filter_storage_instance.filter_id,
                    filter_storage_instance.is_filter_visible,
                )
                action_return_value.update_sep(
                    True,
                    "Successfully set filter visibility status {} in view {} to: {}".format(
                        filter_storage_instance.filter_name,
                        view.Name,
                        filter_storage_instance.is_filter_visible,
                    ),
                )

                # filter enabled
                view.SetIsFilterEnabled(
                    filter_storage_instance.filter_id,
                    filter_storage_instance.is_filter_enabled,
                )
                action_return_value.update_sep(
                    True,
                    "Successfully set filter enabled status {} in view {} to: {}".format(
                        filter_storage_instance.filter_name,
                        view.Name,
                        filter_storage_instance.is_filter_enabled,
                    ),
                )

            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to set filter override : {} to view: {} with exception: {}".format(
                        filter_storage_instance.filter_name,
                        view.Name,
                        e,
                    ),
                )
            return action_return_value

        transaction = Transaction(
            doc,
            "Updating filter override {}".format(
                filter_storage_instance.filter_name,
            ),
        )
        update_category_override = in_transaction(transaction, action)
        return_value.update(update_category_override)

    return return_value


def view_has_filter(view, filter_to_check_id):
    """
    Checks if a specific filter is applied to a given view.

    :param view: The view object to check for applied filters.
    :type view: Autodesk.Revit.DB.View
    :param filter_to_check_id: The ID of the filter to check if it is applied.
    :type filter_to_check_id: Autodesk.Revit.DB.ElementId

    :return: A boolean value indicating whether the specified filter is applied to the view.
    :rtype: bool
    """
    filter_is_applied = False
    filters_applied_to_view_as_ids = view.GetFilters()
    if filter_to_check_id in filters_applied_to_view_as_ids:
        filter_is_applied = True
    return filter_is_applied


def add_filter_to_view(doc, filter, view):
    """
    Adds a filter to a view in Autodesk Revit.

    :param doc: The current model document in Autodesk Revit.
    :type doc: Autodesk.Revit.DB.Document
    :param filter: The filter to be added to the view.
    :type filter: Autodesk.Revit.DB.ParameterFilterElement
    :param view: The view to which the filter will be added.
    :type view: Autodesk.Revit.DB.View

    :return: An instance of the Result class that contains the result of the filter addition. The result attribute is True if the filter was added successfully, otherwise False. The message attribute contains additional information about the result.
    :rtype: :class:`.Result`
    """
    return_value = res.Result()

    def action():
        action_return_value = res.Result()
        try:
            view.AddFilter(filter.id)
            return_value.append_message(
                "Filter: {} added to view: {} successfully.".format(
                    filter.Name, view.Name
                )
            )
        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to apply filter: {} to view: {} with exception: {}".format(
                    filter.Name,
                    view.Name,
                    e,
                ),
            )
        return action_return_value

    transaction = Transaction(
        doc,
        "Adding filter: {} to view: {}".format(
            filter.Name,
            view.Name,
        ),
    )
    add_filter_status = in_transaction(transaction, action)
    return_value.update(add_filter_status)
    return return_value


def remove_filter_from_view(doc, filter, view):
    """
    Removes a filter from a view.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filter: The filter to be removed from the view.
    :type filter: Autodesk.Revit.DB.ParameterFilterElement
    :param view: The view (can be a view template too!)
    :type view: Autodesk.Revit.DB.View
    :return:
        Result class instance.

        - .result True if filter was removed successfully or if filter was not applied or if view does not support filters, otherwise False
        - .message will contain deletion status.
        - . result (empty list)

        on exception:

        - .result Will be False
        - .message will contain exception message.
        - . result (empty list)

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    if view.ViewType in VIEW_TYPE_WHICH_CAN_HAVE_FILTERS:
        filters_applied = view.GetFilters()
        if filter.Id in filters_applied:

            def action():
                action_return_value = res.Result()
                try:
                    view.RemoveFilter(filter.Id)
                    action_return_value.update_sep(
                        True,
                        "Remove filter: {} from template: {}".format(
                            filter.Name, view.Name
                        ),
                    )
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "Failed to remove filter: {} from template: {} with exception: {}".format(
                            filter.Name, view.Name, e
                        ),
                    )
                return action_return_value

            transaction = Transaction(doc, "Removing filter: {}".format(filter.Name))
            # execute the transaction
            return_value = in_transaction(transaction, action)
        else:
            return_value.update_sep(
                True,
                "Filter: {} is not applied to view template: {}".format(
                    filter.Name, view.Name
                ),
            )
    else:
        return_value.update_sep(
            True,
            "View template: {} if of type: {} which does not support filters.".format(
                view.Name, view.ViewType
            ),
        )
    return return_value
