from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Revit.LinePattern.purge_unused_line_patterns_by_delete import (
    purge_line_pattern_by_delete,
    get_line_pattern_ids,
)
from duHast.Revit.LinePattern.purge_unused_line_styles_by_delete import (
    purge_line_styles_by_delete,
    get_line_style_ids,
)
from duHast.Revit.LinePattern.purge_unused_fill_patterns_by_delete import (
    purge_fill_pattern_by_delete,
    get_fill_pattern_ids,
)
from duHast.pyRevit.ui_element_selection import get_element_selection_from_user


def purge_line_patterns(doc, output, forms):
    """
    Purges all unused line patterns from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if line patterns where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """
    
    # set up a status tracker
    return_value = Result()

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Purging Line Patterns: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # purge it
        purge_status = purge_line_pattern_by_delete(
            doc=doc, progress_callback=progress_callback, debug=True
        )

        # update our status object
        return_value.update(purge_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(purge_status)

    print("Finished.")

    return return_value


def purge_line_patterns_by_selection(doc, output, forms):
    """
    Purges all unused line patterns from a selection from a model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if line patterns where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # build action to get fill patterns from model
    def action(doc):
        result_action = get_line_pattern_ids(
            doc=doc,
            element_ids=None,
        )
        return result_action

    # get user to select which fill patterns to purge
    selected_line_pattern_ids = get_element_selection_from_user(
        doc=doc,
        forms=forms,
        element_getter=action,
        element_selection_description="Select Line Patterns To Purge",
    )

    if selected_line_pattern_ids is None:
        return_value.update_sep(False, "No line patterns to purge where selected.")
        print("{}\nFinished.".format(return_value.message))
        return return_value

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Purging Line Patterns: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # purge it
        purge_status = purge_line_pattern_by_delete(
            doc=doc,
            progress_callback=progress_callback,
            debug=True,
            element_ids=selected_line_pattern_ids,
            element_ids_list_is_inclusive_filter=True,
        )

        # update our status object
        return_value.update(purge_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(purge_status)

    print("Finished.")

    return return_value


def purge_line_styles(doc, output, forms):
    """
    Purges all unused line styles from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if line styles where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Purging Line Styles: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # purge it
        purge_status = purge_line_styles_by_delete(
            doc=doc, progress_callback=progress_callback, debug=True
        )

        # update our status object
        return_value.update(purge_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(purge_status)

    print("Finished.")

    return return_value


def purge_line_styles_by_selection(doc, output, forms):
    """
    Purges all unused line styles from a selection from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if line styles where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # build action to get fill patterns from model
    def action(doc):
        result_action = get_line_style_ids(
            doc=doc,
            element_ids=None,
        )
        return result_action

    # get user to select which fill patterns to purge
    selected_line_styles_ids = get_element_selection_from_user(
        doc=doc,
        forms=forms,
        element_getter=action,
        element_selection_description="Select Line Styles To Purge",
    )

    if selected_line_styles_ids is None:
        return_value.update_sep(False, "No line styles to purge where selected.")
        print("{}\nFinished.".format(return_value.message))
        return return_value

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Purging Line Styles: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # purge it
        purge_status = purge_line_styles_by_delete(
            doc=doc,
            progress_callback=progress_callback,
            debug=True,
            element_ids=selected_line_styles_ids,
            element_ids_list_is_inclusive_filter=True,
        )

        # update our status object
        return_value.update(purge_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(purge_status)

    print("Finished.")

    return return_value


def purge_fill_patterns(doc, output, forms):
    """
    Purges all unused fill patterns from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if fill patterns where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Purging Fill Patterns: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # purge it
        purge_status = purge_fill_pattern_by_delete(
            doc=doc, progress_callback=progress_callback, debug=True
        )

        # update our status object
        return_value.update(purge_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(purge_status)

    print("Finished.")

    return return_value


def purge_fill_patterns_by_selection(doc, output, forms):
    """
    Purges all unused fill patterns from a selection from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if fill patterns where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # build action to get fill patterns from model
    def action(doc):
        result_action = get_fill_pattern_ids(
            doc=doc,
            element_ids=None,
        )
        return result_action

    # get user to select which fill patterns to purge
    selected_fill_pattern_ids = get_element_selection_from_user(
        doc=doc,
        forms=forms,
        element_getter=action,
        element_selection_description="Select Fill Pattern To Purge",
    )

    if selected_fill_pattern_ids is None:
        return_value.update_sep(False, "No fill patterns to purge where selected.")
        print("{}\nFinished.".format(return_value.message))
        return return_value

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Purging Fill Patterns: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # purge it
        purge_status = purge_fill_pattern_by_delete(
            doc=doc,
            progress_callback=progress_callback,
            debug=True,
            element_ids=selected_fill_pattern_ids,
            element_ids_list_is_inclusive_filter=True,
        )

        # update our status object
        return_value.update(purge_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(purge_status)

    print("Finished.")

    return return_value
