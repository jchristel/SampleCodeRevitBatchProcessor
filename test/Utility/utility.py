import sys

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
sys.path += [SAMPLES_PATH]

from duHast.Utilities.utility import (
    encode_ascii,
    get_first,
    parse_string_to_bool,
    pad_single_digit_numeric_string,
    PAD_SINGLE_DIGIT_TO_THREE,
    index_of,
    remove_items_from_list,
    flatten,
)


def test_parse_string_to_bool():
    """
    parse_string_to_bool test

    :return: True if all tests pass, otherwise False
    :rtype: bool
    """

    message = "-"
    flag = True
    try:
        result = parse_string_to_bool("true")
        message = "{} \nvs \n{}".format(result, True)
        assert result == True

        result = parse_string_to_bool("True")
        message = message + "{} \nvs \n{}".format(result, True)
        assert result == True

        result = parse_string_to_bool("false")
        message = message + "{} \nvs \n{}".format(result, False)
        assert result == False

        result = parse_string_to_bool("False")
        message = message + "{} \nvs \n{}".format(result, False)
        assert result == False

        try:
            result = parse_string_to_bool("abc")
            message = message + "{} \nvs \n{}".format(
                result, "Expected exception not raised"
            )
            flag = False
            assert False, "Expected exception not raised"
        except Exception as e:
            assert str(e) == "String cant be converted to bool"
    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function parse_string_to_bool {}".format(e))
        )
        flag = False
    return flag, message


def test_pad_single_digit_numeric_string():
    message = "-"
    flag = True
    try:
        # Test padding a single digit integer string with two digits format
        result = pad_single_digit_numeric_string("5")
        message = "{} \nvs \n{}".format(result, "05")
        assert result == "05"

        result = pad_single_digit_numeric_string("8")
        message = message + "{} \nvs \n{}".format(result, "08")
        assert result == "08"

        result = pad_single_digit_numeric_string("9")
        message = message + "{} \nvs \n{}".format(result, "09")
        assert result == "09"

        # Test padding a single digit integer string with three digits format

        result = pad_single_digit_numeric_string("5", format=PAD_SINGLE_DIGIT_TO_THREE)
        message = message + "{} \nvs \n{}".format(result, "005")
        assert result == "005"

        result = pad_single_digit_numeric_string("8", format=PAD_SINGLE_DIGIT_TO_THREE)
        message = message + "{} \nvs \n{}".format(result, "008")
        assert result == "008"

        result = pad_single_digit_numeric_string("9", format=PAD_SINGLE_DIGIT_TO_THREE)
        message = message + "{} \nvs \n{}".format(result, "009")
        assert result == "009"

        # Test with invalid input
        result = pad_single_digit_numeric_string("")
        message = message + "{} \nvs \n{}".format(result, "")
        assert result == ""

        result = pad_single_digit_numeric_string("not_a_digit")
        message = message + "{} \nvs \n{}".format(result, "not_a_digit")
        assert result == "not_a_digit"

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_pad_single_digit_numeric_string {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_encode_ascii():
    """
    encode_ascii test

    :return: True if all tests pass, otherwise False
    :rtype: bool
    """

    message = "-"
    flag = True
    try:
        result = encode_ascii("hello world")
        message = "{} \nvs \n{}".format(result, b"hello world")
        assert encode_ascii(result) == b"hello world"

        result = encode_ascii("Привет, мир!")
        message = message + "\n" + (" {} vs {}".format(result, b"?, ?!"))
        assert encode_ascii(result) == b"??????, ???!"

        result = encode_ascii("")
        message = message + "\n" + (" {} vs {}".format(result, b""))
        assert encode_ascii("") == b""

        result = encode_ascii("123")
        message = message + "\n" + (" {} vs {}".format(result, b"123"))
        assert encode_ascii("123") == b"123"

        result = encode_ascii(123)
        message = message + "\n" + (" {} vs {}".format(result, 123))
        assert encode_ascii(123) == 123

        result = encode_ascii(None)
        message = message + "\n" + (" {} vs {}".format(result, None))
        assert encode_ascii(None) == None

        result = encode_ascii(True)
        message = message + "\n" + (" {} vs {}".format(result, True))
        assert encode_ascii(True) == True

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_encode_ascii {}".format(e))
        )
        flag = False
    return flag, message


def test_get_first():
    """
    get_first test

    :return: True if all tests pass, otherwise False
    :rtype: bool
    """

    message = "-"
    flag = True

    try:
        # Test when iterable is empty
        result = get_first([], None)
        message = "{} \nvs \n{}".format(result, None)
        assert get_first([], None) == None

        result = get_first([], "default")
        message = message + "\n" + (" {} vs {}".format(result, "default"))
        assert get_first([], "default") == "default"

        # Test when iterable is not empty and condition is met
        result = get_first([1, 2, 3], None, lambda x: x > 2)
        message = message + "\n" + (" {} vs {}".format(result, 3))
        assert get_first([1, 2, 3], None, lambda x: x > 2) == 3

        result = get_first([1, 2, 3], "default", lambda x: x > 2)
        message = message + "\n" + (" {} vs {}".format(result, 3))
        assert get_first([1, 2, 3], "default", lambda x: x > 2) == 3

        # Test when iterable is not empty but condition is not met
        result = get_first([1, 2, 3], None, lambda x: x > 5)
        message = message + "\n" + (" {} vs {}".format(result, None))
        assert get_first([1, 2, 3], None, lambda x: x > 5) == None

        result = get_first([1, 2, 3], "default", lambda x: x > 5)
        message = message + "\n" + (" {} vs {}".format(result, "default"))
        assert get_first([1, 2, 3], "default", lambda x: x > 5) == "default"

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_encode_ascii {}".format(e))
        )
        flag = False
    return flag, message


def test_index_of():
    """
    index of test

    :return: True if all tests pass, otherwise False
    :rtype: bool
    """
    message = "-"
    flag = True

    try:
        # Test with a list that contains the item
        result = index_of([1, 2, 3, 4], 3)
        message = "{} \nvs \n{}".format(result, 2)
        assert index_of([1, 2, 3, 4], 3) == 2

        # Test with a list that doesn't contain the item
        result = index_of([1, 2, 3, 4], 5)
        message = message + "\n" + (" {} vs {}".format(result, -1))
        assert index_of([1, 2, 3, 4], 5) == -1

        # Test with an empty list
        result = index_of([], 1)
        message = message + "\n" + (" {} vs {}".format(result, -1))
        assert index_of([], 1) == -1

        # Test with a list of strings
        result = index_of(["apple", "banana", "orange"], "banana")
        message = message + "\n" + (" {} vs {}".format(result, 1))
        assert index_of(["apple", "banana", "orange"], "banana") == 1

        # Test with a list of mixed types
        result = index_of([1, "apple", 2, "banana"], "banana")
        message = message + "\n" + (" {} vs {}".format(result, 3))
        assert index_of([1, "apple", 2, "banana"], "banana") == 3

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_index_of {}".format(e))
        )
        flag = False
    return flag, message


def test_remove_items():
    """
    remove_items test

    :return: True if all tests pass, otherwise False
    :rtype: bool
    """

    message = "-"
    flag = True
    try:
        # Test removing items from a list
        source_list = [1, 2, 3, 4, 5]
        remove_list = [2, 4]
        expected_result = [1, 3, 5]
        result = remove_items_from_list(source_list, remove_list)
        message = "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

        # remove non existing items
        source_list = [1, 2, 3, 4, 5]
        remove_list = [6, 7]
        expected_result = [1, 2, 3, 4, 5]
        result = remove_items_from_list(source_list, remove_list)
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

        # test empty lists
        source_list = []
        remove_list = []
        expected_result = []
        result = remove_items_from_list(source_list, remove_list)
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_remove_items {}".format(e))
        )
        flag = False
    return flag, message


def test_flatten_dict():
    """
    flatten_dict test

    :return: True if all tests pass, otherwise False
    :rtype: bool
    """

    message = "-"
    flag = True
    try:
        # Test flattening a nested dictionary
        nested_dict = {
            "a": {"b": {"c": 1, "d": 2}},
            "e": {"f": {"g": 3, "h": 4}, "i": 5},
        }

        result = flatten(nested_dict)
        expected_result = {"a_b_c": 1, "a_b_d": 2, "e_f_g": 3, "e_f_h": 4, "e_i": 5}

        message = "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

        # Test flattening an empty dictionary
        nested_dict = {}
        result = flatten(nested_dict)
        expected_result = {}
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

        # Test flattening a dictionary with nested lists
        nested_dict = {"a": {"b": {"c": [1, 2, 3], "d": [4, 5]}}}
        result = flatten(nested_dict)
        expected = {"a_b_c": [1, 2, 3], "a_b_d": [4, 5]}
        message = message + "\n" + (" {} vs {}".format(result, expected_result))
        assert result == expected_result

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_flatten_dict {}".format(e))
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
        ["test_parse_string_to_bool", test_parse_string_to_bool],
        ["test_pad_single_digit_numeric_string", test_pad_single_digit_numeric_string],
        ["test_encode_ascii", test_encode_ascii],
        ["test_get_first", test_get_first],
        ["test_index_of", test_index_of],
        ["test_remove_items", test_remove_items],
        ["test_flatten_dict", test_flatten_dict],
    ]

    # execute tests
    for test in tests:
        flag, message = test[1]()
        all_tests = all_tests & flag
        output(test[0], flag, message)

    return all_tests


if __name__ == "__main__":
    # in line function to print
    def action(function, flag, message):
        print("{} [{}]".format(function, flag))
        print(message)

    run_tests(action)
