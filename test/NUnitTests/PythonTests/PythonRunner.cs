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

            // add local python 3.4 install lib to path
            path.Add(@"C:\Program Files\IronPython 3.4\Lib");

            //ensure search path are set
            engine.SetSearchPaths(path);

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
