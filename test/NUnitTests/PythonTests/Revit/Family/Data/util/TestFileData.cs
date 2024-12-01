using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PythonTests.Revit.Family.Data.util
{
    public class TestFileData
    {

        public string FileName { get; }
        public bool ExpectedStatus { get; }
        public int ExpectedCount { get; }
        public List<List<string>> ExpectedData { get; }

        public TestFileData(string fileName, bool expectedStatus, int expectedCount, List<List<string>> expectedData)
        {
            FileName = fileName;
            ExpectedStatus = expectedStatus;
            ExpectedCount = expectedCount;
            ExpectedData = expectedData;
        }
    }
}
