using IronPython.Runtime;
using PythonTests.Setup;
using System.Text;

namespace PythonTests.PyRevitToolbar
{
    /// <summary>
    /// Tests for the logic behind the buttons of the pyRevit toolbar's Families panel > Catalogue Files pull down:
    /// DefaultCatalogueFileType and DeleteParametersFromCatalogueFile (ExportCatalogueFile only asks for a folder, the export itself is duHast:
    /// see FamilyTypesCatalogueTests).
    /// The pyRevit dialogs are not tested: where the code asks the user something the answer comes from a patched function.
    /// The family document is a fake from revit_test_doubles, the output the recording output of the pyrevit stand-in.
    /// </summary>
    public class CatalogueFilesPulldownTests
    {
        private const string CleanerModule = "families.cleanupCatalogueFiles.cleaner";
        private const string DefaultTypeModule = "families.defaultCatalogueFileType";

        private string tempDirectory;
        private dynamic doubles;
        private readonly List<(string module, string name, object original)> patched = new();

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
            doubles = PythonEngineManager.Import("revit_test_doubles");
        }

        [TearDown]
        public void TearDown()
        {
            foreach (var (module, name, original) in patched)
            {
                PythonEngineManager.Scope.SetVariable("_restore_value", original);
                PythonEngineManager.PythonEngine.Execute($"import {module} as _m\n_m.{name} = _restore_value\n", PythonEngineManager.Scope);
            }
            patched.Clear();
            if (Directory.Exists(tempDirectory)) Directory.Delete(tempDirectory, true);
        }

        private static PythonList Py(params object[] items)
        {
            var list = new PythonList();
            foreach (var i in items) list.Add(i);
            return list;
        }

        private static PythonList PyStrings(IEnumerable<string> items) => Py(items.Cast<object>().ToArray());

        private static PythonList PyRows(params string[][] rows) => Py(rows.Select(r => (object)PyStrings(r)).ToArray());

        private static List<string> ToList(dynamic pythonList) => ((IEnumerable<object>)pythonList).Select(o => (string)o).ToList();

        private static List<List<string>> ToRows(dynamic rows) => ((IEnumerable<object>)rows).Select(r => ToList(r)).ToList();

        private dynamic Cleaner => PythonEngineManager.Import(CleanerModule);

        private dynamic NewOutput() => PythonEngineManager.Import("pyrevit.script").RecordingOutput();

        /// <summary>Replaces a function of a module for the duration of the test.</summary>
        private void Patch(string module, string name, string pythonDefinition)
        {
            PythonEngineManager.PythonEngine.Execute($"import {module} as _m\n_original = _m.{name}\n", PythonEngineManager.Scope);
            patched.Add((module, name, PythonEngineManager.Scope.GetVariable("_original")));
            PythonEngineManager.PythonEngine.Execute(pythonDefinition + $"\n_m.{name} = _fake\n", PythonEngineManager.Scope);
        }

        /// <summary>The user 'picks' this catalogue file (null: picks nothing).</summary>
        private void ChooseCatalogueFile(string? file)
        {
            PythonEngineManager.Import(CleanerModule);
            PythonEngineManager.Scope.SetVariable("_chosen_file", file);
            Patch(CleanerModule, "get_file_path_from_user", "def _fake(forms, title, file_extension, multi_file=False):\n    return _chosen_file\n");
        }

        /// <summary>The user answers the 'delete all types?' question with this option (null: closes the dialog).</summary>
        private void AnswerDeleteAllTypesQuestion(string? answer)
        {
            PythonEngineManager.Import(DefaultTypeModule);
            PythonEngineManager.Scope.SetVariable("_answer", answer);
            Patch(DefaultTypeModule, "get_user_options", "def _fake(forms):\n    return _answer\n");
        }

        // ================================================= DeleteParametersFromCatalogueFile: helper functions =================================================

        [TestCase("Width##length##millimeters", "Width")]
        [TestCase("Width[1]", "Width")]
        [TestCase("Door_Panel_Width##length##millimeters", "Door_Panel_Width")]
        [TestCase("Plain", "Plain")]
        [TestCase("", "")]
        public void ExtractParameterName(string header, string expected)
        {
            Assert.That((string)Cleaner.extract_parameter_name(header), Is.EqualTo(expected));
        }

        [Test]
        public void GetColumnIndicesToIgnore_MatchesByParameterName_SkippingTheTypeNameColumn()
        {
            var header = PyStrings(new[] { "", "Width##length##millimeters", "Height##length##millimeters", "Mark##other##" });
            dynamic indices = Cleaner.get_column_indices_to_ignore(PyStrings(new[] { "Height", "Mark", "NotThere" }), header);
            Assert.That(((IEnumerable<object>)indices).Select(Convert.ToInt32), Is.EqualTo(new[] { 2, 3 }));
        }

        [Test]
        public void GetColumnIndicesToIgnore_HeaderWithoutTypeMarker_DoesNotThrow()
        {
            // a header cell without '[' or '#' used to raise ValueError
            var header = PyStrings(new[] { "", "Width##length##millimeters", "Plain" });
            dynamic indices = Cleaner.get_column_indices_to_ignore(PyStrings(new[] { "Plain" }), header);
            Assert.That(((IEnumerable<object>)indices).Select(Convert.ToInt32), Is.EqualTo(new[] { 2 }));
        }

        [Test]
        public void FilterOriginalCatalogueData_RemovesTheColumnsInEveryRow()
        {
            var rows = PyRows(new[] { "", "a", "b", "c" }, new[] { "T1", "1", "2", "3" });
            dynamic filtered = Cleaner.filter_original_catalogue_data(rows, Py(1, 3));
            Assert.That(ToRows(filtered), Is.EqualTo(new List<List<string>> { new() { "", "b" }, new() { "T1", "2" } }));
        }

        [Test]
        public void FilterOriginalCatalogueData_NothingToRemove_KeepsAllColumns()
        {
            var rows = PyRows(new[] { "", "a" }, new[] { "T1", "1" });
            dynamic filtered = Cleaner.filter_original_catalogue_data(rows, Py());
            Assert.That(ToRows(filtered), Is.EqualTo(new List<List<string>> { new() { "", "a" }, new() { "T1", "1" } }));
        }

        [Test]
        public void ReorderColumns_DesiredOrderFirst_RestAlphabetical_TypeNameColumnStays()
        {
            var data = PyRows(
                new[] { "", "Zeta##x", "Alpha##x", "Door_Panel_Width##x", "Clear_Opening_Width##x" },
                new[] { "T1", "z", "a", "d", "c" });
            dynamic sorted = Cleaner.reorder_columns(data, PyStrings(new[] { "Door_Panel_Width", "Clear_Opening_Width" }));
            var result = ToRows(sorted);
            Assert.That(result[0], Is.EqualTo(new List<string> { "", "Door_Panel_Width##x", "Clear_Opening_Width##x", "Alpha##x", "Zeta##x" }));
            Assert.That(result[1], Is.EqualTo(new List<string> { "T1", "d", "c", "a", "z" }), "values follow their columns");
        }

        [Test]
        public void ReorderColumns_DesiredParameterMissing_IsSkipped()
        {
            var data = PyRows(new[] { "", "B##x", "A##x" }, new[] { "T1", "b", "a" });
            dynamic sorted = Cleaner.reorder_columns(data, PyStrings(new[] { "Not_There" }));
            Assert.That(ToRows(sorted)[0], Is.EqualTo(new List<string> { "", "A##x", "B##x" }));
        }

        [Test]
        public void ReorderColumns_HeaderOnly_Works()
        {
            dynamic sorted = Cleaner.reorder_columns(PyRows(new[] { "", "B##x", "A##x" }), PyStrings(new[] { "B" }));
            Assert.That(ToRows(sorted)[0], Is.EqualTo(new List<string> { "", "B##x", "A##x" }));
        }

        [Test]
        public void GetParameterNames_ReturnsTheDefinitionNames()
        {
            var parameters = Py(doubles.FakeParameter("Width"), doubles.FakeParameter("Height", true));
            Assert.That(ToList(Cleaner.get_parameter_names(parameters)), Is.EqualTo(new[] { "Width", "Height" }));
        }

        [Test]
        public void FilterParametersByFormulaDriven_KeepsOneKindOrTheOther()
        {
            var parameters = Py(doubles.FakeParameter("Driven", false, true), doubles.FakeParameter("Free", false, false));
            Assert.That(ToList(Cleaner.get_parameter_names(Cleaner._filter_parameters_by_formula_driven(parameters, true))), Is.EqualTo(new[] { "Driven" }));
            Assert.That(ToList(Cleaner.get_parameter_names(Cleaner._filter_parameters_by_formula_driven(parameters, false))), Is.EqualTo(new[] { "Free" }));
        }

        [Test]
        public void CheckUtf16LeBom_DetectsTheByteOrderMark()
        {
            string withBom = Path.Combine(tempDirectory, "bom.txt");
            string without = Path.Combine(tempDirectory, "nobom.txt");
            File.WriteAllText(withBom, "abc", Encoding.Unicode);
            File.WriteAllText(without, "abc", new UTF8Encoding(false));
            Assert.That((bool)Cleaner.check_utf16le_bom(withBom), Is.True);
            Assert.That((bool)Cleaner.check_utf16le_bom(without), Is.False);
        }

        [Test]
        public void PrintCleanData_OneFormatPerColumn()
        {
            dynamic output = NewOutput();
            var data = PyRows(new[] { "", "A", "B", "C" }, new[] { "T1", "1", "2", "3" });
            Cleaner._print_clean_data(data, output);
            dynamic table = output.tables[0];
            Assert.That((int)table["formats"].Count, Is.EqualTo(4), "one format per column");
            Assert.That(ToList(table["columns"]), Is.EqualTo(new[] { "", "A", "B", "C" }));
            Assert.That((int)table["table_data"].Count, Is.EqualTo(1));
        }

        // ================================================= DeleteParametersFromCatalogueFile: the clean up =================================================

        private string WriteCatalogueFile(string name = "Door.txt")
        {
            string file = Path.Combine(tempDirectory, name);
            File.WriteAllText(file,
                ",Width##length##millimeters,Height##length##millimeters,Door_Panel_Width##length##millimeters,Mark##other##\n" +
                "Type A,900,2100,40,A1\n" +
                "Type B,1000,2200,45,B1\n",
                Encoding.Unicode);
            return file;
        }

        private dynamic CatalogueFamilyDoc() =>
            doubles.FakeFamilyDoc("Door.rfa", "", null, null,
                Py(
                    doubles.FakeParameter("Width"),                      // type parameter, kept
                    doubles.FakeParameter("Height", false, true),        // type parameter driven by a formula, removed
                    doubles.FakeParameter("Door_Panel_Width"),           // type parameter, kept and sorted first
                    doubles.FakeParameter("Mark", true)),                // instance parameter, removed
                "Generic Models", Py("Type A", "Type B"));

        private static string[] Lines(string file) =>
            File.ReadAllText(file, Encoding.Unicode).Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

        [Test]
        public void Clean_RemovesInstanceAndFormulaDrivenColumns_SortsTheRest_WritesNewFile()
        {
            string file = WriteCatalogueFile();
            ChooseCatalogueFile(file);
            dynamic output = NewOutput();

            dynamic result = Cleaner.clean_up_catalogue_file(CatalogueFamilyDoc(), output, null);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            string cleaned = Path.Combine(tempDirectory, "Door__.txt");
            Assert.That(File.Exists(cleaned), Is.True, "written next to the original with the suffix __");
            var lines = Lines(cleaned);
            Assert.That(lines[0].TrimStart('﻿'), Is.EqualTo(",Door_Panel_Width##length##millimeters,Width##length##millimeters"));
            Assert.That(lines[1], Is.EqualTo("Type A,40,900"));
            Assert.That(lines[2], Is.EqualTo("Type B,45,1000"));
            Assert.That(File.ReadAllText(file, Encoding.Unicode), Does.Contain("Height"), "the original is not touched");
            Assert.That((int)output.tables.Count, Is.EqualTo(1), "the cleaned data is shown as a table");
        }

        [Test]
        public void Clean_KeepsTheUtf16ByteOrderMark()
        {
            ChooseCatalogueFile(WriteCatalogueFile());
            Cleaner.clean_up_catalogue_file(CatalogueFamilyDoc(), NewOutput(), null);
            byte[] bytes = File.ReadAllBytes(Path.Combine(tempDirectory, "Door__.txt"));
            Assert.That(bytes.Take(2).ToArray(), Is.EqualTo(new byte[] { 0xFF, 0xFE }));
        }

        [Test]
        public void Clean_NotAFamilyDocument_WritesNothing()
        {
            dynamic doc = CatalogueFamilyDoc();
            doc.IsFamilyDocument = false;
            ChooseCatalogueFile(WriteCatalogueFile());
            dynamic result = Cleaner.clean_up_catalogue_file(doc, NewOutput(), null);
            Assert.That((string)result.message, Does.Contain("not a family"));
            Assert.That(File.Exists(Path.Combine(tempDirectory, "Door__.txt")), Is.False);
        }

        [Test]
        public void Clean_TargetFileAlreadyExists_FailsAndKeepsIt()
        {
            string existing = Path.Combine(tempDirectory, "Door__.txt");
            File.WriteAllText(existing, "keep me");
            ChooseCatalogueFile(WriteCatalogueFile());
            dynamic result = Cleaner.clean_up_catalogue_file(CatalogueFamilyDoc(), NewOutput(), null);
            Assert.That((bool)result.status, Is.False);
            Assert.That(File.ReadAllText(existing), Is.EqualTo("keep me"));
        }

        [Test]
        public void Clean_FamilyWithoutParametersToRemove_StillSortsColumns()
        {
            string file = Path.Combine(tempDirectory, "Plain.txt");
            File.WriteAllText(file, ",Zeta##x##y,Alpha##x##y\nT1,z,a\n", Encoding.Unicode);
            dynamic doc = doubles.FakeFamilyDoc("Plain.rfa", "", null, null, Py(doubles.FakeParameter("Zeta"), doubles.FakeParameter("Alpha")), "Generic Models", Py("T1"));
            ChooseCatalogueFile(file);

            dynamic result = Cleaner.clean_up_catalogue_file(doc, NewOutput(), null);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            var lines = Lines(Path.Combine(tempDirectory, "Plain__.txt"));
            Assert.That(lines[0].TrimStart('﻿'), Is.EqualTo(",Alpha##x##y,Zeta##x##y"));
            Assert.That(lines[1], Is.EqualTo("T1,a,z"));
        }

        // ================================================= DefaultCatalogueFileType =================================================

        private dynamic DefaultTypeEntry => PythonEngineManager.ImportFrom(DefaultTypeModule, "default_catalogue_file_type_entry");

        private dynamic FamilyWithTypes(params string[] typeNames) =>
            doubles.FakeFamilyDoc("Door.rfa", "", null, null, null, "Generic Models", PyStrings(typeNames));

        [Test]
        public void DefaultType_Confirmed_CreatesTheReferToCatalogFileTypeAndDeletesTheOthers()
        {
            AnswerDeleteAllTypesQuestion("Yes");
            dynamic doc = FamilyWithTypes("Type A", "Type B", "Type C");
            dynamic result = DefaultTypeEntry(doc, NewOutput(), null);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(ToList(doc.FamilyManager.type_names), Is.EqualTo(new[] { "Refer To Catalog File" }));
        }

        [TestCase("Oh No, Get me out of here!")]
        [TestCase(null)]
        public void DefaultType_UserDeclinesOrCloses_ChangesNothing(string? answer)
        {
            AnswerDeleteAllTypesQuestion(answer);
            dynamic doc = FamilyWithTypes("Type A", "Type B");
            dynamic result = DefaultTypeEntry(doc, NewOutput(), null);
            Assert.That((bool)result.status, Is.False);
            Assert.That(ToList(doc.FamilyManager.type_names), Is.EqualTo(new[] { "Type A", "Type B" }));
        }

        [Test]
        public void DefaultType_TypeAlreadyThere_FailsWithoutDeletingAnything()
        {
            AnswerDeleteAllTypesQuestion("Yes");
            dynamic doc = FamilyWithTypes("Refer To Catalog File", "Type B");
            dynamic result = DefaultTypeEntry(doc, NewOutput(), null);
            Assert.That((bool)result.status, Is.False);
            Assert.That(ToList(doc.FamilyManager.type_names), Is.EqualTo(new[] { "Refer To Catalog File", "Type B" }));
        }

        [Test]
        public void DefaultType_NotAFamilyDocument_Fails()
        {
            AnswerDeleteAllTypesQuestion("Yes");
            dynamic doc = FamilyWithTypes("Type A", "Type B");
            doc.IsFamilyDocument = false;
            dynamic result = DefaultTypeEntry(doc, NewOutput(), null);
            Assert.That((bool)result.status, Is.False);
            Assert.That(ToList(doc.FamilyManager.type_names), Is.EqualTo(new[] { "Type A", "Type B" }));
        }

        [Test]
        public void DefaultType_FamilyWithASingleType_EndsWithOnlyTheDefaultType()
        {
            AnswerDeleteAllTypesQuestion("Yes");
            dynamic doc = FamilyWithTypes("Type A");
            dynamic result = DefaultTypeEntry(doc, NewOutput(), null);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(ToList(doc.FamilyManager.type_names), Is.EqualTo(new[] { "Refer To Catalog File" }));
        }
    }
}
