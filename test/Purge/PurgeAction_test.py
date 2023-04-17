import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

from duHast.APISamples.Purge.RevitPurgeAction import PurgeAction

import unittest

class TestPurgeAction(unittest.TestCase):

    def test_constructor(self):
        # Test that constructor initializes variables correctly
        purgeTransactionName = "testTransaction"
        purgeIdsGetter = lambda: [1,2,3]
        purgeReportHeader = "Test Purge Report Header"
        testReportHeader = "Test Test Report Header"
        testIdsGetter = lambda: [1,2,3,4,5]

        purgeAction = PurgeAction(
            purgeTransactionName, 
            purgeIdsGetter, 
            purgeReportHeader, 
            testReportHeader, 
            testIdsGetter
        )

        self.assertEqual(purgeAction.purge_transaction_name, purgeTransactionName)
        self.assertEqual(purgeAction.purge_ids_getter, purgeIdsGetter)
        self.assertEqual(purgeAction.purge_report_header, purgeReportHeader)
        self.assertEqual(purgeAction.test_report_header, testReportHeader)
        self.assertEqual(purgeAction.test_ids_getter, testIdsGetter)

        print(purgeAction)

if __name__ == '__main__':
    unittest.main()