from test.utils.rbp_setup import add_rbp_ref, output

import revision as revTest
import sequence as seqTest

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