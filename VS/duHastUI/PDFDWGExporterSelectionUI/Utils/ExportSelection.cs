using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Utils
{
    public class ExportSelection
    {

        public List<int> SheetIdsToExport
        {
            get; set;
        }

        public string ExportDirectoryPath { get; set; }

        public string ExportModus {  get; set; }

    }
}
