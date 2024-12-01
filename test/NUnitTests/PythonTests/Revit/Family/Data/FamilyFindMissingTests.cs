using Newtonsoft.Json;
using PythonTests.Setup;
using PythonTests.Revit.Family.Data.util;

namespace PythonTests.Revit.Family.Data
{
    public class FamilyFindMissingTests
    {
        private string dataTestDirectory;
        private List<TestFileData> testFilesMultiple;

        [SetUp]
        public void SetUp()
        {
            dataTestDirectory = PythonTests.PythonRunner.GetTestDataPath();
            //[('Sample_Family_Seven', 'Electrical Fixtures'), ('Label_Text_Rotation_1_5mm_ANN', 'Generic Annotations'), ('Label_Text_1_5mm_ANN', 'Generic Annotations'), ('Section Tail - Upgrade', 'Section Marks'), ('Symbol_Outlet_GPO_Single_Emergency_ANN', 'Generic Annotations'), ('Sample_Family_Eight', 'Furniture Systems')]
            testFilesMultiple = new List<TestFileData>
            {
                new TestFileData("Sample_Family_Seven", true, 1, new List<List<string>> { new List<string> { "Electrical Fixtures" } }),
                new TestFileData("Sample_Family_Eight", true, 1, new List<List<string>> { new List<string> { "Furniture Systems" } }),
                new TestFileData("Label_Text_Rotation_1_5mm_ANN", true, 1, new List<List<string>> { new List<string> { "Generic Annotations" } }),
                new TestFileData("Label_Text_1_5mm_ANN", true, 1, new List<List<string>> { new List<string> { "Generic Annotations" } }),
                new TestFileData("Section Tail - Upgrade", true, 1, new List<List<string>> { new List<string> { "Section Marks" } }),
                new TestFileData("Symbol_Outlet_GPO_Single_Emergency_ANN", true, 1, new List<List<string>> { new List<string> { "Generic Annotations" } }),
            };
        }

        [Test]
        public void ModuleShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.FamilyMissingFamiliesModule, Is.Not.Null, "data_family_base_data_missing_families should be loaded.");
            Console.WriteLine(dataTestDirectory);
        }

        [Test]
        public void TestCheckFamiliesMissingFromLibrary()
        {
            dynamic familyReportReader = PythonEngineManager.FamilyMissingFamiliesModule;
            string dataTestDirectoryReader01 = Path.Combine(dataTestDirectory, @"ReadMissingFamilies_01\FamilyBaseDataCombinedReport_original.csv");
            Console.WriteLine(dataTestDirectoryReader01);

            
            var testResultMissing = familyReportReader.check_families_missing_from_library(dataTestDirectoryReader01);
            Console.WriteLine(testResultMissing.result);
            Console.WriteLine(testResultMissing.message);
            Assert.That(testResultMissing.status, Is.True, "Expecting successfully reading of all files");
            Assert.That(testResultMissing.result.Count, Is.EqualTo(testFilesMultiple.Count), "Expecting number of missing root families to match");
            

            // Check if all expected data is present
            foreach (var testFile in testFilesMultiple)
            {
                bool foundMatch = false;
                foreach (var familyData in testResultMissing.result)
                {
                    if (familyData[0] == testFile.FileName && familyData[1] == testFile.ExpectedData[0][0])
                    {
                        foundMatch = true;
                        break;
                    }
                }
                if (!foundMatch)
                {
                    Assert.Fail($"No match found for family: {testFile.FileName} with category: {testFile.ExpectedData[0][0]}");
                }
            }
        }
    }
}
