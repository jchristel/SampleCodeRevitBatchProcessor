using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class Settings
    {
        // path to the data file containing the schedule of accommodations
        public string DataPath { get; set; }

        // list of supported Revit categories
        public List<string> SupportedCategories { get; set; }
    }
}
