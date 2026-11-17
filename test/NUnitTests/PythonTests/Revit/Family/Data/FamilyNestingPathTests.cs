using PythonTests.Setup;

namespace PythonTests.Revit.Family.Data
{
    public class FamilyNestingPathTests
    {
        private string tempDirectory;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory))
            {
                Directory.Delete(tempDirectory, true);
            }
        }

        private static dynamic NestingPath(string namePath, string categoryPath)
        {
            return PythonEngineManager.FamilyNestingPathClass(namePath, categoryPath);
        }

        [Test]
        public void ClassShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.FamilyNestingPathClass, Is.Not.Null, "FamilyNestingPath should be loaded.");
        }

        [Test]
        public void IsPartOf_StartOfPath_ReturnsTrue()
        {
            dynamic path = NestingPath("Table :: Leg", "Furniture :: Furniture");
            dynamic longer = NestingPath("Table :: Leg :: Bolt", "Furniture :: Furniture :: Generic Models");
            Assert.That((bool)path.is_part_of(longer), Is.True, "Table :: Leg is the start of Table :: Leg :: Bolt");
        }

        [Test]
        public void IsPartOf_SamePath_ReturnsTrue()
        {
            dynamic path = NestingPath("Table :: Leg", "Furniture :: Furniture");
            dynamic same = NestingPath("Table :: Leg", "Furniture :: Furniture");
            Assert.That((bool)path.is_part_of(same), Is.True, "A path is part of itself");
        }

        [Test]
        public void IsPartOf_FamilyNameIsStartOfAnotherName_ReturnsFalse()
        {
            dynamic path = NestingPath("Table :: Leg", "Furniture :: Furniture");
            dynamic other = NestingPath("Table :: Legacy :: Bolt", "Furniture :: Furniture :: Generic Models");
            Assert.That((bool)path.is_part_of(other), Is.False, "Leg is a different family from Legacy");
        }

        [Test]
        public void IsPartOf_CategoryIsStartOfAnotherCategory_ReturnsFalse()
        {
            dynamic path = NestingPath("Table :: Leg", "Furniture :: Furniture");
            dynamic other = NestingPath("Table :: Leg :: Bolt", "Furniture :: Furniture Systems :: Generic Models");
            Assert.That((bool)path.is_part_of(other), Is.False, "Furniture is a different category from Furniture Systems");
        }

        [Test]
        public void IsPartOf_LongerPath_ReturnsFalse()
        {
            dynamic path = NestingPath("Table :: Leg :: Bolt", "Furniture :: Furniture :: Generic Models");
            dynamic shorter = NestingPath("Table :: Leg", "Furniture :: Furniture");
            Assert.That((bool)path.is_part_of(shorter), Is.False, "A longer path is not part of a shorter one");
        }

        [Test]
        public void IsPartOf_SameNamesDifferentCategories_ReturnsFalse()
        {
            dynamic path = NestingPath("Table :: Leg", "Furniture :: Generic Models");
            dynamic other = NestingPath("Table :: Leg :: Bolt", "Furniture :: Furniture :: Generic Models");
            Assert.That((bool)path.is_part_of(other), Is.False, "Same family names in different categories are different families");
        }

        [Test]
        public void GetChunks_PathsOfDifferentLength_Throws()
        {
            dynamic path = NestingPath("Table :: Leg", "Furniture");
            Assert.Catch<Exception>(() => path.get_chunks(), "Name and category paths of different length should raise");
        }

        [Test]
        public void CheckFamiliesMissingFromLibrary_FamilyNameIsStartOfAnotherName_ReportsMissingFamily()
        {
            // Table nests Leg (nothing nested) and Legacy (nests Bolt). Leg has no row of its own: it is missing from the library.
            string reportPath = Path.Combine(tempDirectory, "FamilyBaseDataCombinedReport.csv");
            File.WriteAllLines(reportPath, new[]
            {
                "data_type,root_name_path,root_category_path,family_name,family_file_path",
                "FamilyBase,Table,Furniture,Table,C:\\lib\\Table.rfa",
                "FamilyBase,Table :: Leg,Furniture :: Furniture,Leg,C:\\lib\\Leg.rfa",
                "FamilyBase,Table :: Legacy,Furniture :: Furniture,Legacy,C:\\lib\\Legacy.rfa",
                "FamilyBase,Table :: Legacy :: Bolt,Furniture :: Furniture :: Generic Models,Bolt,C:\\lib\\Bolt.rfa",
                "FamilyBase,Legacy,Furniture,Legacy,C:\\lib\\Legacy.rfa",
                "FamilyBase,Legacy :: Bolt,Furniture :: Generic Models,Bolt,C:\\lib\\Bolt.rfa",
                "FamilyBase,Bolt,Generic Models,Bolt,C:\\lib\\Bolt.rfa",
            });

            dynamic missingFamiliesModule = PythonEngineManager.FamilyMissingFamiliesModule;
            var testResult = missingFamiliesModule.check_families_missing_from_library(reportPath);
            Console.WriteLine(testResult.message);

            Assert.That(testResult.status, Is.True, "Expecting the report to be read");
            Assert.That(testResult.result.Count, Is.EqualTo(1), "Expecting one missing family");
            Assert.That(testResult.result[0].family_name, Is.EqualTo("Leg"), "Expecting Leg to be missing");
            Assert.That(testResult.result[0].family_category, Is.EqualTo("Furniture"), "Expecting Leg's category");
        }
    }
}
