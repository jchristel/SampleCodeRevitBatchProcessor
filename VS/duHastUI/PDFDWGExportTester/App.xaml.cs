using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
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
            // Initialize the application
            var main = new duHastNet.UI.PDFDWGExporterUI.Main(
                currentPDFExportString: "PDFExportString",
                currentDWGExportString: "*Parameter1**Parameter2*-DWG-*Parameter3*[*Parameter4*]",
                parameterNames: new List<string> { "Parameter1", "Parameter2", "Parameter3", "Parameter4" }
            );

            // Execute the main function to get the settings
            var settings = main.Execute();
        }
    }
}
