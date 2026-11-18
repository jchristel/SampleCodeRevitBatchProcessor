using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.Revit.Family.Data
{
    /// <summary>
    /// Tests for the post actions of the line pattern and category processors: usage found in nested families is added to the
    /// matching entry of the root family. The data storage instances are built directly, no Revit document is involved.
    /// </summary>
    public class FamilyProcessorPostActionTests
    {
        private static PythonList Py(params object[] items)
        {
            var list = new PythonList();
            foreach (var i in items) list.Add(i);
            return list;
        }

        // ---------------------------------------- line patterns ----------------------------------------

        private const string LinePatternProcessorModule = "duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor";
        private const string LinePatternDataModule = "duHast.Revit.LinePattern.Data.Objects.line_pattern_data";
        private const string LinePatternStorageModule = "duHast.Revit.LinePattern.Data.Objects.line_pattern_data_storage";
        private const string LinePatternUsedByModule = "duHast.Revit.LinePattern.Data.Objects.line_pattern_storage_used_by";

        private dynamic LinePatternProcessor()
            => PythonEngineManager.ImportFrom(LinePatternProcessorModule, "LinePatternProcessor")();

        private dynamic LinePatternData(string rootPath, string rootCategoryPath, params dynamic[] storages)
        {
            dynamic data = PythonEngineManager.ImportFrom(LinePatternDataModule, "LinePatternData")(rootPath, rootCategoryPath);
            foreach (var s in storages) data.add_data(s);
            return data;
        }

        private dynamic LinePatternStorage(string rootPath, string rootCategoryPath, string pattern, int useCounter, int usedByCount = 0)
        {
            dynamic storage = PythonEngineManager.ImportFrom(LinePatternStorageModule, "FamilyLinePatternDataStorage");
            dynamic usedBy = PythonEngineManager.ImportFrom(LinePatternUsedByModule, "FamilyLinePatternDataStorageUsedBy");
            var usedByList = Py();
            for (int i = 0; i < usedByCount; i++) usedByList.Add(usedBy(rootPath, 1000 + i));
            return storage(rootPath, rootCategoryPath, rootPath.Split(" :: ").Last(), "-", useCounter, usedByList, pattern, 1);
        }

        [Test]
        public void LinePattern_UsageInNestedFamily_IsAddedToTheRootFamily()
        {
            dynamic processor = LinePatternProcessor();
            dynamic rootStorage = LinePatternStorage("Chair", "Furniture", "Dash", 0);
            processor.data.append(LinePatternData("Chair", "Furniture", rootStorage));
            processor.data.append(LinePatternData("Chair :: Leg", "Furniture :: Generic Models", LinePatternStorage("Chair :: Leg", "Furniture :: Generic Models", "Dash", 2, 2)));

            dynamic result = processor.post_process_actions(null);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)rootStorage.use_counter, Is.EqualTo(2));
            Assert.That((int)rootStorage.used_by.Count, Is.EqualTo(2));
        }

        [Test]
        public void LinePattern_UsageInSeveralNestedFamilies_IsSummed()
        {
            dynamic processor = LinePatternProcessor();
            dynamic rootStorage = LinePatternStorage("Chair", "Furniture", "Dash", 1, 1);
            processor.data.append(LinePatternData("Chair", "Furniture", rootStorage));
            processor.data.append(LinePatternData("Chair :: Leg", "Furniture :: Generic Models", LinePatternStorage("Chair :: Leg", "Furniture :: Generic Models", "Dash", 2, 2)));
            processor.data.append(LinePatternData("Chair :: Seat", "Furniture :: Generic Models", LinePatternStorage("Chair :: Seat", "Furniture :: Generic Models", "Dash", 3, 3)));

            processor.post_process_actions(null);

            Assert.That((int)rootStorage.use_counter, Is.EqualTo(6));
            Assert.That((int)rootStorage.used_by.Count, Is.EqualTo(6));
        }

        [Test]
        public void LinePattern_PatternOnlyInNestedFamily_IsIgnored()
        {
            dynamic processor = LinePatternProcessor();
            dynamic rootStorage = LinePatternStorage("Chair", "Furniture", "Dash", 0);
            processor.data.append(LinePatternData("Chair", "Furniture", rootStorage));
            processor.data.append(LinePatternData("Chair :: Leg", "Furniture :: Generic Models", LinePatternStorage("Chair :: Leg", "Furniture :: Generic Models", "Dot", 2, 2)));

            dynamic result = processor.post_process_actions(null);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)rootStorage.use_counter, Is.EqualTo(0));
        }

        [Test]
        public void LinePattern_UnusedInNestedFamily_IsIgnored()
        {
            dynamic processor = LinePatternProcessor();
            dynamic rootStorage = LinePatternStorage("Chair", "Furniture", "Dash", 0);
            processor.data.append(LinePatternData("Chair", "Furniture", rootStorage));
            processor.data.append(LinePatternData("Chair :: Leg", "Furniture :: Generic Models", LinePatternStorage("Chair :: Leg", "Furniture :: Generic Models", "Dash", 0)));

            processor.post_process_actions(null);

            Assert.That((int)rootStorage.use_counter, Is.EqualTo(0));
        }

        [Test]
        public void LinePattern_NoNestedFamilies_Succeeds()
        {
            dynamic processor = LinePatternProcessor();
            dynamic rootStorage = LinePatternStorage("Chair", "Furniture", "Dash", 1, 1);
            processor.data.append(LinePatternData("Chair", "Furniture", rootStorage));

            dynamic result = processor.post_process_actions(null);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)rootStorage.use_counter, Is.EqualTo(1));
        }

        [Test]
        public void LinePattern_DataThatIsNotFamilyData_FailsTheAction()
        {
            dynamic processor = LinePatternProcessor();
            processor.data.append("not family data");

            dynamic result = processor.post_process_actions(null);

            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("IFamilyData"));
        }

        // ---------------------------------------- categories ----------------------------------------

        private const string CategoryProcessorModule = "duHast.Revit.Categories.Data.Objects.category_data_processor";
        private const string CategoryDataModule = "duHast.Revit.Categories.Data.Objects.category_data";
        private const string CategoryStorageModule = "duHast.Revit.Categories.Data.Objects.category_data_storage";
        private const string CategoryUsedByModule = "duHast.Revit.Categories.Data.Objects.category_data_storage_used_by";

        private dynamic CategoryProcessor()
            => PythonEngineManager.ImportFrom(CategoryProcessorModule, "CategoryProcessor")();

        private dynamic CategoryData(string rootPath, string rootCategoryPath, params dynamic[] storages)
        {
            dynamic data = PythonEngineManager.ImportFrom(CategoryDataModule, "CategoryData")(rootPath, rootCategoryPath);
            foreach (var s in storages) data.add_data(s);
            return data;
        }

        private dynamic CategoryStorage(string rootPath, string rootCategoryPath, string category, string subCategory, int useCounter, int usedByCount = 0)
        {
            dynamic storage = PythonEngineManager.ImportFrom(CategoryStorageModule, "FamilyCategoryDataStorage");
            dynamic usedBy = PythonEngineManager.ImportFrom(CategoryUsedByModule, "FamilyCategoryDataStorageUsedBy");
            var usedByList = Py();
            for (int i = 0; i < usedByCount; i++) usedByList.Add(usedBy(rootPath, 2000 + i));
            return storage(rootPath, rootCategoryPath, rootPath.Split(" :: ").Last(), "-", useCounter, usedByList,
                category, subCategory, 5, "1", "2", "3", "Wood", "7", "1", "1", "0", "0", "0");
        }

        [Test]
        public void Category_UsageInNestedFamily_IsAddedToTheRootFamily()
        {
            dynamic processor = CategoryProcessor();
            dynamic rootStorage = CategoryStorage("Chair", "Furniture", "Generic Models", "Handle", 0);
            processor.data.append(CategoryData("Chair", "Furniture", rootStorage));
            processor.data.append(CategoryData("Chair :: Leg", "Furniture :: Generic Models", CategoryStorage("Chair :: Leg", "Furniture :: Generic Models", "Generic Models", "Handle", 2, 2)));

            dynamic result = processor.post_process_actions(null);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)rootStorage.use_counter, Is.EqualTo(2));
            Assert.That((int)rootStorage.used_by.Count, Is.EqualTo(2));
        }

        [Test]
        public void Category_NestedStorageOfADifferentCategory_IsIgnored()
        {
            // only sub categories of the nested family's own category count (plus the corner cases)
            dynamic processor = CategoryProcessor();
            dynamic rootStorage = CategoryStorage("Chair", "Furniture", "Lighting Fixtures", "Handle", 0);
            processor.data.append(CategoryData("Chair", "Furniture", rootStorage));
            processor.data.append(CategoryData("Chair :: Leg", "Furniture :: Generic Models", CategoryStorage("Chair :: Leg", "Furniture :: Generic Models", "Lighting Fixtures", "Handle", 2, 2)));

            processor.post_process_actions(null);

            Assert.That((int)rootStorage.use_counter, Is.EqualTo(0));
        }

        [TestCase("Imports in Families")]
        [TestCase("Reference Planes")]
        public void Category_CornerCaseCategories_AreCountedForAnyNestedFamily(string cornerCase)
        {
            dynamic processor = CategoryProcessor();
            dynamic rootStorage = CategoryStorage("Chair", "Furniture", cornerCase, "Dwg", 0);
            processor.data.append(CategoryData("Chair", "Furniture", rootStorage));
            processor.data.append(CategoryData("Chair :: Leg", "Furniture :: Generic Models", CategoryStorage("Chair :: Leg", "Furniture :: Generic Models", cornerCase, "Dwg", 1, 1)));

            processor.post_process_actions(null);

            Assert.That((int)rootStorage.use_counter, Is.EqualTo(1));
        }

        [Test]
        public void Category_SubCategoryNotInRootFamily_IsIgnored()
        {
            dynamic processor = CategoryProcessor();
            dynamic rootStorage = CategoryStorage("Chair", "Furniture", "Generic Models", "Handle", 0);
            processor.data.append(CategoryData("Chair", "Furniture", rootStorage));
            processor.data.append(CategoryData("Chair :: Leg", "Furniture :: Generic Models", CategoryStorage("Chair :: Leg", "Furniture :: Generic Models", "Generic Models", "Other", 2, 2)));

            dynamic result = processor.post_process_actions(null);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)rootStorage.use_counter, Is.EqualTo(0));
        }

        [Test]
        public void Category_UnusedInNestedFamily_IsIgnored()
        {
            dynamic processor = CategoryProcessor();
            dynamic rootStorage = CategoryStorage("Chair", "Furniture", "Generic Models", "Handle", 0);
            processor.data.append(CategoryData("Chair", "Furniture", rootStorage));
            processor.data.append(CategoryData("Chair :: Leg", "Furniture :: Generic Models", CategoryStorage("Chair :: Leg", "Furniture :: Generic Models", "Generic Models", "Handle", 0)));

            processor.post_process_actions(null);

            Assert.That((int)rootStorage.use_counter, Is.EqualTo(0));
        }

        [Test]
        public void Category_AdditionalPostActionsRunAfterTheDefaultOne()
        {
            PythonEngineManager.PythonEngine.Execute(
                "calls = []\n" +
                "def _extra_post_action(doc):\n" +
                "    import duHast.Utilities.Objects.result as res\n" +
                "    calls.append(doc)\n" +
                "    return res.Result()\n",
                PythonEngineManager.Scope);
            dynamic extra = PythonEngineManager.Scope.GetVariable("_extra_post_action");
            dynamic processor = PythonEngineManager.ImportFrom(CategoryProcessorModule, "CategoryProcessor")(null, Py(extra));

            processor.post_process_actions("doc");

            Assert.That((int)PythonEngineManager.Scope.GetVariable("calls").Count, Is.EqualTo(1));
            Assert.That((int)processor.post_actions.Count, Is.EqualTo(2));
        }
    }
}
