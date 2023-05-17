import sys, os, csv

#: path to samples library in repository
SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
#: path to test directory in repository
TEST_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path += [SAMPLES_PATH, TEST_PATH]

from Utility.temp_files_dirs import write_file_with_data, call_with_temp_directory

from duHast.Utilities.files_csv import (
    read_csv_file,
    get_first_row_in_csv_file,
    write_report_data_as_csv,
)

def test_get_first_row_in_csv_file(tmp_dir):
    """
    get first row in csv file test

    :param tmp_dir: temp directory
    :type tmp_dir: str
    :return: True if all tests past, otherwise False
    :rtype: _bool
    """

    flag = True
    message = "-"
    try:
        # test data
        data = [
            "1,John,Doe",
            "2,Jane,Smith",
            "3,Bob,Johnson",
        ]

        csv_file = "test_file.csv"

        # write test file
        write_file_with_data(csv_file, tmp_dir, data)

        result = get_first_row_in_csv_file(os.path.join(tmp_dir, csv_file))
        expected_result = data[0].split(",")
        message = "{} \nvs \n{}".format(result, expected_result)
        assert result == expected_result

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_first_row_in_csv_file {}".format(
                    e
                )
            )
        )
    return flag, message


def test_write_report_data_as_csv(tmp_dir):
    """
    write report data as csv test

    :param tmp_dir: temp directory
    :type tmp_dir: str
    :return: True if all tests past, otherwise False
    :rtype: _bool
    """

    flag = True
    message = "-"
    try:
        # test data
        header = ["Name", "Age", "Gender"]
        data = [["John", "25", "Male"], ["Sara", "32", "Female"]]

        csv_file = "test_file.csv"
        full_csv_path = os.path.join(tmp_dir, csv_file)

        # write test file
        write_report_data_as_csv(full_csv_path, header, data)

        with open(full_csv_path, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            message = "{} \nvs \n{}".format(rows[0], header)
            message = message + "\n" + "{} \nvs \n{}".format(rows[1:], data)
            assert rows[0] == header
            assert rows[1:] == data

        # Test appending to an existing file
        more_data = [["Mike", "45", "Male"], ["Alice", "29", "Female"]]
        write_report_data_as_csv(full_csv_path, [], more_data, "a")
        with open(full_csv_path, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            message = message + "\n" + "{} \nvs \n{}".format(rows[0], header)
            message = message + "\n" + "{} \nvs \n{}".format(rows[1:3], data)
            message = message + "\n" + "{} \nvs \n{}".format(rows[3:], more_data)
            assert rows[0] == header
            assert rows[1:3] == data
            assert rows[3:] == more_data

    except Exception as e:
        flag = False
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_write_report_data_as_csv {}".format(
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
    tests = []

    # test requiring a temp directory
    tests_temp_files = [
        ["test_read_csv_file", test_read_csv_file],
        ["test_get_first_row_in_csv_file", test_get_first_row_in_csv_file],
        ["test_write_report_data_as_csv", test_write_report_data_as_csv],
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
