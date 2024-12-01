using Newtonsoft.Json;
using NUnit.Framework;
using PythonTests.Setup;
using System;
using System.Collections.Generic;
using System.IO;

namespace PythonTests.Revit.Family.Data
{
    public class FamilyIndividualReportReaderTests
    {
        private string dataTestDirectory;
        private List<TestFileData> familyBaseTestFiles;
        private List<TestFileData> familyWarningsTestFiles;
        private List<TestFileData> familyLinePatternsTestFiles;
        private List<TestFileData> familyCategoriesTestFiles;
        private List<TestFileData> familySharedParametersTestFiles;

        [SetUp]
        public void SetUp()
        {
            dataTestDirectory = PythonTests.PythonRunner.GetTestDataPath();

            familyBaseTestFiles = new List<TestFileData>
            {
                new TestFileData("FamilyBaseDataCombinedReport_empty_file.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilyBaseDataCombinedReport_empty.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilyBaseDataCombinedReport_multiple.csv", true, 5, new List<List<string>>
                {
                    new List<string> { "FamilyBase", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa" },
                    new List<string> { "FamilyBase", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-" },
                    new List<string> { "FamilyBase", "Sample_Family_Ten", "Generic Annotations", "Sample_Family_Ten", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa" },
                    new List<string> { "FamilyBase", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa" },
                    new List<string> { "FamilyBase", "Sample_Family_Six :: Sample_Family_Thirteen", "Specialty Equipment :: Section Marks", "Sample_Family_Thirteen", "-" }
                }),
                new TestFileData("FamilyBaseDataCombinedReport_single.csv", true, 1, new List<List<string>>
                {
                    new List<string> { "FamilyBase", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa" }
                })
            };

            familyWarningsTestFiles = new List<TestFileData>
            {
                new TestFileData("FamilyWarningsCombinedReport_empty_file.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilyWarningsCombinedReport_empty.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilyWarningsCombinedReport_multiple.csv", true, 5, new List<List<string>>
                {
                    new List<string> { "Warnings", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "No warnings present in family.", "", "None", "None" },
                    new List<string> { "Warnings", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-", "No warnings present in family.", "", "None", "None" },
                    new List<string> { "Warnings", "Sample_Family_Ten", "Generic Annotations", "Sample_Family_Ten", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa", "No warnings present in family.", "", "None", "None" },
                    new List<string> { "Warnings", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "No warnings present in family.", "", "None", "None" },
                    new List<string> { "Warnings", "Sample_Family_Six :: Sample_Family_Thirteen", "Specialty Equipment :: Section Marks", "Sample_Family_Thirteen", "-", "No warnings present in family.", "", "None", "None" }
                }),
                new TestFileData("FamilyWarningsCombinedReport_single.csv", true, 1, new List<List<string>>
                {
                    new List<string> { "Warnings", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "No warnings present in family.", "", "None", "None" }
                })
            };

            familyLinePatternsTestFiles = new List<TestFileData>
            {
                new TestFileData("FamilyLinePatternsCombinedReport_empty_file.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilyLinePatternsCombinedReport_empty.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilyLinePatternsCombinedReport_multiple.csv", true, 14, new List<List<string>>
                {
                    new List<string> { "LinePattern", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "1", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": -2009518}]", "Hidden 04_BVN", "1428068" },
                    new List<string> { "LinePattern", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "2", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight :: Sample_Family_Thirteen\", \"element_id\": -2000530}]", "Reference Plane 02_BVN", "1428069" },
                    new List<string> { "LinePattern", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "2", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight :: Sample_Family_Thirteen\", \"element_id\": -2000083}]", "Dash 06_BVN", "1436489" },
                    new List<string> { "LinePattern", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "1", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 10600768}]", "Dash dot", "1499753" },
                    new List<string> { "LinePattern", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-", "0", "None", "Hidden 04_BVN", "1428068" },
                    new List<string> { "LinePattern", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-", "1", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight :: Sample_Family_Thirteen\", \"element_id\": -2000530}]", "Reference Plane 02_BVN", "1428069" },
                    new List<string> { "LinePattern", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-", "1", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight :: Sample_Family_Thirteen\", \"element_id\": -2000083}]", "Dash 06_BVN", "1436489" },
                    new List<string> { "LinePattern", "Sample_Family_Ten", "Generic Annotations", "Sample_Family_Ten", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa", "0", "None", "Hidden 04_BVN", "1428068" },
                    new List<string> { "LinePattern", "Sample_Family_Ten", "Generic Annotations", "Sample_Family_Ten", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa", "1", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": -2000530}]", "Reference Plane 02_BVN", "1428069" },
                    new List<string> { "LinePattern", "Sample_Family_Ten", "Generic Annotations", "Sample_Family_Ten", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa", "1", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": -2000083}]", "Dash 06_BVN", "1436489" },
                    new List<string> { "LinePattern", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "3", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": -2009527},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Eleven\", \"element_id\": -2009512},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": -2009517}]", "Hidden 04_BVN", "1428068" },
                    new List<string> { "LinePattern", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "9", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Thirteen\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Eleven\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Eleven :: Section Tail - Upgrade\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven :: Symbol_Outlet_GPO_Single_Emergency_ANN\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven :: Section Tail - Upgrade\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN :: Label_Text_1_5mm_ANN\", \"element_id\": -2000530}]", "Reference Plane 02_BVN", "1428069" },
                    new List<string> { "LinePattern", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "9", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Thirteen\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Eleven\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Eleven :: Section Tail - Upgrade\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven :: Symbol_Outlet_GPO_Single_Emergency_ANN\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven :: Section Tail - Upgrade\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN :: Label_Text_1_5mm_ANN\", \"element_id\": -2000083}]", "Dash 06_BVN", "1436489" },
                    new List<string> { "LinePattern", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "3", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 8485759},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Eleven\", \"element_id\": 9152387},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 9156917}]", "Dash dot", "1499753" }
                }),
                new TestFileData("FamilyLinePatternsCombinedReport_single.csv", true, 4, new List<List<string>>
                {
                    new List<string> { "LinePattern", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "1", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": -2009518}]", "Hidden 04_BVN", "1428068" },
                    new List<string> { "LinePattern", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "2", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": -2000530},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight :: Sample_Family_Thirteen\", \"element_id\": -2000530}]", "Reference Plane 02_BVN", "1428069" },
                    new List<string> { "LinePattern", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "2", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": -2000083},{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight :: Sample_Family_Thirteen\", \"element_id\": -2000083}]", "Dash 06_BVN", "1436489" },
                    new List<string> { "LinePattern", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "1", "[{\"data_type\": \"FamilyLinePatternDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 10600768}]", "Dash dot", "1499753" },
                    new List<string> { "LinePattern", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-", "0", "None", "Hidden 04_BVN", "1428068" }
                })
            };

            familyCategoriesTestFiles = new List<TestFileData>
            {
                new TestFileData("FamilyCategoriesCombinedReport_empty_file.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilyCategoriesCombinedReport_empty.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilyCategoriesCombinedReport_multiple.csv", true, 6, new List<List<string>>
                {
                    new List<string> { "Category", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "1", "[{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 10601223}]", "Furniture Systems", "Fixed Furniture", "3674407", "None", "None", "None", "None", "-1", "None", "1", "0", "0", "0" },
                    new List<string> { "Category", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "0", "None", "Furniture Systems", "<Hidden Lines>", "-2009518", "None", "None", "None", "None", "-1", "None", "3", "0", "0", "0" },
                    new List<string> { "Category", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-", "0", "None", "Section Marks", "<Wide Lines>", "-2000404", "None", "None", "None", "None", "-1", "None", "3", "0", "0", "0" },
                    new List<string> { "Category", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-", "0", "None", "Section Marks", "<Medium Lines>", "-2000403", "None", "None", "None", "None", "-1", "None", "3", "0", "0", "0" },
                    new List<string> { "Category", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-", "4", "[{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Thirteen\", \"element_id\": 10600645},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Thirteen\", \"element_id\": 10600646},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Thirteen\", \"element_id\": 10600647},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Thirteen\", \"element_id\": 10600648}]", "Section Marks", "<Thin Lines>", "-2000401", "None", "None", "None", "None", "-1", "None", "1", "0", "0", "0" },
                    new List<string> { "Category", "Sample_Family_Ten", "Generic Annotations", "Sample_Family_Ten", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa", "14", "[{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156354},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156355},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156356},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156369},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156370},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156371},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156372},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156373},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156374},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156375},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156376},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156377},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156378},{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Ten\", \"element_id\": 9156379}]", "Generic Annotations", "Generic Annotation_Ceiling Only", "1639988", "None", "None", "None", "None", "-1", "None", "5", "0", "0", "0" }
                }),
                new TestFileData("FamilyCategoriesCombinedReport_single.csv", true, 2, new List<List<string>>
                {
                    new List<string> { "Category", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "1", "[{\"data_type\": \"FamilyCategoryDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 10601223}]", "Furniture Systems", "Fixed Furniture", "3674407", "None", "None", "None", "None", "-1", "None", "1", "0", "0", "0" },
                    new List<string> { "Category", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "0", "None", "Furniture Systems", "<Hidden Lines>", "-2009518", "None", "None", "None", "None", "-1", "None", "3", "0", "0", "0" }
                })
            };

            familySharedParametersTestFiles = new List<TestFileData>
            {
                new TestFileData("FamilySharedParametersCombinedReport_empty_file.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilySharedParametersCombinedReport_empty.csv", false, 0, new List<List<string>>()),
                new TestFileData("FamilySharedParametersCombinedReport_multiple.csv", true, 34, new List<List<string>>
                {
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "94e25b89-289e-43d7-bba9-c1c23be396e9", "Author", "118408", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 118408}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "3091b658-a4ec-4130-98c3-f9e7dfd4c071", "ItemCode", "1640398", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1640398}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "81cfdf2f-1f17-4a3e-a245-37a65b7b16a0", "ItemDescription", "1640399", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1640399}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "be50f510-c92c-4c52-9dcf-b152201710df", "ItemGroup", "1640401", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1640401}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "1d88889c-80d2-4aad-acbe-11076796e986", "Copyright", "1642131", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1642131}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "0e397bbd-a378-4824-b08a-3c03423f5545", "HEIGHT_BVN", "1642132", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1642132}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "980aef7a-c409-4f02-acb2-895aed435f26", "DEPTH_BVN", "1642133", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1642133}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "10fc5a92-3d94-4deb-b74a-23825ebce640", "WIDTH_BVN", "1642135", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1642135}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "6a99c82d-821c-4726-8c75-a4e0097f4441", "DetailedCategory", "1698538", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698538}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "a65f6d59-9c87-44bc-866b-5644e8412a3f", "ModifiedIssue", "1698539", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698539}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "bf4c7aa0-8e21-4b5c-922b-204d48970e70", "Responsibility", "1698541", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698541}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "9fb538e8-0a21-47d8-aa80-79ca7db6dccc", "UniqueID", "1698542", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698542}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "6cc0c155-4ff7-44e0-9ed0-2b7e49c17aeb", "MOUNTING_HEIGHT_TOP_BVN", "1698543", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698543}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "f074bc9a-c650-42f4-aeb1-29de0255343f", "MOUNTING_HEIGHT_US_BVN", "1698544", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698544}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "c26b60fc-38e7-410b-97ce-ab7c4c36ea01", "CEILING_HEIGHT_BVN", "1721566", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1721566}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight :: Sample_Family_Thirteen", "Furniture Systems :: Section Marks", "Sample_Family_Thirteen", "-", "", "No shared parameter present in family.", "-1", "0", "None" },
                    new List<string> { "SharedParameter", "Sample_Family_Ten", "Generic Annotations", "Sample_Family_Ten", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa", "", "No shared parameter present in family.", "-1", "0", "None" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "94e25b89-289e-43d7-bba9-c1c23be396e9", "Author", "118408", "3", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 118408},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Eleven\", \"element_id\": 118408},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 118408}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "3091b658-a4ec-4130-98c3-f9e7dfd4c071", "ItemCode", "1640398", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1640398},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1640398}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "81cfdf2f-1f17-4a3e-a245-37a65b7b16a0", "ItemDescription", "1640399", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1640399},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1640399}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "be50f510-c92c-4c52-9dcf-b152201710df", "ItemGroup", "1640401", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1640401},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1640401}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "1d88889c-80d2-4aad-acbe-11076796e986", "Copyright", "1642131", "3", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1642131},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Eleven\", \"element_id\": 1642131},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1642131}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "0e397bbd-a378-4824-b08a-3c03423f5545", "HEIGHT_BVN", "1642132", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1642132},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1642132}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "980aef7a-c409-4f02-acb2-895aed435f26", "DEPTH_BVN", "1642133", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1642133},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1642133}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "10fc5a92-3d94-4deb-b74a-23825ebce640", "WIDTH_BVN", "1642135", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1642135},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1642135}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "6a99c82d-821c-4726-8c75-a4e0097f4441", "DetailedCategory", "1698538", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1698538},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1698538}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "a65f6d59-9c87-44bc-866b-5644e8412a3f", "ModifiedIssue", "1698539", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1698539},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1698539}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "bf4c7aa0-8e21-4b5c-922b-204d48970e70", "Responsibility", "1698541", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1698541},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1698541}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "9fb538e8-0a21-47d8-aa80-79ca7db6dccc", "UniqueID", "1698542", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1698542},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1698542}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "c26b60fc-38e7-410b-97ce-ab7c4c36ea01", "CEILING_HEIGHT_BVN", "1721566", "2", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six\", \"element_id\": 1721566},{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 1721566}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "b74b295e-c1e3-4d7d-b98a-29a1af08d12d", "Modified Issue", "9133881", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Eleven\", \"element_id\": 9133881}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "3f3f6ed3-c88f-443e-a0b0-b09bbb067881", "MOUNTING_HEIGHT_CENTRE_BVN", "9133882", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 9133882}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "6cc0c155-4ff7-44e0-9ed0-2b7e49c17aeb", "MOUNTING_HEIGHT_TOP_BVN", "9133883", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 9133883}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Six", "Specialty Equipment", "Sample_Family_Six", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa", "f074bc9a-c650-42f4-aeb1-29de0255343f", "MOUNTING_HEIGHT_US_BVN", "9133884", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Six :: Sample_Family_Seven\", \"element_id\": 9133884}]" },
                }),
                new TestFileData("FamilySharedParametersCombinedReport_single.csv", true, 15, new List<List<string>>
                {
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "94e25b89-289e-43d7-bba9-c1c23be396e9", "Author", "118408", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 118408}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "3091b658-a4ec-4130-98c3-f9e7dfd4c071", "ItemCode", "1640398", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1640398}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "81cfdf2f-1f17-4a3e-a245-37a65b7b16a0", "ItemDescription", "1640399", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1640399}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "be50f510-c92c-4c52-9dcf-b152201710df", "ItemGroup", "1640401", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1640401}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "1d88889c-80d2-4aad-acbe-11076796e986", "Copyright", "1642131", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1642131}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "0e397bbd-a378-4824-b08a-3c03423f5545", "HEIGHT_BVN", "1642132", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1642132}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "980aef7a-c409-4f02-acb2-895aed435f26", "DEPTH_BVN", "1642133", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1642133}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "10fc5a92-3d94-4deb-b74a-23825ebce640", "WIDTH_BVN", "1642135", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1642135}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "6a99c82d-821c-4726-8c75-a4e0097f4441", "DetailedCategory", "1698538", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698538}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "a65f6d59-9c87-44bc-866b-5644e8412a3f", "ModifiedIssue", "1698539", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698539}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "bf4c7aa0-8e21-4b5c-922b-204d48970e70", "Responsibility", "1698541", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698541}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "9fb538e8-0a21-47d8-aa80-79ca7db6dccc", "UniqueID", "1698542", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698542}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "6cc0c155-4ff7-44e0-9ed0-2b7e49c17aeb", "MOUNTING_HEIGHT_TOP_BVN", "1698543", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698543}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "f074bc9a-c650-42f4-aeb1-29de0255343f", "MOUNTING_HEIGHT_US_BVN", "1698544", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1698544}]" },
                    new List<string> { "SharedParameter", "Sample_Family_Eight", "Furniture Systems", "Sample_Family_Eight", @"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa", "c26b60fc-38e7-410b-97ce-ab7c4c36ea01", "CEILING_HEIGHT_BVN", "1721566", "1", "[{\"data_type\": \"FamilySharedParameterDataStorageUsedBy\", \"root_name_path\": \"Sample_Family_Eight\", \"element_id\": 1721566}]" }
                })
            };
        }

        [Test]
        public void ModuleShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.FamilyReportReaderModule, Is.Not.Null, "data_family_report_reader should be loaded.");
            Console.WriteLine(dataTestDirectory);
        }

        [Test]
        public void TestReadFamilyBaseData()
        {

            dynamic familyReportReader = PythonEngineManager.FamilyReportReaderModule;

            string dataTestDirectoryReader01 = Path.Combine(dataTestDirectory, "ReadReport_01");
            Console.WriteLine(dataTestDirectoryReader01);

            foreach (var testFile in familyBaseTestFiles)
            {
                Console.WriteLine(testFile.FileName);
                var filePath = Path.Combine(dataTestDirectoryReader01, testFile.FileName);

                var result = familyReportReader.read_family_base_data(filePath);

                Assert.That(testFile.ExpectedStatus, Is.EqualTo(result.status), $"Expecting status {testFile.ExpectedStatus} but got {result.status}");
                Assert.That(testFile.ExpectedCount, Is.EqualTo(result.result.Count), $"Expecting number of entries {testFile.ExpectedCount} but got {result.result.Count}");

                if (result.result.Count > 0)
                {
                    foreach (var data in result.result)
                    {
                        Console.WriteLine(data.formatted_indented_str(0, "..."));
                        var dataValues = data.get_data_values_as_list_of_strings();
                        Assert.That(testFile.ExpectedData, Does.Contain(dataValues), $"Expecting data {dataValues} in list but no match");
                    }
                }
            }
        }

        [Test]
        public void TestReadFamilyWarningsData()
        {
            dynamic familyReportReader = PythonEngineManager.FamilyReportReaderModule;

            string dataTestDirectoryReader01 = Path.Combine(dataTestDirectory, "ReadReport_05");
            Console.WriteLine(dataTestDirectoryReader01);

            foreach (var testFile in familyWarningsTestFiles)
            {
                Console.WriteLine(testFile.FileName);
                var filePath = Path.Combine(dataTestDirectoryReader01, testFile.FileName);

                var result = familyReportReader.read_family_warnings_data(filePath);

                Assert.That(testFile.ExpectedStatus, Is.EqualTo(result.status), $"Expecting status {testFile.ExpectedStatus} but got {result.status}");
                Assert.That(testFile.ExpectedCount, Is.EqualTo(result.result.Count), $"Expecting number of entries {testFile.ExpectedCount} but got {result.result.Count}");

                if (result.result.Count > 0)
                {
                    foreach (var data in result.result)
                    {
                        Console.WriteLine(data.formatted_indented_str(0, "..."));
                        var dataValues = data.get_data_values_as_list_of_strings();
                        Assert.That(testFile.ExpectedData, Does.Contain(dataValues), $"Expecting data {dataValues} in list but no match");
                    }
                }
            }
        }

        [Test]
        public void TestReadFamilyLinePatternsData()
        {
            dynamic familyReportReader = PythonEngineManager.FamilyReportReaderModule;

            string dataTestDirectoryReader01 = Path.Combine(dataTestDirectory, "ReadReport_03");
            Console.WriteLine(dataTestDirectoryReader01);

            foreach (var testFile in familyLinePatternsTestFiles)
            {
                Console.WriteLine(testFile.FileName);
                var filePath = Path.Combine(dataTestDirectoryReader01, testFile.FileName);

                var result = familyReportReader.read_family_line_pattern_base_data(filePath);

                Assert.That(testFile.ExpectedStatus, Is.EqualTo(result.status), $"Expecting status {testFile.ExpectedStatus} but got {result.status}");
                Assert.That(testFile.ExpectedCount, Is.EqualTo(result.result.Count), $"Expecting number of entries {testFile.ExpectedCount} but got {result.result.Count}");

                for (int i = 0; i < result.result.Count; i++)
                {
                    var data = result.result[i];
                    var expectedData = testFile.ExpectedData[i];
                    Console.WriteLine(data.formatted_indented_str(1, "..."));
                    var dataValues = data.get_data_values_as_list_of_strings();
                    Assert.That(dataValues, Is.EqualTo(expectedData), $"Expecting data {expectedData} but got {dataValues}");
                }
            }
        }

        [Test]
        public void TestReadFamilyCategoriesData()
        {
            dynamic familyReportReader = PythonEngineManager.FamilyReportReaderModule;

            string dataTestDirectoryReader01 = Path.Combine(dataTestDirectory, "ReadReport_02");
            Console.WriteLine(dataTestDirectoryReader01);

            foreach (var testFile in familyCategoriesTestFiles)
            {
                Console.WriteLine(testFile.FileName);
                var filePath = Path.Combine(dataTestDirectoryReader01, testFile.FileName);

                var result = familyReportReader.read_family_category_base_data(filePath);

                Assert.That(testFile.ExpectedStatus, Is.EqualTo(result.status), $"Expecting status {testFile.ExpectedStatus} but got {result.status}");
                Assert.That(testFile.ExpectedCount, Is.EqualTo(result.result.Count), $"Expecting number of entries {testFile.ExpectedCount} but got {result.result.Count}");

                for (int i = 0; i < result.result.Count; i++)
                {
                    var data = result.result[i];
                    var expectedData = testFile.ExpectedData[i];
                    Console.WriteLine(data.formatted_indented_str(1, "..."));
                    var dataValues = data.get_data_values_as_list_of_strings();
                    Assert.That(dataValues, Is.EqualTo(expectedData), $"Expecting data {expectedData} but got {dataValues}");
                }
            }
        }

        [Test]
        public void TestReadFamilySharedParameterData()
        {
            dynamic familyReportReader = PythonEngineManager.FamilyReportReaderModule;

            string dataTestDirectoryReader01 = Path.Combine(dataTestDirectory, "ReadReport_04");
            Console.WriteLine(dataTestDirectoryReader01);

            foreach (var testFile in familySharedParametersTestFiles)
            {
                Console.WriteLine(testFile.FileName);
                var filePath = Path.Combine(dataTestDirectoryReader01, testFile.FileName);

                var result = familyReportReader.read_family_shared_parameter_data(filePath);

                Assert.That(result.status, Is.EqualTo(testFile.ExpectedStatus), $"Expecting status {testFile.ExpectedStatus} but got {result.status}");
                Assert.That(result.result.Count, Is.EqualTo(testFile.ExpectedCount), $"Expecting number of entries {testFile.ExpectedCount} but got {result.result.Count}");

                if (result.result.Count > 0)
                {
                    for (int i = 0; i < result.result.Count; i++)
                    {
                        var data = result.result[i].get_data_values_as_list_of_strings();
                        var dataList = new List<object>(data); // Convert PythonList to List<object> to be able to use .GetRange later on
                        Console.WriteLine(dataList);

                        bool foundMatch = false;

                        // check if entry at position nine is not "None" indicating a used by entry
                        if (dataList[9].ToString() == "None")
                        {
                            Console.WriteLine("No used by entry found");
                            //no used by entry found, a simple check if data is in list
                            Assert.That(testFile.ExpectedData, Does.Contain(dataList.ConvertAll(d => d.ToString())), $"Expecting data {dataList} in list but no match");
                            foundMatch = true;
                        }
                        else
                        {
                            Console.WriteLine("Used by entry found");
                            // a used by test result was found, check result list before and after used by entry if equal and then compare used by entry
                            foreach (var expectedData in testFile.ExpectedData)
                            {
                                var preExpectedData = expectedData.GetRange(0, 8);
                                //check string up unitl used by data is identical
                                if (dataList.GetRange(0, 8).ConvertAll(d => d.ToString()).SequenceEqual(preExpectedData))
                                {
                                    //attempt to compare used by to json and compare to expected (also json)
                                    try
                                    {
                                        var retrievedUsedBy = JsonConvert.DeserializeObject<List<Dictionary<string, object>>>(dataList[9].ToString());
                                        var expectedUsedBy = JsonConvert.DeserializeObject<List<Dictionary<string, object>>>(expectedData[9]);

                                        Assert.That(retrievedUsedBy, Is.EqualTo(expectedUsedBy), $"Expecting used by entries to match but got {retrievedUsedBy} and {expectedUsedBy}");
                                        foundMatch = true;
                                        break;
                                    }
                                    catch (Exception e)
                                    {
                                        Console.WriteLine($"Error comparing used by entries: {e.Message}\n{dataList[9]}\n{expectedData[9]}");
                                    }
                                }
                                
                            }
                        }

                        if (!foundMatch)
                        {
                            Assert.Fail($"No match found for data: {dataList}");
                        }
                    }
                }
            }
        }

        private class TestFileData
        {
            public string FileName { get; }
            public bool ExpectedStatus { get; }
            public int ExpectedCount { get; }
            public List<List<string>> ExpectedData { get; }

            public TestFileData(string fileName, bool expectedStatus, int expectedCount, List<List<string>> expectedData)
            {
                FileName = fileName;
                ExpectedStatus = expectedStatus;
                ExpectedCount = expectedCount;
                ExpectedData = expectedData;
            }
        }
    }
}