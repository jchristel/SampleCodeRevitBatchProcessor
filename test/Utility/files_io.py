import sys, os

#: path to samples library in repository
SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
#: path to test directory in repository
TEST_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path += [SAMPLES_PATH, TEST_PATH]

from Utility.temp_files_dirs import write_test_files, call_with_temp_directory

from duHast.Utilities.files_io import (
    file_exist,
    file_delete,
    get_directory_path_from_file_path,
    rename_file,
    get_file_name_without_ext,
    get_file_size,
    FILE_SIZE_IN_KB,
    FILE_SIZE_IN_MB,
    FILE_SIZE_IN_GB,
)


def test_file_exist(tmp_dir):
    """
    Test file_exist.

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: bool
    """
    flag = True
    message = "-"
    try:
        # test data
        test_files = [
            "test_file_size.txt",
        ]

        # write out test files
        write_test_files(test_files, tmp_dir)

        result = file_exist(os.path.join(tmp_dir, test_files[0]))
        expected_result = True
        message = " {} vs {}".format(result, expected_result)
        assert expected_result == result

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_file_exist {}".format(e))
        )
    return flag, message


def test_file_delete(tmp_dir):
    """
    file_delete test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    try:
        # test data
        test_files = [
            "test_file_delete.txt",
        ]

        # write out test files
        write_test_files(test_files, tmp_dir)

        result = file_delete(os.path.join(tmp_dir, test_files[0]))
        expected_result = True
        expected_result_check = file_exist(os.path.join(tmp_dir, test_files[0]))
        message = "File deleted: {} vs  expected: {} vs file check {}".format(
            result, expected_result, not expected_result_check
        )
        assert result == expected_result
        # file exist should have returned a false!
        assert result is not expected_result_check

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_file_delete {}".format(e))
        )
    return flag, message


def test_get_directory_path_from_file_path():
    """
    get_directory_path_from_file_path test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    try:
        # test data
        test_files = [
            ["/path/to/file.txt", "/path/to"],
            ["invalid/file/path", "invalid/file"],
            ["/path/to/directory/", "/path/to/directory"],
        ]

        # test valid file path
        result = get_directory_path_from_file_path(test_files[0][0])
        expected_result = test_files[0][1]
        message = " {} vs {}".format(result, expected_result)
        assert result == expected_result

        # tet invalid file path
        result = get_directory_path_from_file_path(test_files[1][0])
        expected_result = test_files[1][1]
        message = message + "\n" + " {} vs {}".format(result, expected_result)
        assert result == expected_result

        # test directory path
        result = get_directory_path_from_file_path(test_files[2][0])
        expected_result = test_files[2][1]
        message = message + "\n" + " {} vs {}".format(result, expected_result)
        assert result == expected_result

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_directory_path_from_file_path {}".format(
                    e
                )
            )
        )
    return flag, message


def test_rename_file(tmp_dir):
    """
    rename_files test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    try:
        # test data
        test_files = [
            ["file.txt", "file_after.txt"],
            ["file_2.text", "file_after.txt"],
            ["file_2.text", ""],
        ]

        test_file_to_be_written = list(entry[0] for entry in test_files)
        # write out test files
        write_test_files(test_file_to_be_written, tmp_dir)

        # test valid scenario
        result = rename_file(
            os.path.join(tmp_dir, test_files[0][0]),
            os.path.join(tmp_dir, test_files[0][1]),
        )
        result_file_exist = file_exist(os.path.join(tmp_dir, test_files[0][1]))
        message = (
            "rename result: {} vs expected result: {} vs file check result: {}".format(
                result, True, result_file_exist
            )
        )
        assert result == True
        assert result == result_file_exist

        result = rename_file(
            os.path.join(tmp_dir, test_files[1][0]),
            os.path.join(tmp_dir, test_files[1][1]),
        )
        message = message + "\n" + " {} vs {}".format(result, False)
        assert result == False

        result = rename_file(
            os.path.join(tmp_dir, test_files[2][0]),
            os.path.join(tmp_dir, test_files[2][1]),
        )
        message = message + "\n" + " {} vs {}".format(result, False)
        assert result == False

        # check non existing source file
        result = rename_file(
            os.path.join(tmp_dir, "not here.txt"),
            os.path.join(tmp_dir, test_files[2][1]),
        )
        message = message + "\n" + " {} vs {}".format(result, False)
        assert result == False

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_directory_path_from_file_path {}".format(
                    e
                )
            )
        )
    return flag, message

def test_copy_file(tmp_dir):
    flag = True
    message = "-"
    try:
        # test data
        test_files = [
            "test_file_size.txt",
        ]
    
    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_copy_file {}".format(e))
        )
    return flag, message

def test_file_size(tmp_dir):
    """
    file_size test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    try:
        # test data
        test_files = [
            "test_file_size.txt",
        ]

        # write out test files
        write_test_files(test_files, tmp_dir)

        # get full test file path
        file_path = os.path.join(tmp_dir, test_files[0])

        # get file size
        file_size = os.path.getsize(file_path)
        message = "File size in byte on disk: {}".format(file_size)

        # Test file size in KB
        result = get_file_size(file_path, unit=FILE_SIZE_IN_KB)
        expected_result = file_size / 1024
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert expected_result == result

        # Test file size in MB
        result = get_file_size(file_path, unit=FILE_SIZE_IN_MB)
        expected_result = file_size / (1024 * 1024)
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert expected_result == result

        # Test file size in GB
        result = get_file_size(file_path, unit=FILE_SIZE_IN_GB)
        expected_result = file_size / (1024 * 1024 * 1024)
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert expected_result == result

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_file_size {}".format(e))
        )
    return flag, message


def test_get_file_name_without_ext():
    """
    get_file_name_without_ext test

    :return: True if all tests pass, otherwise False
    :rtype: _bool
    """

    flag = True
    message = "-"
    try:
        file_path = "/path/to/example_file.txt"
        expected_result = "example_file"
        result = get_file_name_without_ext(file_path)
        message = " {} vs {}".format(result, expected_result)
        assert result == expected_result

        file_path = "/path/to/another_example_file.csv"
        expected_result = "another_example_file"
        result = get_file_name_without_ext(file_path)
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

        file_path = "\\path/to/another_example_file.csv"
        expected_result = "another_example_file"
        result = get_file_name_without_ext(file_path)
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

        file_path = "C:\path/to some/another_example_file.csv"
        expected_result = "another_example_file"
        result = get_file_name_without_ext(file_path)
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

        file_path = "\\path/to/another_example_file.0001.csv"
        expected_result = "another_example_file.0001"
        result = get_file_name_without_ext(file_path)
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

        file_path = "example_file.docx"
        expected_result = "example_file"
        result = get_file_name_without_ext(file_path)
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_file_name_without_ext {}".format(
                    e
                )
            )
        )
        flag = False
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
        ["test_get_file_name_without_ext", test_get_file_name_without_ext],
        [
            "test_get_directory_path_from_file_path",
            test_get_directory_path_from_file_path,
        ],
    ]

    tests_temp_files = [
        ["test_file_size", test_file_size],
        ["test_file_exist", test_file_exist],
        ["test_file_delete", test_file_delete],
        ["test_rename_file", test_rename_file],
    ]

    # execute tests
    for test in tests:
        flag, message = test[1]()
        all_tests = all_tests & flag
        output(test[0], flag, message)

    # exec tests requiring a temp directory
    for test in tests_temp_files:
        flag, message = call_with_temp_directory(test[1])
        all_tests = all_tests & flag
        output(test[0], flag, message)

    return all_tests


if __name__ == "__main__":
    # in line function to print
    def action(function, flag, message):
        print("{} [{}]".format(function, flag))
        print(message)

    run_tests(action)
