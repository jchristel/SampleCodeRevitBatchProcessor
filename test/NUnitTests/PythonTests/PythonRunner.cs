using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
using NUnit.Framework.Internal;
using static IronPython.Runtime.Profiler;

namespace PythonTests
{
    public class PythonRunner
    {
        static public ScriptEngine SetupEngine()
        {
            // get path to duHast
            var duHastDir = GetRepositoryPath();

            // set up the engine
            ScriptRuntimeSetup setup = Python.CreateRuntimeSetup(null);
            ScriptRuntime runtime = new ScriptRuntime(setup);

            // get the engine
            ScriptEngine engine = Python.GetEngine(runtime);

            // add reference to duHast
            var path = engine.GetSearchPaths();
            path.Add(duHastDir);

            // add the generated Revit API stubs (Autodesk.Revit.DB...) so modules importing the Revit API can be loaded without Revit
            var stubsDir = Path.GetFullPath(Path.Combine(duHastDir, "..", "test", "RevitApiStubs", "2026"));
            if (Directory.Exists(stubsDir))
            {
                path.Add(stubsDir);
            }
            var fakesDir = Path.GetFullPath(Path.Combine(duHastDir, "..", "test", "RevitApiStubs", "overrides"));
            if (Directory.Exists(fakesDir))
            {
                path.Add(fakesDir);
            }

            // add the lib folder of the pyRevit sample toolbar (modules the buttons import: families.*, ...). Added last so it cannot shadow duHast or the stubs.
            var toolbarLibDir = Path.GetFullPath(Path.Combine(duHastDir, "..", "Samples", "pyRevit", "Extensions", "duHast-2025.extension", "duHast.tab", "lib"));
            if (Directory.Exists(toolbarLibDir))
            {
                path.Add(toolbarLibDir);
            }

            // add local python 3.4 install lib to path
            path.Add(@"C:\Program Files\IronPython 3.4\Lib");

            //ensure search path are set
            engine.SetSearchPaths(path);

            // replace the few stub classes tests need behaviour from (before any duHast module is loaded)
            if (Directory.Exists(fakesDir))
            {
                engine.Execute("import revit_api_fakes");
            }

            //return engine
            return engine;
        }

        static public string GetRepositoryPath()
        {
            // Get the directory of the current assembly (where test project is located)
            var currentAssemblyLocation = Path.GetDirectoryName(typeof(PythonRunner).Assembly.Location);

            // Move up two directories to reach the solution folder
            string? solutionDirectory = Directory.GetParent(currentAssemblyLocation).Parent.FullName;
            string? oneUp = Directory.GetParent(solutionDirectory).Parent.FullName;

            // add referece to duHast
            var duHastDir = Path.Combine(oneUp, @"..\..\src");
            return duHastDir;
        }

        static public string GetTestDataPath()
        {
            // Get the directory of the current assembly (where test project is located)
            var currentAssemblyLocation = Path.GetDirectoryName(typeof(PythonRunner).Assembly.Location);

            // Move up two directories to reach the solution folder
            string? solutionDirectory = Directory.GetParent(currentAssemblyLocation).Parent.FullName;
            string? oneUp = Directory.GetParent(solutionDirectory).Parent.FullName;

            // add referece to duHast
            var duHastTestDataDir = Path.Combine(oneUp, @"..\..\test\Data"); 
            return duHastTestDataDir;
        }
    }
}
