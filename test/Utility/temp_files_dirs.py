import os
import tempfile


def call_with_temp_directory(func):
    """
    Utility function setting up a temp directory and calling pass in function with that directory as an argument.
    :param func: test function to be executed
    :type func: func
    :return: True if all tests past, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    with tempfile.TemporaryDirectory() as tmp_dir:
        flag, message = func(tmp_dir)
    return flag, message


def write_test_files(file_names, tmp_dir):
    """
    Utility function writing out test files into given directory
    :param file_names: A list of file names.
    :type file_names: [str]
    :param temp_dir: Fully qualified directory path.
    :type temp_dir: str
    """

    for file_name in file_names:
        file_path = os.path.join(tmp_dir, file_name)
        with open(file_path, "w") as f1:
            f1.write("test content")


def write_file_with_data(file_name, tmp_dir, data):
    """
    Function writing out a text file with given data.

    :param file_name: The file name.
    :type file_name: str
    :param tmp_dir: The directory path.
    :type tmp_dir: str
    :param data: data to be written to file
    :type data: [str]
    """

    with open(os.path.join(tmp_dir, file_name), "w") as f:
        for d in data:
            f.write(d + "\n")
        f.close()
