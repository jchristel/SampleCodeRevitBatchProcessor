using Newtonsoft.Json;
using PythonTests.Setup;
using PythonTests.Revit.Family.Data.util;

namespace PythonTests.Revit.Family.Data
{
    public class FamilyFromAllReportsReaderTests
    {
        private string dataTestDirectory;
        private List<TestFileData> testFilesMultiple;

        [SetUp]
        public void SetUp()
        {
            dataTestDirectory = PythonTests.PythonRunner.GetTestDataPath();

            testFilesMultiple = new List<TestFileData>
            {
                new TestFileData("Sample_Family_One", true, 1, new List<List<string>> { new List<string> { "1", "3" } }),
                new TestFileData("Sample_Family_Two", true, 1, new List<List<string>> { new List<string> { "1", "3" } }),
                new TestFileData("Sample_Family_Three", true, 1, new List<List<string>> { new List<string> { "1", "1" } }),
                new TestFileData("Sample_Family_Four", true, 1, new List<List<string>> { new List<string> { "1", "1" } }),
                new TestFileData("Sample_Family_Five", true, 1, new List<List<string>> { new List<string> { "1", "1" } }),
                new TestFileData("Sample_Family_Six", true, 1, new List<List<string>> { new List<string> { "1", "8" } }),
                new TestFileData("Sample_Family_Seven", true, 1, new List<List<string>> { new List<string> { "1", "4" } }),
                new TestFileData("Sample_Family_Eight", true, 1, new List<List<string>> { new List<string> { "1", "1" } }),
                new TestFileData("Sample_Family_Nine", true, 1, new List<List<string>> { new List<string> { "1", "3" } }),
                new TestFileData("Sample_Family_Ten", true, 1, new List<List<string>> { new List<string> { "1", "0" } }),
                new TestFileData("Sample_Family_Eleven", true, 1, new List<List<string>> { new List<string> { "1", "1" } }),
                new TestFileData("Sample_Family_Twelve", true, 1, new List<List<string>> { new List<string> { "1", "0" } }),
                new TestFileData("Sample_Family_Thirteen", true, 1, new List<List<string>> { new List<string> { "1", "0" } }),
                new TestFileData("Sample_Family_Fourteen", true, 1, new List<List<string>> { new List<string> { "1", "1" } })
            };

        }

        [Test]
        public void ModuleShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.FamilyReportReaderModule, Is.Not.Null, "data_family_report_reader should be loaded.");
            Console.WriteLine(dataTestDirectory);
        }

        [Test]
        public void TestReadMultipleFamilyDataIntoMultipleFamilyInstances()
        {
            dynamic familyReportReader = PythonEngineManager.FamilyReportReaderModule;
            string dataTestDirectoryReader01 = Path.Combine(dataTestDirectory, "ReadFamilies_01");
            Console.WriteLine(dataTestDirectoryReader01);

            try
            {
                var testResultMultiple = familyReportReader.read_data_into_families(dataTestDirectoryReader01);
                Assert.That(testResultMultiple.result.Count, Is.EqualTo(testFilesMultiple.Count), "Expecting number of family instances to match");
                Assert.That(testResultMultiple.status, Is.True, "Expecting succesfully reading of all files");

                //check if all expected data is present
                foreach (var testFile in testFilesMultiple)
                {
                    bool foundMatch = false;
                    foreach (var familyInstance in testResultMultiple.result)
                    {
                        if (familyInstance.family_name == testFile.FileName)
                        {
                            foundMatch = true;
                            Assert.That(familyInstance.data_containers_unsorted.Count, Is.EqualTo(int.Parse(testFile.ExpectedData[0][0])), $"Expecting number of containers for {testFile.FileName} to match");
                            Assert.That(familyInstance.nested_families_unsorted.Count, Is.EqualTo(int.Parse(testFile.ExpectedData[0][1])), $"Expecting number of nested families for {testFile.FileName} to match");

                            break;
                        }
                    }
                    if (!foundMatch)
                    {
                        Assert.Fail($"No match found for family: {testFile.FileName}");
                    }
                }
            }
            catch (Exception e)
            {
                Assert.Fail($"Failed test with: {e}");
            }
        }
    }
}
