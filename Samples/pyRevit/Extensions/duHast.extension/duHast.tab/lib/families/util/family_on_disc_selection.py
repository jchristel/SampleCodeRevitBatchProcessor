from duHast.Utilities.Objects.result import Result
import os
from duHast.Utilities.files_get import (
    get_files_from_directory_walker_with_filters_simple,
)
from duHast.Utilities.files_io import remove_backup_revit_files_from_list


def get_families(directory):
    """
    Get all families in a directory and discard any family that occurs more than once

    :param directory: the directory to search for families
    :type directory: str
    :return: a list of unique family file paths
    :rtype: list
    """

    families_in_directory = get_files_from_directory_walker_with_filters_simple(
        folder_path=directory, file_extension=".rfa"
    )

    filtered_families = []
    file_names = []

    # filter out family backup files ( ending in .00??.rfa )
    families_in_directory = remove_backup_revit_files_from_list(families_in_directory)

    # filter out families which occur more than once
    for path in families_in_directory:
        file_name = os.path.basename(path)
        if file_name not in file_names:
            filtered_families.append(path)

    return filtered_families


def get_user_selection(forms, families):
    """
    Get user to select families to load

    :param families: a list of family file paths
    :type families: list
    :return: a list of family file paths selected by the user
    :rtype: list
    """

    # check if we got any?
    if len(families) == 0:
        return None

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(families), button_name="Select families to load", multiselect=True
    )

    if selection == None:
        return None
    else:
        return selection
