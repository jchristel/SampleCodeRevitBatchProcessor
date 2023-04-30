import sys

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
TEST_PATH = r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor"
TEST_PATH_TEST = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\test"
)
sys.path += [SAMPLES_PATH, TEST_PATH, TEST_PATH_TEST]


from test.utils.rbp_setup import add_rbp_ref, output as rbp_out

from test.Revit.Revision import revision as revTest
from test.Revit.Revision import sequence as seqTest

from test.utils.padding import pad_header_no_time_stamp, pad_string

#: Type of test run flag. If False run in revit python shell. If True runs in revit batch processor.
IS_RBP_RUN = False


def run_revision_tests(doc, rbp_run_type=IS_RBP_RUN):
    """
    Runs all revision related tests.

    :param doc: Current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if all tests completed successfully, otherwise False.
    :rtype: bool
    """

    output_function = out
    output_function_header = out_header
    if rbp_run_type == True:
        # add revit batch processor references and get the current document
        doc = add_rbp_ref()
        output_function = rbp_out
        output_function_header = rbp_out

    #: overall test status
    overall_status = True

    # start tests
    output_function_header(pad_header_no_time_stamp("Revisions"))
    result = revTest.run_tests(doc, output_function)
    overall_status = overall_status & result
    output_function_header(pad_header_no_time_stamp("Revision Sequence"))
    result = seqTest.run_tests(doc, output_function)
    overall_status = overall_status & result

    return overall_status


def out_header(header):
    """
    Just prints header.

    :param header: A header line.
    :type header: str
    """

    print(header)


def out(func_name, result_flag, message):
    """
    print messages to screen when debugging

    :param func_name: The function tested name.
    :type func_name: str
    :param result_flag: True if test completed successfully, otherwise False
    :type result_flag: bool
    :param message: Any debug message coming back from the test function.
    :type message: str
    """

    message = "{} [{}]".format(func_name, result_flag)
    print(pad_string(message))
    if IS_RBP_RUN:
        print(pad_string(message))


if __name__ == "__main__":
    run_revision_tests(doc)
