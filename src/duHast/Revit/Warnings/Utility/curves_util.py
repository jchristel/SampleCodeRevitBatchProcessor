from duHast.Revit.Warnings.Objects.warnings_overlap_storage import RevitWarningOverlap
from duHast.Revit.Warnings.warnings import get_warnings_by_guid
from duHast.Revit.Common.Geometry.curve import (
    is_curve_is_within_curve,
    calculate_lengthened_curve_geometry,
    calculate_shortened_curve_geometry,
)
from duHast.Revit.Common.delete import delete_by_element_ids
from duHast.Revit.Common.transaction import in_transaction
from duHast.Utilities.Objects import result as res

from Autodesk.Revit.DB import Document, Transaction


def get_curves_from_failure_messages(doc, failure_messages):
    """
    Loops over failure messages and extracts separation lines listed. There are always two curves per exception, even if one curve overlaps a number of other curves.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param failure_messages: List of failure messages relating to separation lines overlap
    :type failure_messages: [Autodesk.Revit.DB.FailureMessage]
    :return: List of RevitWarningOverlap instances.
    :rtype: [:class:`RevitWarningOverlap`]
    """

    if not isinstance(doc, Document):
        raise TypeError("doc must be an instance of Autodesk.Revit.DB.Document")
    if not isinstance(failure_messages, list):
        raise TypeError("failure_messages must be a list")

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
    Check a list of curve sets for overlaps or duplicates.


    :param curves: A list of curve sets, where each set contains two curves.
    :type  curves: [:class: `RevitWarningOverlap`]

    Returns:
        list: A list of curves that can be deleted because they are either completely within another curve or identical to another curve.

    Raises:
        ValueError: If a curve set does not have a length of 2.

    Example:
        curves = [[curve1, curve2], [curve3, curve4], ...]
        result = check_curves_overlaps(curves)
        print(result)
    """

    if not isinstance(check_curves_overlaps, list):
        raise TypeError("check_curves_overlaps must be a list")

    curves_to_delete = []
    # a curve set should always contain 2 curves
    for curve_set in curves:
        if len(curve_set) == 2:
            # Both curves need to be either in the main model ( group id of -1) or in the same group
            # alternatively the curve to be deleted is in the main model (group id of -1). The other curve can be in a group.
            curve_to_delete = is_curve_is_within_curve(curve_set[0], curve_set[1])
            if curve_to_delete:
                if curve_set[0].group_id == curve_set[1].group_id or curves_to_delete.group_id == -1:
                    curves_to_delete.append(curve_to_delete)
            '''
            if curve_set[0].group_id == curve_set[1].group_id:
                curve_to_delete = is_curve_is_within_curve(curve_set[0], curve_set[1])
                if curve_to_delete:
                    curves_to_delete.append(curve_to_delete)
            else:
                curves_to_delete.append(None)
            '''
        else:
            raise ValueError("Curve set does not have a length of 2")
    return curves_to_delete


def _identify_curve_in_set_to_amend_lengthening(curve_set):
    """
    Returns two lists:
    First one contains curves to change the geometry of
    Second one contains curves to delete

    :param curve_set: A set of curves that needs to be analyzed and identified for amendment
    :type curve_set: [:class: `RevitWarningOverlap`]
    :return: A tuple containing two lists - curves_to_amend and curves_to_delete
    :rtype: tuple
    :raises ValueError: If the length of curve_set is not equal to 2
    """

    if not isinstance(curve_set, list):
        raise TypeError("curve_set must be a list")

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
    """
    Deletes curves in a Revit model.

    :param doc: The Revit model document.
    :type doc:  (Autodesk.Revit.DB.Document)
    :param curves_to_delete: List of curves to be deleted.
    :type curves_to_delete: [:class: `RevitWarningOverlap`]

    Returns:
        res.Result: A res.Result object that contains the status of the deletion operation.
    """

    if not isinstance(doc, Document):
        raise TypeError("doc must be an instance of Autodesk.Revit.DB.Document")
    if not isinstance(curves_to_delete, list):
        raise TypeError("curves_to_delete must be a list")

    return_value = res.Result()
    # get unique ids for deletion
    if len(curves_to_delete) > 0:
        ids = [
            c.id for c in curves_to_delete if c and c.id is not None and c.id not in ids
        ]

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


def _modify_separation_lines(doc, curves, transaction_manager=in_transaction):
    """
    Modify the geometry of separation lines in a Revit model.

    :param doc: The Revit model document.
    :type doc:  (Autodesk.Revit.DB.Document)
    :param curves: List of curves to be deleted.
    :type curves: [:class: `RevitWarningOverlap`]
    :param  transaction_manager:  An optional transaction manager function used to perform the modifications.
    :type  transaction_manager: (function, optional)

    Returns:
        res.Result: A `res.Result` object that contains the status of the modifications performed for each curve.
    """

    if not isinstance(doc, Document):
        raise TypeError("doc must be an instance of Autodesk.Revit.DB.Document")
    if not isinstance(curves, list):
        raise TypeError("curves must be a list")

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
    """
    Modifies curves in a Revit model by lengthening them.

    :param doc: The Revit model document.
    :type doc:  (Autodesk.Revit.DB.Document)
    :param guid: The GUID used to filter the failure messages.
    :type guid: (Autodesk.Revit.DB.Guid):
    :param transaction_manager: The transaction manager used to perform the modifications.
    :type transaction_manager: (function)

    Returns:
        res.Result: A `res.Result` object that contains the status of the modifications performed.
    """

    if not isinstance(doc, Document):
        raise TypeError("doc must be an instance of Autodesk.Revit.DB.Document")

    return_value = res.Result()
    # maximum number of loops
    max_loop = len(get_warnings_by_guid(doc, guid=guid))
    if max_loop is not None and max_loop > 0:
        return_value.append_message("Found {} warnings...".format(max_loop))
        ignore_these_curves = []
        counter = 0
        for i in range(max_loop):
            # start again, this time to change curve geometry
            failure_messages = get_warnings_by_guid(doc, guid=guid)
            return_value.append_message(
                "Found {} failure messages in loop {}.".format(
                    len(failure_messages), counter
                )
            )
            # check if anything is left to process
            if len(failure_messages) == len(ignore_these_curves):
                return_value.append_message("Finished processing warnings.")
                break
            else:
                # get next curve sets from failure message
                warning_curve_sets = get_curves_from_failure_messages(
                    doc, failure_messages
                )
                for failure_set in warning_curve_sets:
                    # check if needs to be ignored ( already tried to process before )
                    curve_identifier = (failure_set[0].id, failure_set[1].id)
                    if curve_identifier not in ignore_these_curves:
                        (
                            curves_to_change,
                            curves_to_delete,
                        ) = _identify_curve_in_set_to_amend_lengthening(failure_set)
                        if curves_to_change == None and curves_to_delete == None:
                            return_value.append_message(
                                "Neither curve {} {} in exception set could be amended...".format(
                                    failure_set[0].id, failure_set[1].id
                                )
                            )
                            # make sure to flag this set as not to be processed again
                            ignore_these_curves.append(curve_identifier)
                        else:
                            # check if any curves to change came back
                            if curves_to_change:
                                return_value.append_message(
                                    "Found a curve: {} to amend".format(
                                        curves_to_change[0].id
                                    )
                                )
                                # amend curves first....
                                status_update = _modify_separation_lines(
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
    else:
        return_value.append_message(
            "No overlap warnings with guid: {} in model.".format(guid)
        )
    return return_value


def _identify_curves_to_amend_short(curves):
    """
    Returns one lists  contains separation lines to change the geometry of
    """
    curves_to_amend = []
    for curve_set in curves:
        if len(curve_set) == 2:
            if curve_set[0].group_id == curve_set[1].group_id:
                curve_to_change = calculate_shortened_curve_geometry(
                    curve_set[0], curve_set[1]
                )
                if curve_to_change:
                    curves_to_amend.append(curve_to_change)
            else:
                curves_to_amend.append(None)
        else:
            raise ValueError("Curve set does not have a length of 2")
    return curves_to_amend


def modify_curves_by_shortening(doc, guid, transaction_manager):
    """
    Modifies curves in a Revit model by lengthening them.

    :param doc: The Revit model document.
    :type doc:  (Autodesk.Revit.DB.Document)
    :param guid: The GUID used to filter the failure messages.
    :type guid: (Autodesk.Revit.DB.Guid):
    :param transaction_manager: The transaction manager used to perform the modifications.
    :type transaction_manager: (function)

    Returns:
        res.Result: A `res.Result` object that contains the status of the modifications performed.
    """

    if not isinstance(doc, Document):
        raise TypeError("doc must be an instance of Autodesk.Revit.DB.Document")

    return_value = res.Result()
    # start again, this time to change curve geometry
    failure_messages = get_warnings_by_guid(doc, guid=guid)
    if failure_messages is not None and len(failure_messages) > 0:
        return_value.append_message(
            "Found {} warnings...".format(len(failure_messages))
        )
        lines_ex = get_curves_from_failure_messages(doc, failure_messages)
        curves_to_change = _identify_curves_to_amend_short(lines_ex)
        # amend curves first....
        status_update = _modify_separation_lines(
            doc=doc,
            curves=curves_to_change,
            transaction_manager=transaction_manager,
        )
        return_value.update(status_update)
    else:
        return_value.append_message(
            "No overlap warnings with guid: {} in model.".format(guid)
        )
    return return_value
