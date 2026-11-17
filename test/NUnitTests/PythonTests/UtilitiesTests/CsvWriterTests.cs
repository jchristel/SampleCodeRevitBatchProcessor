using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    /// <summary>
    /// Tests for write_report_data_as_csv, which uses the duHast .net (CsvHelper) file writer.
    /// </summary>
    public class CsvWriterTests
    {
        private string tempDirectory;
        private dynamic filesCsv;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
            filesCsv = PythonEngineManager.Import("duHast.Utilities.files_csv");
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory)) Directory.Delete(tempDirectory, true);
        }

        private static List<string> L(params string[] values) => new List<string>(values);

        // the writer checks for python lists, so hand it python lists
        private static IronPython.Runtime.PythonList Py(IEnumerable<string> values)
        {
            var list = new IronPython.Runtime.PythonList();
            foreach (var v in values) list.Add(v);
            return list;
        }

        private static IronPython.Runtime.PythonList Py(List<List<string>> rows)
        {
            var list = new IronPython.Runtime.PythonList();
            foreach (var r in rows) list.Add(Py(r));
            return list;
        }

        private dynamic Write(string file, List<string> header, List<List<string>> data, string writeType = "w", bool enforceAscii = false, int quoting = 0)
            => filesCsv.write_report_data_as_csv(file, Py(header), Py(data), writeType, enforceAscii, "utf-8", null, quoting);

        [Test]
        public void Write_BackslashesAreNotEscaped()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            dynamic result = Write(file, L("path"), new List<List<string>> { L(@"C:\lib\A.rfa") });
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(File.ReadAllText(file), Does.Contain(@"C:\lib\A.rfa").And.Not.Contain(@"C:\\lib"));
        }

        [Test]
        public void Write_QuotesOnlyFieldsThatNeedIt()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            Write(file, L("a", "b"), new List<List<string>> { L("plain", "x,y"), L("say \"hi\"", "z") });
            string text = File.ReadAllText(file);
            Assert.That(text, Does.Contain("plain,\"x,y\""));
            Assert.That(text, Does.Contain("\"say \"\"hi\"\"\",z"));
            Assert.That(text, Does.Not.Contain("\"plain\""));
        }

        [Test]
        public void WriteThenRead_RoundTripsBackslashesCommasAndQuotes()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            var rows = new List<List<string>> { L(@"C:\lib\A.rfa", "x,y", "say \"hi\""), L("", "b", "c") };
            Assert.That((bool)Write(file, L("p", "q", "r"), rows).status, Is.True);
            dynamic read = filesCsv.read_csv_file(file);
            Assert.That((bool)read.status, Is.True, (string)read.message);
            Assert.That((int)read.result.Count, Is.EqualTo(3));
            Assert.That(((IEnumerable<object>)read.result[1]).Select(o => (string)o), Is.EqualTo(rows[0]));
            Assert.That(((IEnumerable<object>)read.result[2]).Select(o => (string)o), Is.EqualTo(rows[1]));
        }

        [Test]
        public void Append_AddsRowsWithoutRepeatingTheHeader()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            Write(file, L("p"), new List<List<string>> { L("1") });
            Assert.That((bool)Write(file, L("p"), new List<List<string>> { L("2") }, "a").status, Is.True);
            dynamic read = filesCsv.read_csv_file(file);
            Assert.That((int)read.result.Count, Is.EqualTo(3));
        }

        [Test]
        public void EnforceAscii_RemovesNonAsciiCharacters()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            dynamic result = filesCsv.write_report_data_as_csv(file, L("p"), new List<List<string>> { L("caf\u00e9") }, enforce_ascii: true);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(File.ReadAllText(file), Does.Contain("caf").And.Not.Contain("\u00e9"));
        }

        [Test]
        public void Quoting_All_QuotesEveryField()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            Write(file, L("a", "b"), new List<List<string>> { L("1", "x") }, quoting: 1);
            Assert.That(File.ReadAllLines(file), Is.EqualTo(new[] { "\"a\",\"b\"", "\"1\",\"x\"" }));
        }

        [Test]
        public void Quoting_NonNumeric_QuotesTextOnly()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            Write(file, L("a"), new List<List<string>> { L("12"), L("x") }, quoting: 2);
            Assert.That(File.ReadAllLines(file), Is.EqualTo(new[] { "\"a\"", "12", "\"x\"" }));
        }

        [Test]
        public void Quoting_None_WritesFieldsAsTheyAre()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            Write(file, L("a", "b"), new List<List<string>> { L("x,y", "z") }, quoting: 3);
            Assert.That(File.ReadAllLines(file)[1], Is.EqualTo("x,y,z"));
        }

        [Test]
        public void Quoting_Invalid_Fails()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            dynamic result = Write(file, L("a"), new List<List<string>> { L("1") }, quoting: 7);
            Assert.That((bool)result.status, Is.False);
            Assert.That(File.Exists(file), Is.False);
        }

        [Test]
        public void Write_NoByteOrderMarkUnlessRequested()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            Write(file, L("a"), new List<List<string>> { L("1") });
            byte[] bytes = File.ReadAllBytes(file);
            Assert.That(bytes.Take(3).SequenceEqual(new byte[] { 0xEF, 0xBB, 0xBF }), Is.False);
            Assert.That(File.ReadAllText(file), Is.EqualTo("a\n1\n"));
        }

        [Test]
        public void GetFirstRow_ReturnsTheRowItself_AndFailsForEmptyFile()
        {
            string file = Path.Combine(tempDirectory, "a.csv");
            Write(file, L("p", "q"), new List<List<string>> { L("1", "2") });
            dynamic first = filesCsv.get_first_row_in_csv_file(file);
            Assert.That((bool)first.status, Is.True, (string)first.message);
            Assert.That(((IEnumerable<object>)first.result).Select(o => (string)o), Is.EqualTo(new[] { "p", "q" }));

            string empty = Path.Combine(tempDirectory, "empty.csv");
            File.WriteAllText(empty, "");
            Assert.That((bool)filesCsv.get_first_row_in_csv_file(empty).status, Is.False);
        }

        [Test]
        public void TabSeparated_WriteThenRead_RoundTrips()
        {
            dynamic filesTab = PythonEngineManager.Import("duHast.Utilities.files_tab");
            string file = Path.Combine(tempDirectory, "a.txt");
            var rows = new List<List<string>> { L(@"C:\lib\A.rfa", "x\ty", "say \"hi\"") };
            dynamic written = filesTab.write_report_data_as_tab_separated_file(file, Py(L("p", "q", "r")), Py(rows));
            Assert.That((bool)written.status, Is.True, (string)written.message);
            dynamic read = filesTab.read_tab_separated_file(file);
            Assert.That((bool)read.status, Is.True, (string)read.message);
            Assert.That(((IEnumerable<object>)read.result[1]).Select(o => (string)o), Is.EqualTo(rows[0]));
        }
    }
}
