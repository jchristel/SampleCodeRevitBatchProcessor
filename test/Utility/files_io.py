import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]


from duHast.Utilities.files_io import get_file_name_without_ext

def test_get_file_name_without_ext():
    '''
    get_file_name_without_ext test

    :return: True if all tests pass, otherwise False
    :rtype: _bool
    '''

    flag = True
    message = '-'
    try:
        file_path = '/path/to/example_file.txt'
        expected_result = 'example_file'
        result = get_file_name_without_ext(file_path)
        message = (' {} vs {}'.format(result, expected_result))
        assert result == expected_result
        
        file_path = '/path/to/another_example_file.csv'
        expected_result = 'another_example_file'
        result = get_file_name_without_ext(file_path)
        message = message + '\n' + (' {} vs {}'.format(result, expected_result))
        assert result == expected_result
        
        file_path = '\\path/to/another_example_file.csv'
        expected_result = 'another_example_file'
        result = get_file_name_without_ext(file_path)
        message = message + '\n' + (' {} vs {}'.format(result, expected_result))
        assert result == expected_result

        file_path = 'C:\path/to some/another_example_file.csv'
        expected_result = 'another_example_file'
        result = get_file_name_without_ext(file_path)
        message = message + '\n' + (' {} vs {}'.format(result, expected_result))
        assert result == expected_result

        file_path = '\\path/to/another_example_file.0001.csv'
        expected_result = 'another_example_file.0001'
        result = get_file_name_without_ext(file_path)
        message = message + '\n' + (' {} vs {}'.format(result, expected_result))
        assert result == expected_result

        file_path = 'example_file.docx'
        expected_result = 'example_file'
        result = get_file_name_without_ext(file_path)
        message = message + '\n' + (' {} vs {}'.format(result, expected_result))
        assert result == expected_result

    except Exception as e:
        message = message + '\n' + ('An exception occurred in function test_get_file_name_without_ext {}'.format(e))
        flag = False
    return flag, message

def run_tests(output):
    '''
    Runs all tests in this module

    :param output: A function to direct any output to.
    :type output: fun(message)
    :return: True if all tests returned True, otherwise False
    :rtype: boolean
    '''

    all_tests = True
    
    flag, message = test_get_file_name_without_ext()
    all_tests = all_tests & flag
    output('test_get_file_name_without_ext()', flag, message)

    return all_tests

if __name__ == "__main__":
    flag, message = test_get_file_name_without_ext()
    print('test_get_file_name_without_ext() [{}]'.format(flag))