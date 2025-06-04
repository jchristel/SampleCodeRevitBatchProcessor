using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public class DynamicColumnDefinition
    {
        public string PropertyName { get; set; }
        public string DisplayName { get; set; }
        public Type DataType { get; set; }
        public double Width { get; set; } = 100;
        public bool IsReadOnly { get; set; } = false;

        public DynamicColumnDefinition(string propertyName, string displayName, Type dataType)
        {
            PropertyName = propertyName;
            DisplayName = displayName;
            DataType = dataType;
        }
    }
}
