using System.Text.RegularExpressions;
using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    /// <summary>
    /// Tests for the utility modules used by the flows of The Chain: utility, date_stamps, files_io, files_get, util_batch_p
    /// and the file item class of the file selection UI.
    /// </summary>
    public class ChainUtilityTests
    {
        private string tempDirectory;

        private dynamic utility;
        private dynamic dateStamps;
        private dynamic filesIo;
        private dynamic filesGet;
        private dynamic utilBatchP;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
            utility = PythonEngineManager.Import("duHast.Utilities.utility");
            dateStamps = PythonEngineManager.Import("duHast.Utilities.date_stamps");
            filesIo = PythonEngineManager.Import("duHast.Utilities.files_io");
            filesGet = PythonEngineManager.Import("duHast.Utilities.files_get");
            utilBatchP = PythonEngineManager.Import("duHast.Utilities.util_batch_p");
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory))
            {
                Directory.Delete(tempDirectory, true);
            }
        }

        private string Touch(string relativePath, string content = "x")
        {
            string path = Path.Combine(tempDirectory, relativePath);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllText(path, content);
            return path;
        }

        private static List<string> Names(IEnumerable<object> paths) =>
            paths.Select(p => Path.GetFileName((string)p)).OrderBy(n => n).ToList();

        // ======================================== utility ========================================

        [Test]
        public void ParseStringToBool_TrueAndFalse_AnyCase()
        {
            Assert.That((bool)utility.parse_string_to_bool("true"), Is.True);
            Assert.That((bool)utility.parse_string_to_bool("TRUE"), Is.True);
            Assert.That((bool)utility.parse_string_to_bool("False"), Is.False);
        }

        [Test]
        public void ParseStringToBool_Anything_Else_Throws()
        {
            var ex = Assert.Catch<Exception>(() => utility.parse_string_to_bool("yes"));
            Assert.That(ex!.Message, Does.Contain("String cant be converted to bool"));
        }

        [Test]
        public void PadSingleDigitNumericString_PadsToTwoByDefault()
        {
            Assert.That((string)utility.pad_single_digit_numeric_string("5"), Is.EqualTo("05"));
            Assert.That((string)utility.pad_single_digit_numeric_string("12"), Is.EqualTo("12"));
        }

        [Test]
        public void PadSingleDigitNumericString_ThreeDigits_AndNonNumericUnchanged()
        {
            Assert.That((string)utility.pad_single_digit_numeric_string("5", utility.PAD_SINGLE_DIGIT_TO_THREE), Is.EqualTo("005"));
            Assert.That((string)utility.pad_single_digit_numeric_string("abc"), Is.EqualTo("abc"));
        }

        [Test]
        public void EncodeAscii_ReplacesNonAsciiCharacters_NonStringUnchanged()
        {
            Assert.That((string)utility.encode_ascii("caf\u00e9"), Is.EqualTo("caf?"));
            Assert.That((int)utility.encode_ascii(5), Is.EqualTo(5));
        }

        [Test]
        public void EncodeUtf8_KeepsText_NonStringUnchanged()
        {
            Assert.That((string)utility.encode_utf8("caf\u00e9"), Is.EqualTo("caf\u00e9"));
            Assert.That((int)utility.encode_utf8(5), Is.EqualTo(5));
        }

        [Test]
        public void GetFirst_ReturnsFirstMatch_OrDefault()
        {
            var list = new PythonList { 1, 2, 3, 4 };
            Assert.That((int)utility.get_first(list, -1), Is.EqualTo(1));
            Assert.That((int)utility.get_first(list, -1, (Func<object, bool>)(x => (int)x > 2)), Is.EqualTo(3));
            Assert.That((int)utility.get_first(list, -1, (Func<object, bool>)(x => (int)x > 10)), Is.EqualTo(-1));
        }

        [Test]
        public void IndexOf_FoundOrMinusOne()
        {
            var list = new PythonList { "a", "b" };
            Assert.That((int)utility.index_of(list, "b"), Is.EqualTo(1));
            Assert.That((int)utility.index_of(list, "z"), Is.EqualTo(-1));
        }

        [Test]
        public void RemoveItemsFromList_RemovesAllGivenItems()
        {
            var list = new PythonList { "a", "b", "c", "d" };
            dynamic result = utility.remove_items_from_list(list, new PythonList { "b", "d" });
            Assert.That(((IEnumerable<object>)result).Select(o => (string)o), Is.EqualTo(new[] { "a", "c" }));
        }

        [Test]
        public void RemoveItemsFromList_ItemNotInList_DoesNotStopRemovingTheOthers()
        {
            var list = new PythonList { "a", "b", "c" };
            dynamic result = utility.remove_items_from_list(list, new PythonList { "not there", "b" });
            Assert.That(((IEnumerable<object>)result).Select(o => (string)o), Is.EqualTo(new[] { "a", "c" }));
        }

        [Test]
        public void Flatten_NestedDictionary_JoinsKeys()
        {
            string code = "{'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}";
            PythonEngineManager.PythonEngine.Execute("_flatten_in = " + code, PythonEngineManager.Scope);
            dynamic input = PythonEngineManager.Scope.GetVariable("_flatten_in");
            dynamic flat = utility.flatten(input);
            Assert.That((int)flat["a"], Is.EqualTo(1));
            Assert.That((int)flat["b_c"], Is.EqualTo(2));
            Assert.That((int)flat["b_d_e"], Is.EqualTo(3));
            Assert.That((int)flat.Count, Is.EqualTo(3));
        }

        [Test]
        public void Flatten_CustomSeparator()
        {
            PythonEngineManager.PythonEngine.Execute("_flatten_in = {'b': {'c': 2}}", PythonEngineManager.Scope);
            dynamic input = PythonEngineManager.Scope.GetVariable("_flatten_in");
            dynamic flat = utility.flatten(input, "", "/");
            Assert.That((int)flat["b/c"], Is.EqualTo(2));
        }

        [Test]
        public void FlattenList_NestedLists()
        {
            PythonEngineManager.PythonEngine.Execute("_flat_list_in = [1, [2, [3, 4]], 5]", PythonEngineManager.Scope);
            dynamic input = PythonEngineManager.Scope.GetVariable("_flat_list_in");
            dynamic flat = utility.flatten_list(input);
            Assert.That(((IEnumerable<object>)flat).Select(o => (int)o), Is.EqualTo(new[] { 1, 2, 3, 4, 5 }));
        }

        // ======================================== date_stamps ========================================

        [Test]
        public void DateTimeStampBuilder_FormatsNow()
        {
            string year = (string)dateStamps.date_time_stamp_builder("%Y");
            Assert.That(year, Is.EqualTo(DateTime.Now.Year.ToString()));
        }

        [Test]
        public void DateTimeStampBuilder_Milliseconds_AreThreeDigits_AtTheEnd()
        {
            string stamp = (string)dateStamps.date_time_stamp_builder("%H_%M_%S_%f");
            Assert.That(stamp, Does.Match(@"^\d\d_\d\d_\d\d_\d{3}$"));
        }

        [Test]
        public void DateTimeStampBuilder_Milliseconds_NotAtTheEnd_AreStillThreeDigits()
        {
            // trimming the last 3 characters of the result would cut into the seconds here
            string stamp = (string)dateStamps.date_time_stamp_builder("%f_%H");
            Assert.That(stamp, Does.Match(@"^\d{3}_\d\d$"));
        }

        [Test]
        public void DateTimeStampBuilder_NotAString_Throws()
        {
            Assert.Catch<Exception>(() => dateStamps.date_time_stamp_builder(5));
        }

        [Test]
        public void GetFolderDateStamp_DefaultIsYyyyMmDd()
        {
            Assert.That((string)dateStamps.get_folder_date_stamp(), Is.EqualTo(DateTime.Now.ToString("yyyyMMdd")));
        }

        [Test]
        public void GetDateStamp_UsesTheGivenFormat()
        {
            Assert.That((string)dateStamps.get_date_stamp(dateStamps.FILE_DATE_STAMP_YYYY_MM_DD), Is.EqualTo(DateTime.Now.ToString("yyyy_MM_dd")));
        }

        [Test]
        public void GetDateStampedFileName_PrefixNameSuffixExtension()
        {
            string name = (string)dateStamps.get_date_stamped_file_name(@"C:\temp\Chair.rfa", ".csv", "_suffix");
            Assert.That(name, Does.Match(@"^\d\d_\d\d_\d\d_Chair_suffix\.csv$"));
        }

        // ======================================== files_io ========================================

        [Test]
        public void FileExist_AndDelete()
        {
            string file = Touch("a.txt");
            Assert.That((bool)filesIo.file_exist(file), Is.True);
            Assert.That((bool)filesIo.file_exist(tempDirectory), Is.False, "a directory is not a file");
            Assert.That((bool)filesIo.file_delete(file), Is.True);
            Assert.That((bool)filesIo.file_exist(file), Is.False);
            Assert.That((bool)filesIo.file_delete(file), Is.False, "already gone");
        }

        [Test]
        public void FilesDeleteInDirectory_OnlyMatchingPattern()
        {
            Touch("a.txt");
            Touch("b.txt");
            Touch("c.csv");
            Assert.That((bool)filesIo.files_delete_in_directory(tempDirectory, "*.txt"), Is.True);
            Assert.That(Directory.GetFiles(tempDirectory).Select(Path.GetFileName), Is.EqualTo(new[] { "c.csv" }));
        }

        [Test]
        public void FilesDeleteInDirectory_DirectoryMissing_ReturnsFalse()
        {
            Assert.That((bool)filesIo.files_delete_in_directory(Path.Combine(tempDirectory, "nothere"), "*.txt"), Is.False);
        }

        [Test]
        public void RenameCopyMove()
        {
            string file = Touch("a.txt", "content");
            string renamed = Path.Combine(tempDirectory, "b.txt");
            Assert.That((bool)filesIo.rename_file(file, renamed), Is.True);
            Assert.That(File.Exists(renamed), Is.True);

            string copy = Path.Combine(tempDirectory, "c.txt");
            Assert.That((bool)filesIo.copy_file(renamed, copy), Is.True);
            Assert.That(File.ReadAllText(copy), Is.EqualTo("content"));

            string moved = Path.Combine(tempDirectory, "d.txt");
            Assert.That((bool)filesIo.file_move(copy, moved), Is.True);
            Assert.That(File.Exists(copy), Is.False);
            Assert.That(File.Exists(moved), Is.True);

            Assert.That((bool)filesIo.rename_file(Path.Combine(tempDirectory, "nothere.txt"), file), Is.False);
        }

        [Test]
        public void MoveAllFilesFromDirToDir_MovesFilesNotDirectories()
        {
            string src = Path.Combine(tempDirectory, "src");
            string dest = Path.Combine(tempDirectory, "dest");
            Directory.CreateDirectory(dest);
            Touch(@"src\a.txt");
            Touch(@"src\b.txt");
            Directory.CreateDirectory(Path.Combine(src, "sub"));
            Assert.That((bool)filesIo.move_all_files_from_dir_to_dir(src, dest), Is.True);
            Assert.That(Directory.GetFiles(dest).Select(Path.GetFileName).OrderBy(n => n), Is.EqualTo(new[] { "a.txt", "b.txt" }));
            Assert.That(Directory.GetFiles(src), Is.Empty);
            Assert.That(Directory.Exists(Path.Combine(src, "sub")), Is.True);
        }

        [Test]
        public void GetFileNameWithoutExt_KeepsDotsInTheName()
        {
            Assert.That((string)filesIo.get_file_name_without_ext(@"C:\lib\Chair.v2.rfa"), Is.EqualTo("Chair.v2"));
            Assert.That((string)filesIo.get_file_name_without_ext(@"C:\lib\Chair.rfa"), Is.EqualTo("Chair"));
            Assert.That((string)filesIo.get_file_name_without_ext(@"C:\lib\Chair"), Is.EqualTo("Chair"));
        }

        [Test]
        public void GetFileExtension_AndDirectoryPath()
        {
            Assert.That((string)filesIo.get_file_extension(@"C:\lib\Chair.rfa"), Is.EqualTo(".rfa"));
            Assert.That((string)filesIo.get_file_extension(@"C:\lib\Chair"), Is.EqualTo(""));
            Assert.That((string)filesIo.get_directory_path_from_file_path(@"C:\lib\Chair.rfa"), Is.EqualTo(@"C:\lib"));
        }

        [Test]
        public void ReadTextFile_AndIntoList()
        {
            string file = Touch("t.txt", "one\ntwo\r\nthree");
            Assert.That((string)filesIo.read_text_file(file), Does.Contain("two"));
            dynamic lines = filesIo.read_text_file_into_list(file);
            Assert.That(((IEnumerable<object>)lines).Select(o => (string)o), Is.EqualTo(new[] { "one", "two", "three" }));
            Assert.That(filesIo.read_text_file(Path.Combine(tempDirectory, "nothere.txt")), Is.Null);
            Assert.That((int)filesIo.read_text_file_into_list(Path.Combine(tempDirectory, "nothere.txt")).Count, Is.EqualTo(0));
        }

        [Test]
        public void GetFirstRowInFile_StrippedAndNot()
        {
            string file = Touch("t.txt", "  first row  \nsecond");
            Assert.That((string)filesIo.get_first_row_in_file(file), Is.EqualTo("first row"));
            Assert.That((string)filesIo.get_first_row_in_file_no_strip(file), Is.EqualTo("  first row  \n"));
            Assert.That(filesIo.get_first_row_in_file(Path.Combine(tempDirectory, "nothere.txt")), Is.Null);
        }

        [Test]
        public void IsBackUpFile_FourDigitsBeforeTheExtension()
        {
            Assert.That((bool)filesIo.is_back_up_file(@"C:\lib\Chair.0001.rfa"), Is.True);
            Assert.That((bool)filesIo.is_back_up_file(@"C:\lib\Chair.rfa"), Is.False);
            Assert.That((bool)filesIo.is_back_up_file(@"C:\lib\Chair.00a1.rfa"), Is.False, "not a number");
            Assert.That((bool)filesIo.is_back_up_file(@"C:\lib\Chair.12345.rfa"), Is.False, "not 4 characters");
        }

        [Test]
        public void RemoveBackupRevitFilesFromList()
        {
            var files = new PythonList { @"C:\lib\Chair.rfa", @"C:\lib\Chair.0001.rfa", @"C:\lib\Table.rfa" };
            dynamic result = filesIo.remove_backup_revit_files_from_list(files);
            Assert.That(((IEnumerable<object>)result).Select(o => (string)o), Is.EqualTo(new[] { @"C:\lib\Chair.rfa", @"C:\lib\Table.rfa" }));
        }

        [Test]
        public void GetFileSize_InMegabytes_MissingFileIsMinusOne()
        {
            string file = Path.Combine(tempDirectory, "big.bin");
            File.WriteAllBytes(file, new byte[1024 * 1024]);
            Assert.That((double)filesIo.get_file_size(file), Is.EqualTo(1.0).Within(0.0001));
            Assert.That((double)filesIo.get_file_size(file, filesIo.FILE_SIZE_IN_KB), Is.EqualTo(1024.0).Within(0.0001));
            Assert.That((double)filesIo.get_file_size(Path.Combine(tempDirectory, "nothere.bin")), Is.EqualTo(-1));
        }

        [Test]
        public void ConvertRelativePathToFullPath_OneUp()
        {
            string result = (string)filesIo.convert_relative_path_to_full_path(@"..\myfile.ext", @"C:\temp\Sample\someOtherFile.ext");
            Assert.That(result, Is.EqualTo(@"C:\temp\Sample\myfile.ext"));
        }

        [Test]
        public void ConvertRelativePathToFullPath_NoRelativePart_Unchanged()
        {
            Assert.That((string)filesIo.convert_relative_path_to_full_path(@"C:\a\b.txt", @"C:\temp\x.ext"), Is.EqualTo(@"C:\a\b.txt"));
        }

        [Test]
        public void TimeSpanFileEditedLast_AndWasEditedInTimeSpan()
        {
            string file = Touch("t.txt");
            Assert.That((int)filesIo.time_span_file_edited_last(file), Is.LessThanOrEqualTo(1));
            Assert.That((bool)filesIo.was_file_edited_in_time_span(file, 5), Is.True);
            File.SetLastWriteTime(file, DateTime.Now.AddMinutes(-30));
            Assert.That((bool)filesIo.was_file_edited_in_time_span(file, 5), Is.False);
            Assert.That((bool)filesIo.was_file_edited_in_time_span(file, 60), Is.True);
            Assert.That((int)filesIo.time_span_file_edited_last(Path.Combine(tempDirectory, "nothere.txt")), Is.EqualTo(-1));
            Assert.That((bool)filesIo.was_file_edited_in_time_span(Path.Combine(tempDirectory, "nothere.txt"), 60), Is.False);
        }

        // ======================================== files_get ========================================

        [Test]
        public void GetFilesSingleDirectory_PrefixSuffixExtension_NoSubDirectories()
        {
            Touch("Report_a_old.csv");
            Touch("Report_b_new.csv");
            Touch("Other_a_new.csv");
            Touch(@"sub\Report_c_new.csv");
            dynamic files = filesGet.get_files_single_directory(tempDirectory, "Report", "_new", ".csv");
            Assert.That(Names(files), Is.EqualTo(new List<string> { "Report_b_new.csv" }));
        }

        [Test]
        public void GetFilesFromDirectoryWalkerWithFilters_IncludesSubDirectories()
        {
            Touch("Directive_a.csv");
            Touch(@"sub\Directive_b.csv");
            Touch(@"sub\sub2\Directive_c.csv");
            Touch("Directive_d.txt");
            Touch("Other.csv");
            dynamic files = filesGet.get_files_from_directory_walker_with_filters(tempDirectory, "Directive", "", ".csv");
            Assert.That(Names(files), Is.EqualTo(new List<string> { "Directive_a.csv", "Directive_b.csv", "Directive_c.csv" }));
        }

        [Test]
        public void GetFilesFromDirectoryWalkerWithFilters_Suffix_AppliesToTheNameWithoutExtension()
        {
            Touch("a_final.csv");
            Touch("a_draft.csv");
            dynamic files = filesGet.get_files_from_directory_walker_with_filters(tempDirectory, "", "_final", ".csv");
            Assert.That(Names(files), Is.EqualTo(new List<string> { "a_final.csv" }));
        }

        [Test]
        public void GetFilesFromDirectoryWalkerWithFiltersSimple_ExtensionOnly()
        {
            Touch("a.rfa");
            Touch(@"sub\b.rfa");
            Touch("c.rvt");
            dynamic files = filesGet.get_files_from_directory_walker_with_filters_simple(tempDirectory, ".rfa");
            Assert.That(Names(files), Is.EqualTo(new List<string> { "a.rfa", "b.rfa" }));
        }

        [Test]
        public void FilesAsDictionary_GroupsByNameWithoutExtension_ListsDuplicates()
        {
            Touch("Chair.rfa");
            Touch(@"sub\Chair.rfa");
            Touch(@"sub\Table.rfa");
            dynamic dic = filesGet.files_as_dictionary(tempDirectory, "", "", ".rfa", true);
            Assert.That((int)dic.Count, Is.EqualTo(2));
            Assert.That((int)dic["Chair"].Count, Is.EqualTo(2), "Chair occurs in two directories");
            Assert.That((int)dic["Table"].Count, Is.EqualTo(1));
        }

        [Test]
        public void FilesAsDictionary_WithoutSubDirectories_OnlyTopLevel()
        {
            Touch("Chair.rfa");
            Touch(@"sub\Table.rfa");
            dynamic dic = filesGet.files_as_dictionary(tempDirectory, "", "", ".rfa", false);
            Assert.That((int)dic.Count, Is.EqualTo(1));
            Assert.That((bool)dic.__contains__("Chair"), Is.True);
        }

        [Test]
        public void GetFiles_ExtensionOnly_TopLevel()
        {
            Touch("a.rvt");
            Touch("b.rfa");
            Touch(@"sub\c.rvt");
            Assert.That(Names(filesGet.get_files(tempDirectory)), Is.EqualTo(new List<string> { "a.rvt" }), "default extension is .rvt");
            Assert.That(Names(filesGet.get_files(tempDirectory, ".rfa")), Is.EqualTo(new List<string> { "b.rfa" }));
        }

        [Test]
        public void GetFilesWithFilter_FileNameFilter()
        {
            Touch("Chair_01.rfa");
            Touch("Table_01.rfa");
            Assert.That(Names(filesGet.get_files_with_filter(tempDirectory, ".rfa", "Chair*")), Is.EqualTo(new List<string> { "Chair_01.rfa" }));
        }

        [Test]
        public void GetFilesFromDirectoryWalker_FileNameContainsFilter()
        {
            Touch("a_Chair.rfa");
            Touch(@"sub\Chair_b.csv");
            Touch("Table.rfa");
            Assert.That(Names(filesGet.get_files_from_directory_walker(tempDirectory, "Chair")), Is.EqualTo(new List<string> { "a_Chair.rfa", "Chair_b.csv" }));
        }

        // ======================================== util_batch_p ========================================

        [Test]
        public void AdjustSessionIdForDirectoryName_RemovesChevrons_ReplacesSeparators()
        {
            Assert.That((string)utilBatchP.adjust_session_id_for_directory_name("<2024-01-02 12:30:45.123>"), Is.EqualTo("2024_01_02_12_30_45_123"));
        }

        [Test]
        public void AdjustSessionIdForFileName_RemovesChevrons_ReplacesColons()
        {
            Assert.That((string)utilBatchP.adjust_session_id_for_file_name("<ab:cd:ef>"), Is.EqualTo("ab_cd_ef"));
        }

        [Test]
        public void AdjustSessionIdFileNameBack_RestoresChevronsAndColons()
        {
            Assert.That((string)utilBatchP.adjust_session_id_file_name_back("ab_cd_ef"), Is.EqualTo("<ab:cd:ef>"));
        }

        // ======================================== MyFileItem ========================================

        private static dynamic FileItem(string name, int size, string project = null, string file = null, string version = "-", string region = null, bool selected = false)
        {
            dynamic cls = PythonEngineManager.ImportFrom("duHast.UI.Objects.file_item", "MyFileItem");
            return cls(name, size, project, file, version, region, selected);
        }

        [Test]
        public void MyFileItem_StoresValues_AndDefaults()
        {
            dynamic cls = PythonEngineManager.ImportFrom("duHast.UI.Objects.file_item", "MyFileItem");
            dynamic item = cls(@"C:\lib\Chair.rfa", 12);
            Assert.That((string)item.name, Is.EqualTo(@"C:\lib\Chair.rfa"));
            Assert.That((int)item.size, Is.EqualTo(12));
            Assert.That(item.bim_360_project_guid, Is.Null);
            Assert.That(item.bim_360_file_guid, Is.Null);
            Assert.That((string)item.bim_360_revit_version, Is.EqualTo("-"));
            Assert.That(item.bim_360_region, Is.Null);
            Assert.That((bool)item.is_selected, Is.False);
        }

        [Test]
        public void MyFileItem_Equality_ComparesAllPropertiesButSelection()
        {
            Assert.That((bool)(FileItem("a", 1, "p", "f", "2024", "AU") == FileItem("a", 1, "p", "f", "2024", "AU")), Is.True);
            Assert.That((bool)(FileItem("a", 1, selected: true) == FileItem("a", 1, selected: false)), Is.True, "selection is not part of the identity");
            Assert.That((bool)(FileItem("a", 1) == FileItem("b", 1)), Is.False);
            Assert.That((bool)(FileItem("a", 1) == FileItem("a", 2)), Is.False);
            Assert.That((bool)(FileItem("a", 1, "p") == FileItem("a", 1, "q")), Is.False);
            Assert.That((bool)(FileItem("a", 1, region: "AU") == FileItem("a", 1, region: "US")), Is.False);
        }

        [Test]
        public void MyFileItem_NotEqual_AndOtherTypes()
        {
            Assert.That((bool)(FileItem("a", 1) != FileItem("b", 1)), Is.True);
            Assert.That((bool)(FileItem("a", 1) != FileItem("a", 1)), Is.False);
            Assert.That((bool)(FileItem("a", 1) == "a"), Is.False);
        }

        // ======================================== report names the flows rely on ========================================

        [TestCase("duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults", "FamilyBaseDataCombinedReport")]
        [TestCase("duHast.Revit.Family.Data.Objects.family_type_data_processor_defaults", "FamilyTypeDataCombinedReport")]
        [TestCase("duHast.Revit.Categories.Data.Objects.category_data_processor_defaults", "FamilyCategoriesCombinedReport")]
        [TestCase("duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor_defaults", "FamilyLinePatternsCombinedReport")]
        [TestCase("duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor_defaults", "FamilySharedParametersCombinedReport")]
        [TestCase("duHast.Revit.Warnings.Data.Objects.warnings_data_processor_defaults", "FamilyWarningsCombinedReport")]
        public void ProcessorDefaults_ReportNames(string module, string reportName)
        {
            // the start scripts and The Chain look for these file names
            dynamic defaults = PythonEngineManager.Import(module);
            Assert.That((string)defaults.DATA_REPORT_NAME, Is.EqualTo(reportName));
            Assert.That((string)defaults.DATA_TYPE_PROCESSOR, Does.EndWith("Processor"));
        }
    }
}
