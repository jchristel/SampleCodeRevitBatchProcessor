from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Revit.Family.family_rename_files_utils import _read_rename_directives
from duHast.Revit.Family.Data.family_rename_loaded_families import (
    _rename_loaded_families,
)
from duHast.Revit.Family import family_utils as rFamUtils
from duHast.pyRevit.file_picker import get_file_path_from_user


def rename_loaded_families(doc, output, forms):
    """
    Renames loaded families based on a csv file.
    Refer to duHast.Revit.Family.family_rename_files_utils for csv file format.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if files where renamed without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get the user to select the file to be imported
    file_path = get_file_path_from_user(
        forms=forms, title="Select rename file", file_extension="csv"
    )
    if file_path is None:
        print("No file selected. Exiting.")
        return_value.update_sep(False, "No file selected. Exiting.")
        return return_value

    # attempt to read rename file
    print("Reading file: {}".format(file_path))
    data = []
    try:
        data = _read_rename_directives([file_path])
    except Exception as e:
        message = "failed to read rename file with exception: {}".format(e)
        print(message)
        return_value.update_sep(False, message=message)
        return return_value

    # check if any data in file
    if len(data) == 0:
        message = "Rename file did not contain any data"
        return_value.update_sep(False, message=message)
        return return_value

    # get all family ids in file
    family_ids = rFamUtils.get_all_loadable_family_ids_through_types(doc)

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Renaming families: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # rename them
        rename_status = _rename_loaded_families(
            doc=doc,
            rename_directives=data,
            family_ids=family_ids,
            progress_callback=progress_callback,
        )

        # update our status object
        return_value.update(rename_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(rename_status.message)

    print("Finished.")

    return return_value
