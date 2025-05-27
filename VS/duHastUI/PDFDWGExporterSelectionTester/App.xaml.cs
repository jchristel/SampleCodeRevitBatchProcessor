using duHastNet.UI.PDFDWGExporterSelectionUI;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Xml;
using Newtonsoft.Json;

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

            List<duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet> printSets = new List<duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet>
            {
                new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet("set 1"),
                new duHastNet.UI.PDFDWGExporterSelectionUI.Models.RevitPrintSet("set 2")
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
                currentPDFExportString:jsonPDF,
                currentDWGExportString:jsonDWG,
                parameterNames: new List<string> { "Sheet Number", "Sheet Name", "Parameter4" });

            var settings = main.Execute();
        }
    }
}
