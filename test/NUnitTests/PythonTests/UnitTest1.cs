using NUnit.Framework;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;

namespace PythonTests
{
    public class Tests
    {
        private dynamic myClass;

        [SetUp]
        public void Setup()
        {
            // Get the directory of the current assembly (where test project is located)
            var currentAssemblyLocation = Path.GetDirectoryName(typeof(Tests).Assembly.Location);

            // Move up two directories to reach the solution folder
            var solutionDirectory = Directory.GetParent(currentAssemblyLocation).Parent.FullName;
            var oneUp = Directory.GetParent(solutionDirectory).Parent.FullName;
            
            // Move two directories up and then three down to reach MyClass.py
            var pythonFilePath = Path.Combine(oneUp, @"..\..\src\duHast\Geometry\point_2.py");

            // add referece to duHast
            var duHastDir = Path.Combine(oneUp, @"..\..\src");
            
            // set up the engine
            ScriptRuntimeSetup setup = Python.CreateRuntimeSetup(null);
            ScriptRuntime runtime = new ScriptRuntime(setup);

            // get the engine
            ScriptEngine engine = Python.GetEngine(runtime);
            var scope = engine.CreateScope();

            // need to add path (might need to be to duHast??)
            var path = engine.GetSearchPaths();
            path.Add(duHastDir);
            // add local python 3.4 install lib
            path.Add(@"C:\Program Files\IronPython 3.4\Lib");
            engine.SetSearchPaths(path);
            
           //run the file
            engine.ExecuteFile(pythonFilePath, scope);
            myClass = scope.GetVariable("Point2")(0.0,0.0);
        }

        [Test]
        public void Test1()
        {
            var result = myClass.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"y\": 0.0, \"x\": 0.0}";

            Assert.AreEqual(jsonString, result);
        }
    }
}