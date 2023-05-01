import sys, os, tempfile

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
sys.path += [SAMPLES_PATH]

from duHast.Utilities.files_get import (
    get_files_from_directory_walker_with_filters,
    get_files_with_filter,
    get_files_single_directory,
    files_as_dictionary,
    get_files_from_directory_walker,
)


def _write_test_files(file_names, tmp_dir):
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


def _call_with_temp_directory(func):
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


def test_get_files_single_directory(tmp_dir):
    """
    get_files_single_directory test

    :param tmp_dir: temp directory
    :type tmp_dir: str
    ::return: True if all tests past, otherwise False
    :rtype: _bool
    """

    flag = True
    message = "-"
    try:
        # test data
        test_files = [
            "test_prefix_name_suffix_1.txt",
            "test_prefix_suffix_2.txt",
            "test_prefix_suffix_3.csv",
        ]

        file_prefix = "test_prefix"
        file_suffix = "suffix_1"
        file_extension = ".txt"

        # write out test files
        _write_test_files(test_files, tmp_dir)

        # get files and check result
        result = get_files_single_directory(
            tmp_dir, file_prefix, file_suffix, file_extension
        )

        # Check the actual output matches the expected output
        expected_result = [
            os.path.join(tmp_dir, "test_prefix_name_suffix_1.txt"),
        ]

        message = "{} \nvs \n{}".format(result, expected_result)

        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_files_single_directory {}".format(
                    e
                )
            )
        )
    return flag, message


def test_get_files_from_directory_walker_with_filters(tmp_dir):
    """
    get_files_from_directory_walker_with_filters test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: _bool
    """

    flag = True
    message = "-"
    try:
        # Create some files with different prefixes, suffixes, and extensions
        test_files = [
            "file1_prefix_suffix.csv",
            "file2_prefix_suffix.txt",
            "prefix_file3_suffix.jpg",
            "file4_prefix_suffix.png",
            "prefix_file5_suffix.csv",
            "prefix_file6_suffix.txt",
            "file7_prefix_suffix.jpg",
            "file8_prefix_suffix.txt",
            "prefix_file9_suffix.csv",
            "file10_prefix_suffix.jpg",
        ]

        # write out test files
        _write_test_files(test_files, tmp_dir)

        # Set up the input parameters for the function
        folder_path = tmp_dir
        file_prefix = "prefix"
        file_suffix = "suffix"
        file_extension = ".csv"

        # Call the function to get the actual output
        result = get_files_from_directory_walker_with_filters(
            folder_path, file_prefix, file_suffix, file_extension
        )

        # Check the actual output matches the expected output
        expected_result = [
            os.path.join(folder_path, "prefix_file5_suffix.csv"),
            os.path.join(folder_path, "prefix_file9_suffix.csv"),
        ]

        message = "{} \nvs \n{}".format(result, expected_result)

        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_files_from_directory_walker_with_filters {}".format(
                    e
                )
            )
        )
    return flag, message


def test_files_as_dictionary(tmp_dir):
    """
    files_as_dictionary test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    try:
        test_files = [
            "test_prefix_file1_test_suffix.rfa",
            "test_prefix_file1_something_test_suffix.rfa",
            "test_prefix_file2_test_suffix.rfa",
            "test_file2_test_suffix.rfa",
            "test_prefix_file2_test_suffix.txt",
            "test_prefix_file2_suffix.rfa",
        ]

        # write out test files
        _write_test_files(test_files, tmp_dir)

        # Call the function with the temporary directory and filter values
        result = files_as_dictionary(tmp_dir, "test_prefix", "_test_suffix", ".rfa")

        # Check that the dictionary contains the expected keys and values
        expected_result = {
            "test_prefix_file1_test_suffix": [os.path.join(tmp_dir, test_files[0])],
            "test_prefix_file1_something_test_suffix": [
                os.path.join(tmp_dir, test_files[1])
            ],
            "test_prefix_file2_test_suffix": [os.path.join(tmp_dir, test_files[2])],
        }

        message = "{} \nvs \n{}".format(result, expected_result)

        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_files_as_dictionary {}".format(
                    e
                )
            )
        )
    return flag, message


def test_get_files_with_filter(tmp_dir):
    """
    get_files_with_filter test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    try:
        # Create some files with different extensions and names
        test_files = [
            "file1.rvt",
            "file2.rvt",
            "file3.rfa",
            "file4.rvt",
            "something1.rvt",
            "something2.rvt",
            "nothing.txt",
        ]

        # write out test files
        _write_test_files(test_files, tmp_dir)

        # Set up the input parameters for the function
        file_extension = ".rvt"
        filter = "something*"

        # Call the function to get the actual output
        result = get_files_with_filter(tmp_dir, file_extension, filter)

        # Check the actual output matches the expected output
        expected_result = [
            os.path.join(tmp_dir, "something1.rvt"),
            os.path.join(tmp_dir, "something2.rvt"),
        ]

        message = "{} \nvs \n{}".format(result, expected_result)

        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_files_with_filter {}".format(
                    e
                )
            )
        )
    return flag, message


def test_get_files_from_directory_walker(tmp_dir):
    """
    get_files_from_directory_walker test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    try:
        test_files = [
            "testfile1.txt",
            "testfile2.csv",
            "testfile3.rfa",
            "tetfile3.rfa",
        ]

        # write out test files
        _write_test_files(test_files, tmp_dir)

        filter = "testfile"
        result = get_files_from_directory_walker(tmp_dir, filter)
        expected_result = [
            os.path.join(tmp_dir, file) for file in test_files if filter in file
        ]

        message = "{} \nvs \n{}".format(result, expected_result)

        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_files_from_directory_walker {}".format(
                    e
                )
            )
        )
    return flag, message


def run_tests(output):
    """
    Runs all tests in this module

    :param output: A function to direct any output to.
    :type output: fun(message)
    :return: True if all tests returned True, otherwise False
    :rtype: boolean
    """

    all_tests = True

    # lists of tests to be executed
    tests = [
        ["test_get_files_single_directory", test_get_files_single_directory],
        ["test_get_files_with_filter", test_get_files_with_filter],
        ["test_files_as_dictionary", test_files_as_dictionary],
        [
            "test_get_files_from_directory_walker_with_filters",
            test_get_files_from_directory_walker_with_filters,
        ],
        ["test_get_files_from_directory_walker", test_get_files_from_directory_walker],
    ]

    # execute tests
    for test in tests:
        flag, message = _call_with_temp_directory(test[1])
        all_tests = all_tests & flag
        output(test[0], flag, message)

    return all_tests


if __name__ == "__main__":
    # in line function to print
    def action(function, flag, message):
        print("{} [{}]".format(function, flag))
        print(message)

    run_tests(action)
