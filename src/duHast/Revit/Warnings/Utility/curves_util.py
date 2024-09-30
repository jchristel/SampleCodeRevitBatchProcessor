from duHast.Revit.Warnings.Objects.warnings_overlap_storage import RevitWarningOverlap
from duHast.Revit.Warnings.warnings import get_warnings_by_guid
from duHast.Revit.Common.Geometry.curve import (
    is_curve_is_within_curve,
    calculate_lengthened_curve_geometry,
    calculate_shortened_curve_geometry,
)
from duHast.Revit.Common.groups import get_model_group_instances_by_type
from duHast.Revit.Common.delete import delete_by_element_ids
from duHast.Revit.Common.transaction import in_transaction
from duHast.Utilities.Objects import result as res

from Autodesk.Revit.DB import (
    BuiltInCategory,
    Category,
    Document,
    ElementId,
    Transaction,
    ModelLine,
)


def get_curves_from_failure_messages(doc, failure_messages, group_id):
    """
    Loops over failure messages and extracts separation lines listed.
    There are always two curves per exception, even if one curve overlaps a number of other curves.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param failure_messages: List of failure messages relating to separation lines overlap
    :type failure_messages: [Autodesk.Revit.DB.FailureMessage]
    :param group_id: group id curves need to belong to for processing (-1 not in a group)
    :type group_id: int
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
        # area line overlap warnings are also covering other overlap warnings which have more then 2 elements
        # check that elements involved are ModelLines ( room sep, area sep)
        # TODO: use builtincategory instead! OST_AreaPolylines, OST_RoomPolylines
        if len(ids) == 2:
            lines_by_exception = []
            are_matching_group_id = True
            for id in ids:
                sep_line = doc.GetElement(id)
                cat = sep_line.Category
                if (
                    cat.Name
                    == Category.GetCategory(
                        doc, BuiltInCategory.OST_AreaSchemeLines
                    ).Name
                    or cat.Name
                    == Category.GetCategory(
                        doc, BuiltInCategory.OST_RoomSeparationLines
                    ).Name
                ):
                    curve = sep_line.GeometryCurve
                    group_id_curve = sep_line.GroupId.IntegerValue
                    if group_id_curve != group_id:
                        are_matching_group_id = False

                    design_option_id = -1
                    if sep_line.DesignOption:
                        design_option_id = sep_line.DesignOption.Id

                    created_phase_id = sep_line.CreatedPhaseId
                    demolished_phase_id = sep_line.DemolishedPhaseId

                    dummy = RevitWarningOverlap(
                        id=id,
                        element=sep_line,
                        curve=curve,
                        group_id=group_id_curve,
                        design_option_id=design_option_id,
                        created_phase_id=created_phase_id,
                        demolished_phase_id=demolished_phase_id,
                    )
                    lines_by_exception.append(dummy)

            # only add warnings if both elements belong to the same group (or both are not in a group)
            # if elements are of type model line ( if not lines_by_exception will be empty )
            if are_matching_group_id and len(lines_by_exception) == 2:
                revit_warnings_overlap_storage.append(lines_by_exception)

    return revit_warnings_overlap_storage


def check_curves_overlaps(curves, group_id):
    """
    Check a list of curve sets for overlaps or duplicates.


    :param curves: A list of curve sets, where each set contains two curves.
    :type  curves: [:class: `RevitWarningOverlap`]
    :param group_id: group id curves need to belong to for processing (-1 not in a group)
    :type group_id: int

    Returns:
        list: A list of curves that can be deleted because they are either completely within another curve or identical to another curve.

    Raises:
        ValueError: If a curve set does not have a length of 2.

    Example:
        curves = [[curve1, curve2], [curve3, curve4], ...]
        result = check_curves_overlaps(curves)
        print(result)
    """

    if not isinstance(curves, list):
        raise TypeError("curves must be a list")
    if not isinstance(group_id, int):
        raise TypeError("group_id must be an instance of integer")

    curves_to_delete = []
    # a curve set should always contain 2 curves
    for curve_set in curves:
        if len(curve_set) == 2:
            # currently only works when separation lines are outside a group..
            # if inside a group the lines get excluded from a group but not actually deleted

            curve_to_delete = is_curve_is_within_curve(curve_set[0], curve_set[1])
            # can anything be deleted?
            # need to be in main model, same design option, same phase created and demoed
            if curve_to_delete:
                if (
                    curve_to_delete.group_id == group_id
                    and curve_set[0].design_option_id == curve_set[1].design_option_id
                    and curve_set[0].phase_created_id == curve_set[1].phase_created_id
                    and curve_set[0].phase_demolished_id
                    == curve_set[1].phase_demolished_id
                ):
                    # check if the curve to be deleted is in the main model
                    curves_to_delete.append(curve_to_delete)
        else:
            raise ValueError("Curve set does not have a length of 2")
    return curves_to_delete


def _identify_curve_in_set_to_amend_lengthening(curve_set, group_id):
    """
    Returns two lists:
    First one contains curves to change the geometry of
    Second one contains curves to delete

    :param curve_set: A set of curves that needs to be analyzed and identified for amendment
    :type curve_set: [:class: `RevitWarningOverlap`]
    :return: A tuple containing two lists - curves_to_amend and curves_to_delete
    :param group_id: group id curves need to belong to for processing (-1 not in a group)
    :type group_id: int
    :rtype: tuple
    :raises ValueError: If the length of curve_set is not equal to 2
    """

    if not isinstance(curve_set, list):
        raise TypeError("curve_set must be a list")
    if not isinstance(group_id, int):
        raise TypeError("group_id must be an instance of integer")

    curves_to_delete = []
    curves_to_amend = []

    if len(curve_set) == 2:
        # calculate changes
        curve_to_change, curve_to_delete = calculate_lengthened_curve_geometry(
            curve_set[0], curve_set[1]
        )

        # check whether changes can be executed
        # need to be in main model, same design option, same phase created and demoed
        if (
            curve_to_delete
            and curve_to_change
            and curve_to_delete.group_id == group_id
            and curve_to_change.group_id == group_id
            and curve_set[0].design_option_id == curve_set[1].design_option_id
            and curve_set[0].phase_created_id == curve_set[1].phase_created_id
            and curve_set[0].phase_demolished_id == curve_set[1].phase_demolished_id
        ):
            # check if the curve to be deleted is in the main model, that there us a curve to lengthen and its also in main model
            curves_to_delete.append(curve_to_delete)
            curves_to_amend.append(curve_to_change)
        else:
            return None, None
    else:
        raise ValueError("Curve set does not have a length of 2")

    return curves_to_amend, curves_to_delete


def delete_curves(doc, curves_to_delete, curve_descriptor):
    """
    Deletes curves in a Revit model.

    :param doc: The Revit model document.
    :type doc:  (Autodesk.Revit.DB.Document)
    :param curves_to_delete: List of curves to be deleted.
    :type curves_to_delete: [:class: `RevitWarningOverlap`]
    :param curve_descriptor: line type descriptor
    :type curve_descriptor: str

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
        # need to declare ids first ....
        ids = []
        # populate ids
        ids = [
            c.id for c in curves_to_delete if c and c.id is not None and c.id not in ids
        ]

        # bombs away...
        result_delete = delete_by_element_ids(
            doc=doc,
            ids=ids,
            transaction_name="delete overlapping {}: {}".format(
                curve_descriptor, len(ids)
            ),
            element_name="{}".format(curve_descriptor),
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
            update_curve_geometry = transaction_manager(transaction, action)
            # update_sep_geo = in_transaction(transaction, action)
            return_value.update(update_curve_geometry)
    return return_value


def modify_curves_by_lengthening(doc, guid, transaction_manager, group_id, callback):
    """
    Modifies curves in a Revit model by lengthening them.

    :param doc: The Revit model document.
    :type doc:  (Autodesk.Revit.DB.Document)
    :param guid: The GUID used to filter the failure messages.
    :type guid: (Autodesk.Revit.DB.Guid):
    :param transaction_manager: The transaction manager used to perform the modifications.
    :type transaction_manager: (function)
    :param group_id: group id curves need to belong to for processing (-1 not in a group)
    :type group_id: int
    :param callback: function reporting progress update.
    :type callback: func (value, maximum_value)

    Returns:
        res.Result: A `res.Result` object that contains the status of the modifications performed.
    """

    if not isinstance(doc, Document):
        raise TypeError("doc must be an instance of Autodesk.Revit.DB.Document")
    if not isinstance(group_id, int):
        raise TypeError("group_id must be an instance of integer")

    return_value = res.Result()
    failure_messages = get_warnings_by_guid(doc, guid=guid)
    # get curve sets from failure message with matching group id
    warning_curve_sets = get_curves_from_failure_messages(
        doc=doc,
        failure_messages=failure_messages,
        group_id=group_id,
    )

    # maximum number of loops
    max_loop = len(warning_curve_sets)
    if max_loop > 0:
        return_value.append_message(
            "Found {} warnings matching group id: {}".format(max_loop, group_id)
        )

        ignore_these_curves = []
        for i in range(max_loop):
            # update the call back function with any progress made
            if callback:
                callback.update(i, max_loop)
            # start again, this time to change curve geometry
            failure_messages = get_warnings_by_guid(doc, guid=guid)
            # get next curve sets from failure message
            warning_curve_sets = get_curves_from_failure_messages(
                doc=doc,
                failure_messages=failure_messages,
                group_id=group_id,
            )
            return_value.append_message(
                "Found {} failure sets applying to group id: {}.".format(
                    len(warning_curve_sets), group_id
                )
            )
            for failure_set in warning_curve_sets:
                # check if needs to be ignored ( already tried to process before )
                curve_identifier = (failure_set[0].id, failure_set[1].id)
                # check if this set needs processing or can be ignored
                if curve_identifier not in ignore_these_curves:
                    # get geometry calcs
                    (
                        curves_to_change,
                        curves_to_delete,
                    ) = _identify_curve_in_set_to_amend_lengthening(
                        curve_set=failure_set, group_id=group_id
                    )
                    # check if None values ( cant change curves ) came back
                    if curves_to_change == None and curves_to_delete == None:
                        return_value.append_message(
                            "Neither curve {} , {} in curve set could be amended...".format(
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
                        else:
                            return_value.append_message(
                                "Set: {} of group {} and {} of group {} contains no curve to change geometry of.".format(
                                    failure_set[0].id,
                                    failure_set[0].group_id,
                                    failure_set[1].id,
                                    failure_set[1].group_id,
                                )
                            )
                        # check if anything needs deleting
                        if curves_to_delete:
                            return_value.append_message(
                                "Found a curve: {} to delete".format(
                                    curves_to_delete[0].id
                                )
                            )
                            # delete the now overlapping curves
                            status_delete = delete_curves(
                                doc, curves_to_delete, "separation line"
                            )
                            return_value.update(status_delete)
                        else:
                            return_value.append_message(
                                "Set: {} of group {} and {} of group {} contains no curve to delete.".format(
                                    failure_set[0].id,
                                    failure_set[0].group_id,
                                    failure_set[1].id,
                                    failure_set[1].group_id,
                                )
                            )
                    # get out of loop and start again by getting the current set of warnings from the model
                    break

            # check if cancelled
            if callback:
                if callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break
    else:
        return_value.append_message(
            "No overlap warnings with guid: {} in model.".format(guid)
        )
    return return_value


def _identify_curves_to_amend_short(curve_set, group_id):
    """
    Returns a lists containing 2 curves to change the geometry of

    :param curve_set: A set of curves that needs to be analyzed and identified for amendment
    :type curve_set: [:class: `RevitWarningOverlap`]
    :return: A tuple containing two lists - curves_to_amend and curves_to_delete
    :param group_id: group id curves need to belong to for processing (-1 not in a group)
    :type group_id: int
    :rtype: tuple
    :raises ValueError: If the length of curve_set is not equal to 2
    """

    if not isinstance(curve_set, list):
        raise TypeError("curve_set must be a list")
    if not isinstance(group_id, int):
        raise TypeError("group_id must be an instance of integer")

    curves_to_amend = []
    if len(curve_set) == 2:
        curve_to_change = calculate_shortened_curve_geometry(curve_set[0], curve_set[1])
        # check whether changes can be executed
        # need to be in main model, same design option, same phase created and demoed
        if (
            curve_to_change
            and curve_set[0].group_id == curve_set[1].group_id
            and curve_set[0].design_option_id == curve_set[1].design_option_id
            and curve_set[0].phase_created_id == curve_set[1].phase_created_id
            and curve_set[0].phase_demolished_id == curve_set[1].phase_demolished_id
        ):
            curves_to_amend.append(curve_to_change)
        else:
            curves_to_amend.append(None)
    else:
        raise ValueError("Curve set does not have a length of 2")
    return curves_to_amend


def modify_curves_by_shortening(doc, guid, transaction_manager, group_id, callback):
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
    if not isinstance(group_id, int):
        raise TypeError("group_id must be an instance of integer")

    return_value = res.Result()
    failure_messages = get_warnings_by_guid(doc, guid=guid)
    # get curve sets from failure message with matching group id
    warning_curve_sets = get_curves_from_failure_messages(
        doc=doc,
        failure_messages=failure_messages,
        group_id=group_id,
    )

    # maximum number of loops
    max_loop = len(warning_curve_sets)
    if max_loop > 0:
        return_value.append_message(
            "Found {} warnings matching group id: {}".format(max_loop, group_id)
        )
        ignore_these_curves = []
        for i in range(max_loop):
            # update the call back function with any progress made
            if callback:
                callback.update(i, max_loop)
            # start again, this time to change curve geometry
            failure_messages = get_warnings_by_guid(doc, guid=guid)
            # get next curve sets from failure message
            warning_curve_sets = get_curves_from_failure_messages(
                doc=doc,
                failure_messages=failure_messages,
                group_id=group_id,
            )
            return_value.append_message(
                "Found {} failure sets applying to group id: {}.".format(
                    len(warning_curve_sets), group_id
                )
            )
            for failure_set in warning_curve_sets:
                # check if needs to be ignored ( already tried to process before )
                curve_identifier = (failure_set[0].id, failure_set[1].id)
                # check if this set needs processing or can be ignored
                if curve_identifier not in ignore_these_curves:
                    # get geometry calcs
                    curves_to_change = _identify_curves_to_amend_short(
                        curve_set=failure_set, group_id=group_id
                    )
                    # check if None values ( cant change curves ) came back
                    if curves_to_change == None:
                        return_value.append_message(
                            "Neither curve {} , {} in curve set could be amended...".format(
                                failure_set[0].id, failure_set[1].id
                            )
                        )
                        # make sure to flag this set as not to be processed again
                        ignore_these_curves.append(curve_identifier)
                    else:
                        return_value.append_message(
                            "Found a curve: {} to amend".format(curves_to_change[0].id)
                        )
                        # amend curves first....
                        status_update = _modify_separation_lines(
                            doc=doc,
                            curves=curves_to_change,
                            transaction_manager=transaction_manager,
                        )
                        return_value.update(status_update)
                    # get out of loop and start again by getting the current set of warnings from the model
                    break

            # check if cancelled
            if callback:
                if callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break
    else:
        return_value.append_message(
            "No overlap warnings with guid: {} in model.".format(guid)
        )
    return return_value
