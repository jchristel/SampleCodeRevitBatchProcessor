using duHastNet.UI.PDFDWGExporterUI.Utils;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Windows;

namespace PDFDWGExportTester
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        public App()
        {
            var settingsPDF = new List<DocumentSetting>
            {
                new DocumentSetting("", "", "", "Parameter1"),
                new DocumentSetting("", "", "-", "Parameter2"),
                new DocumentSetting("", "", "", "Parameter3"),
                new DocumentSetting("[", "]", "", "Parameter4")
            };

            string jsonPDF = JsonConvert.SerializeObject(settingsPDF, Formatting.None);

            var settingsDWG = new List<DocumentSetting>
            {
                new DocumentSetting("", "", "", "Parameter1"),
                new DocumentSetting("", "-DWG", " ", "Parameter2"),
                new DocumentSetting("", "", "", "Parameter3"),
                new DocumentSetting("[", "]", "", "Parameter4")
            };

            string jsonDWG = JsonConvert.SerializeObject(settingsDWG, Formatting.None);


            // Initialize the application
            var main = new duHastNet.UI.PDFDWGExporterUI.Main(
                currentPDFExportString: jsonPDF,
                currentDWGExportString: jsonDWG,
                parameterNames: new List<string> { "Parameter1", "Parameter2", "Parameter4" },
                dwgExportSchemes: new List<string> { "Scheme1", "Scheme2" },
                selectedDWGExportScheme: "Scheme2"
            );

            // Execute the main function to get the settings
            var settings = main.Execute();
        }
    }
}
