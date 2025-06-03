using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.UI.CustomControls
{
    public class Data
    {
        public static List<string> Headers { get; set; } = new List<string>(); // Global headers
        public Dictionary<string, object> Values { get; set; } = new Dictionary<string, object>(); // Row data

        public Data()
        {
            // Ensure each row has every header
            foreach (var header in Headers)
            {
                if (!Values.ContainsKey(header))
                    Values[header] = null; // Default value
            }
        }
    }
}
