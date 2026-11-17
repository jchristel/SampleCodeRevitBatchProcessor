using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.Revit.Family
{
    /// <summary>
    /// Tests for renaming family files (and their catalogue and part atom files) from rename directives,
    /// processing family report data, and the console output helpers used by The Chain's scripts.
    /// </summary>
    public class FamilyRenameFilesTests
    {
        private string tempDirectory;
        private dynamic renameFiles;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
            renameFiles = PythonEngineManager.Import("duHast.Revit.Family.family_rename_files");
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory))
            {
                Directory.Delete(tempDirectory, true);
            }
        }

        private string Touch(string name)
        {
            string path = Path.Combine(tempDirectory, name);
            File.WriteAllText(path, name);
            return path;
        }

        private void WriteDirectives(params string[] rows)
        {
            var lines = new List<string> { "name,path,category,newname" };
            lines.AddRange(rows);
            File.WriteAllLines(Path.Combine(tempDirectory, "RenameDirective_01.csv"), lines);
        }

        private List<string> FileNames() =>
            Directory.GetFiles(tempDirectory).Select(Path.GetFileName).Where(n => !n!.StartsWith("RenameDirective")).OrderBy(n => n).ToList()!;

        // ---------------------------------------- rename_family_files ----------------------------------------

        [Test]
        public void RenameFamilyFiles_RenamesFamilyFile()
        {
            string rfa = Touch("Chair.rfa");
            WriteDirectives($"Chair,{rfa},Furniture,Chair_New");
            dynamic result = renameFiles.rename_family_files(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(FileNames(), Is.EqualTo(new List<string> { "Chair_New.rfa" }));
            Assert.That((string)result.message, Does.Contain("Chair -> Chair_New"));
        }

        [Test]
        public void RenameFamilyFiles_RenamesCatalogueAndPartAtomFilesToo()
        {
            string rfa = Touch("Chair.rfa");
            Touch("Chair.txt");
            Touch("Chair.xml");
            Touch("Other.txt");
            WriteDirectives($"Chair,{rfa},Furniture,Chair_New");
            dynamic result = renameFiles.rename_family_files(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(FileNames(), Is.EqualTo(new List<string> { "Chair_New.rfa", "Chair_New.txt", "Chair_New.xml", "Other.txt" }));
        }

        [Test]
        public void RenameFamilyFiles_NoAssociatedFiles_IsNotAFailure()
        {
            string rfa = Touch("Chair.rfa");
            WriteDirectives($"Chair,{rfa},Furniture,Chair_New");
            dynamic result = renameFiles.rename_family_files(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((string)result.message, Does.Contain("No catalogue file found"));
            Assert.That((string)result.message, Does.Contain("No part atom file found"));
        }

        [Test]
        public void RenameFamilyFiles_SeveralDirectives()
        {
            string chair = Touch("Chair.rfa");
            string table = Touch("Table.rfa");
            WriteDirectives($"Chair,{chair},Furniture,Chair_New", $"Table,{table},Furniture,Table_New");
            dynamic result = renameFiles.rename_family_files(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(FileNames(), Is.EqualTo(new List<string> { "Chair_New.rfa", "Table_New.rfa" }));
        }

        [Test]
        public void RenameFamilyFiles_FamilyFileMissing_Fails_ButCarriesOn()
        {
            string table = Touch("Table.rfa");
            WriteDirectives($"Chair,{Path.Combine(tempDirectory, "Chair.rfa")},Furniture,Chair_New", $"Table,{table},Furniture,Table_New");
            dynamic result = renameFiles.rename_family_files(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("File not found: Chair"));
            Assert.That(FileNames(), Is.EqualTo(new List<string> { "Table_New.rfa" }), "the other directive was still processed");
        }

        [Test]
        public void RenameFamilyFiles_TargetExists_FailsAndKeepsBothFiles()
        {
            string chair = Touch("Chair.rfa");
            Touch("Chair_New.rfa");
            WriteDirectives($"Chair,{chair},Furniture,Chair_New");
            dynamic result = renameFiles.rename_family_files(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That(FileNames(), Is.EquivalentTo(new List<string> { "Chair.rfa", "Chair_New.rfa" }));
        }

        [Test]
        public void RenameFamilyFiles_NoDirectiveFile_Fails()
        {
            Touch("Chair.rfa");
            dynamic result = renameFiles.rename_family_files(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Rename directive file does not exist."));
            Assert.That(FileNames(), Is.EqualTo(new List<string> { "Chair.rfa" }));
        }

        // ---------------------------------------- process_data ----------------------------------------

        private string WriteReport()
        {
            string file = Path.Combine(tempDirectory, "FamilyBaseDataCombinedReport.csv");
            File.WriteAllLines(file, new[]
            {
                "data_type,root_name_path,root_category_path,family_name,family_file_path",
                @"FamilyBase,A,C_A,A,C:\lib\A.rfa",
                @"FamilyBase,A :: N,C_A :: C_N,N,-",
                @"FamilyBase,B,C_B,B,C:\lib\B.rfa"
            });
            return file;
        }

        [Test]
        public void ProcessData_HandsFamiliesToTheFunction_ReturnsWhatItCollected()
        {
            dynamic module = PythonEngineManager.Import("duHast.Revit.Family.Data.family_data_family_processor_utils");
            PythonEngineManager.PythonEngine.Execute(
                "def _collect_names(families, results):\n    results.extend([f.family_name for f in families])\n    return results\n",
                PythonEngineManager.Scope);
            dynamic collect = PythonEngineManager.Scope.GetVariable("_collect_names");
            dynamic result = module.process_data(WriteReport(), collect);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(((IEnumerable<object>)result.result).Select(o => (string)o).OrderBy(n => n), Is.EqualTo(new[] { "A", "B" }));
        }

        [Test]
        public void ProcessData_MissingReport_Fails()
        {
            dynamic module = PythonEngineManager.Import("duHast.Revit.Family.Data.family_data_family_processor_utils");
            PythonEngineManager.PythonEngine.Execute("def _noop(families, results):\n    return results\n", PythonEngineManager.Scope);
            dynamic noop = PythonEngineManager.Scope.GetVariable("_noop");
            dynamic result = module.process_data(Path.Combine(tempDirectory, "nothere.csv"), noop);
            Assert.That((bool)result.status, Is.False);
            Assert.That((int)result.result.Count, Is.EqualTo(0));
        }

        [Test]
        public void ProcessData_FunctionThrows_Fails()
        {
            dynamic module = PythonEngineManager.Import("duHast.Revit.Family.Data.family_data_family_processor_utils");
            PythonEngineManager.PythonEngine.Execute("def _boom(families, results):\n    raise ValueError('boom')\n", PythonEngineManager.Scope);
            dynamic boom = PythonEngineManager.Scope.GetVariable("_boom");
            dynamic result = module.process_data(WriteReport(), boom);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("boom"));
        }

        // ---------------------------------------- console_out ----------------------------------------

        private dynamic consoleOut => PythonEngineManager.Import("duHast.Utilities.console_out");

        private List<string> Collect(Action<Action<object>> call)
        {
            var lines = new List<string>();
            call(o => lines.Add(o?.ToString() ?? ""));
            return lines;
        }

        [Test]
        public void Output_PipesTheMessage()
        {
            var lines = Collect(pipe => consoleOut.output("hello", pipe));
            Assert.That(lines.Count, Is.EqualTo(1));
            Assert.That(lines[0], Does.Contain("hello"));
        }

        [Test]
        public void Output_MultiLineMessage_OneCallPerLine()
        {
            var lines = Collect(pipe => consoleOut.output("one\ntwo\nthree", pipe));
            Assert.That(lines.Count, Is.EqualTo(3));
            Assert.That(lines[1], Does.Contain("two"));
        }

        [Test]
        public void Output_NotAString_IsConverted()
        {
            var lines = Collect(pipe => consoleOut.output(42, pipe));
            Assert.That(lines.Count, Is.EqualTo(1));
            Assert.That(lines[0], Does.Contain("42"));
        }

        [Test]
        public void OutputWithTimeStamp_PrefixedWithDateAndTime()
        {
            var lines = Collect(pipe => consoleOut.output_with_time_stamp("hello", pipe));
            Assert.That(lines.Count, Is.EqualTo(1));
            Assert.That(lines[0], Does.Match(@"^\d\d-\d\d-\d\d \d\d_\d\d_\d\d : .*hello"));
        }

        [Test]
        public void OutputWithTimeStamp_MultiLine_EachLineStamped()
        {
            var lines = Collect(pipe => consoleOut.output_with_time_stamp("a\nb", pipe));
            Assert.That(lines.Count, Is.EqualTo(2));
            Assert.That(lines.All(l => System.Text.RegularExpressions.Regex.IsMatch(l, @"^\d\d-\d\d-\d\d \d\d_\d\d_\d\d : ")), Is.True);
        }

        [Test]
        public void OutputHeader_ContainsTheMessage()
        {
            var lines = Collect(pipe => consoleOut.output_header("The Chain", pipe));
            Assert.That(lines.Count, Is.EqualTo(1));
            Assert.That(lines[0], Does.Contain("THE CHAIN").Or.Contain("The Chain"));
        }

        [Test]
        public void OutputHeaderWithTimeStamp_ContainsTheMessage()
        {
            var lines = Collect(pipe => consoleOut.output_header_with_time_stamp("The Chain", pipe));
            Assert.That(lines.Count, Is.EqualTo(1));
            Assert.That(lines[0], Does.Contain("THE CHAIN").Or.Contain("The Chain"));
        }
    }
}
