using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.Revit.Family
{
    /// <summary>
    /// Tests for reading the type rename directive files and reading / writing the swap directive files
    /// (Families panel > Rename and SwapFamilies pull downs of the pyRevit toolbar).
    /// </summary>
    public class FamilyTypeDirectiveFilesTests
    {
        private string tempDirectory;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory)) Directory.Delete(tempDirectory, true);
        }

        private string WriteFile(string relativePath, params string[] lines)
        {
            string path = Path.Combine(tempDirectory, relativePath);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllLines(path, lines);
            return path;
        }

        /// <summary>The named attribute of every directive, as strings.</summary>
        private static List<string> Attribute(dynamic directives, string name)
        {
            var values = new List<string>();
            foreach (object directive in (IEnumerable<object>)directives)
            {
                values.Add((string)PythonEngineManager.PythonEngine.Operations.GetMember(directive, name));
            }
            return values;
        }

        private static PythonList Py(params object[] items)
        {
            var list = new PythonList();
            foreach (var i in items) list.Add(i);
            return list;
        }

        // ---------------------------------------- type rename directives ----------------------------------------

        private dynamic TypeRename => PythonEngineManager.Import("duHast.Revit.Family.Utility.family_rename_types_utils");

        private const string TypeRenameHeader = "Family name,Family type name,File path,Category,New family type name";

        [Test]
        public void TypeRename_ReadsEveryRowIgnoringTheHeader()
        {
            WriteFile("TypeRenameDirective_01.csv", TypeRenameHeader,
                @"Door,Type A,C:\lib\Door.rfa,Doors,Type A1",
                @"Window,Type B,C:\lib\Window.rfa,Windows,Type B1");

            dynamic result = TypeRename.get_rename_directives(tempDirectory);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(2));
            dynamic first = result.result[0];
            Assert.That((string)first.name, Is.EqualTo("Door"));
            Assert.That((string)first.old_type_name, Is.EqualTo("Type A"));
            Assert.That((string)first.file_path, Is.EqualTo(@"C:\lib\Door.rfa"));
            Assert.That((string)first.category, Is.EqualTo("Doors"));
            Assert.That((string)first.new_type_name, Is.EqualTo("Type A1"));
        }

        [Test]
        public void TypeRename_RowWithTooFewColumns_IsSkipped_NotRepeatedOrFatal()
        {
            WriteFile("TypeRenameDirective_01.csv", TypeRenameHeader,
                @"Short,Row",
                @"Door,Type A,C:\lib\Door.rfa,Doors,Type A1",
                @"Four,Columns,C:\lib\x.rfa,Doors",
                @"Window,Type B,C:\lib\Window.rfa,Windows,Type B1");

            dynamic result = TypeRename.get_rename_directives(tempDirectory);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(Attribute(result.result, "name"), Is.EqualTo(new[] { "Door", "Window" }));
        }

        [Test]
        public void TypeRename_SeveralFilesInSubDirectories_AllAreRead()
        {
            WriteFile("TypeRenameDirective_01.csv", TypeRenameHeader, @"Door,Type A,C:\lib\Door.rfa,Doors,Type A1");
            WriteFile(@"sub\TypeRenameDirective_02.csv", TypeRenameHeader, @"Window,Type B,C:\lib\Window.rfa,Windows,Type B1");
            WriteFile("OtherFile.csv", TypeRenameHeader, @"Ignored,Type,C:\x.rfa,Doors,New");

            dynamic result = TypeRename.get_rename_directives(tempDirectory);

            List<string> names = Attribute(result.result, "name");
            Assert.That(names.OrderBy(n => n), Is.EqualTo(new[] { "Door", "Window" }));
        }

        [Test]
        public void TypeRename_NoDirectiveFile_FailsWithTheTypeRenameMessage()
        {
            dynamic result = TypeRename.get_rename_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Type rename directive file does not exist."));
        }

        [Test]
        public void TypeRename_FileWithHeaderOnly_FailsWithTheTypeRenameMessage()
        {
            WriteFile("TypeRenameDirective_01.csv", TypeRenameHeader);
            dynamic result = TypeRename.get_rename_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Empty type rename directive file!"));
        }

        // ---------------------------------------- swap directives ----------------------------------------

        private dynamic Swap => PythonEngineManager.Import("duHast.Revit.Family.Utility.family_swap_instances_by_type_utils");

        private dynamic SwapDirective(string family, string category, string sourceType, string targetFamily, string targetType) =>
            PythonEngineManager.ImportFrom("duHast.Revit.Family.Data.Objects.family_directive_swap_instances_of_type", "FamilyDirectiveSwap")(family, category, sourceType, targetFamily, targetType);

        private const string SwapHeader = "Source Family Name,Source Family Category Name,Source Family Type Name,Target Family Name,Target Family Type Name";

        [Test]
        public void Swap_ReadsEveryRowIgnoringTheHeader()
        {
            WriteFile("SwapDirective_01.csv", SwapHeader,
                "Chair,Furniture,Type A,Chair New,Type A1",
                "Table,Furniture,Type B,Table New,Type B1");

            dynamic result = Swap.get_swap_directives(tempDirectory);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(2));
            dynamic first = result.result[0];
            Assert.That((string)first.name, Is.EqualTo("Chair"));
            Assert.That((string)first.category, Is.EqualTo("Furniture"));
            Assert.That((string)first.source_type_name, Is.EqualTo("Type A"));
            Assert.That((string)first.target_family_name, Is.EqualTo("Chair New"));
            Assert.That((string)first.target_family_type_name, Is.EqualTo("Type A1"));
        }

        [Test]
        public void Swap_RowWithTooFewColumns_IsSkipped_NotRepeatedOrFatal()
        {
            WriteFile("SwapDirective_01.csv", SwapHeader,
                "Short,Row",
                "Chair,Furniture,Type A,Chair New,Type A1",
                "Four,Columns,Type,Target",
                "Table,Furniture,Type B,Table New,Type B1");

            dynamic result = Swap.get_swap_directives(tempDirectory);

            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(Attribute(result.result, "name"), Is.EqualTo(new[] { "Chair", "Table" }));
        }

        [Test]
        public void Swap_NoDirectiveFile_Fails()
        {
            dynamic result = Swap.get_swap_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Swap directive file does not exist."));
        }

        [Test]
        public void Swap_FileWithHeaderOnly_Fails()
        {
            WriteFile("SwapDirective_01.csv", SwapHeader);
            dynamic result = Swap.get_swap_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Empty swap directive file!"));
        }

        [Test]
        public void SwapWrite_NewFile_WritesHeaderAndRows_AndReadsBack()
        {
            string file = Path.Combine(tempDirectory, "SwapDirective_01.csv");

            dynamic write = Swap.write_swap_directives_to_file(Py(SwapDirective("Chair", "Furniture", "Type A", "Chair New", "Type A1")), file);

            Assert.That((bool)write.status, Is.True, (string)write.message);
            var lines = File.ReadAllLines(file);
            Assert.That(lines[0].TrimStart('\ufeff'), Is.EqualTo(SwapHeader));
            Assert.That(lines[1], Is.EqualTo("Chair,Furniture,Type A,Chair New,Type A1"));

            dynamic read = Swap.get_swap_directives(tempDirectory);
            Assert.That((bool)read.status, Is.True, (string)read.message);
            Assert.That(Attribute(read.result, "target_family_name"), Is.EqualTo(new[] { "Chair New" }));
        }

        [Test]
        public void SwapWrite_ExistingFile_AppendsRowsWithoutAnotherHeader()
        {
            string file = Path.Combine(tempDirectory, "SwapDirective_01.csv");
            Swap.write_swap_directives_to_file(Py(SwapDirective("Chair", "Furniture", "Type A", "Chair New", "Type A1")), file);

            dynamic write = Swap.write_swap_directives_to_file(Py(SwapDirective("Table", "Furniture", "Type B", "Table New", "Type B1")), file);

            Assert.That((bool)write.status, Is.True, (string)write.message);
            var lines = File.ReadAllLines(file).Select(l => l.TrimStart('\ufeff')).ToList();
            Assert.That(lines.Count(l => l == SwapHeader), Is.EqualTo(1), "one header");
            Assert.That(lines.Where(l => l.Length > 0).Count(), Is.EqualTo(3));
            dynamic read = Swap.get_swap_directives(tempDirectory);
            Assert.That(Attribute(read.result, "name"), Is.EqualTo(new[] { "Chair", "Table" }));
        }

        [Test]
        public void SwapWrite_SeveralDirectives_OneRowEach()
        {
            string file = Path.Combine(tempDirectory, "SwapDirective_01.csv");
            Swap.write_swap_directives_to_file(Py(
                SwapDirective("Chair", "Furniture", "Type A", "Chair New", "Type A1"),
                SwapDirective("Table", "Furniture", "Type B", "Table New", "Type B1")), file);
            dynamic read = Swap.get_swap_directives(tempDirectory);
            Assert.That((int)read.result.Count, Is.EqualTo(2));
        }

        [Test]
        public void SwapWrite_ValuesWithCommas_SurviveTheRoundTrip()
        {
            string file = Path.Combine(tempDirectory, "SwapDirective_01.csv");
            Swap.write_swap_directives_to_file(Py(SwapDirective("Chair, big", "Furniture", "Type, A", "Chair New", "Type A1")), file);
            dynamic read = Swap.get_swap_directives(tempDirectory);
            Assert.That((bool)read.status, Is.True, (string)read.message);
            Assert.That((string)read.result[0].name, Is.EqualTo("Chair, big"));
            Assert.That((string)read.result[0].source_type_name, Is.EqualTo("Type, A"));
        }

        [Test]
        public void SwapWrite_ObjectsThatAreNotDirectives_Fails()
        {
            dynamic write = Swap.write_swap_directives_to_file(Py("not a directive"), Path.Combine(tempDirectory, "SwapDirective_01.csv"));
            Assert.That((bool)write.status, Is.False);
        }
    }
}
