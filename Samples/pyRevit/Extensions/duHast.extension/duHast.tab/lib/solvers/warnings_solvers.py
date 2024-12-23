from duHast.Revit.Warnings.solver_room_tag_to_room import (
    RevitWarningsSolverRoomTagToRoom,
)
from duHast.Revit.Warnings.solver_duplicate_mark import RevitWarningsSolverDuplicateMark
from duHast.Revit.Warnings.solver_area_separation_lines_overlap import (
    RevitWarningsSolverAreaSepLinesOverlap,
)
from duHast.Revit.Warnings.solver_room_separation_lines_overlap import (
    RevitWarningsSolverRoomSepLinesOverlap,
)
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling
from duHast.Revit.Warnings.warnings import get_warnings_by_guid
from duHast.Revit.Warnings.warning_guids import (
    ROOM_TAG_OUTSIDE_ROOM,
    DUPLICATE_MARK_VALUE,
    ROOM_SEPARATION_LINES_OVERLAP,
    AREA_SEPARATION_LINES_OVERLAP,
)
from duHast.Utilities.Objects.result import Result


def solve_warning_room_tag_outside_of_room(doc, output, forms):
    """
    Entry point for pyRevit script.

    Will solve warnings by: unpinning room tags, removing the room tag leader and finally moving the room tag to the room location point.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if warnings where solved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get any room tag warnings
    warnings = get_warnings_by_guid(doc=doc, guid=ROOM_TAG_OUTSIDE_ROOM)

    if len(warnings) == 0:
        print("No warnings of type room tags outside of room in file. Exiting.")
        return_value.update_sep(
            False, "No warnings of type room tags outside of room in file. Exiting."
        )
        return return_value

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Solving room tags outside of room warnings: {value} of {max_value}",
        cancellable=True,
    ) as pb:

        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # set up a solver instance
        solver = RevitWarningsSolverRoomTagToRoom(
            transaction_manager=in_transaction_with_failure_handling,
            callback=progress_callback,
        )

        # solve it
        solver_result = solver.solve_warnings(doc=doc, warnings=warnings)

        return_value.update(solver_result)
        print(solver_result.message)
        print("Finished")

        return return_value


def filter_duplicate_marks(*args, **kwargs):
    """
    Default filter for duplicate marks warnings ( all elements will pass!)

    :return: Always True
    :rtype: bool
    """
    return True


def solve_duplicate_mark_warnings(doc, output, forms):
    """
    Entry point for pyRevit script.

    Will solve duplicate mark warnings by setting the mark value to empty.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if warnings where solved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get any room tag warnings
    warnings = get_warnings_by_guid(doc=doc, guid=DUPLICATE_MARK_VALUE)

    if len(warnings) == 0:
        print("No warnings of type duplicate mark in file. Exiting.")
        return_value.update_sep(
            False, "No warnings of type duplicate mark in file. Exiting."
        )
        return return_value

    # set up a pyrevit progress bar
    with forms.ProgressBar(
        title="Solving duplicate mark warnings: {value} of {max_value}",
        cancellable=True,
    ) as pb:

        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # set up a solver instance
        # the filter used here will pass all elements
        # but could be set up to ignore doors for instance
        solver = RevitWarningsSolverDuplicateMark(
            filter_func=filter_duplicate_marks, callback=progress_callback
        )

        # solve it
        solver_result = solver.solve_warnings(doc=doc, warnings=warnings)
        return_value.update(solver_result)
        print(solver_result.message)
        print("Finished")

        return return_value


def _solve_room_sep_line_warnings(doc, forms, by_lengthening):
    """
    Worker function to address room separation line overlap warnings

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: PyRevit forms
    :type forms: pyRevit forms module
    :param by_lengthening: If true, warnings are solve to extend the longer of the two separation lines to completely overlap the shorter, if False, the shorter line will be shortened to avoid any overlap.
    :type by_lengthening: boolean

    :return:
        Result class instance.

        - result.status (bool) True if warnings where solved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get any room tag warnings
    warnings = get_warnings_by_guid(doc=doc, guid=ROOM_SEPARATION_LINES_OVERLAP)

    if len(warnings) == 0:
        return_value.update_sep(
            False, "No warnings of type room separation lines overlap in file. Exiting."
        )
        return return_value

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Solving room separation lines overlap warnings: {value} of {max_value}",
        cancellable=True,
    ) as pb:

        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # set up a solver instance
        # the filter used here will pass all elements
        # but could be set up to ignore doors for instance
        solver = RevitWarningsSolverRoomSepLinesOverlap(
            solve_by_lengthening_curves=by_lengthening,
            transaction_manager=in_transaction_with_failure_handling,
            callback=progress_callback,
        )

        # solve it
        solver_result = solver.solve_warnings(doc=doc, warnings=warnings)
        return_value.update(solver_result)

        return return_value


def solve_duplicate_room_separation_lines_long(doc, output, forms):
    """
    Entry point for pyRevit script

    Will extend overlapping separation lines, so one can be deleted.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if warnings where solved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    return_value = _solve_room_sep_line_warnings(
        doc=doc, forms=forms, by_lengthening=True
    )
    print(return_value.message)
    print("Finished")

    return return_value


def solve_duplicate_room_separation_lines_short(doc, output, forms):
    """
    Entry point for pyRevit script.

    Will shorten room separation line to remove the overlap

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if warnings where solved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    return_value = _solve_room_sep_line_warnings(
        doc=doc, forms=forms, by_lengthening=False
    )
    print(return_value.message)
    print("Finished")

    return return_value


def _solve_area_sep_line_warnings(doc, forms, by_lengthening):
    """
    Worker function to address area separation line overlap warnings

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: PyRevit forms
    :type forms: pyRevit forms module
    :param by_lengthening: If true, warnings are solve to extend the longer of the two separation lines to completely overlap the shorter, if False, the shorter line will be shortened to avoid any overlap.
    :type by_lengthening: boolean
    
    :return:
        Result class instance.

        - result.status (bool) True if warnings where solved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get any room tag warnings
    warnings = get_warnings_by_guid(doc=doc, guid=AREA_SEPARATION_LINES_OVERLAP)

    if len(warnings) == 0:
        return_value.update_sep(
            False, "No warnings of type area separation lines overlap in file. Exiting."
        )
        return return_value

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Solving area separation lines overlap warnings: {value} of {max_value}",
        cancellable=True,
    ) as pb:

        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # set up a solver instance
        # the filter used here will pass all elements
        # but could be set up to ignore doors for instance
        solver = RevitWarningsSolverAreaSepLinesOverlap(
            solve_by_lengthening_curves=by_lengthening,
            transaction_manager=in_transaction_with_failure_handling,
            callback=progress_callback,
        )

        # solve it
        solver_result = solver.solve_warnings(doc=doc, warnings=warnings)
        return_value.update(solver_result)

        return return_value


def solve_duplicate_area_separation_lines_long(doc, output, forms):
    """
    Entry point for pyRevit script

    Will extend overlapping area separation lines, so one can be deleted.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if warnings where solved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    return_value = _solve_area_sep_line_warnings(
        doc=doc, forms=forms, by_lengthening=True
    )
    print(return_value.message)
    print("Finished")

    return return_value


def solve_duplicate_area_separation_lines_short(doc, output, forms):
    """
    Entry point for pyRevit script.

    Will shorten area separation line to remove the overlap and therefore the warning.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if warnings where solved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """
    
    # set up a status tracker
    return_value = Result()

    return_value = _solve_area_sep_line_warnings(
        doc=doc, forms=forms, by_lengthening=False
    )
    print(return_value.message)
    print("Finished")

    return return_value
