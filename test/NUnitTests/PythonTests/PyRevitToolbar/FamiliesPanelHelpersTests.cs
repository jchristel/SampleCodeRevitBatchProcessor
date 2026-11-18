using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.PyRevitToolbar
{
    /// <summary>
    /// Tests for helper functions in the toolbar's lib/families modules behind the Rename (rename_families_in_folder) and
    /// Reports (compare_library_reports) pull downs. The pyRevit dialogs are not tested: the directory picker is patched and the
    /// list the user would choose from is recorded.
    /// </summary>
    public class FamiliesPanelHelpersTests
    {
        private const string RenameModule = "families.rename.rename_families_in_folder";
        private const string CompareModule = "families.compare_library_reports";

        private string tempDirectory;
        private readonly List<(string module, string name, object original)> patched = new();

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
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

        private string Touch(string relativePath)
        {
            string path = Path.Combine(tempDirectory, relativePath);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllText(path, "x");
            return path;
        }

        // ---------------------------------------- rename_families_in_folder ----------------------------------------

        private dynamic Rename => PythonEngineManager.Import(RenameModule);

        private dynamic RenameDirective(string name, string category, string newName, string filePath = "") =>
            PythonEngineManager.ImportFrom("duHast.Revit.Family.Data.Objects.family_directive_rename", "FamilyDirectiveRename")(name, category, filePath, newName);

        [Test]
        public void FindFiles_MatchesByFileNameOnly()
        {
            var paths = Py(@"C:\a\Door.rfa", @"C:\b\Door.rfa", @"C:\a\Door.rfa.bak", @"C:\a\Window.rfa");
            dynamic found = Rename.find_files(paths, "Door.rfa");
            Assert.That(((IEnumerable<object>)found).Select(o => (string)o), Is.EqualTo(new[] { @"C:\a\Door.rfa", @"C:\b\Door.rfa" }));
        }

        [Test]
        public void UpdatedRenameDirectives_FamilyFoundOnce_GetsTheFilePath()
        {
            string door = Touch(@"lib\Door.rfa");
            dynamic result = Rename.updated_rename_directives(tempDirectory, Py(RenameDirective("Door", "Doors", "Door_New")));
            Assert.That((int)result.Count, Is.EqualTo(1));
            Assert.That((string)result[0].name, Is.EqualTo("Door"));
            Assert.That((string)result[0].category, Is.EqualTo("Doors"));
            Assert.That((string)result[0].file_path, Is.EqualTo(door));
            Assert.That((string)result[0].new_name, Is.EqualTo("Door_New"));
        }

        [Test]
        public void UpdatedRenameDirectives_FamilyNotFound_IsLeftOut()
        {
            Touch(@"lib\Window.rfa");
            dynamic result = Rename.updated_rename_directives(tempDirectory, Py(RenameDirective("Door", "Doors", "Door_New")));
            Assert.That((int)result.Count, Is.EqualTo(0));
        }

        [Test]
        public void UpdatedRenameDirectives_SameNameInSeveralFolders_IsLeftOutAsAmbiguous()
        {
            Touch(@"lib\one\Door.rfa");
            Touch(@"lib\two\Door.rfa");
            dynamic result = Rename.updated_rename_directives(tempDirectory, Py(RenameDirective("Door", "Doors", "Door_New")));
            Assert.That((int)result.Count, Is.EqualTo(0));
        }

        [Test]
        public void UpdatedRenameDirectives_OnlyFamilyFilesAreConsidered_AndSeveralDirectives()
        {
            string door = Touch(@"lib\Door.rfa");
            Touch(@"lib\Door.xml");
            string window = Touch(@"lib\sub\Window.rfa");
            dynamic result = Rename.updated_rename_directives(tempDirectory, Py(RenameDirective("Door", "Doors", "D2"), RenameDirective("Window", "Windows", "W2"), RenameDirective("Missing", "Doors", "M2")));
            Assert.That(((IEnumerable<object>)result).Select(d => (string)((dynamic)d).file_path), Is.EquivalentTo(new[] { door, window }));
        }

        // ---------------------------------------- compare_library_reports ----------------------------------------

        private dynamic Compare => PythonEngineManager.Import(CompareModule);

        [Test]
        public void ConvertDataToCsv_KeyAndValuesBecomeOneRow_SortedByFamilyThenType()
        {
            var data = new PythonDictionary
            {
                [new PythonTuple(new object[] { "Window", "Windows", "T2", "Height" })] = Py("1200", "1300"),
                [new PythonTuple(new object[] { "Door", "Doors", "T2", "Width" })] = Py("900", "1000"),
                [new PythonTuple(new object[] { "Door", "Doors", "T1", "Width" })] = Py("800", "N/A"),
            };

            dynamic rows = Compare.convert_data_to_csv(data);

            Assert.That((int)rows.Count, Is.EqualTo(3));
            Assert.That(((IEnumerable<object>)rows[0]).Select(o => (string)o), Is.EqualTo(new[] { "Door", "Doors", "T1", "Width", "800", "N/A" }));
            Assert.That(((IEnumerable<object>)rows[1]).Select(o => (string)o), Is.EqualTo(new[] { "Door", "Doors", "T2", "Width", "900", "1000" }));
            Assert.That((string)rows[2][0], Is.EqualTo("Window"));
        }

        [Test]
        public void ConvertDataToCsv_NoData_NoRows()
        {
            dynamic rows = Compare.convert_data_to_csv(new PythonDictionary());
            Assert.That((int)rows.Count, Is.EqualTo(0));
        }

        /// <summary>The user picks these library report directories (status false: cancelled).</summary>
        private void ChooseDirectories(bool status, params string[] directories)
        {
            PythonEngineManager.Import(CompareModule);
            PythonEngineManager.PythonEngine.Execute($"import {CompareModule} as _m\n_original = _m.get_process_directories\n", PythonEngineManager.Scope);
            patched.Add((CompareModule, "get_process_directories", PythonEngineManager.Scope.GetVariable("_original")));
            PythonEngineManager.Scope.SetVariable("_directories", Py(directories.Cast<object>().ToArray()));
            PythonEngineManager.Scope.SetVariable("_picked", status);
            PythonEngineManager.PythonEngine.Execute(
                "import duHast.Utilities.Objects.result as _res\n" +
                "def _fake(forms):\n" +
                "    r = _res.Result()\n" +
                "    r.update_sep(_picked, 'directories')\n" +
                "    r.result = list(_directories)\n" +
                "    return r\n" +
                "_m.get_process_directories = _fake\n",
                PythonEngineManager.Scope);
        }

        /// <summary>A stand-in for the selection list: records what it was offered and 'selects' everything.</summary>
        private dynamic ListThatSelectsEverything()
        {
            PythonEngineManager.PythonEngine.Execute(
                "class _Select(object):\n" +
                "    def __init__(self):\n" +
                "        self.offered = []\n" +
                "    def show(self, items, button_name=None, multiselect=False):\n" +
                "        self.offered.append(list(items))\n" +
                "        return list(items)\n" +
                "class _Forms(object):\n" +
                "    def __init__(self):\n" +
                "        self.SelectFromList = _Select()\n",
                PythonEngineManager.Scope);
            return PythonEngineManager.Scope.GetVariable("_Forms")();
        }

        [Test]
        public void GetLibraryReports_OffersTheReportsOfEveryChosenDirectory()
        {
            string one = Path.GetDirectoryName(Touch(@"one\ReportA.csv"))!;
            Touch(@"one\ReportB.csv");
            string two = Path.GetDirectoryName(Touch(@"two\ReportC.csv"))!;
            Touch(@"two\notes.txt");
            ChooseDirectories(true, one, two);
            dynamic forms = ListThatSelectsEverything();

            dynamic selected = Compare.get_library_reports(forms);

            var offered = ((IEnumerable<object>)forms.SelectFromList.offered[0]).Select(o => Path.GetFileName((string)o)).ToList();
            Assert.That(offered, Is.EqualTo(new[] { "ReportA.csv", "ReportB.csv", "ReportC.csv" }), "the reports of both directories, csv files only");
            Assert.That((int)selected.Count, Is.EqualTo(3));
        }

        [Test]
        public void GetLibraryReports_LastDirectoryWithoutReports_StillOffersTheEarlierOnes()
        {
            string one = Path.GetDirectoryName(Touch(@"one\ReportA.csv"))!;
            string two = Path.Combine(tempDirectory, "two");
            Directory.CreateDirectory(two);
            ChooseDirectories(true, one, two);
            dynamic forms = ListThatSelectsEverything();

            dynamic selected = Compare.get_library_reports(forms);

            Assert.That((int)selected.Count, Is.EqualTo(1));
        }

        [Test]
        public void GetLibraryReports_NoReportsAnywhere_AsksNothing()
        {
            string empty = Path.Combine(tempDirectory, "empty");
            Directory.CreateDirectory(empty);
            ChooseDirectories(true, empty);
            dynamic forms = ListThatSelectsEverything();

            dynamic selected = Compare.get_library_reports(forms);

            Assert.That((int)selected.Count, Is.EqualTo(0));
            Assert.That((int)forms.SelectFromList.offered.Count, Is.EqualTo(0));
        }

        [Test]
        public void GetLibraryReports_DirectoriesNotChosen_ReturnsNothing()
        {
            ChooseDirectories(false);
            dynamic forms = ListThatSelectsEverything();
            dynamic selected = Compare.get_library_reports(forms);
            Assert.That((int)selected.Count, Is.EqualTo(0));
            Assert.That((int)forms.SelectFromList.offered.Count, Is.EqualTo(0));
        }
    }
}
