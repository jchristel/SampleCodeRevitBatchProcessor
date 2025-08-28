using Newtonsoft.Json;
using System.Collections.Generic;
using System.Windows;

namespace PDFDWGExporterSelectionTester
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        public App()
        {
            List<duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitSheet> sheets = new List<duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitSheet>
            {
                new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitSheet("123", "First sheet", "123000"),
                new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitSheet("456", "Second sheet" , "123001"),
                new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitSheet("890", "third sheet", "123002")
            };



            var printSet_One = new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet("set 1");
            printSet_One.AddRevitSheet(sheets[0]);
            printSet_One.AddRevitSheet(sheets[2]);


            var printSetTwo = new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet("set 2");
            printSetTwo.AddRevitSheet(sheets[0]);
            printSetTwo.AddRevitSheet(sheets[1]);

            var printSetThree = new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet("set 3");

            var printSetFour = new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet("set 4");
            printSetFour.AddRevitSheet(sheets[0]);
            printSetFour.AddRevitSheet(sheets[1]);
            printSetFour.AddRevitSheet(sheets[2]);


            List<duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet> printSets = new List<duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet>
            {
                printSet_One,
                printSetTwo,
                printSetThree,
                printSetFour
            };


            var scheduleOne = new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitSchedule("schedule 1");
            scheduleOne.AddRevitSheet(sheets[0]);
            scheduleOne.AddRevitSheet(sheets[1]);
            var scheduleTwo = new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitSchedule("schedule 2");
            scheduleTwo.AddRevitSheet(sheets[2]);
            List<duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitSchedule> schedules = new List<duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitSchedule>
            {
                scheduleOne,
                scheduleTwo
            };



            var settingsPDF = new List<duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting>
            {
                new duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting("", "", "_", "Sheet Number"),
                new duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting("", "", "-", "Sheet Name"),
                new duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting("", "", "", "Parameter3"),
                new duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting("[", "]", "", "Parameter4")
            };

            string jsonPDF = JsonConvert.SerializeObject(settingsPDF, Newtonsoft.Json.Formatting.None);

            var settingsDWG = new List<duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting>
            {
                new duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting("", "-DWG", " ", "Sheet Number"),
                new duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting("", "", "", "Sheet Name"),
                new duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting("", "", "", "Parameter3"),
                new duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting("[", "]", "", "Parameter4")
            };

            string jsonDWG = JsonConvert.SerializeObject(settingsDWG, Newtonsoft.Json.Formatting.None);


            var main = new duHastNet.UI.PDFDWGExporterSelectionUI.Main(
                sheetsInModel: sheets,
                printSetsInModel: printSets,
                schedulesInModel: schedules,
                currentPDFExportString: jsonPDF,
                currentDWGExportString: jsonDWG,
                parameterNames: new List<string> { "Sheet Number", "Sheet Name", "Parameter4" });

            var settings = main.Execute();
        }
    }
}
