from duHast.Revit.Warnings.Objects.warinings_overlap_storage import RevitWarningOverlap
from duHast.Revit.Warnings.warnings import get_warnings_by_guid
from duHast.Revit.Common.Geometry.curve import (
    is_curve_is_within_curve,
    calculate_lengthened_curve_geometry,
    calculate_shortened_curve_geometry,
)
from duHast.Revit.Common.delete import delete_by_element_ids
from duHast.Revit.Common.transaction import in_transaction
from duHast.Utilities.Objects import result as res

from Autodesk.Revit.DB import Transaction


def get_curves_from_failure_messages(doc, failure_messages):
    """
    Loops over failure messages and extracts separation lines listed. There are always two curves per exception, even if one curve overlaps a number of other curves.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param failure_messages: List of failure messages relating to separation lines overlap
    :type failure_messages: [Autodesk.Revit.DB.FailureMessage]
    :return: List of RevitWarningOverlap instances.
    :rtype: [:class:RevitWarningOverlap]
    """

    revit_warnings_overlap_storage = []
    for f_message in failure_messages:
        ids = f_message.GetFailingElements()
        if len(ids) > 2:
            raise ValueError(
                "Revit separation line warning contains more then 2 associated elements."
            )
        lines_by_exception = []
        for id in ids:
            room_sep_line = doc.GetElement(id)
            curve = room_sep_line.GeometryCurve
            group_id = room_sep_line.GroupId.IntegerValue
            dummy = RevitWarningOverlap(
                id=id, element=room_sep_line, curve=curve, group_id=group_id
            )
            lines_by_exception.append(dummy)
        revit_warnings_overlap_storage.append(lines_by_exception)
    return revit_warnings_overlap_storage


def check_curves_overlaps(curves):
    """
    loop over curves per exception and determine which one can be deleted because
    its either completely within of of the other curves listed in the revit warning, or is identical to one of the other curves listed in the revit warning

    Returns a list of RevitWarningOverlap instance which contain separation lines which can be deleted.
    ( Note there might be multiple instances of the same separation line! )
    """
    curves_to_delete = []
    # a curve set should always contain 2 curves
    for curve_set in curves:
        if len(curve_set) == 2:
            if curve_set[0].group_id == curve_set[1].group_id:
                curve_to_delete = is_curve_is_within_curve(curve_set[0], curve_set[1])
                if curve_to_delete:
                    curves_to_delete.append(curve_to_delete)
            else:
                curves_to_delete.append(None)
        else:
            raise ValueError("Curve set does not have a length of 2")
    return curves_to_delete


def identify_curve_in_set_to_amend(curve_set):
    """
    Returns two lists:
    First one contains separation lines to change the geometry of
    second one contains separation lines to delete
    """

    curves_to_delete = []
    curves_to_amend = []
    if len(curve_set) == 2:
        if curve_set[0].group_id == curve_set[1].group_id:
            curve_to_change, curve_to_delete = calculate_lengthened_curve_geometry(
                curve_set[0], curve_set[1]
            )
            if curve_to_delete:
                curves_to_delete.append(curve_to_delete)
            if curve_to_change:
                curves_to_amend.append(curve_to_change)
        else:
            return None, None
    else:
        raise ValueError("Curve set does not have a length of 2")
    return curves_to_amend, curves_to_delete


def delete_curves(doc, curves_to_delete):
    return_value = res.Result()
    # get unique ids for deletion
    if len(curves_to_delete) > 0:
        ids = []
        for c in curves_to_delete:
            if c and c.id not in ids:
                ids.append(c.id)

        # bombs away...
        result_delete = delete_by_element_ids(
            doc=doc,
            ids=ids,
            transaction_name="delete overlapping room separation lines".format(
                len(ids)
            ),
            element_name="room separation line(s)",
        )
        return_value.update(result_delete)
    else:
        return_value.update_sep(True, "No curves where required to be deleted.")
    return return_value


def modify_separation_lines(doc, curves, transaction_manager=in_transaction):
    return_value = res.Result()
    for curve in curves:
        if curve:

            def action():
                action_return_value = res.Result()
                try:
                    # make sure to set this to True, otherwise adjoining room separation lines will change as well
                    curve.element.SetGeometryCurve(curve.new_curve, True)
                    action_return_value.update_sep(
                        True,
                        "Successfully change geometry of element: {}".format(curve.id),
                    )
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "Failed to change geometry of element {} with exception: {}".format(
                            curve.id, e
                        ),
                    )
                return action_return_value

            transaction = Transaction(
                doc, "Updating separation line geometry: {}".format(curve.id)
            )
            update_curve_geometry = transaction_manager(transaction, action, doc)
            # update_sep_geo = in_transaction(transaction, action)
            return_value.update(update_curve_geometry)
    return return_value


def modify_curves_by_lengthening(doc, guid, transaction_manager):
    return_value = res.Result()
    # maximum number of loops
    max_loop = len(get_warnings_by_guid(doc, guid=guid))
    return_value.append_message("Found {} warnings...".format(max_loop))
    ignore_these_curves = {}
    counter = 0
    loop_flag = True
    while loop_flag:
        # start again, this time to change curve geometry
        failure_messages = get_warnings_by_guid(doc, guid=guid)
        return_value.append_message(
            "Found {} failure messages in loop {}.".format(
                len(failure_messages), counter
            )
        )
        # check if anything is left
        if len(failure_messages) == len(ignore_these_curves):
            return_value.append_message("Finished processing warnings.")
            loop_flag = False
        else:
            # get next curve sets from failure message
            warning_curve_sets = get_curves_from_failure_messages(doc, failure_messages)
            for failure_set in warning_curve_sets:
                # check if needs to be ignored ( already tried to process before )
                if (
                    hash(failure_set[0]) + hash(failure_set[1])
                    not in ignore_these_curves
                ):
                    (
                        curves_to_change,
                        curves_to_delete,
                    ) = identify_curve_in_set_to_amend(failure_set)
                    if curves_to_change == None and curves_to_delete == None:
                        return_value.append_message(
                            "Neither curve {} {} in exception set could be amended...".format(
                                failure_set[0].id, failure_set[1].id
                            )
                        )
                        # make sure to flag this set as not to be processed again
                        ignore_these_curves[
                            hash(failure_set[0]) + hash(failure_set[1])
                        ] = failure_set
                    else:
                        # check if any curves to change came back
                        if curves_to_change:
                            return_value.append_message(
                                "Found a curve: {} to amend".format(
                                    curves_to_change[0].id
                                )
                            )
                            # amend curves first....
                            status_update = modify_separation_lines(
                                doc=doc,
                                curves=curves_to_change,
                                transaction_manager=transaction_manager,
                            )
                            return_value.update(status_update)
                        # check if anything needs deleting
                        if curves_to_delete:
                            # delete the now overlapping curves
                            status_delete = delete_curves(doc, curves_to_delete)
                            return_value.update(status_delete)
                # get out of loop and start again by getting the current set of warnings from the model
                break
        counter = counter + 1
        if max_loop == counter:
            return_value.append_message("Reached maximum loop counter.")
            loop_flag = False
    return return_value
