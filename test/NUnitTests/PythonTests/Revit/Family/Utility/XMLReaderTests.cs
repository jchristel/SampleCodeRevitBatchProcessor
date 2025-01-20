using PythonTests.Setup;
using System.Xml;

namespace PythonTests.Revit.Family.Utility
{
    public class XMLReaderTests
    {
        private string dataTestDirectory;

        [SetUp]
        public void SetUp()
        {
            dataTestDirectory = PythonTests.PythonRunner.GetTestDataPath();
        }


        [Test]
        public void ModuleShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.FamilyXMLTypeReaderModule, Is.Not.Null, "family_xml_type_reader should be loaded.");
            Console.WriteLine(dataTestDirectory);
        }

       

        [Test]
        public void ReadXMLIntoStorage_ValidData()
        {
            dynamic familyXMLTypeReader = PythonEngineManager.FamilyXMLTypeReaderModule;
            dynamic xmlReader = PythonEngineManager.FilesXMLModule;

            // Arrange
            string fileName = Path.Combine(dataTestDirectory, @"XMLData_01\Sample_Family_Five.xml");
            string familyName = "SampleFamily";
            string familyPath = fileName;

            // Act
            var docXml = xmlReader.read_xml_file(file_path: fileName);
            var result = familyXMLTypeReader.read_xml_into_storage(doc_xml: docXml.result, family_name: familyName, family_path: familyPath);

            // Assert
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Is.InstanceOf<IronPython.Runtime.PythonList>());
            Assert.That(result.Count, Is.EqualTo(1), "expect one type");
        }

        [Test]
        public void ReadXMLIntoStorage_CheckFamilyTypeDataStorageProperties()
        {

            dynamic familyXMLTypeReader = PythonEngineManager.FamilyXMLTypeReaderModule;
            dynamic xmlReader = PythonEngineManager.FilesXMLModule;

            // Arrange
            var testFiles = new Dictionary<string, string>
            {
                { "Sample_Family_Five.xml", "SampleFamily" },
                { "Sample_Family_Nine.xml", "AnotherFamily" },
                {"Sample_Family_One.xml","" },
                {"Sample_Family_Six.xml","" },
                {"Sample_Family_Three.xml","" },
                {"Sample_Family_Two.xml","" }//,
                // Add more files and expected family names as needed
            };

            foreach (var testFile in testFiles)
            {
                Console.WriteLine($"file name: {testFile.Key}");

                string fileName = Path.Combine(dataTestDirectory, @"XMLData_01\", testFile.Key);
                string familyName = testFile.Value;
                string familyPath = fileName;

                // Act
                var docXml = xmlReader.read_xml_file(file_path: fileName);
                var result = familyXMLTypeReader.read_xml_into_storage(doc_xml: docXml, family_name: familyName, family_path: familyPath);

                // Assert
                Assert.That(result, Is.Not.Null,"xml document should not be null");
                Assert.That(result, Is.InstanceOf<IronPython.Runtime.PythonList>(),"should be an ironpython list");

                // Read the XML file using C# libraries
                var xmlDoc = new XmlDocument();
                xmlDoc.Load(fileName);

                // Create a namespace manager and add the necessary namespaces
                var namespaceManager = new XmlNamespaceManager(xmlDoc.NameTable);
                namespaceManager.AddNamespace("atom", "http://www.w3.org/2005/Atom");
                namespaceManager.AddNamespace("A", "urn:schemas-autodesk-com:partatom");

                var familyNode = xmlDoc.SelectSingleNode("//A:family", namespaceManager);
                Assert.That(familyNode, Is.Not.Null, "Document should have a family node");

                // Iterate over each type returned from the function
                foreach (var type in result)
                {
                    Console.WriteLine($"type name: {type.family_type_name}");
                    // Find the corresponding part node in the XML
                    var partNode = familyNode.SelectSingleNode($"A:part[atom:title='{type.family_type_name}']", namespaceManager);
                    Assert.That(partNode, Is.Not.Null, "xml document should have a title node");

                    // Print out the names of the child nodes within the part node for debugging
                    //foreach (XmlNode childNode in partNode.ChildNodes)
                    //{
                    //    Console.WriteLine($"Child node name: [{childNode.Name}]");
                    //}

                    // Iterate over the parameters property of the type
                    foreach (var parameter in type.parameters)
                    {
                        //Console.WriteLine($"parameter name: [{parameter.name}]");

                        bool match = false;
                        // Print out the names of the child nodes within the part node for debugging
                        foreach (XmlNode childNode in partNode.ChildNodes)
                        {
                            //Console.WriteLine($"Child node name: [{childNode.Name}]");
                            if(childNode.Name == parameter.name)
                            {
                                match = true;

                                // Check the parameter properties
                                Assert.That(parameter.type, Is.EqualTo(childNode.Attributes["type"].Value), $"Parameter {parameter.name} type mismatch.");
                                Assert.That(parameter.type_of_parameter, Is.EqualTo(childNode.Attributes["typeOfParameter"].Value), $"Parameter {parameter.name} type_of_parameter mismatch.");

                                // Compare the value up to the length of the value retrieved from parameter.value
                                // in order to ignore any unit string contained in the XML
                                string expectedValue = childNode.InnerText.Substring(0, parameter.value.Length);
                                Assert.That(parameter.value, Is.EqualTo(expectedValue), $"Parameter {parameter.name} value mismatch. {parameter.value}");

                                string expectedUnits = childNode.Attributes["units"] != null ? childNode.Attributes["units"].Value : "unitless";
                                Assert.That(parameter.units, Is.EqualTo(expectedUnits), $"Parameter {parameter.name} units mismatch.");

                                break;
                            }
                        }
                        Assert.That(match, Is.True, $"Parameter {parameter.name} not found in XML.");
                    }
                }
            }
        }
    }
}
