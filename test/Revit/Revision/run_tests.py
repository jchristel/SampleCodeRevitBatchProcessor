import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
TEST_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor'
sys.path += [SAMPLES_PATH, TEST_PATH]


from test.utils.rbp_setup import add_rbp_ref, output

from test.Revit.Revision import revision as revTest
from  test.Revit.Revision import sequence as seqTest


#: overall debug flag. If False no messages from tests will be printed to console. If True messages will be printed.
IS_DEBUG = True

def run_revision_tests(doc):

    # add revit batch processor references and get the current document
    doc = add_rbp_ref()

    #: overall test status
    overall_status = True

    # start tests
    result = revTest.run_tests(doc, output)
    overall_status = overall_status  & result
    result = seqTest.run_tests(doc, output)
    overall_status = overall_status  & result

    return overall_status

def out(func_name, result_flag, message):
    print ("{} [{}]".format(func_name, result_flag))
    if IS_DEBUG:
        print(message)

if __name__ == "__main__":
    #: overall test status
    overall_status = True

    # start tests
    result = revTest.run_tests(doc, out)
    overall_status = overall_status  & result
    result = seqTest.run_tests(doc, out)
    overall_status = overall_status  & result