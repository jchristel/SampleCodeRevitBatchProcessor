import sys

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
sys.path += [SAMPLES_PATH]

from duHast.Revit.Purge.purge_unused import purge_unused


result = purge_unused(doc, doc.Title, False)
print(result.status)
print(result.message)
