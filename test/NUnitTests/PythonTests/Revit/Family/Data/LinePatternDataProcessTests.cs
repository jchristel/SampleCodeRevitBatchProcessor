using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.Revit.Family.Data
{
    /// <summary>
    /// LinePatternProcessor.process: line patterns of a family document and where they are used (categories, level types).
    /// The helpers which read categories and levels from a real document are replaced with fakes; the collector and
    /// ElementId are the fakes from revit_api_fakes.
    /// </summary>
    public class LinePatternDataProcessTests
    {
        private const string DataModule = "duHast.Revit.LinePattern.Data.Objects.line_pattern_data";

        private dynamic doubles;
        private readonly List<string> patchedNames = new();
        private readonly Dictionary<string, object> originals = new();

        [SetUp]
        public void SetUp()
        {
            doubles = PythonEngineManager.Import("revit_test_doubles");
            PythonEngineManager.Import(DataModule);
            PythonEngineManager.PythonEngine.Execute(
                "import Autodesk.Revit.DB as _db\n" +
                "from revit_api_fakes import ElementId as _EId\n" +
                "class _Pattern(_db.LinePatternElement):\n" +
                "    def __init__(self, element_id, name):\n" +
                "        self.Id = _EId(element_id)\n" +
                "        self.Name = name\n" +
                "class _Owner(object):\n" +
                "    # a category or level type using a line pattern\n" +
                "    def __init__(self, element_id, pattern_id):\n" +
                "        self.Id = _EId(element_id)\n" +
                "        self.pattern_id = _EId(pattern_id)\n",
                PythonEngineManager.Scope);
        }

        [TearDown]
        public void TearDown()
        {
            foreach (var name in patchedNames)
            {
                PythonEngineManager.Scope.SetVariable("_restore", originals[name]);
                PythonEngineManager.PythonEngine.Execute($"import {DataModule} as _m\n_m.{name} = _restore\n", PythonEngineManager.Scope);
            }
            patchedNames.Clear();
            originals.Clear();
        }

        private static PythonList Py(params object[] items)
        {
            var list = new PythonList();
            foreach (var i in items) list.Add(i);
            return list;
        }

        private dynamic Owner(int elementId, int patternId) => PythonEngineManager.Scope.GetVariable("_Owner")(elementId, patternId);
        private dynamic Pattern(int elementId, string name) => PythonEngineManager.Scope.GetVariable("_Pattern")(elementId, name);

        private void PatchHelpers(PythonList familyCategories, PythonList levels)
        {
            foreach (var name in new[] { "rCats", "get_line_pattern_from_category", "get_line_pattern_from_level_element", "get_levels_list_ascending" })
            {
                PythonEngineManager.PythonEngine.Execute($"import {DataModule} as _m\n_o = _m.{name}\n", PythonEngineManager.Scope);
                originals[name] = PythonEngineManager.Scope.GetVariable("_o");
                patchedNames.Add(name);
            }
            PythonEngineManager.Scope.SetVariable("_family_categories", familyCategories);
            PythonEngineManager.Scope.SetVariable("_levels", levels);
            PythonEngineManager.PythonEngine.Execute(
                $"import {DataModule} as _m\n" +
                "class _Cats(object):\n" +
                "    def get_family_category(self, doc):\n" +
                "        return dict((str(i), c) for i, c in enumerate(_family_categories))\n" +
                "    def get_main_sub_categories(self, doc):\n" +
                "        return {}\n" +
                "    def get_other_sub_categories(self, doc):\n" +
                "        return {}\n" +
                "    def get_category_by_built_in_def_name(self, doc, names):\n" +
                "        return []\n" +
                "_m.rCats = _Cats()\n" +
                "_m.get_line_pattern_from_category = lambda category, doc: {_m.PROPERTY_PATTERN_ID: category.pattern_id}\n" +
                "_m.get_line_pattern_from_level_element = lambda doc, level: {_m.PROPERTY_PATTERN_ID: level.pattern_id}\n" +
                "_m.get_levels_list_ascending = lambda doc: list(_levels)\n",
                PythonEngineManager.Scope);
        }

        private dynamic Process(PythonList elements, PythonList familyCategories, PythonList levels)
        {
            PatchHelpers(familyCategories, levels);
            dynamic processor = PythonEngineManager.ImportFrom("duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor", "LinePatternProcessor")();
            processor.process(doubles.FakeFamilyDoc("Chair.rfa", @"C:\lib\Chair.rfa", elements), "Chair", "Furniture");
            return processor;
        }

        [Test]
        public void Process_OneStoragePerLinePatternInTheDocument()
        {
            dynamic processor = Process(Py(Pattern(1, "Dash"), Pattern(2, "Dot")), Py(Owner(50, 1)), Py());

            dynamic data = processor.data[0].data;
            Assert.That((int)data.Count, Is.EqualTo(2));
            Assert.That((string)data[0].pattern_name, Is.EqualTo("Dash"));
            Assert.That(Convert.ToInt64(data[0].pattern_id), Is.EqualTo(1));
            Assert.That((string)data[0].family_name, Is.EqualTo("Chair"));
            Assert.That((string)data[0].family_file_path, Is.EqualTo(@"C:\lib\Chair.rfa"));
        }

        [Test]
        public void Process_PatternUsedByACategory_IsCountedAndReportsTheCategory()
        {
            dynamic processor = Process(Py(Pattern(1, "Dash"), Pattern(2, "Dot")), Py(Owner(50, 1)), Py());

            dynamic dash = processor.data[0].data[0];
            dynamic dot = processor.data[0].data[1];
            Assert.That((int)dash.use_counter, Is.EqualTo(1));
            Assert.That((int)dash.used_by.Count, Is.EqualTo(1));
            Assert.That(Convert.ToInt64(dash.used_by[0].element_id), Is.EqualTo(50));
            Assert.That((string)dash.used_by[0].root_name_path, Is.EqualTo("Chair"));
            Assert.That((int)dot.use_counter, Is.EqualTo(0));
            Assert.That((int)dot.used_by.Count, Is.EqualTo(0));
        }

        [Test]
        public void Process_PatternUsedByCategoriesAndLevelTypes_CountsBoth()
        {
            dynamic processor = Process(Py(Pattern(1, "Dash")), Py(Owner(50, 1), Owner(51, 1)), Py(Owner(60, 1)));

            dynamic dash = processor.data[0].data[0];
            Assert.That((int)dash.use_counter, Is.EqualTo(3));
            Assert.That((int)dash.used_by.Count, Is.EqualTo(3));
        }

        [Test]
        public void Process_NoLinePatternsInDocument_CollectsNothing()
        {
            dynamic processor = Process(Py(), Py(Owner(50, 1)), Py());

            Assert.That((int)processor.data.Count, Is.EqualTo(1));
            Assert.That((int)processor.data[0].data.Count, Is.EqualTo(0));
        }
    }
}
