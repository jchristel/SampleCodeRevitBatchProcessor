using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.Revit.Family.Data
{
    /// <summary>
    /// Tests for writing family reports back to file, combining reports, and selecting families by sub category directive.
    /// </summary>
    public class FamilyReportUtilsTests
    {
        private string tempDirectory;
        private string dataDirectory;

        private dynamic reportReader;
        private dynamic reportWriter;
        private dynamic reportUtils;
        private dynamic changeCategoryUtils;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
            dataDirectory = Path.Combine(PythonTests.PythonRunner.GetTestDataPath(), "ReadFamilies_01");
            reportReader = PythonEngineManager.Import("duHast.Revit.Family.Data.family_report_reader");
            reportWriter = PythonEngineManager.Import("duHast.Revit.Family.Data.family_report_data_writer");
            reportUtils = PythonEngineManager.Import("duHast.Revit.Family.Data.family_report_utils");
            changeCategoryUtils = PythonEngineManager.Import("duHast.Revit.Family.family_change_category_utils");
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory))
            {
                Directory.Delete(tempDirectory, true);
            }
        }

        private PythonList ReadSampleFamilies()
        {
            dynamic result = reportReader.read_data_into_families(dataDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            return (PythonList)result.result;
        }

        private static List<string> Names(IEnumerable<object> families) =>
            families.Select(f => (string)((dynamic)f).family_name).OrderBy(n => n).ToList();

        // ---------------------------------------- report names ----------------------------------------

        [TestCase("FamilyBaseDataCombinedReport")]
        [TestCase("FamilyBaseDataCombinedReport.csv")]
        public void GetDataTypeByReportName_BaseReport_WithAndWithoutExtension(string reportName)
        {
            Assert.That((string)reportWriter.get_data_type_by_report_name(reportName), Is.EqualTo("FamilyBase"));
        }

        [Test]
        public void GetDataTypeByReportName_UnknownReport_IsNone()
        {
            Assert.That(reportWriter.get_data_type_by_report_name("NotAReport"), Is.Null);
        }

        [Test]
        public void ReportNamesByDataType_CoverAllSixReports()
        {
            Assert.That((int)reportWriter.REPORT_NAME_BY_DATA_TYPE.Count, Is.EqualTo(6));
            Assert.That((string)reportWriter.REPORT_FILE_EXTENSION, Is.EqualTo(".csv"));
        }

        // ---------------------------------------- writing reports ----------------------------------------

        [Test]
        public void WriteDataFromFamiliesToFiles_WritesOneFilePerReportWithData()
        {
            var families = ReadSampleFamilies();
            dynamic result = reportWriter.write_data_from_families_to_files(families, tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);

            var written = Directory.GetFiles(tempDirectory, "*.csv").Select(Path.GetFileNameWithoutExtension).OrderBy(n => n).ToList();
            Assert.That(written, Is.EqualTo(new List<string>
            {
                "FamilyBaseDataCombinedReport",
                "FamilyCategoriesCombinedReport",
                "FamilyLinePatternsCombinedReport",
                "FamilySharedParametersCombinedReport",
                "FamilyWarningsCombinedReport"
            }));
            Assert.That((int)result.result.Count, Is.EqualTo(written.Count));
        }

        [Test]
        public void WriteDataFromFamiliesToFiles_ReportsReadBackIntoTheSameFamilies()
        {
            var families = ReadSampleFamilies();
            dynamic result = reportWriter.write_data_from_families_to_files(families, tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);

            dynamic readBack = reportReader.read_data_into_families(tempDirectory);
            Assert.That((bool)readBack.status, Is.True, (string)readBack.message);
            Assert.That(Names(((IEnumerable<object>)readBack.result)), Is.EqualTo(Names(families)));
        }

        [Test]
        public void WriteDataFromFamiliesToFiles_NotAList_Fails()
        {
            dynamic result = reportWriter.write_data_from_families_to_files("not a list", tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Family_data needs to be a list"));
        }

        [Test]
        public void WriteDataFromFamiliesToFiles_DirectoryNotAString_Fails()
        {
            dynamic result = reportWriter.write_data_from_families_to_files(new PythonList(), 5);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Directory_path needs to be a string"));
        }

        [Test]
        public void WriteDataFromFamiliesToFiles_DirectoryMissing_Fails()
        {
            dynamic result = reportWriter.write_data_from_families_to_files(ReadSampleFamilies(), Path.Combine(tempDirectory, "nothere"));
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("does not exist"));
        }

        [Test]
        public void WriteDataFromFamiliesToFiles_NoFamilies_Fails()
        {
            dynamic result = reportWriter.write_data_from_families_to_files(new PythonList(), tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Failed to get any storage data"));
        }

        [Test]
        public void WriteDataTypeFromFamiliesToFile_WritesOneReport()
        {
            var families = ReadSampleFamilies();
            string file = Path.Combine(tempDirectory, "base.csv");
            dynamic result = reportWriter.write_data_type_from_families_to_file(families, "FamilyBase", file);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(File.Exists(file), Is.True);
            Assert.That(File.ReadAllLines(file).Length, Is.GreaterThan(1), "header and data rows");
        }

        [Test]
        public void WriteDataTypeFromFamiliesToFile_NotAList_Fails()
        {
            dynamic result = reportWriter.write_data_type_from_families_to_file("x", "FamilyBase", Path.Combine(tempDirectory, "x.csv"));
            Assert.That((bool)result.status, Is.False);
        }

        [Test]
        public void WriteDataTypeFromFamiliesToFile_NoDataOfThatType_Fails()
        {
            dynamic result = reportWriter.write_data_type_from_families_to_file(ReadSampleFamilies(), "NotADataType", Path.Combine(tempDirectory, "x.csv"));
            Assert.That((bool)result.status, Is.False);
            Assert.That(File.Exists(Path.Combine(tempDirectory, "x.csv")), Is.False);
        }

        // ---------------------------------------- combining reports ----------------------------------------

        /// <summary>
        /// Writes a base data report with the given root families (each with one nested family N), and creates the family files.
        /// </summary>
        private string WriteBaseReport(string name, params string[] families)
        {
            var rows = new List<string> { "data_type,root_name_path,root_category_path,family_name,family_file_path" };
            foreach (string family in families)
            {
                string path = Path.Combine(tempDirectory, family + ".rfa");
                File.WriteAllText(path, "x");
                rows.Add($"FamilyBase,{family},C_{family},{family},{path}");
                rows.Add($"FamilyBase,{family} :: N,C_{family} :: C_N,N,-");
            }
            string file = Path.Combine(tempDirectory, name);
            File.WriteAllLines(file, rows);
            return file;
        }

        [Test]
        public void CombineReports_NewAndPrevious_Combined_NoDuplicates()
        {
            string previous = WriteBaseReport("previous.csv", "A", "B");
            string current = WriteBaseReport("new.csv", "B", "C");
            dynamic result = reportUtils.combine_reports(previous, current);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(Names(result.result), Is.EqualTo(new List<string> { "A", "B", "C" }));
            Assert.That((string)result.message, Does.Contain("2 new families and 1 previous report families"));
        }

        [Test]
        public void CombineReports_EmptyNewReport_KeepsAllPrevious()
        {
            string previous = WriteBaseReport("previous.csv", "A", "B");
            string current = Path.Combine(tempDirectory, "new.csv");
            File.WriteAllText(current, "data_type,root_name_path,root_category_path,family_name,family_file_path\n");
            dynamic result = reportUtils.combine_reports(previous, current);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(Names(result.result), Is.EqualTo(new List<string> { "A", "B" }));
        }

        [Test]
        public void CombineReports_FamilyFileNoLongerExists_IsDropped()
        {
            string previous = WriteBaseReport("previous.csv", "A", "B");
            string current = WriteBaseReport("new.csv", "C");
            File.Delete(Path.Combine(tempDirectory, "A.rfa"));
            dynamic result = reportUtils.combine_reports(previous, current);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(Names(result.result), Is.EqualTo(new List<string> { "B", "C" }));
            Assert.That((string)result.message, Does.Contain("Removed 1 families"));
        }

        [Test]
        public void CombineReports_PathsNotStrings_Fail()
        {
            dynamic result = reportUtils.combine_reports(5, "x.csv");
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("previous_report_path should be of type string"));
            result = reportUtils.combine_reports("x.csv", 5);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("new_report_path should be of type string"));
        }

        [Test]
        public void CombineReports_MissingReport_Fails()
        {
            string previous = WriteBaseReport("previous.csv", "A");
            dynamic result = reportUtils.combine_reports(previous, Path.Combine(tempDirectory, "nothere.csv"));
            Assert.That((bool)result.status, Is.False);
        }

        // ---------------------------------------- families requiring a sub category change ----------------------------------------

        private dynamic SubCategoryDirective(string category, string oldName, string newName)
        {
            dynamic cls = PythonEngineManager.ImportFrom("duHast.Revit.Family.Data.Objects.family_directive_change_sub_category", "FamilyDirectiveChangeSubCategory");
            return cls(category, oldName, newName);
        }

        private List<string> FilePaths(dynamic paths)
        {
            var list = new List<string>();
            foreach (dynamic p in paths) list.Add((string)p);
            return list;
        }

        [Test]
        public void GetFamiliesRequiringSubCategoryChange_MatchesCategoryAndSubCategory()
        {
            var families = ReadSampleFamilies();
            var directives = new PythonList { SubCategoryDirective("Furniture Systems", "<Hidden Lines>", "Renamed") };
            dynamic paths = changeCategoryUtils.get_families_requiring_sub_category_change(families, directives);
            List<string> list = FilePaths(paths);
            Assert.That(list, Is.Not.Empty);
            Assert.That(list.Any(p => p.EndsWith("Sample_Family_Eight.rfa")), Is.True);
            Assert.That(list.Distinct().Count(), Is.EqualTo(list.Count), "file paths are unique");
        }

        [Test]
        public void GetFamiliesRequiringSubCategoryChange_OnlyFamiliesOfTheDirectivesCategory()
        {
            var families = ReadSampleFamilies();
            var directives = new PythonList { SubCategoryDirective("Furniture Systems", "<Hidden Lines>", "Renamed") };
            dynamic paths = changeCategoryUtils.get_families_requiring_sub_category_change(families, directives);
            var matching = new HashSet<string>((List<string>)FilePaths(paths));
            foreach (dynamic family in families)
            {
                if (matching.Contains((string)family.family_file_path))
                {
                    Assert.That((string)family.family_category, Is.EqualTo("Furniture Systems"));
                }
            }
        }

        [Test]
        public void GetFamiliesRequiringSubCategoryChange_UnknownSubCategory_NoFamilies()
        {
            var families = ReadSampleFamilies();
            var directives = new PythonList { SubCategoryDirective("Furniture Systems", "No Such Sub Category", "Renamed") };
            dynamic paths = changeCategoryUtils.get_families_requiring_sub_category_change(families, directives);
            Assert.That((int)paths.Count, Is.EqualTo(0));
        }

        [Test]
        public void GetFamiliesRequiringSubCategoryChange_WrongCategory_NoFamilies()
        {
            var families = ReadSampleFamilies();
            var directives = new PythonList { SubCategoryDirective("Not A Category", "<Hidden Lines>", "Renamed") };
            dynamic paths = changeCategoryUtils.get_families_requiring_sub_category_change(families, directives);
            Assert.That((int)paths.Count, Is.EqualTo(0));
        }

        [Test]
        public void GetFamiliesRequiringSubCategoryChange_NoDirectives_NoFamilies()
        {
            var families = ReadSampleFamilies();
            dynamic paths = changeCategoryUtils.get_families_requiring_sub_category_change(families, new PythonList());
            Assert.That((int)paths.Count, Is.EqualTo(0));
        }

        [Test]
        public void GetFamiliesRequiringSubCategoryChange_TwoDirectivesHittingTheSameFamily_ListedOnce()
        {
            var families = ReadSampleFamilies();
            var directives = new PythonList
            {
                SubCategoryDirective("Furniture Systems", "<Hidden Lines>", "Renamed 1"),
                SubCategoryDirective("Furniture Systems", "<Hidden Lines>", "Renamed 2")
            };
            dynamic once = changeCategoryUtils.get_families_requiring_sub_category_change(families, new PythonList { directives[0] });
            dynamic twice = changeCategoryUtils.get_families_requiring_sub_category_change(families, directives);
            Assert.That((int)twice.Count, Is.EqualTo((int)once.Count));
        }
    }
}
