import sys

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
sys.path += [SAMPLES_PATH]

from duHast.Revit.Common.revit_version import get_revit_version_number


def test_get_revision_seq_of_name(self):
        # create a mock revision sequence
        seq = rdb.RevisionNumberingSequence.Create(self.doc)
        seq.Name = "Test Sequence"
        
        # call the function and assert it returns the correct sequence
        result = get_revision_seq_of_name(self.doc

def test_get_revit_version_number(doc):
    flag = True
    message = '-'
    try:
        expected_result = 2022
        result = get_revit_version_number(doc)
        message = (' {} vs {}'.format(result, expected_result))
        assert result == expected_result
    except Exception as e:
        message = message + '\n' + ('An exception occurred in function test_get_revit_version_number {}'.format(e))
        flag = False
    return flag, message



if __name__ == "__main__":
    flag, message = test_get_revit_version_number(doc)
    print('test_get_revit_version_number() [{}]'.format(flag))
    print(message)
