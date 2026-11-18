using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.Revit.Family.Data
{
    /// <summary>
    /// Tests for FamilyTypeProcessor / FamilyTypeData. Reading the type data of a family goes through a part atom (xml) export, which needs
    /// Revit: those two functions are replaced with fakes returning prepared storage objects.
    /// </summary>
    public class FamilyTypeProcessorTests
    {
        private const string ProcessorModule = "duHast.Revit.Family.Data.Objects.family_type_data_processor";
        private const string DataModule = "duHast.Revit.Family.Data.Objects.family_type_data";

        private dynamic doubles;
        private readonly List<(string module, string name, object original)> patched = new();

        [SetUp]
        public void SetUp()
        {
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
        }

        private static PythonList Py(params object[] items)
        {
            var list = new PythonList();
            foreach (var i in items) list.Add(i);
            return list;
        }

        /// <summary>Replaces a function of a duHast module for the duration of the test.</summary>
        private void Patch(string module, string name, string pythonDefinition)
        {
            PythonEngineManager.PythonEngine.Execute($"import {module} as _m\n_original = _m.{name}\n", PythonEngineManager.Scope);
            patched.Add((module, name, PythonEngineManager.Scope.GetVariable("_original")));
            PythonEngineManager.PythonEngine.Execute(pythonDefinition + $"\n_m.{name} = _fake\n", PythonEngineManager.Scope);
        }

        private dynamic ParameterStorage(string root, string category, string typeName, string parameterName)
        {
            dynamic cls = PythonEngineManager.ImportFrom("duHast.Revit.Family.Data.Objects.family_type_parameter_data_storage", "FamilyTypeParameterDataStorage");
            return cls(root, category, root.Split(" :: ").Last(), "-", typeName, parameterName, "Length", "Dimensions", "mm", "100");
        }

        /// <summary>Makes the xml reader return one storage manager holding one type with the given parameters.</summary>
        private void FakeTypeData(string function, string module, params dynamic[] parameters)
        {
            PythonEngineManager.Scope.SetVariable("_fake_parameters", Py(parameters));
            Patch(module, function,
                "import duHast.Utilities.Objects.result as _res\n" +
                "class _Type(object):\n" +
                "    def __init__(self, parameters):\n" +
                "        self.parameters = parameters\n" +
                "class _Manager(object):\n" +
                "    def __init__(self, parameters):\n" +
                "        self.family_type_data_storage = [_Type(parameters)]\n" +
                "_calls = []\n" +
                "def _fake(*args):\n" +
                "    _calls.append(args)\n" +
                "    r = _res.Result()\n" +
                "    r.update_sep(True, 'ok')\n" +
                "    r.result.append(_Manager(list(_fake_parameters)))\n" +
                "    return r\n");
        }

        private dynamic Calls => PythonEngineManager.Scope.GetVariable("_calls");

        private dynamic TypeProcessor(string? familyFilePath = null)
            => PythonEngineManager.ImportFrom(ProcessorModule, "FamilyTypeProcessor")(null, null, null, familyFilePath, null);

        // ---------------------------------------- process: types of nested families ----------------------------------------

        [Test]
        public void Process_CollectsTypeParametersOfEachFamilyInTheDocument()
        {
            FakeTypeData("get_type_data_via_XML_from_family_object", DataModule,
                ParameterStorage("Chair :: Leg", "Furniture :: Generic Models", "Type 1", "Height"));
            dynamic doc = doubles.FakeFamilyDoc("Chair.rfa", @"C:\lib\Chair.rfa", Py(doubles.FakeFamily("Leg", "Generic Models")));
            dynamic processor = TypeProcessor();

            processor.process(doc, "Chair", "Furniture");

            Assert.That((int)processor.data.Count, Is.EqualTo(1));
            Assert.That((int)processor.data[0].data.Count, Is.EqualTo(1));
            Assert.That((string)processor.data[0].data[0].name, Is.EqualTo("Height"));
            Assert.That((string)processor.data[0].saved_file_name, Is.EqualTo(@"C:\lib\Chair.rfa"));
        }

        [Test]
        public void Process_PassesNestedPathsToTheXmlReader()
        {
            FakeTypeData("get_type_data_via_XML_from_family_object", DataModule);
            dynamic doc = doubles.FakeFamilyDoc("Chair.rfa", "", Py(doubles.FakeFamily("Leg", "Generic Models")));
            dynamic processor = TypeProcessor();

            processor.process(doc, "Chair", "Furniture");

            Assert.That((int)Calls.Count, Is.EqualTo(1));
            Assert.That((string)Calls[0][1], Is.EqualTo("Chair :: Leg"));
            Assert.That((string)Calls[0][2], Is.EqualTo("Furniture :: Generic Models"));
        }

        [Test]
        public void Process_FamilyNameEndingInRfa_DropsTheExtensionFromTheNestedPath()
        {
            FakeTypeData("get_type_data_via_XML_from_family_object", DataModule);
            dynamic doc = doubles.FakeFamilyDoc("Chair.rfa", "", Py(doubles.FakeFamily("Leg.rfa", "Generic Models")));
            dynamic processor = TypeProcessor();

            processor.process(doc, "Chair", "Furniture");

            Assert.That((string)Calls[0][1], Is.EqualTo("Chair :: Leg"));
        }

        [Test]
        public void Process_DocumentWithoutFamilies_CollectsNothing()
        {
            FakeTypeData("get_type_data_via_XML_from_family_object", DataModule);
            dynamic processor = TypeProcessor();

            processor.process(doubles.FakeFamilyDoc("Chair.rfa"), "Chair", "Furniture");

            Assert.That((int)processor.data[0].data.Count, Is.EqualTo(0));
            Assert.That((int)Calls.Count, Is.EqualTo(0));
        }

        [Test]
        public void Process_XmlReaderFails_CollectsNothingForThatFamily()
        {
            Patch(DataModule, "get_type_data_via_XML_from_family_object",
                "import duHast.Utilities.Objects.result as _res\n" +
                "def _fake(*args):\n" +
                "    r = _res.Result()\n" +
                "    r.update_sep(False, 'export failed')\n" +
                "    return r\n");
            dynamic doc = doubles.FakeFamilyDoc("Chair.rfa", "", Py(doubles.FakeFamily("Leg", "Generic Models")));
            dynamic processor = TypeProcessor();

            processor.process(doc, "Chair", "Furniture");

            Assert.That((int)processor.data[0].data.Count, Is.EqualTo(0));
        }

        // ---------------------------------------- pre action: type data of the root family ----------------------------------------

        [Test]
        public void PreAction_IsRegisteredByDefault_AndAddsTheRootFamilyTypeData()
        {
            FakeTypeData("get_type_data_via_XML_from_family_file", ProcessorModule,
                ParameterStorage("Chair", "Furniture", "Type 1", "Width"));
            dynamic processor = TypeProcessor(@"C:\lib\Chair.rfa");
            Assert.That((int)processor.pre_actions.Count, Is.EqualTo(1));

            dynamic result = processor.pre_process_actions(doubles.FakeFamilyDoc("Chair.rfa", "", null, null, null, "Furniture"));

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)processor.data.Count, Is.EqualTo(1));
            Assert.That((string)processor.data[0].root_path, Is.EqualTo("Chair"));
            Assert.That((string)processor.data[0].root_category_path, Is.EqualTo("Furniture"));
            Assert.That((string)processor.data[0].data[0].name, Is.EqualTo("Width"));
            Assert.That((string)Calls[0][1], Is.EqualTo("Chair"), "family name without extension");
            Assert.That((string)Calls[0][2], Is.EqualTo(@"C:\lib\Chair.rfa"));
        }

        [Test]
        public void PreAction_XmlReaderFails_FailsWithItsMessage()
        {
            Patch(ProcessorModule, "get_type_data_via_XML_from_family_file",
                "import duHast.Utilities.Objects.result as _res\n" +
                "def _fake(*args):\n" +
                "    r = _res.Result()\n" +
                "    r.update_sep(False, 'export failed')\n" +
                "    return r\n");
            dynamic processor = TypeProcessor(@"C:\lib\Chair.rfa");

            dynamic result = processor.pre_process_actions(doubles.FakeFamilyDoc("Chair.rfa"));

            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("export failed"));
            Assert.That((int)processor.data.Count, Is.EqualTo(0));
        }

        [Test]
        public void PreAction_NoFamilyFilePath_Fails()
        {
            dynamic processor = TypeProcessor(null);

            dynamic result = processor.pre_process_actions(doubles.FakeFamilyDoc("Chair.rfa"));

            Assert.That((bool)result.status, Is.False);
        }

        [Test]
        public void PreAction_AdditionalPreActionsAreKept()
        {
            PythonEngineManager.PythonEngine.Execute("def _extra_pre(doc):\n    return None\n", PythonEngineManager.Scope);
            dynamic extra = PythonEngineManager.Scope.GetVariable("_extra_pre");
            dynamic processor = PythonEngineManager.ImportFrom(ProcessorModule, "FamilyTypeProcessor")(null, Py(extra), null, null, null);
            Assert.That((int)processor.pre_actions.Count, Is.EqualTo(2));
        }
    }
}
