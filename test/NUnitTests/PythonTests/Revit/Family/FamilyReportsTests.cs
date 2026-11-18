using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.Revit.Family
{
    /// <summary>
    /// Tests for the duHast code behind the Families panel > Reports pull down of the pyRevit toolbar:
    /// comparing library reports, removing obsolete part atom (xml) exports, creating part atom exports and reporting family types from xml files.
    /// The Revit application (ExtractPartAtomFromFamilyFile) is replaced by a fake which writes a small xml file.
    /// </summary>
    public class FamilyReportsTests
    {
        private string tempDirectory;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
            PythonEngineManager.PythonEngine.Execute(
                "class _FakeApplication(object):\n" +
                "    def __init__(self, fail=False):\n" +
                "        self.fail = fail\n" +
                "        self.calls = []\n" +
                "    def ExtractPartAtomFromFamilyFile(self, family_path, xml_path):\n" +
                "        self.calls.append((family_path, xml_path))\n" +
                "        if self.fail:\n" +
                "            raise ValueError('export failed')\n" +
                "        with open(xml_path, 'w') as f:\n" +
                "            f.write('<entry/>')\n",
                PythonEngineManager.Scope);
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory)) Directory.Delete(tempDirectory, true);
        }

        private static PythonList Py(params object[] items)
        {
            var list = new PythonList();
            foreach (var i in items) list.Add(i);
            return list;
        }

        private static PythonList PyStrings(params string[] items) => Py(items.Cast<object>().ToArray());

        private static dynamic FakeApplication(bool fail = false) => PythonEngineManager.Scope.GetVariable("_FakeApplication")(fail);

        private string Touch(string relativePath, string content = "x", DateTime? lastWrite = null)
        {
            string path = Path.Combine(tempDirectory, relativePath);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllText(path, content);
            if (lastWrite != null) File.SetLastWriteTime(path, lastWrite.Value);
            return path;
        }

        // ---------------------------------------- report_differences_in_reports ----------------------------------------

        private dynamic Differences => PythonEngineManager.Import("duHast.Revit.Family.Reporting.report_differences_in_reports");

        private static PythonList Row(string family, string category, string type, string parameter, string value) =>
            PyStrings("project.rvt", family, category, type, "date", "time", parameter, "Length", "Double", "mm", value);

        private static PythonList Header() => PyStrings("PROJECT FILE NAME", "FAMILY NAME", "CATEGORY", "TYPE NAME", "DATE REPORTED", "TIME REPORTED", "PARAMETER NAME", "PARAMETER TYPE", "PARAMETER STORAGE TYPE", "PARAMETER UNIT", "PARAMETER VALUE");

        /// <summary>A report as read by read_report: [ {report name: rows} ].</summary>
        private static PythonList Report(string name, params PythonList[] rows)
        {
            var content = new PythonList { Header() };
            foreach (var r in rows) content.Add(r);
            var dict = new PythonDictionary { [name] = content };
            return Py(dict);
        }

        private static object Key(string family, string category, string type, string parameter) =>
            new PythonTuple(new object[] { family, category, type, parameter });

        [Test]
        public void OuterJoin_ValueInBothReports_ShowsBothValues()
        {
            var a = Report("A", Row("Door", "Doors", "T1", "Width", "900"));
            var b = Report("B", Row("Door", "Doors", "T1", "Width", "1000"));
            dynamic join = Differences.outer_join_report_a_vs_b(a, b);
            dynamic values = join[Key("Door", "Doors", "T1", "Width")];
            Assert.That((string)values[0], Is.EqualTo("900"));
            Assert.That((string)values[1], Is.EqualTo("1000"), "the second column holds report B's value");
        }

        [Test]
        public void OuterJoin_KeyInOneReportOnly_OtherColumnIsEmpty()
        {
            var a = Report("A", Row("Door", "Doors", "T1", "Width", "900"));
            var b = Report("B", Row("Window", "Windows", "T1", "Height", "1200"));
            dynamic join = Differences.outer_join_report_a_vs_b(a, b);
            Assert.That((int)join.Count, Is.EqualTo(2));
            dynamic onlyA = join[Key("Door", "Doors", "T1", "Width")];
            dynamic onlyB = join[Key("Window", "Windows", "T1", "Height")];
            Assert.That((string)onlyA[0], Is.EqualTo("900"));
            Assert.That(onlyA[1], Is.Null);
            Assert.That(onlyB[0], Is.Null);
            Assert.That((string)onlyB[1], Is.EqualTo("1200"));
        }

        [Test]
        public void OuterJoin_HeaderRowIsNotPartOfTheComparison()
        {
            dynamic join = Differences.outer_join_report_a_vs_b(Report("A"), Report("B"));
            Assert.That((int)join.Count, Is.EqualTo(0));
        }

        [Test]
        public void CompareWithFurtherReport_AddsAColumn_MissingValuesAreNotAvailable()
        {
            var a = Report("A", Row("Door", "Doors", "T1", "Width", "900"), Row("Door", "Doors", "T1", "Height", "2100"));
            var b = Report("B", Row("Door", "Doors", "T1", "Width", "900"));
            var c = Report("C", Row("Door", "Doors", "T1", "Width", "950"), Row("Window", "Windows", "T1", "Height", "1200"));
            dynamic join = Differences.outer_join_report_a_vs_b(a, b);
            dynamic result = Differences.compare_outer_join_result_with_report(c, join);

            dynamic width = result[Key("Door", "Doors", "T1", "Width")];
            Assert.That((int)width.Count, Is.EqualTo(3));
            Assert.That((string)width[2], Is.EqualTo("950"));
            dynamic heightOnlyInA = result[Key("Door", "Doors", "T1", "Height")];
            Assert.That((string)heightOnlyInA[2], Is.EqualTo("N/A"), "not in the third report");
            dynamic windowOnlyInC = result[Key("Window", "Windows", "T1", "Height")];
            Assert.That(((IEnumerable<object>)windowOnlyInC).Select(o => o?.ToString()), Is.EqualTo(new[] { "N/A", "N/A", "1200" }));
        }

        private string WriteReport(string name, params string[] rows)
        {
            string path = Path.Combine(tempDirectory, name + ".csv");
            var lines = new List<string> { "PROJECT FILE NAME,FAMILY NAME,CATEGORY,TYPE NAME,DATE REPORTED,TIME REPORTED,PARAMETER NAME,PARAMETER TYPE,PARAMETER STORAGE TYPE,PARAMETER UNIT,PARAMETER VALUE" };
            lines.AddRange(rows);
            File.WriteAllLines(path, lines);
            return path;
        }

        [Test]
        public void ReadReport_KeyedByTheFileNameWithoutExtension()
        {
            string path = WriteReport("Library_2024", "p.rvt,Door,Doors,T1,d,t,Width,Length,Double,mm,900");
            dynamic result = Differences.read_report(path);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            dynamic report = result.result[0];
            Assert.That((bool)report.ContainsKey("Library_2024"), Is.True);
            Assert.That((int)report["Library_2024"].Count, Is.EqualTo(2), "header and one row");
        }

        [Test]
        public void ReadReport_MissingFile_Fails()
        {
            dynamic result = Differences.read_report(Path.Combine(tempDirectory, "nothere.csv"));
            Assert.That((bool)result.status, Is.False);
        }

        [Test]
        public void CompareFamilyReports_NeedsAtLeastTwoReports()
        {
            Assert.That(() => Differences.compare_family_reports_outer_join(PyStrings(WriteReport("A"))), Throws.Exception);
        }

        [Test]
        public void CompareFamilyReports_TwoReports_ReportsTheDifferentValues()
        {
            string a = WriteReport("A", "p.rvt,Door,Doors,T1,d,t,Width,Length,Double,mm,900");
            string b = WriteReport("B", "p.rvt,Door,Doors,T1,d,t,Width,Length,Double,mm,1000");
            dynamic result = Differences.compare_family_reports_outer_join(PyStrings(a, b));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            dynamic values = result.result[Key("Door", "Doors", "T1", "Width")];
            Assert.That(((IEnumerable<object>)values).Select(o => o?.ToString()), Is.EqualTo(new[] { "900", "1000" }));
        }

        [Test]
        public void CompareFamilyReports_ThreeReports_OneColumnPerReport()
        {
            string a = WriteReport("A", "p.rvt,Door,Doors,T1,d,t,Width,Length,Double,mm,900");
            string b = WriteReport("B", "p.rvt,Door,Doors,T1,d,t,Width,Length,Double,mm,1000");
            string c = WriteReport("C");
            dynamic result = Differences.compare_family_reports_outer_join(PyStrings(a, b, c));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            dynamic values = result.result[Key("Door", "Doors", "T1", "Width")];
            Assert.That(((IEnumerable<object>)values).Select(o => o?.ToString()), Is.EqualTo(new[] { "900", "1000", "N/A" }));
        }

        [Test]
        public void CompareFamilyReports_UnreadableReport_FailsWithItsMessage()
        {
            dynamic result = Differences.compare_family_reports_outer_join(PyStrings(WriteReport("A"), Path.Combine(tempDirectory, "nothere.csv")));
            Assert.That((bool)result.status, Is.False);
        }

        // ---------------------------------------- xml_remove_obsolete_exports ----------------------------------------

        private dynamic RemoveObsolete => PythonEngineManager.ImportFrom("duHast.Revit.Family.Utility.xml_remove_obsolete_exports", "remove_obsolete_part_atom_exports");

        [Test]
        public void RemoveObsoleteExports_DeletesXmlWithoutFamily_KeepsTheRest()
        {
            string keptXml = Touch(@"lib\A.xml");
            Touch(@"lib\A.rfa");
            string orphan = Touch(@"lib\B.xml");
            string orphanInSubDirectory = Touch(@"lib\sub\C.xml");
            string familyOnly = Touch(@"lib\D.rfa");

            dynamic result = RemoveObsolete(PyStrings(Path.Combine(tempDirectory, "lib")));

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(File.Exists(keptXml), Is.True);
            Assert.That(File.Exists(orphan), Is.False);
            Assert.That(File.Exists(orphanInSubDirectory), Is.False);
            Assert.That(File.Exists(familyOnly), Is.True);
            Assert.That((string)result.message, Does.Contain("Deleted"));
        }

        [Test]
        public void RemoveObsoleteExports_SeveralDirectories()
        {
            string orphanOne = Touch(@"one\A.xml");
            string orphanTwo = Touch(@"two\B.xml");
            RemoveObsolete(PyStrings(Path.Combine(tempDirectory, "one"), Path.Combine(tempDirectory, "two")));
            Assert.That(File.Exists(orphanOne) || File.Exists(orphanTwo), Is.False);
        }

        [Test]
        public void RemoveObsoleteExports_NothingToDelete_Succeeds()
        {
            Touch(@"lib\A.rfa");
            dynamic result = RemoveObsolete(PyStrings(Path.Combine(tempDirectory, "lib")));
            Assert.That((bool)result.status, Is.True, (string)result.message);
        }

        [Test]
        public void RemoveObsoleteExports_OnlyXmlFilesAreConsidered()
        {
            string other = Touch(@"lib\notes.txt");
            RemoveObsolete(PyStrings(Path.Combine(tempDirectory, "lib")));
            Assert.That(File.Exists(other), Is.True);
        }

        // ---------------------------------------- xml_create_atom_exports ----------------------------------------

        private dynamic AtomExports => PythonEngineManager.Import("duHast.Revit.Family.Utility.xml_create_atom_exports");

        [Test]
        public void GetFamiliesAndXmlFromDirectory_ListsFilesByExtension_IgnoringBackups()
        {
            Touch(@"lib\A.rfa");
            Touch(@"lib\A.0001.rfa");     // Revit back up file
            Touch(@"lib\A.xml");
            string directory = Path.Combine(tempDirectory, "lib");

            var families = ((IEnumerable<object>)AtomExports.get_families_from_directory(directory)).Select(f => Path.GetFileName((string)((dynamic)f).name)).ToList();
            var xmls = ((IEnumerable<object>)AtomExports.get_xml_files_from_directory(directory)).Select(f => Path.GetFileName((string)((dynamic)f).name)).ToList();

            Assert.That(families, Is.EqualTo(new[] { "A.rfa" }));
            Assert.That(xmls, Is.EqualTo(new[] { "A.xml" }));
        }

        private dynamic FileItems(string directory, string extension) =>
            extension == ".rfa" ? AtomExports.get_families_from_directory(directory) : AtomExports.get_xml_files_from_directory(directory);

        private List<string> FamiliesRequiringUpdate(string directory)
        {
            dynamic result = AtomExports.get_families_requiring_update(FileItems(directory, ".rfa"), FileItems(directory, ".xml"));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            return ((IEnumerable<object>)result.result).Select(o => Path.GetFileName((string)o)).OrderBy(n => n).ToList();
        }

        [Test]
        public void FamiliesRequiringUpdate_FamilyWithoutXml()
        {
            Touch(@"lib\A.rfa");
            Assert.That(FamiliesRequiringUpdate(Path.Combine(tempDirectory, "lib")), Is.EqualTo(new[] { "A.rfa" }));
        }

        [Test]
        public void FamiliesRequiringUpdate_XmlOlderThanFamily()
        {
            var now = DateTime.Now;
            Touch(@"lib\A.xml", "x", now.AddHours(-2));
            Touch(@"lib\A.rfa", "x", now.AddHours(-1));
            Assert.That(FamiliesRequiringUpdate(Path.Combine(tempDirectory, "lib")), Is.EqualTo(new[] { "A.rfa" }));
        }

        [Test]
        public void FamiliesRequiringUpdate_XmlOlderThanCatalogueFile()
        {
            var now = DateTime.Now;
            Touch(@"lib\A.rfa", "x", now.AddHours(-3));
            Touch(@"lib\A.xml", "x", now.AddHours(-2));
            Touch(@"lib\A.txt", "x", now.AddHours(-1));
            Assert.That(FamiliesRequiringUpdate(Path.Combine(tempDirectory, "lib")), Is.EqualTo(new[] { "A.rfa" }));
        }

        [Test]
        public void FamiliesRequiringUpdate_UpToDate_NothingToDo()
        {
            var now = DateTime.Now;
            Touch(@"lib\A.rfa", "x", now.AddHours(-3));
            Touch(@"lib\A.txt", "x", now.AddHours(-2));
            Touch(@"lib\A.xml", "x", now.AddHours(-1));
            Touch(@"lib\B.rfa", "x", now.AddHours(-3));
            Touch(@"lib\B.xml", "x", now.AddHours(-1));
            Assert.That(FamiliesRequiringUpdate(Path.Combine(tempDirectory, "lib")), Is.Empty);
        }

        [Test]
        public void CheckFileItemExists_ByName()
        {
            string a = Touch(@"lib\A.rfa");
            var items = AtomExports.get_families_from_directory(Path.Combine(tempDirectory, "lib"));
            Assert.That((bool)AtomExports.check_file_item_exists(items, a), Is.True);
            Assert.That((bool)AtomExports.check_file_item_exists(items, Path.Combine(tempDirectory, "lib", "B.rfa")), Is.False);
        }

        [Test]
        public void CopyFamilyToLocalDirectory_CopiesTheFamilyAndItsCatalogueFile()
        {
            string family = Touch(@"lib\A.rfa", "family");
            Touch(@"lib\A.txt", "catalogue");
            string local = Path.Combine(tempDirectory, "local", "nested");

            string copy = AtomExports.copy_family_to_local_directory(family, local);

            Assert.That(copy, Is.EqualTo(Path.Combine(local, "A.rfa")));
            Assert.That(File.ReadAllText(copy), Is.EqualTo("family"));
            Assert.That(File.ReadAllText(Path.Combine(local, "A.txt")), Is.EqualTo("catalogue"));
        }

        [Test]
        public void CopyFamilyToLocalDirectory_NoCatalogueFile_CopiesTheFamilyOnly()
        {
            string family = Touch(@"lib\A.rfa");
            string local = Path.Combine(tempDirectory, "local");
            AtomExports.copy_family_to_local_directory(family, local);
            Assert.That(Directory.GetFiles(local).Select(Path.GetFileName), Is.EqualTo(new[] { "A.rfa" }));
        }

        [Test]
        public void CopyXmlFileToOriginalDirectory_CopiesNextToTheOriginalFamily()
        {
            string family = Touch(@"lib\A.rfa");
            string local = Path.Combine(tempDirectory, "local");
            Touch(@"local\A.xml", "xml");

            string copied = AtomExports.copy_xml_file_to_original_directory(family, local);

            Assert.That(copied, Is.EqualTo(Path.Combine(tempDirectory, "lib", "A.xml")));
            Assert.That(File.ReadAllText(copied), Is.EqualTo("xml"));
        }

        [Test]
        public void CopyXmlFileToOriginalDirectory_NoXmlFile_ReturnsNone()
        {
            string family = Touch(@"lib\A.rfa");
            Assert.That(AtomExports.copy_xml_file_to_original_directory(family, Path.Combine(tempDirectory, "local")), Is.Null);
        }

        [Test]
        public void WriteDataToXmlFile_AsksTheApplicationToExtractThePartAtom()
        {
            dynamic app = FakeApplication();
            string xml = Path.Combine(tempDirectory, "A.xml");
            dynamic result = AtomExports.write_data_to_xml_file(app, @"C:\lib\A.rfa", xml);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(File.Exists(xml), Is.True);
            Assert.That((string)app.calls[0][0], Is.EqualTo(@"C:\lib\A.rfa"));
        }

        [Test]
        public void WriteDataToXmlFile_ApplicationFails_ReportsIt()
        {
            dynamic result = AtomExports.write_data_to_xml_file(FakeApplication(true), @"C:\lib\A.rfa", Path.Combine(tempDirectory, "A.xml"));
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("export failed"));
        }

        [Test]
        public void CreateXmlFile_WritesTheXmlNextToTheFamily()
        {
            string family = Touch(@"lib\A.rfa");
            dynamic result = AtomExports.create_xml_file(FakeApplication(), family);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(File.Exists(Path.Combine(tempDirectory, "lib", "A.xml")), Is.True);
        }

        [Test]
        public void CreateXmlFile_ApplicationFails_Fails()
        {
            string family = Touch(@"lib\A.rfa");
            dynamic result = AtomExports.create_xml_file(FakeApplication(true), family);
            Assert.That((bool)result.status, Is.False);
            Assert.That(File.Exists(Path.Combine(tempDirectory, "lib", "A.xml")), Is.False);
        }

        private dynamic XmlWriter(bool succeed)
        {
            PythonEngineManager.Scope.SetVariable("_succeed", succeed);
            PythonEngineManager.PythonEngine.Execute(
                "import duHast.Utilities.Objects.result as _res\n" +
                "def _write_xml(path):\n" +
                "    r = _res.Result()\n" +
                "    if not _succeed:\n" +
                "        r.update_sep(False, 'cannot write')\n" +
                "        return r\n" +
                "    with open(path, 'w') as f:\n" +
                "        f.write('<entry><title>Chair</title></entry>')\n" +
                "    r.update_sep(True, 'written')\n" +
                "    return r\n",
                PythonEngineManager.Scope);
            return PythonEngineManager.Scope.GetVariable("_write_xml");
        }

        [Test]
        public void WriteAndReadBack_ReturnsTheXmlDocument()
        {
            string xml = Path.Combine(tempDirectory, "A.xml");
            dynamic result = AtomExports.write_data_to_xml_file_and_read_it_back(XmlWriter(true), xml);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(result.result, Is.Not.Null);
            Assert.That(File.Exists(xml), Is.True, "the file stays");
        }

        [Test]
        public void WriteAndReadBack_WriterFails_Fails()
        {
            dynamic result = AtomExports.write_data_to_xml_file_and_read_it_back(XmlWriter(false), Path.Combine(tempDirectory, "A.xml"));
            Assert.That((bool)result.status, Is.False);
        }

        [Test]
        public void WriteToTempFileAndReadBack_ReturnsTheXmlDocument_AndRemovesTheTempFile()
        {
            dynamic result = AtomExports.write_data_to_temp_xml_file_and_read_it_back(XmlWriter(true));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(result.result, Is.Not.Null);
        }

        [Test]
        public void WriteToTempFileAndReadBack_WriterFails_Fails()
        {
            dynamic result = AtomExports.write_data_to_temp_xml_file_and_read_it_back(XmlWriter(false));
            Assert.That((bool)result.status, Is.False);
        }

        // ---------------------------------------- create_family_xml_files ----------------------------------------

        [Test]
        public void CreateFamilyXmlFiles_CreatesAnXmlFilePerFamilyWithoutOne()
        {
            Touch(@"lib\A.rfa");
            Touch(@"lib\sub\B.rfa");
            dynamic app = FakeApplication();

            dynamic result = AtomExports.create_family_xml_files(app, PyStrings(Path.Combine(tempDirectory, "lib")));

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(File.Exists(Path.Combine(tempDirectory, "lib", "A.xml")), Is.True);
            Assert.That((int)app.calls.Count, Is.GreaterThanOrEqualTo(1));
        }

        [Test]
        public void CreateFamilyXmlFiles_SecondRun_OnlyUpdatesWhatChanged()
        {
            var old = DateTime.Now.AddHours(-3);
            Touch(@"lib\A.rfa", "x", old);
            Touch(@"lib\B.rfa", "x", old);
            dynamic first = FakeApplication();
            AtomExports.create_family_xml_files(first, PyStrings(Path.Combine(tempDirectory, "lib")));
            Assert.That((int)first.calls.Count, Is.EqualTo(2));

            dynamic second = FakeApplication();
            AtomExports.create_family_xml_files(second, PyStrings(Path.Combine(tempDirectory, "lib")));
            Assert.That((int)second.calls.Count, Is.EqualTo(0), "xml files are up to date");

            File.SetLastWriteTime(Path.Combine(tempDirectory, "lib", "A.rfa"), DateTime.Now.AddMinutes(5));
            dynamic third = FakeApplication();
            AtomExports.create_family_xml_files(third, PyStrings(Path.Combine(tempDirectory, "lib")));
            Assert.That((int)third.calls.Count, Is.EqualTo(1), "only the family saved after its xml was written");
        }

        [Test]
        public void CreateFamilyXmlFiles_MissingDirectory_IsSkippedAndReported()
        {
            Touch(@"lib\A.rfa");
            dynamic result = AtomExports.create_family_xml_files(FakeApplication(), PyStrings(Path.Combine(tempDirectory, "missing"), Path.Combine(tempDirectory, "lib")));
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("does not exist"));
            Assert.That(File.Exists(Path.Combine(tempDirectory, "lib", "A.xml")), Is.True, "the other directory is still processed");
        }

        [Test]
        public void CreateFamilyXmlFiles_ExportFails_IsReported()
        {
            Touch(@"lib\A.rfa");
            dynamic result = AtomExports.create_family_xml_files(FakeApplication(true), PyStrings(Path.Combine(tempDirectory, "lib")));
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("export failed"));
        }

        [Test]
        public void CreateFamilyXmlFiles_DirectoriesNotAList_Throws()
        {
            Assert.That(() => AtomExports.create_family_xml_files(FakeApplication(), "not a list"), Throws.Exception);
        }

        [Test]
        public void CreateFamilyXmlFiles_UseTempDirectory_XmlEndsUpNextToTheOriginalAndNoTempCopyIsLeft()
        {
            string family = Touch(@"lib\A.rfa", "family");
            dynamic app = FakeApplication();

            dynamic result = AtomExports.create_family_xml_files(app, PyStrings(Path.Combine(tempDirectory, "lib")), null, true);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(File.Exists(Path.Combine(tempDirectory, "lib", "A.xml")), Is.True);
            Assert.That((string)app.calls[0][0], Is.Not.EqualTo(family), "the export read the local copy");
            Assert.That(File.ReadAllText(family), Is.EqualTo("family"));
        }

        [Test]
        public void CreateFamilyXmlFiles_LocalDirectoryMapper_XmlEndsUpNextToTheOriginal()
        {
            Touch(@"lib\A.rfa");
            string local = Path.Combine(tempDirectory, "local");
            string lib = Path.Combine(tempDirectory, "lib");
            var mapper = new PythonDictionary { [lib] = local };

            dynamic result = AtomExports.create_family_xml_files(FakeApplication(), PyStrings(lib), mapper);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(File.Exists(Path.Combine(lib, "A.xml")), Is.True);
            Assert.That(File.Exists(Path.Combine(local, "A.rfa")), Is.True);
        }

        // ---------------------------------------- report_fam_types_from_XML ----------------------------------------

        private dynamic XmlReport => PythonEngineManager.Import("duHast.Revit.Family.Reporting.report_fam_types_from_XML");

        [Test]
        public void BuildReport_CollectsTheRowsOfEveryManager()
        {
            PythonEngineManager.PythonEngine.Execute(
                "class _Manager(object):\n" +
                "    def __init__(self, rows):\n" +
                "        self.rows = rows\n" +
                "    def get_report_data(self):\n" +
                "        return self.rows\n",
                PythonEngineManager.Scope);
            dynamic manager = PythonEngineManager.Scope.GetVariable("_Manager");
            dynamic result = XmlReport.build_report(Py(manager(Py(PyStrings("a"), PyStrings("b"))), manager(Py(PyStrings("c")))));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(3));
        }

        [Test]
        public void BuildReport_ManagerWithoutReportData_Fails()
        {
            dynamic result = XmlReport.build_report(Py("not a manager"));
            Assert.That((bool)result.status, Is.False);
        }

        [Test]
        public void GetFamilyTypeData_NoXmlFiles_Fails()
        {
            Touch(@"lib\A.rfa");
            dynamic result = XmlReport.get_family_type_data_from_library_xml(PyStrings(Path.Combine(tempDirectory, "lib")));
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("No XML files found"));
        }

        [Test]
        public void GetFamilyTypeData_ProgressCallbackOfTheWrongType_Throws()
        {
            Assert.That(() => XmlReport.get_family_type_data_from_library_xml(PyStrings(tempDirectory), "not a progress callback"), Throws.Exception);
        }

        [Test]
        public void GetFamilyTypeData_PartAtomExports_OneReportRowPerParameterOfEveryType()
        {
            string library = Path.Combine(tempDirectory, "lib");
            Directory.CreateDirectory(library);
            foreach (string file in Directory.GetFiles(Path.Combine(PythonRunner.GetTestDataPath(), "XMLData_01"), "*.xml"))
            {
                File.Copy(file, Path.Combine(library, Path.GetFileName(file)));
            }

            dynamic result = XmlReport.get_family_type_data_from_library_xml(PyStrings(library));

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.GreaterThan(0));
            dynamic header = PythonEngineManager.ImportFrom("duHast.Revit.Family.Reporting.families_report_header", "LIBRARY_FAMILIES_HEADER");
            foreach (dynamic row in (IEnumerable<object>)result.result)
            {
                Assert.That((int)row.Count, Is.EqualTo((int)header.Count), "a row has one value per report column");
            }
        }
    }
}
