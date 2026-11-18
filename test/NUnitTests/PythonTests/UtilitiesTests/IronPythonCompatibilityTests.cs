using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    /// <summary>
    /// duHast and the samples run under IronPython 3.4 (Revit Batch Processor, pyRevit). CPython accepts some code IronPython does not:
    /// - a last line made of whitespace only, without a line break ("unindent does not match any outer indentation level"),
    /// - the 'None' member of a .net enum written as an attribute (Enum.None: None is a keyword in python 3; use getattr(Enum, "None")).
    /// A file with either cannot be imported, so every module importing it fails. These tests compile every file with the IronPython engine.
    /// </summary>
    public class IronPythonCompatibilityTests
    {
        private static string RepositoryRoot => Path.GetFullPath(Path.Combine(PythonRunner.GetRepositoryPath(), ".."));

        private static List<string> FindCompileFailures(string relativeFolder)
        {
            var failures = new List<string>();
            string folder = Path.Combine(RepositoryRoot, relativeFolder);
            Assert.That(Directory.Exists(folder), Is.True, $"{folder} not found");

            var engine = PythonEngineManager.PythonEngine;
            var scope = PythonEngineManager.Scope;
            foreach (string file in Directory.EnumerateFiles(folder, "*.py", SearchOption.AllDirectories).OrderBy(f => f))
            {
                if (file.Contains(Path.DirectorySeparatorChar + "__pycache__" + Path.DirectorySeparatorChar)) continue;
                scope.SetVariable("_source", File.ReadAllText(file));
                scope.SetVariable("_file", file);
                try
                {
                    engine.Execute("compile(_source, _file, 'exec')", scope);
                }
                catch (Exception e)
                {
                    failures.Add($"{Path.GetRelativePath(RepositoryRoot, file)}: {e.Message}");
                }
            }
            return failures;
        }

        [Test]
        public void AllDuHastModulesCompileUnderIronPython()
        {
            Assert.That(FindCompileFailures("src"), Is.Empty);
        }

        [Test]
        public void AllPyRevitToolbarModulesCompileUnderIronPython()
        {
            Assert.That(FindCompileFailures(Path.Combine("Samples", "pyRevit", "Extensions", "duHast-2025.extension", "duHast.tab")), Is.Empty);
        }

        [Test]
        public void AllFlowScriptsCompileUnderIronPython()
        {
            Assert.That(FindCompileFailures(Path.Combine("Samples", "Flows")), Is.Empty);
        }
    }
}
