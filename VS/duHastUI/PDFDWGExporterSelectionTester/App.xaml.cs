using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using duHastNet.UI.PDFDWGExporterSelectionUI;

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

            var main = new duHastNet.UI.PDFDWGExporterSelectionUI.Main(
                sheetsInModel: sheets,
                printSetsInModel: printSets);

            var settings = main.Execute();
        }
    }
}
