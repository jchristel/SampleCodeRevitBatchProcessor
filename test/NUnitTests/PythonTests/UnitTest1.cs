using NUnit.Framework;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;

namespace PythonTests
{
    public class Point2Tests
    {
        private dynamic point2Instance;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            var scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to point2 class
            var pythonFilePath = Path.Combine(repoPath, @"duHast\Geometry\point_2.py");
            
           //run the file
            engine.ExecuteFile(pythonFilePath, scope);

            // set up a point2 instance
            point2Instance = scope.GetVariable("Point2")(0.0,0.0);
        }

        [Test]
        public void TestToJson()
        {
            var result = point2Instance.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"x\": 0.0, \"y\": 0.0, \"json_ini\": null}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void TestToJsonUtf()
        {
            var result = point2Instance.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"x\": 0.0, \"y\": 0.0, \"json_ini\": null}";

            Assert.AreEqual(jsonString, result);
        }
    }
}