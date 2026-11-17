using PythonTests.Setup;

namespace PythonTests.Revit.Family.Data
{
    /// <summary>
    /// Tests for the family processors, which import the Revit API (Autodesk.Revit.DB).
    /// They load against the generated Revit 2026 API stubs (test/RevitApiStubs) and are driven with a fake family document.
    /// </summary>
    public class FamilyBaseProcessorTests
    {
        private string tempDirectory;
        private string outDirectory;
        private dynamic processorModule;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            outDirectory = Path.Combine(tempDirectory, "out");
            Directory.CreateDirectory(outDirectory);
            processorModule = PythonEngineManager.Import("duHast.Revit.Family.Data.Objects.family_base_data_processor");
            PythonEngineManager.PythonEngine.Execute(
                "class _FakeFamilyDoc(object):\n" +
                "    def __init__(self, title, path_name=\"\"):\n" +
                "        self.Title = title\n" +
                "        self.PathName = path_name\n" +
                "        self.saved_as = []\n" +
                "    def SaveAs(self, path, options):\n" +
                "        self.saved_as.append(path)\n",
                PythonEngineManager.Scope);
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory)) Directory.Delete(tempDirectory, true);
        }

        private dynamic FakeDoc(string title, string pathName = "")
        {
            dynamic cls = PythonEngineManager.Scope.GetVariable("_FakeFamilyDoc");
            return cls(title, pathName);
        }

        private string WriteReference(params string[] rows)
        {
            string file = Path.Combine(tempDirectory, "FamilyBaseDataCombinedReport.csv");
            var lines = new List<string> { "data_type,root_name_path,root_category_path,family_name,family_file_path" };
            lines.AddRange(rows);
            File.WriteAllLines(file, lines);
            return file;
        }

        private dynamic NewProcessor(string? reference = null, string? outDir = null, string? session = "session")
            => processorModule.FamilyBaseProcessor(reference, outDir, session);

        // ---------------------------------------- data collected ----------------------------------------

        [Test]
        public void Process_StoresNameCategoryAndPathOfTheFamily()
        {
            dynamic processor = NewProcessor();
            dynamic doc = FakeDoc("Chair.rfa", @"C:\lib\Chair.rfa");
            processor.process(doc, "Chair", "Furniture");
            Assert.That((int)processor.data.Count, Is.EqualTo(1));
            dynamic storage = processor.data[0].data[0];
            Assert.That((string)storage.family_name, Is.EqualTo("Chair"));
            Assert.That((string)storage.root_name_path, Is.EqualTo("Chair"));
            Assert.That((string)storage.root_category_path, Is.EqualTo("Furniture"));
            Assert.That((string)storage.family_file_path, Is.EqualTo(@"C:\lib\Chair.rfa"));
        }

        [Test]
        public void Process_UnsavedDocument_HasDashAsFilePath()
        {
            dynamic processor = NewProcessor();
            processor.process(FakeDoc("Chair.rfa", ""), "Chair", "Furniture");
            Assert.That((string)processor.data[0].data[0].family_file_path, Is.EqualTo("-"));
        }

        [Test]
        public void Process_NestedFamily_KeepsTheFullPaths()
        {
            dynamic processor = NewProcessor();
            processor.process(FakeDoc("Leg.rfa"), "Chair :: Leg", "Furniture :: Generic Models");
            dynamic storage = processor.data[0].data[0];
            Assert.That((string)storage.root_name_path, Is.EqualTo("Chair :: Leg"));
            Assert.That((string)storage.root_category_path, Is.EqualTo("Furniture :: Generic Models"));
            Assert.That((string)storage.family_name, Is.EqualTo("Leg"));
            Assert.That((string)processor.data[0].category, Is.EqualTo("Generic Models"), "the category is the last node of the category path");
        }

        [Test]
        public void Process_CalledForSeveralFamilies_CollectsAll()
        {
            dynamic processor = NewProcessor();
            processor.process(FakeDoc("A.rfa"), "A", "C");
            processor.process(FakeDoc("B.rfa"), "B", "C");
            Assert.That((int)processor.data.Count, Is.EqualTo(2));
        }

        // ---------------------------------------- saving out families missing from the reference ----------------------------------------

        [Test]
        public void Process_FamilyNotInReference_IsSavedToSessionAndCategoryFolder()
        {
            string reference = WriteReference(@"FamilyBase,Table,Furniture,Table,C:\lib\Table.rfa");
            dynamic processor = NewProcessor(reference, outDirectory);
            dynamic doc = FakeDoc("Chair.rfa");
            processor.process(doc, "Chair", "Furniture");
            Assert.That((int)doc.saved_as.Count, Is.EqualTo(1));
            string saved = (string)doc.saved_as[0];
            Assert.That(saved, Is.EqualTo(Path.Combine(outDirectory, (string)processor.session_id, "Furniture", "Chair.rfa")));
            Assert.That(Directory.Exists(Path.Combine(outDirectory, (string)processor.session_id, "Furniture")), Is.True);
        }

        [Test]
        public void Process_FamilyInReference_IsNotSaved()
        {
            string reference = WriteReference(@"FamilyBase,Chair,Furniture,Chair,C:\lib\Chair.rfa");
            dynamic processor = NewProcessor(reference, outDirectory);
            dynamic doc = FakeDoc("Chair.rfa");
            processor.process(doc, "Chair", "Furniture");
            Assert.That((int)doc.saved_as.Count, Is.EqualTo(0));
        }

        [Test]
        public void Process_SameNameDifferentCategory_IsSaved()
        {
            string reference = WriteReference(@"FamilyBase,Chair,Seating,Chair,C:\lib\Chair.rfa");
            dynamic processor = NewProcessor(reference, outDirectory);
            dynamic doc = FakeDoc("Chair.rfa");
            processor.process(doc, "Chair", "Furniture");
            Assert.That((int)doc.saved_as.Count, Is.EqualTo(1));
        }

        [Test]
        public void Process_OnlyNestedRowInReference_IsStillSaved()
        {
            // a nested row is not a family file in the library, so it does not count as a match
            string reference = WriteReference(@"FamilyBase,Table :: Chair,Table :: Furniture,Chair,-");
            dynamic processor = NewProcessor(reference, outDirectory);
            dynamic doc = FakeDoc("Chair.rfa");
            processor.process(doc, "Chair", "Furniture");
            Assert.That((int)doc.saved_as.Count, Is.EqualTo(1));
        }

        [Test]
        public void Process_ReferenceFileDoesNotExist_NothingIsSaved()
        {
            dynamic processor = NewProcessor(Path.Combine(tempDirectory, "nothere.csv"), outDirectory);
            dynamic doc = FakeDoc("Chair.rfa");
            processor.process(doc, "Chair", "Furniture");
            Assert.That((int)doc.saved_as.Count, Is.EqualTo(0));
            Assert.That((int)processor.data.Count, Is.EqualTo(1), "data is still collected");
        }

        [Test]
        public void Process_NoOutDirectoryOrSession_NothingIsSaved()
        {
            string reference = WriteReference(@"FamilyBase,Table,Furniture,Table,C:\lib\Table.rfa");
            dynamic noOut = NewProcessor(reference, null);
            dynamic doc = FakeDoc("Chair.rfa");
            noOut.process(doc, "Chair", "Furniture");
            Assert.That((int)doc.saved_as.Count, Is.EqualTo(0));

            dynamic noSession = NewProcessor(reference, outDirectory, null);
            dynamic doc2 = FakeDoc("Chair.rfa");
            noSession.process(doc2, "Chair", "Furniture");
            Assert.That((int)doc2.saved_as.Count, Is.EqualTo(0));
        }

        // ---------------------------------------- all processors load against the stubs ----------------------------------------

        [TestCase("duHast.Revit.Family.Data.Objects.family_base_data_processor", "FamilyBaseProcessor")]
        [TestCase("duHast.Revit.Family.Data.Objects.family_type_data_processor", "FamilyTypeProcessor")]
        [TestCase("duHast.Revit.Categories.Data.Objects.category_data_processor", "CategoryProcessor")]
        [TestCase("duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor", "LinePatternProcessor")]
        [TestCase("duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor", "SharedParameterProcessor")]
        [TestCase("duHast.Revit.Warnings.Data.Objects.warnings_data_processor", "WarningsProcessor")]
        public void Processors_LoadAndHaveADataType(string module, string className)
        {
            PythonEngineManager.Import(module);
            dynamic cls = PythonEngineManager.ImportFrom(module, className);
            dynamic instance = cls();
            Assert.That((string)instance.data_type, Is.Not.Empty);
            Assert.That((int)instance.data.Count, Is.EqualTo(0));
        }
    }
}
