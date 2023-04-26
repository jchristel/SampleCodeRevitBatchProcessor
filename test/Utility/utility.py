import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

from duHast.Utilities.utility import encode_ascii, get_first

def test_encode_ascii():
    '''
    encode_ascii test
    
    :return: True if all tests pass, otherwise False
    :rtype: _bool
    '''

    message = '-'
    flag = True
    try:
        result = encode_ascii("hello world")
        message = ('{} \nvs \n{}'.format(result, b"hello world"))
        assert encode_ascii(result) == b"hello world"
        
        result = encode_ascii("Привет, мир!")
        message = message + '\n' + (' {} vs {}'.format(result, b"?, ?!"))
        assert encode_ascii(result) == b"??????, ???!"
        
        result = encode_ascii("")
        message = message + '\n' + (' {} vs {}'.format(result, b""))
        assert encode_ascii("") == b""

        result = encode_ascii("123")
        message = message + '\n' + (' {} vs {}'.format(result, b"123"))
        assert encode_ascii("123") == b"123"

        result = encode_ascii(123)
        message = message + '\n' + (' {} vs {}'.format(result, 123))
        assert encode_ascii(123) == 123

        result = encode_ascii(None)
        message = message + '\n' + (' {} vs {}'.format(result, None))
        assert encode_ascii(None) == None

        result = encode_ascii(True)
        message = message + '\n' + (' {} vs {}'.format(result, True))
        assert encode_ascii(True) == True
        
    except Exception as e:
        message = message + '\n' + ('An exception occurred in function test_encode_ascii {}'.format(e))
        flag = False
    return flag, message

def test_get_first():

    message = '-'
    flag = True

    try:
        # Test when iterable is empty
        result = get_first([], None)
        message = ('{} \nvs \n{}'.format(result, None))
        assert get_first([], None) == None

        result = get_first([], 'default')
        message = message + '\n' + (' {} vs {}'.format(result, 'default'))
        assert get_first([], 'default') == 'default'


        # Test when iterable is not empty and condition is met
        result = get_first([1, 2, 3], None, lambda x: x > 2)
        message = message + '\n' + (' {} vs {}'.format(result, 3))
        assert get_first([1, 2, 3], None, lambda x: x > 2) == 3

        result = get_first([1, 2, 3], 'default', lambda x: x > 2)
        message = message + '\n' + (' {} vs {}'.format(result, 3))
        assert get_first([1, 2, 3], 'default', lambda x: x > 2) == 3


        # Test when iterable is not empty but condition is not met
        result = get_first([1, 2, 3], None, lambda x: x > 5)
        message = message + '\n' + (' {} vs {}'.format(result, None))
        assert get_first([1, 2, 3], None, lambda x: x > 5) == None

        result = get_first([1, 2, 3], 'default', lambda x: x > 5)
        message = message + '\n' + (' {} vs {}'.format(result, 'default'))
        assert get_first([1, 2, 3], 'default', lambda x: x > 5) == 'default'

    except Exception as e:
        message = message + '\n' + ('An exception occurred in function test_encode_ascii {}'.format(e))
        flag = False
    return flag, message

def run_tests(output):
    '''
    Runs all tests in this module
    '''

    all_tests = True
    
    flag, message = test_encode_ascii()
    all_tests = all_tests & flag
    output('test_encode_ascii()', flag, message)

    flag, message = test_get_first()
    all_tests = all_tests & flag
    output('test_get_first()', flag, message)

    return all_tests


if __name__ == "__main__":
    flag,message = test_encode_ascii()
    print('test_encode_ascii [{}]'.format(flag))

    flag,message = test_get_first()
    print('test_get_first [{}]'.format(flag))