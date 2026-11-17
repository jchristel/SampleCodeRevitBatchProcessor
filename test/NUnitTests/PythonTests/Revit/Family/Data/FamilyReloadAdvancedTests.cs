using IronPython.Runtime;
using PythonTests.Setup;

namespace PythonTests.Revit.Family.Data
{
    /// <summary>
    /// Tests for the advanced family reload: which families get reloaded, and in which order.
    ///
    /// Families are reloaded bottom up through the inverted nesting tree:
    /// - level 0: the families directly hosting a changed family
    /// - level 1: the families hosting those, and so on
    /// A family hosting changed families at more than one level is reloaded once, at the highest level only.
    /// Shared nested families (a family nested in more than one host, which is also a root family itself) are hosts' children
    /// in all their hosts: every host of a shared family is reloaded at the same level.
    /// </summary>
    public class FamilyReloadAdvancedTests
    {
        private string tempDirectory;
        private string outputDirectory;

        private dynamic reloadModule;
        private dynamic reloadUtils;
        private dynamic familyUtils;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            outputDirectory = Path.Combine(tempDirectory, "out");
            Directory.CreateDirectory(outputDirectory);
            reloadModule = PythonEngineManager.Import("duHast.Revit.Family.Data.family_base_data_reload_advanced");
            reloadUtils = PythonEngineManager.Import("duHast.Revit.Family.Data.family_reload_advanced_utils");
            familyUtils = PythonEngineManager.Import("duHast.Revit.Family.Data.family_data_family_utils");
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory))
            {
                Directory.Delete(tempDirectory, true);
            }
        }

        // ---------------------------------------- helpers ----------------------------------------

        /// <summary>
        /// Writes a family base data report. Each family has the category C_name.
        /// Nested families are given relative to their root, e.g. "M", "M/X" (X nested in M nested in the root).
        /// </summary>
        private string WriteReport(params (string root, string[] nested)[] tree)
        {
            var rows = new List<string> { "data_type,root_name_path,root_category_path,family_name,family_file_path" };
            foreach (var (root, nested) in tree)
            {
                rows.Add($"FamilyBase,{root},C_{root},{root},C:\\lib\\{root}.rfa");
                foreach (string path in nested)
                {
                    var names = new List<string> { root };
                    names.AddRange(path.Split('/'));
                    rows.Add($"FamilyBase,{string.Join(" :: ", names)},{string.Join(" :: ", names.Select(n => "C_" + n))},{names.Last()},-");
                }
            }
            string file = Path.Combine(tempDirectory, "FamilyBaseDataCombinedReport.csv");
            File.WriteAllLines(file, rows);
            return file;
        }

        private string WriteChangeList(params string[] changed)
        {
            var rows = new List<string> { "name,path,category" };
            rows.AddRange(changed.Select(c => $"{c},C:\\lib\\{c}.rfa,C_{c}"));
            string file = Path.Combine(tempDirectory, "ChangedFilesTaskList.csv");
            File.WriteAllLines(file, rows);
            return file;
        }

        private dynamic BuildWorkLists(string changeList, string report)
        {
            return reloadModule.build_work_lists(changeList, report, outputDirectory);
        }

        /// <summary>
        /// The task lists written: file name (without extension) to the family names in it, sorted by name.
        /// </summary>
        private SortedDictionary<string, List<string>> TaskLists()
        {
            var lists = new SortedDictionary<string, List<string>>();
            foreach (string file in Directory.GetFiles(outputDirectory, "*.txt"))
            {
                lists[Path.GetFileNameWithoutExtension(file)] = File.ReadAllLines(file)
                    .Where(l => l.Trim().Length > 0)
                    .Select(l => Path.GetFileNameWithoutExtension(l.Trim().Trim('"')))
                    .OrderBy(n => n)
                    .ToList();
            }
            return lists;
        }

        private void AssertLevels(params string[][] expected)
        {
            var lists = TaskLists();
            Assert.That(lists.Count, Is.EqualTo(expected.Length), "number of task lists: " + string.Join(", ", lists.Keys));
            for (int i = 0; i < expected.Length; i++)
            {
                string key = $"TaskOutput {i:00}";
                Assert.That(lists.ContainsKey(key), Is.True, $"{key} missing");
                Assert.That(lists[key], Is.EqualTo(expected[i].OrderBy(n => n).ToList()), $"families in {key}");
            }
        }

        private static string[] L(params string[] names) => names;

        // ---------------------------------------- order: bottom up ----------------------------------------

        [Test]
        public void SingleHost_ReloadedAtLevelZero()
        {
            var result = BuildWorkLists(WriteChangeList("X"), WriteReport(("X", new string[0]), ("A", new[] { "X" })));
            Assert.That((bool)result.status, Is.True, (string)result.message);
            AssertLevels(L("A"));
        }

        [Test]
        public void Chain_HostsReloadedBottomUp()
        {
            // X nested in M, M nested in T
            var report = WriteReport(("X", new string[0]), ("M", new[] { "X" }), ("T", new[] { "M", "M/X" }));
            var result = BuildWorkLists(WriteChangeList("X"), report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            // M contains X directly, T contains M: M first, then T
            AssertLevels(L("M"), L("T"));
        }

        [Test]
        public void ChangedFamilyItself_IsNotReloadedUnlessItHostsAChangedFamily()
        {
            var report = WriteReport(("X", new string[0]), ("A", new[] { "X" }));
            BuildWorkLists(WriteChangeList("X"), report);
            Assert.That(TaskLists().Values.SelectMany(v => v), Does.Not.Contain("X"));
        }

        [Test]
        public void TwoChangedFamiliesAtDifferentDepths_AreProcessedBottomUp()
        {
            // X nested in B, B nested in C. X and C changed.
            var report = WriteReport(("X", new string[0]), ("B", new[] { "X" }), ("C", new[] { "B", "B/X" }));
            var result = BuildWorkLists(WriteChangeList("X", "C"), report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            AssertLevels(L("B"), L("C"));
        }

        // ---------------------------------------- shared nested families ----------------------------------------

        [Test]
        public void SharedNestedFamily_AllItsHostsAreReloadedAtTheSameLevel()
        {
            // X is nested in both A and B (and is a root family itself)
            var report = WriteReport(("X", new string[0]), ("A", new[] { "X" }), ("B", new[] { "X" }));
            var result = BuildWorkLists(WriteChangeList("X"), report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            AssertLevels(L("A", "B"));
        }

        [Test]
        public void SharedNestedMiddleFamily_ItsHostsAreReloadedAfterIt()
        {
            // X nested in M, M shared by A and B
            var report = WriteReport(
                ("X", new string[0]),
                ("M", new[] { "X" }),
                ("A", new[] { "M", "M/X" }),
                ("B", new[] { "M", "M/X" }));
            var result = BuildWorkLists(WriteChangeList("X"), report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            AssertLevels(L("M"), L("A", "B"));
        }

        [Test]
        public void HostAtNextLevelToo_IsReloadedAtTheHigherLevelOnly()
        {
            // A hosts X directly and also hosts B, which hosts X
            var report = WriteReport(("X", new string[0]), ("B", new[] { "X" }), ("A", new[] { "X", "B", "B/X" }));
            var result = BuildWorkLists(WriteChangeList("X"), report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            AssertLevels(L("B"), L("A"));
        }

        [Test]
        public void HostSeveralLevelsUp_IsReloadedAtTheHighestLevelOnly()
        {
            // A hosts X directly, and via C -> B -> X: A is a host at level 0 and again at level 2.
            // Reloading A first would be wasted: it is reloaded again after C, and reloads everything nested in it.
            var report = WriteReport(
                ("X", new string[0]),
                ("B", new[] { "X" }),
                ("C", new[] { "B", "B/X" }),
                ("A", new[] { "X", "C", "C/B", "C/B/X" }));
            var result = BuildWorkLists(WriteChangeList("X"), report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            AssertLevels(L("B"), L("C"), L("A"));
        }

        [Test]
        public void TaskListNumbering_HasNoGaps()
        {
            // Q hosts X; P hosts Q and X. Level 0 {Q, P}, level 1 {P}: P moves up to level 1, level 0 keeps Q.
            var report = WriteReport(("X", new string[0]), ("Q", new[] { "X" }), ("P", new[] { "X", "Q", "Q/X" }));
            BuildWorkLists(WriteChangeList("X"), report);
            var keys = TaskLists().Keys.ToList();
            Assert.That(keys, Is.EqualTo(new List<string> { "TaskOutput 00", "TaskOutput 01" }));
        }

        // ---------------------------------------- nothing to do / failures ----------------------------------------

        [Test]
        public void ChangeListWithHeaderOnly_NothingToReload_NoTaskLists()
        {
            var report = WriteReport(("X", new string[0]), ("A", new[] { "X" }));
            var result = BuildWorkLists(WriteChangeList(), report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((string)result.message, Does.Contain("Empty change list"));
            Assert.That(TaskLists(), Is.Empty);
        }

        [Test]
        public void ChangedFamilyNotHostedAnywhere_NoTaskLists()
        {
            var report = WriteReport(("X", new string[0]), ("A", new[] { "X" }));
            var result = BuildWorkLists(WriteChangeList("Unknown"), report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(TaskLists(), Is.Empty);
        }

        [Test]
        public void MissingChangeList_Fails()
        {
            var report = WriteReport(("X", new string[0]));
            var result = BuildWorkLists(Path.Combine(tempDirectory, "nothere.csv"), report);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Changed families list files does not exist."));
        }

        [Test]
        public void MissingReport_Fails()
        {
            var result = BuildWorkLists(WriteChangeList("X"), Path.Combine(tempDirectory, "nothere.csv"));
            Assert.That((bool)result.status, Is.False);
            Assert.That(TaskLists(), Is.Empty);
        }

        [Test]
        public void CircularNesting_Fails_AndWritesNoTaskLists()
        {
            // A contains B, B contains A
            var report = WriteReport(
                ("X", new string[0]),
                ("A", new[] { "X", "B", "B/A" }),
                ("B", new[] { "A", "A/B", "A/X" }));
            var result = BuildWorkLists(WriteChangeList("X"), report);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("circular family nesting"));
            Assert.That(TaskLists(), Is.Empty, "a failed run must not leave partial task lists behind");
        }

        [Test]
        public void MaximumNumberOfTaskLists_Is20()
        {
            Assert.That((int)reloadModule.MAXIMUM_NUMBER_OF_TASK_LISTS, Is.EqualTo(20));
        }

        // ---------------------------------------- task list files ----------------------------------------

        [Test]
        public void GetTaskListFileName_CounterIsZeroPadded()
        {
            Assert.That((string)reloadUtils.get_task_list_file_name(@"C:\out", 0), Is.EqualTo(Path.Combine(@"C:\out", "TaskOutput 00.txt")));
            Assert.That((string)reloadUtils.get_task_list_file_name(@"C:\out", 12), Is.EqualTo(Path.Combine(@"C:\out", "TaskOutput 12.txt")));
        }

        [Test]
        public void WriteReloadListToFile_WritesOneFilePathPerRow_WithoutHeader()
        {
            var report = WriteReport(("A", new string[0]), ("B", new string[0]));
            dynamic roots = familyUtils.read_root_families_from_report(report).result;
            bool written = reloadUtils.write_reload_list_to_file(roots, outputDirectory, 3);
            Assert.That(written, Is.True);
            string[] lines = File.ReadAllLines(Path.Combine(outputDirectory, "TaskOutput 03.txt"));
            // note: the csv writer escapes backslashes (C:\\lib\\A.rfa), which Windows reads as the same path
            Assert.That(lines.Select(l => l.Trim('"').Replace(@"\\", @"\")), Is.EquivalentTo(new[] { @"C:\lib\A.rfa", @"C:\lib\B.rfa" }));
        }

        [Test]
        public void WriteOutEmptyTaskList_WritesEmptyFile()
        {
            Assert.That((bool)reloadUtils.write_out_empty_task_list(outputDirectory, 1), Is.True);
            string file = Path.Combine(outputDirectory, "TaskOutput 01.txt");
            Assert.That(File.Exists(file), Is.True);
            Assert.That(File.ReadAllText(file).Trim(), Is.Empty);
        }

        [Test]
        public void DeleteOldTaskLists_DeletesTaskOutputFilesOnly()
        {
            File.WriteAllText(Path.Combine(outputDirectory, "TaskOutput 00.txt"), "x");
            File.WriteAllText(Path.Combine(outputDirectory, "TaskOutput 01.txt"), "x");
            File.WriteAllText(Path.Combine(outputDirectory, "Other.txt"), "x");
            Assert.That((bool)reloadUtils.delete_old_task_lists(outputDirectory), Is.True);
            Assert.That(Directory.GetFiles(outputDirectory).Select(Path.GetFileName), Is.EqualTo(new[] { "Other.txt" }));
        }

        // ---------------------------------------- change list ----------------------------------------

        [Test]
        public void ReadChangeList_SkipsHeader_StripsRfaFromName()
        {
            string file = Path.Combine(tempDirectory, "chg.csv");
            File.WriteAllLines(file, new[]
            {
                "name,path,category",
                @"Chair.rfa,C:\lib\Chair.rfa,Furniture",
                @"Table,C:\lib\Table.rfa,Furniture"
            });
            dynamic families = reloadUtils.read_change_list(file);
            Assert.That((int)families.Count, Is.EqualTo(2));
            Assert.That((string)families[0].family_name, Is.EqualTo("Chair"));
            Assert.That((string)families[0].family_file_path, Is.EqualTo(@"C:\lib\Chair.rfa"));
            Assert.That((string)families[0].family_category, Is.EqualTo("Furniture"));
            Assert.That((string)families[1].family_name, Is.EqualTo("Table"));
        }

        [Test]
        public void ReadChangeList_MissingFile_Throws()
        {
            var ex = Assert.Catch<Exception>(() => reloadUtils.read_change_list(Path.Combine(tempDirectory, "nothere.csv")));
            Assert.That(ex!.Message, Does.Contain("Changed families list files does not exist."));
        }

        [Test]
        public void ReadChangeList_EmptyFile_Throws()
        {
            string file = Path.Combine(tempDirectory, "empty.csv");
            File.WriteAllText(file, "");
            var ex = Assert.Catch<Exception>(() => reloadUtils.read_change_list(file));
            Assert.That(ex!.Message, Does.Contain("Empty families list file!"));
        }

        // ---------------------------------------- finding hosts ----------------------------------------

        private dynamic RootFamilies(string report) => familyUtils.read_root_families_from_report(report).result;

        private dynamic Family(string name)
        {
            dynamic cls = PythonEngineManager.ImportFrom("duHast.Revit.Family.Data.Objects.family_data_family", "FamilyDataFamily");
            return cls(name, "C_" + name);
        }

        private static List<string> Names(dynamic families)
        {
            var names = new List<string>();
            foreach (dynamic f in families) names.Add((string)f.family_name);
            names.Sort();
            return names;
        }

        [Test]
        public void GetDirectHostRootFamilies_ReturnsRootFamiliesDirectlyHostingTheFamily()
        {
            var roots = RootFamilies(WriteReport(("X", new string[0]), ("M", new[] { "X" }), ("T", new[] { "M", "M/X" })));
            var hosts = familyUtils.get_direct_host_root_families(roots, new PythonList { Family("X") });
            Assert.That(Names(hosts), Is.EqualTo(new List<string> { "M" }), "T hosts M, not X directly");
        }

        [Test]
        public void GetDirectHostRootFamilies_FamilyInNoHost_ReturnsEmpty()
        {
            var roots = RootFamilies(WriteReport(("X", new string[0]), ("A", new[] { "X" })));
            var hosts = familyUtils.get_direct_host_root_families(roots, new PythonList { Family("A") });
            Assert.That((int)hosts.Count, Is.EqualTo(0));
        }

        [Test]
        public void GetDirectHostRootFamilies_MatchesByNameAndCategory()
        {
            var roots = RootFamilies(WriteReport(("X", new string[0]), ("A", new[] { "X" })));
            dynamic cls = PythonEngineManager.ImportFrom("duHast.Revit.Family.Data.Objects.family_data_family", "FamilyDataFamily");
            dynamic wrongCategory = cls("X", "Other Category");
            var hosts = familyUtils.get_direct_host_root_families(roots, new PythonList { wrongCategory });
            Assert.That((int)hosts.Count, Is.EqualTo(0));
        }

        [Test]
        public void GetDirectHostRootFamilies_SharedFamily_ReturnsEachHostOnce()
        {
            var roots = RootFamilies(WriteReport(
                ("X", new string[0]),
                ("A", new[] { "X", "M", "M/X" }),
                ("B", new[] { "X" })));
            var hosts = familyUtils.get_direct_host_root_families(roots, new PythonList { Family("X") });
            // M also hosts X but is not a root family in this report, so it can not be returned
            Assert.That(Names(hosts), Is.EqualTo(new List<string> { "A", "B" }), "A and B host X, once each");
        }

        [Test]
        public void GetDirectHostRootFamilies_NotFamilyDataFamilyInstances_Throws()
        {
            var roots = RootFamilies(WriteReport(("X", new string[0])));
            Assert.Catch<Exception>(() => familyUtils.get_direct_host_root_families(roots, new PythonList { "X" }));
        }

        [Test]
        public void FindAllDirectHostFamilies_ReturnsHostsEvenIfNotRootFamilies()
        {
            // M is only nested, it has no root entry of its own
            var roots = RootFamilies(WriteReport(("X", new string[0]), ("A", new[] { "M", "M/X" })));
            var hosts = familyUtils.find_all_direct_host_families(roots, new PythonList { Family("X") });
            Assert.That(Names(hosts), Is.EqualTo(new List<string> { "M" }));
            var rootHosts = familyUtils.get_direct_host_root_families(roots, new PythonList { Family("X") });
            Assert.That((int)rootHosts.Count, Is.EqualTo(0), "a host which is not a root family can not be reloaded from a file");
        }

        [Test]
        public void GetReportFilePath_FindsReportInSubDirectory_NullIfNone()
        {
            string sub = Path.Combine(tempDirectory, "sub");
            Directory.CreateDirectory(sub);
            File.WriteAllText(Path.Combine(sub, "FamilyBaseDataCombinedReport_01.csv"), "x");
            Assert.That((string)familyUtils.get_report_file_path(tempDirectory, "FamilyBaseDataCombinedReport"),
                Is.EqualTo(Path.Combine(sub, "FamilyBaseDataCombinedReport_01.csv")));
            Assert.That(familyUtils.get_report_file_path(tempDirectory, "NotThere"), Is.Null);
        }

        [Test]
        public void ReadRootFamiliesFromReport_RootsHaveTheirNestedFamilies()
        {
            var roots = RootFamilies(WriteReport(("X", new string[0]), ("M", new[] { "X" }), ("T", new[] { "M", "M/X" })));
            Assert.That(Names(roots), Is.EqualTo(new List<string> { "M", "T", "X" }));
            foreach (dynamic root in roots)
            {
                if ((string)root.family_name == "T")
                {
                    Assert.That((int)root.nested_families_unsorted.Count, Is.EqualTo(2));
                    Assert.That((string)root.family_file_path, Is.EqualTo(@"C:\lib\T.rfa"));
                }
            }
        }

        [Test]
        public void ReadRootFamiliesFromReport_MissingFile_Fails()
        {
            dynamic result = familyUtils.read_root_families_from_report(Path.Combine(tempDirectory, "nothere.csv"));
            Assert.That((bool)result.status, Is.False);
        }

        // ---------------------------------------- FamilyDataFamily.get_direct_hosts ----------------------------------------

        [Test]
        public void GetDirectHosts_ReturnsTheFamilyNestedDirectlyAround()
        {
            var roots = RootFamilies(WriteReport(("X", new string[0]), ("T", new[] { "M", "M/X" })));
            foreach (dynamic root in roots)
            {
                if ((string)root.family_name != "T") continue;
                dynamic hosts = root.get_direct_hosts("X", "C_X");
                Assert.That(Names(hosts), Is.EqualTo(new List<string> { "M" }));
                dynamic hostsOfM = root.get_direct_hosts("M", "C_M");
                Assert.That(Names(hostsOfM), Is.EqualTo(new List<string> { "T" }), "the host of a family nested directly in the root is the root");
                Assert.That((int)root.get_direct_hosts("T", "C_T").Count, Is.EqualTo(0), "the root has no host");
            }
        }

        // ---------------------------------------- circular nesting ----------------------------------------

        [Test]
        public void CheckFamiliesHaveCircularReferences_FindsCircularNesting()
        {
            var report = WriteReport(
                ("X", new string[0]),
                ("A", new[] { "X", "B", "B/A" }),
                ("B", new[] { "A", "A/B", "A/X" }));
            dynamic module = PythonEngineManager.Import("duHast.Revit.Family.Data.family_base_data_circular_referencing");
            dynamic result = module.check_families_have_circular_references(report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.GreaterThan(0));
        }

        [Test]
        public void CheckFamiliesHaveCircularReferences_NoCircularNesting_NoResult()
        {
            var report = WriteReport(("X", new string[0]), ("M", new[] { "X" }), ("T", new[] { "M", "M/X" }));
            dynamic module = PythonEngineManager.Import("duHast.Revit.Family.Data.family_base_data_circular_referencing");
            dynamic result = module.check_families_have_circular_references(report);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(result.result == null || (int)result.result.Count == 0, Is.True);
        }

        // ---------------------------------------- hosts of families to rename ----------------------------------------

        [Test]
        public void FindHostFamiliesWithNestedFamiliesRequiringRename_ReturnsRootsHostingRenamedFamilies()
        {
            WriteReport(("X", new string[0]), ("A", new[] { "X" }), ("B", new[] { "X" }), ("C", new string[0]));
            File.WriteAllLines(Path.Combine(tempDirectory, "RenameDirective_01.csv"), new[]
            {
                "name,path,category,newname",
                @"X,C:\lib\X.rfa,C_X,X_New"
            });
            dynamic module = PythonEngineManager.Import("duHast.Revit.Family.Data.family_rename_find_host_families");
            dynamic result = module.find_host_families_with_nested_families_requiring_rename(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That(Names(result.result), Is.EqualTo(new List<string> { "A", "B" }));
        }

        [Test]
        public void FindHostFamiliesWithNestedFamiliesRequiringRename_NoReport_Fails()
        {
            dynamic module = PythonEngineManager.Import("duHast.Revit.Family.Data.family_rename_find_host_families");
            dynamic result = module.find_host_families_with_nested_families_requiring_rename(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("No family base data report found"));
        }

        [Test]
        public void FindHostFamiliesWithNestedFamiliesRequiringRename_NoDirectives_Fails()
        {
            WriteReport(("X", new string[0]), ("A", new[] { "X" }));
            dynamic module = PythonEngineManager.Import("duHast.Revit.Family.Data.family_rename_find_host_families");
            dynamic result = module.find_host_families_with_nested_families_requiring_rename(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("No rename directives found"));
        }
    }
}
