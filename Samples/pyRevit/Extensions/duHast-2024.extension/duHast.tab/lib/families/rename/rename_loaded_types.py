import os


from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Revit.Family.Utility.family_rename_types_utils import _read_rename_directives
from duHast.Revit.Family.family_rename_loaded_types import (
    _rename_loaded_family_types,
)

from duHast.pyRevit.file_picker import get_file_path_from_user
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict


def rename_loaded_family_types_entry(doc, output, forms):
    """
    Renames loaded family types based on a csv (directive) file.
    
    """
    # set up a status tracker
    return_value = Result()

    # get the user to select the file to be imported
    file_path = get_file_path_from_user(
        forms=forms, title="Select type rename file", file_extension="csv"
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

    # get all family in file
    families = get_name_and_category_to_family_dict(doc)

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Renaming families: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # rename them
        rename_status = _rename_loaded_family_types(
            doc=doc,
            rename_directives=data,
            families=families,
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


    