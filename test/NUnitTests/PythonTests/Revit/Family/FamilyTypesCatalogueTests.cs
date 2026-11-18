using IronPython.Runtime;
using PythonTests.Setup;
using System.Text;

namespace PythonTests.Revit.Family
{
    /// <summary>
    /// Tests for duHast.Revit.Family.family_types_catalogue: the type filters, the parameter order, writing the catalogue file and the export
    /// of a family's types to a catalogue file (the logic behind the pyRevit toolbar's "Export Catalogue File" button).
    /// Reading the type data needs a part atom export from Revit: that one function is replaced with a fake returning prepared storage objects.
    /// </summary>
    public class FamilyTypesCatalogueTests
    {
        private const string Module = "duHast.Revit.Family.family_types_catalogue";

        private string tempDirectory;
        private dynamic doubles;
        private dynamic catalogue;
        private readonly List<(string name, object original)> patched = new();

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
            doubles = PythonEngineManager.Import("revit_test_doubles");
            catalogue = PythonEngineManager.Import(Module);
        }

        [TearDown]
        public void TearDown()
        {
            foreach (var (name, original) in patched)
            {
                PythonEngineManager.Scope.SetVariable("_restore_value", original);
                PythonEngineManager.PythonEngine.Execute($"import {Module} as _m\n_m.{name} = _restore_value\n", PythonEngineManager.Scope);
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

        private static PythonList PyStrings(params string[] items) => Py(items.Cast<object>().ToArray());

        private static List<string> ToList(dynamic pythonList) => ((IEnumerable<object>)pythonList).Select(o => (string)o).ToList();

        // ---------------------------------------- building family type data ----------------------------------------

        private dynamic Parameter(string typeName, string name, string value, string kind = "Length", string units = "mm")
        {
            dynamic cls = PythonEngineManager.ImportFrom("duHast.Revit.Family.Data.Objects.family_type_parameter_data_storage", "FamilyTypeParameterDataStorage");
            return cls("Door", "Furniture", "Door", @"C:\lib\Door.rfa", typeName, name, "Dimensions", kind, units, value);
        }

        private dynamic TypeStorage(string typeName, params (string name, string value)[] parameters)
        {
            dynamic cls = PythonEngineManager.ImportFrom("duHast.Revit.Family.Data.Objects.family_type_data_storage", "FamilyTypeDataStorage");
            return cls("Door", "Furniture", "Door", @"C:\lib\Door.rfa", typeName, Py(parameters.Select(p => (object)Parameter(typeName, p.name, p.value)).ToArray()));
        }

        private dynamic Manager(params dynamic[] types)
        {
            dynamic manager = PythonEngineManager.ImportFrom("duHast.Revit.Family.Data.Objects.family_type_data_storage_manager", "FamilyTypeDataStorageManager")();
            foreach (var t in types) manager.add_family_type_data_storage(t);
            return manager;
        }

        private dynamic DoorTypes() => Manager(
            TypeStorage("Type B", ("Width", "1000"), ("Height", "2200")),
            TypeStorage("Type A", ("Width", "900"), ("Height", "2100")),
            TypeStorage("Other", ("Width", "800"), ("Height", "2000")));

        private dynamic FamilyDoc() => doubles.FakeFamilyDoc("Door.rfa", @"C:\lib\Door.rfa", null, null,
            Py(doubles.FakeParameter("Width"), doubles.FakeParameter("Height"), doubles.FakeParameter("Mark", true), doubles.FakeParameter("Area Formula", false, true)),
            "Furniture", PyStrings("Type A", "Type B", "Other"));

        private void PatchTypeDataReader(string pythonBody)
        {
            PythonEngineManager.PythonEngine.Execute($"import {Module} as _m\n_original = _m.get_type_data_via_XML_from_family_file\n", PythonEngineManager.Scope);
            patched.Add(("get_type_data_via_XML_from_family_file", PythonEngineManager.Scope.GetVariable("_original")));
            PythonEngineManager.PythonEngine.Execute(
                "import duHast.Utilities.Objects.result as _res\n" +
                "reader_calls = []\n" +
                "def _fake(application, family_name, family_path, *args):\n" +
                "    reader_calls.append((application, family_name, family_path))\n" +
                "    r = _res.Result()\n" +
                pythonBody +
                "    return r\n" +
                "_m.get_type_data_via_XML_from_family_file = _fake\n",
                PythonEngineManager.Scope);
        }

        private void ReaderReturns(dynamic manager)
        {
            PythonEngineManager.Scope.SetVariable("_manager", manager);
            PatchTypeDataReader("    r.update_sep(True, 'read')\n    r.result.append(_manager)\n");
        }

        private dynamic ReaderCalls => PythonEngineManager.Scope.GetVariable("reader_calls");

        private string[] Lines(string file) =>
            File.ReadAllText(file, Encoding.Unicode).Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

        // ---------------------------------------- type_name_passes_filters ----------------------------------------

        private static dynamic StartsWith => PythonEngineManager.PythonEngine.Execute("lambda name, value: name.startswith(value)");
        private static dynamic EndsWith => PythonEngineManager.PythonEngine.Execute("lambda name, value: name.endswith(value)");

        private bool Passes(string typeName, object? filters) =>
            (bool)catalogue.type_name_passes_filters(TypeStorage(typeName, ("Width", "1")), filters);

        [Test]
        public void TypePassesFilters_NoFilters_Passes() => Assert.That(Passes("Type A", null), Is.True);

        [Test]
        public void TypePassesFilters_AllFiltersMustPass()
        {
            Assert.That(Passes("Type A", Py(Py(StartsWith, "Type"), Py(EndsWith, "A"))), Is.True);
            Assert.That(Passes("Type B", Py(Py(StartsWith, "Type"), Py(EndsWith, "A"))), Is.False);
            Assert.That(Passes("Other", Py(Py(StartsWith, "Type"))), Is.False);
        }

        [Test]
        public void TypePassesFilters_MalformedFilter_DoesNotPass()
        {
            Assert.That(Passes("Type A", Py("not a list")), Is.False);
            Assert.That(Passes("Type A", Py(Py(StartsWith))), Is.False, "a filter needs a function and a value");
            Assert.That(Passes("Type A", Py(Py("not callable", "Type"))), Is.False);
        }

        // ---------------------------------------- pass_fam_types_through_filters ----------------------------------------

        [Test]
        public void PassTypesThroughFilters_RemovesTheTypesThatDoNotPass()
        {
            dynamic manager = DoorTypes();
            dynamic result = catalogue.pass_fam_types_through_filters(manager, Py(Py(StartsWith, "Type")));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(((IEnumerable<object>)manager.family_type_data_storage).Select(t => (string)((dynamic)t).family_type_name).OrderBy(n => n), Is.EqualTo(new[] { "Type A", "Type B" }));
        }

        [Test]
        public void PassTypesThroughFilters_SeveralFilters_TypesMustPassAll()
        {
            dynamic manager = DoorTypes();
            dynamic result = catalogue.pass_fam_types_through_filters(manager, Py(Py(StartsWith, "Type"), Py(EndsWith, "A")));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(((IEnumerable<object>)manager.family_type_data_storage).Select(t => (string)((dynamic)t).family_type_name), Is.EqualTo(new[] { "Type A" }));
        }

        [Test]
        public void PassTypesThroughFilters_NoTypePasses_RemovesAll()
        {
            dynamic manager = DoorTypes();
            catalogue.pass_fam_types_through_filters(manager, Py(Py(StartsWith, "Nothing")));
            Assert.That((int)manager.family_type_data_storage.Count, Is.EqualTo(0));
        }

        // ---------------------------------------- get_type_parameter_order ----------------------------------------

        [Test]
        public void ParameterOrder_Default_AlphabeticalTypeParametersWithoutFormulaDriven()
        {
            dynamic result = catalogue.get_type_parameter_order(FamilyDoc(), null);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(ToList(result.result), Is.EqualTo(new[] { "Height", "Width" }), "no instance parameter (Mark), no formula driven one");
        }

        [Test]
        public void ParameterOrder_GivenOrderFirst_RestAlphabetical_UnknownReported()
        {
            dynamic result = catalogue.get_type_parameter_order(FamilyDoc(), PyStrings("Width", "Not There"));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(ToList(result.result), Is.EqualTo(new[] { "Width", "Height" }));
            Assert.That((string)result.message, Does.Contain("Not There not found"));
        }

        [Test]
        public void ParameterOrder_NotAFamilyDocument_Fails()
        {
            dynamic doc = FamilyDoc();
            doc.IsFamilyDocument = false;
            Assert.That((bool)catalogue.get_type_parameter_order(doc, null).status, Is.False);
        }

        [Test]
        public void ParameterOrder_OnlyFormulaDrivenTypeParameters_Fails()
        {
            dynamic doc = doubles.FakeFamilyDoc("Door.rfa", "", null, null, Py(doubles.FakeParameter("Driven", false, true)), "Furniture", PyStrings("T"));
            dynamic result = catalogue.get_type_parameter_order(doc, null);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("formula"));
        }

        // ---------------------------------------- write_catalogue_file_to_csv ----------------------------------------

        private dynamic Write(string path, PythonList data, PythonList header, bool overrideExisting = false) =>
            catalogue.write_catalogue_file_to_csv(data, path, header, overrideExisting);

        [Test]
        public void WriteCatalogueFile_Utf16LittleEndianWithByteOrderMark_NamedAfterTheFamilyFile()
        {
            dynamic result = Write(Path.Combine(tempDirectory, "Door.rfa"),
                Py(PyStrings("Type A", "900"), PyStrings("Type B", "1000")), PyStrings("", "Width##LENGTH##MILLIMETERS"));

            Assert.That((bool)result.status, Is.True, (string)result.message);
            string file = Path.Combine(tempDirectory, "Door.txt");
            Assert.That(File.ReadAllBytes(file).Take(2).ToArray(), Is.EqualTo(new byte[] { 0xFF, 0xFE }));
            Assert.That(Lines(file).Select(l => l.TrimStart('\ufeff')), Is.EqualTo(new[] { ",Width##LENGTH##MILLIMETERS", "Type A,900", "Type B,1000" }));
        }

        [Test]
        public void WriteCatalogueFile_ValuesWithCommas_AreQuoted()
        {
            Write(Path.Combine(tempDirectory, "Door.rfa"), Py(PyStrings("Type A", "1,5")), PyStrings("", "Width##LENGTH##MILLIMETERS"));
            Assert.That(Lines(Path.Combine(tempDirectory, "Door.txt"))[1], Is.EqualTo("Type A,\"1,5\""));
        }

        [Test]
        public void WriteCatalogueFile_FileExists_FailsUnlessOverrideRequested()
        {
            string file = Path.Combine(tempDirectory, "Door.txt");
            File.WriteAllText(file, "keep me");
            dynamic header = PyStrings("", "A");
            dynamic data = Py(PyStrings("T", "1"));

            Assert.That((bool)Write(Path.Combine(tempDirectory, "Door.rfa"), data, header).status, Is.False);
            Assert.That(File.ReadAllText(file), Is.EqualTo("keep me"));

            Assert.That((bool)Write(Path.Combine(tempDirectory, "Door.rfa"), data, header, true).status, Is.True);
            Assert.That(File.ReadAllText(file), Is.Not.EqualTo("keep me"));
        }

        // ---------------------------------------- export_catalogue_file ----------------------------------------

        private dynamic Export(dynamic doc, string fileName = "Door.txt", object? filters = null, object? order = null, bool overrideExisting = true) =>
            catalogue.export_catalogue_file(doc, Path.Combine(tempDirectory, fileName), filters, order, overrideExisting);

        [Test]
        public void Export_WritesOneRowPerType_SortedByTypeName_ParametersAlphabetical()
        {
            ReaderReturns(DoorTypes());

            dynamic result = Export(FamilyDoc());

            Assert.That((bool)result.status, Is.True, (string)result.message);
            var lines = Lines(Path.Combine(tempDirectory, "Door.txt"));
            Assert.That(lines[0].TrimStart('\ufeff'), Is.EqualTo(",Height##LENGTH##MILLIMETERS,Width##LENGTH##MILLIMETERS"));
            Assert.That(lines.Skip(1), Is.EqualTo(new[] { "Other,2000,800", "Type A,2100,900", "Type B,2200,1000" }));
        }

        [Test]
        public void Export_ReadsTheTypeDataOfTheFamilyFile()
        {
            ReaderReturns(DoorTypes());
            Export(FamilyDoc());
            Assert.That((int)ReaderCalls.Count, Is.EqualTo(1));
            Assert.That((string)ReaderCalls[0][1], Is.EqualTo("Door"), "family name without extension");
            Assert.That((string)ReaderCalls[0][2], Is.EqualTo(@"C:\lib\Door.rfa"));
        }

        [Test]
        public void Export_GivenParameterOrder_ColumnsFollowIt()
        {
            ReaderReturns(DoorTypes());
            Export(FamilyDoc(), order: PyStrings("Width"));
            var lines = Lines(Path.Combine(tempDirectory, "Door.txt"));
            Assert.That(lines[0].TrimStart('\ufeff'), Is.EqualTo(",Width##LENGTH##MILLIMETERS,Height##LENGTH##MILLIMETERS"));
            Assert.That(lines[2], Is.EqualTo("Type A,900,2100"));
        }

        [Test]
        public void Export_Filters_OnlyMatchingTypesAreExported()
        {
            ReaderReturns(DoorTypes());
            dynamic result = Export(FamilyDoc(), filters: Py(Py(StartsWith, "Type")));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(Lines(Path.Combine(tempDirectory, "Door.txt")).Skip(1), Is.EqualTo(new[] { "Type A,2100,900", "Type B,2200,1000" }));
        }

        [Test]
        public void Export_TypeDataCannotBeRead_Fails()
        {
            PatchTypeDataReader("    r.update_sep(False, 'part atom export failed')\n");
            dynamic result = Export(FamilyDoc());
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("part atom export failed"));
            Assert.That(File.Exists(Path.Combine(tempDirectory, "Door.txt")), Is.False);
        }

        [Test]
        public void Export_FamilyWithoutTypes_Fails()
        {
            ReaderReturns(Manager());
            dynamic result = Export(FamilyDoc());
            Assert.That((bool)result.status, Is.False);
            Assert.That(File.Exists(Path.Combine(tempDirectory, "Door.txt")), Is.False);
        }

        [Test]
        public void Export_NotAFamilyDocument_Fails()
        {
            ReaderReturns(DoorTypes());
            dynamic doc = FamilyDoc();
            doc.IsFamilyDocument = false;
            dynamic result = Export(doc);
            Assert.That((bool)result.status, Is.False);
            Assert.That((int)ReaderCalls.Count, Is.EqualTo(0));
        }

        [Test]
        public void Export_FileExists_OverwrittenOnlyWhenRequested()
        {
            ReaderReturns(DoorTypes());
            string file = Path.Combine(tempDirectory, "Door.txt");
            File.WriteAllText(file, "keep me");

            Assert.That((bool)Export(FamilyDoc(), overrideExisting: false).status, Is.False);
            Assert.That(File.ReadAllText(file), Is.EqualTo("keep me"));

            Assert.That((bool)Export(FamilyDoc(), overrideExisting: true).status, Is.True);
            Assert.That(File.ReadAllText(file), Is.Not.EqualTo("keep me"));
        }
    }
}
