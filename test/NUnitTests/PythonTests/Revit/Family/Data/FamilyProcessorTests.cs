using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.Revit.Family.Data
{
    /// <summary>
    /// Tests for the warnings and shared parameter processors. They run against the generated Revit API stubs with the
    /// fakes in test/RevitApiStubs/overrides (fake family document, warnings, shared parameter elements).
    /// </summary>
    public class FamilyProcessorTests
    {
        private dynamic doubles;

        [SetUp]
        public void SetUp()
        {
            doubles = PythonEngineManager.Import("revit_test_doubles");
        }

        private static PythonList Py(params object[] items)
        {
            var list = new PythonList();
            foreach (var i in items) list.Add(i);
            return list;
        }

        private dynamic Doc(string title, string path = "", PythonList? elements = null, PythonList? warnings = null, PythonList? familyParameters = null)
            => doubles.FakeFamilyDoc(title, path, elements ?? Py(), warnings ?? Py(), familyParameters ?? Py());

        // ---------------------------------------- warnings ----------------------------------------

        private dynamic WarningsProcessor()
            => PythonEngineManager.ImportFrom("duHast.Revit.Warnings.Data.Objects.warnings_data_processor", "WarningsProcessor")();

        [Test]
        public void Warnings_OneStoragePerWarning()
        {
            dynamic processor = WarningsProcessor();
            var warnings = Py(
                doubles.FakeWarning("guid-1", "Elements overlap", Py(10, 11), Py(12)),
                doubles.FakeWarning("guid-2", "Line is slightly off axis", Py(20), Py()));
            processor.process(Doc("Chair.rfa", @"C:\lib\Chair.rfa", null, warnings), "Chair", "Furniture");

            Assert.That((int)processor.data.Count, Is.EqualTo(1));
            dynamic data = processor.data[0].data;
            Assert.That((int)data.Count, Is.EqualTo(2));
            Assert.That((string)data[0].warning_text, Is.EqualTo("Elements overlap"));
            Assert.That((string)data[0].warning_guid, Is.EqualTo("guid-1"));
            Assert.That(((IEnumerable<object>)data[0].warning_related_ids).Select(o => Convert.ToInt64(o)), Is.EqualTo(new long[] { 10, 11 }));
            Assert.That(((IEnumerable<object>)data[0].warning_other_ids).Select(o => Convert.ToInt64(o)), Is.EqualTo(new long[] { 12 }));
            Assert.That((string)data[1].warning_text, Is.EqualTo("Line is slightly off axis"));
            Assert.That((string)data[0].family_name, Is.EqualTo("Chair"));
            Assert.That((string)data[0].family_file_path, Is.EqualTo(@"C:\lib\Chair.rfa"));
            Assert.That((string)data[0].root_name_path, Is.EqualTo("Chair"));
            Assert.That((string)data[0].root_category_path, Is.EqualTo("Furniture"));
        }

        [Test]
        public void Warnings_NoWarnings_ReportsThatExplicitly()
        {
            dynamic processor = WarningsProcessor();
            processor.process(Doc("Chair.rfa"), "Chair", "Furniture");
            dynamic data = processor.data[0].data;
            Assert.That((int)data.Count, Is.EqualTo(1));
            Assert.That((string)data[0].warning_text, Is.EqualTo("No warnings present in family."));
            Assert.That((string)data[0].family_file_path, Is.EqualTo("-"), "unsaved document");
        }

        [Test]
        public void Warnings_NestedFamily_KeepsTheNestingPath()
        {
            dynamic processor = WarningsProcessor();
            processor.process(Doc("Leg.rfa"), "Chair :: Leg", "Furniture :: Generic Models");
            Assert.That((string)processor.data[0].data[0].root_name_path, Is.EqualTo("Chair :: Leg"));
            Assert.That((string)processor.data[0].data[0].family_name, Is.EqualTo("Leg"));
        }

        // ---------------------------------------- shared parameters ----------------------------------------

        private dynamic SharedParameterProcessor()
            => PythonEngineManager.ImportFrom("duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor", "SharedParameterProcessor")();

        [Test]
        public void SharedParameters_UsedAndUnusedDefinitions()
        {
            dynamic processor = SharedParameterProcessor();
            var elements = Py(
                doubles.FakeSharedParameterElement(100, "Fire Rating", "guid-fire"),
                doubles.FakeSharedParameterElement(101, "Unused One", "guid-unused"));
            // only the fire rating parameter is present as a family parameter
            var familyParameters = Py(doubles.FakeFamilyParameter("guid-fire"), doubles.FakeFamilyParameter());
            processor.process(Doc("Door.rfa", @"C:\lib\Door.rfa", elements, null, familyParameters), "Door", "Doors");

            dynamic data = processor.data[0].data;
            Assert.That((int)data.Count, Is.EqualTo(2));
            Assert.That((string)data[0].parameter_name, Is.EqualTo("Fire Rating"));
            Assert.That((string)data[0].parameter_guid, Is.EqualTo("guid-fire"));
            Assert.That(Convert.ToInt64(data[0].parameter_id), Is.EqualTo(100));
            Assert.That((int)data[0].use_counter, Is.EqualTo(1));
            Assert.That((int)data[0].used_by.Count, Is.EqualTo(1));
            Assert.That((string)data[1].parameter_name, Is.EqualTo("Unused One"));
            Assert.That((int)data[1].use_counter, Is.EqualTo(0));
            Assert.That((int)data[1].used_by.Count, Is.EqualTo(0));
        }

        [Test]
        public void SharedParameters_NonSharedFamilyParametersAreNotMatched()
        {
            dynamic processor = SharedParameterProcessor();
            var elements = Py(doubles.FakeSharedParameterElement(100, "Fire Rating", "guid-fire"));
            var familyParameters = Py(doubles.FakeFamilyParameter(), doubles.FakeFamilyParameter("guid-other"));
            processor.process(Doc("Door.rfa", "", elements, null, familyParameters), "Door", "Doors");
            Assert.That((int)processor.data[0].data[0].use_counter, Is.EqualTo(0));
        }

        [Test]
        public void SharedParameters_NoneInFamily_ReportsThatExplicitly()
        {
            dynamic processor = SharedParameterProcessor();
            processor.process(Doc("Door.rfa"), "Door", "Doors");
            dynamic data = processor.data[0].data;
            Assert.That((int)data.Count, Is.EqualTo(1));
            Assert.That((string)data[0].parameter_name, Is.EqualTo("No shared parameter present in family."));
            Assert.That((string)data[0].parameter_guid, Is.EqualTo(""));
            Assert.That(Convert.ToInt64(data[0].parameter_id), Is.EqualTo(-1));
        }

        [Test]
        public void SharedParameters_PostAction_AddsNestedUsageToTheRootFamily()
        {
            dynamic processor = SharedParameterProcessor();
            var familyParametersRoot = Py();
            var rootElements = Py(doubles.FakeSharedParameterElement(100, "Fire Rating", "guid-fire"));
            processor.process(Doc("Door.rfa", "", rootElements, null, familyParametersRoot), "Door", "Doors");
            var nestedElements = Py(doubles.FakeSharedParameterElement(100, "Fire Rating", "guid-fire"));
            processor.process(Doc("Handle.rfa", "", nestedElements, null, Py(doubles.FakeFamilyParameter("guid-fire"))), "Door :: Handle", "Doors :: Door Handles");

            dynamic result = processor.post_process_actions(Doc("Door.rfa"));
            Assert.That(result, Is.Not.Null);
            dynamic rootStorage = processor.data[0].data[0];
            Assert.That((int)rootStorage.use_counter, Is.EqualTo(1), "usage in the nested family is added to the root family");
        }
    }
}
