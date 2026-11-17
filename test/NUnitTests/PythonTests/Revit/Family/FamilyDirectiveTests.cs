using PythonTests.Setup;

namespace PythonTests.Revit.Family
{
    /// <summary>
    /// Tests for the rename, category change and sub category change directives and the functions reading them from files.
    /// </summary>
    public class FamilyDirectiveTests
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
            if (Directory.Exists(tempDirectory))
            {
                Directory.Delete(tempDirectory, true);
            }
        }

        private string WriteFile(string fileName, params string[] lines)
        {
            string path = Path.Combine(tempDirectory, fileName);
            File.WriteAllLines(path, lines);
            return path;
        }

        // ---------------------------------------- loading ----------------------------------------

        [Test]
        public void ClassesAndModulesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.FamilyDirectiveBaseClass, Is.Not.Null);
            Assert.That(PythonEngineManager.FamilyDirectiveRenameClass, Is.Not.Null);
            Assert.That(PythonEngineManager.FamilyDirectiveChangeCategoryClass, Is.Not.Null);
            Assert.That(PythonEngineManager.FamilyDirectiveChangeSubCategoryClass, Is.Not.Null);
            Assert.That(PythonEngineManager.FamilyRenameFilesUtilsModule, Is.Not.Null);
            Assert.That(PythonEngineManager.FamilyChangeCategoryUtilsModule, Is.Not.Null);
        }

        // ---------------------------------------- directive classes ----------------------------------------

        [Test]
        public void Base_StoresNameAndCategory()
        {
            dynamic directive = PythonEngineManager.FamilyDirectiveBaseClass("Chair", "Furniture");
            Assert.That((string)directive.name, Is.EqualTo("Chair"));
            Assert.That((string)directive.category, Is.EqualTo("Furniture"));
        }

        [Test]
        public void Rename_StoresAllValues()
        {
            dynamic directive = PythonEngineManager.FamilyDirectiveRenameClass("Chair", "Furniture", @"C:\lib\Chair.rfa", "Chair_New");
            Assert.That((string)directive.name, Is.EqualTo("Chair"));
            Assert.That((string)directive.category, Is.EqualTo("Furniture"));
            Assert.That((string)directive.file_path, Is.EqualTo(@"C:\lib\Chair.rfa"));
            Assert.That((string)directive.new_name, Is.EqualTo("Chair_New"));
        }

        [Test]
        public void Rename_ConstantsDescribeDirectiveFileLayout()
        {
            dynamic cls = PythonEngineManager.FamilyDirectiveRenameClass;
            Assert.That((int)cls.RENAME_DIRECTIVE_LIST_INDEX_CURRENT_FAMILY_NAME, Is.EqualTo(0));
            Assert.That((int)cls.RENAME_DIRECTIVE_INDEX_FAMILY_FILE_PATH, Is.EqualTo(1));
            Assert.That((int)cls.RENAME_DIRECTIVE_INDEX_CATEGORY, Is.EqualTo(2));
            Assert.That((int)cls.RENAME_DIRECTIVE_LIST_INDEX_NEW_FAMILY_NAME, Is.EqualTo(3));
            Assert.That((string)cls.RENAME_DIRECTIVE_FILE_NAME_PREFIX, Is.EqualTo("RenameDirective"));
            Assert.That((string)cls.RENAME_DIRECTIVE_FILE_EXTENSION, Is.EqualTo(".csv"));
        }

        [Test]
        public void ChangeCategory_NameIsFileNameWithoutExtension_CategoryIsNone()
        {
            dynamic directive = PythonEngineManager.FamilyDirectiveChangeCategoryClass(@"C:\lib\Chairs\Chair 01.rfa", "Casework");
            Assert.That((string)directive.name, Is.EqualTo("Chair 01"));
            Assert.That(directive.category, Is.Null, "the current category is not part of the directive");
            Assert.That((string)directive.file_path, Is.EqualTo(@"C:\lib\Chairs\Chair 01.rfa"));
            Assert.That((string)directive.new_category_name, Is.EqualTo("Casework"));
        }

        [Test]
        public void ChangeSubCategory_AppliesToCategory_NameIsNone()
        {
            dynamic directive = PythonEngineManager.FamilyDirectiveChangeSubCategoryClass("Furniture", "Old Sub", "New Sub");
            Assert.That(directive.name, Is.Null, "applies to all families of the category");
            Assert.That((string)directive.category, Is.EqualTo("Furniture"));
            Assert.That((string)directive.old_sub_category_name, Is.EqualTo("Old Sub"));
            Assert.That((string)directive.new_sub_category_name, Is.EqualTo("New Sub"));
        }

        // ---------------------------------------- get_rename_directives ----------------------------------------

        [Test]
        public void GetRenameDirectives_NoFiles_Fails()
        {
            dynamic result = PythonEngineManager.FamilyRenameFilesUtilsModule.get_rename_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Rename directive file does not exist."));
        }

        [Test]
        public void GetRenameDirectives_HeaderOnly_FailsAsEmpty()
        {
            WriteFile("RenameDirective_01.csv", "name,path,category,newname");
            dynamic result = PythonEngineManager.FamilyRenameFilesUtilsModule.get_rename_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Empty rename directive file!"));
        }

        [Test]
        public void GetRenameDirectives_SkipsHeaderRow_ReadsDirectives()
        {
            WriteFile("RenameDirective_01.csv",
                "name,path,category,newname",
                @"Chair,C:\lib\Chair.rfa,Furniture,Chair_New",
                @"Table,C:\lib\Table.rfa,Furniture,Table_New");
            dynamic result = PythonEngineManager.FamilyRenameFilesUtilsModule.get_rename_directives(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(2));
            Assert.That((string)result.result[0].name, Is.EqualTo("Chair"));
            Assert.That((string)result.result[0].file_path, Is.EqualTo(@"C:\lib\Chair.rfa"));
            Assert.That((string)result.result[0].category, Is.EqualTo("Furniture"));
            Assert.That((string)result.result[0].new_name, Is.EqualTo("Chair_New"));
            Assert.That((string)result.result[1].new_name, Is.EqualTo("Table_New"));
        }

        [Test]
        public void GetRenameDirectives_IgnoresShortRows()
        {
            WriteFile("RenameDirective_01.csv",
                "name,path,category,newname",
                @"Chair,C:\lib\Chair.rfa,Furniture",
                @"Table,C:\lib\Table.rfa,Furniture,Table_New");
            dynamic result = PythonEngineManager.FamilyRenameFilesUtilsModule.get_rename_directives(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(1));
            Assert.That((string)result.result[0].name, Is.EqualTo("Table"));
        }

        [Test]
        public void GetRenameDirectives_IgnoresFilesWithOtherNames()
        {
            WriteFile("SomethingElse.csv", "name,path,category,newname", @"Chair,C:\lib\Chair.rfa,Furniture,Chair_New");
            dynamic result = PythonEngineManager.FamilyRenameFilesUtilsModule.get_rename_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
        }

        // ---------------------------------------- get_category_change_directives ----------------------------------------

        [Test]
        public void GetCategoryChangeDirectives_NoFiles_Fails()
        {
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Category change directive file does not exist."));
        }

        [Test]
        public void GetCategoryChangeDirectives_EmptyFile_Fails()
        {
            WriteFile("CategoryChangeDirective_01.csv");
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
        }

        [Test]
        public void GetCategoryChangeDirectives_NoHeaderRow_ReadsAllRows()
        {
            WriteFile("CategoryChangeDirective_01.csv",
                @"C:\lib\Chair.rfa,Casework",
                @"C:\lib\Table.rfa,Furniture Systems");
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(2));
            Assert.That((string)result.result[0].name, Is.EqualTo("Chair"));
            Assert.That((string)result.result[0].new_category_name, Is.EqualTo("Casework"));
            Assert.That((string)result.result[1].file_path, Is.EqualTo(@"C:\lib\Table.rfa"));
        }

        [Test]
        public void GetCategoryChangeDirectives_RowsRepeatedAcrossFiles_AreReturnedOnce()
        {
            WriteFile("CategoryChangeDirective_01.csv", @"C:\lib\Chair.rfa,Casework");
            WriteFile("CategoryChangeDirective_02.csv", @"C:\lib\Chair.rfa,Casework", @"C:\lib\Table.rfa,Casework");
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(2));
        }

        [Test]
        public void GetCategoryChangeDirectives_IgnoresShortRows()
        {
            WriteFile("CategoryChangeDirective_01.csv", @"C:\lib\Chair.rfa", @"C:\lib\Table.rfa,Casework");
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(1));
        }

        [Test]
        public void GetCategoryChangeDirectives_ReadsFilesInSubDirectories()
        {
            string sub = Path.Combine(tempDirectory, "sub");
            Directory.CreateDirectory(sub);
            File.WriteAllLines(Path.Combine(sub, "CategoryChangeDirective_01.csv"), new[] { @"C:\lib\Chair.rfa,Casework" });
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(1));
        }

        // ---------------------------------------- get_sub_category_change_directives ----------------------------------------

        [Test]
        public void GetSubCategoryChangeDirectives_NoFiles_Fails()
        {
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_sub_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
            Assert.That((string)result.message, Does.Contain("Sub category change directive file does not exist."));
        }

        [Test]
        public void GetSubCategoryChangeDirectives_ReadsRows()
        {
            WriteFile("SubCategoryChangeDirective_01.csv",
                "Furniture,Old A,New A",
                "Casework,Old B,New B");
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_sub_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(2));
            Assert.That((string)result.result[0].category, Is.EqualTo("Furniture"));
            Assert.That((string)result.result[0].old_sub_category_name, Is.EqualTo("Old A"));
            Assert.That((string)result.result[1].new_sub_category_name, Is.EqualTo("New B"));
        }

        [Test]
        public void GetSubCategoryChangeDirectives_IgnoresShortRows()
        {
            WriteFile("SubCategoryChangeDirective_01.csv", "Furniture,Old A", "Casework,Old B,New B");
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_sub_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.True, (string)result.message);
            Assert.That((int)result.result.Count, Is.EqualTo(1));
        }

        [Test]
        public void GetSubCategoryChangeDirectives_DoesNotReadCategoryChangeFiles()
        {
            WriteFile("CategoryChangeDirective_01.csv", @"C:\lib\Chair.rfa,Casework");
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_sub_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
        }

        [Test]
        public void GetCategoryChangeDirectives_DoesNotReadSubCategoryChangeFiles()
        {
            WriteFile("SubCategoryChangeDirective_01.csv", "Furniture,Old A,New A");
            dynamic result = PythonEngineManager.FamilyChangeCategoryUtilsModule.get_category_change_directives(tempDirectory);
            Assert.That((bool)result.status, Is.False);
        }
    }
}
