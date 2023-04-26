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
        result = ([1, 2, 3, 4], 5)
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


def run_tests(output):
    """
    Runs all tests in this module
    """

    all_tests = True

    flag, message = test_parse_string_to_bool()
    all_tests = all_tests & flag
    output("test_parse_string_to_bool()", flag, message)

    flag, message = test_pad_single_digit_numeric_string()
    all_tests = all_tests & flag
    output("test_pad_single_digit_numeric_string()", flag, message)

    flag, message = test_encode_ascii()
    all_tests = all_tests & flag
    output("test_encode_ascii()", flag, message)

    flag, message = test_get_first()
    all_tests = all_tests & flag
    output("test_get_first()", flag, message)

    flag, message = test_index_of()
    all_tests = all_tests & flag
    output("test_index_of()", flag, message)

    return all_tests


if __name__ == "__main__":
    flag, message = test_encode_ascii()
    print("test_encode_ascii [{}]".format(flag))

    flag, message = test_get_first()
    print("test_get_first [{}]".format(flag))

    flag, message = test_parse_string_to_bool()
    print("test_parse_string_to_bool [{}]".format(flag))

    flag, message = test_pad_single_digit_numeric_string()
    print("test_pad_single_digit_numeric_string [{}]".format(flag))

    flag, message = test_index_of()
    print("test_index_of [{}]".format(flag))
