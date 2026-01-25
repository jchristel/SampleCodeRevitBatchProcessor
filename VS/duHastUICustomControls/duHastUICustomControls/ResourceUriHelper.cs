using System;

namespace duHastNet.UI.CustomControls
{
    public static class ResourceUriHelper
    {
        // Assembly info - change this one place when versioning
        private const string ASSEMBLY_NAME = "$225.0.0.3";

        // Base URI pattern
        private static string GetPackUri(string resourcePath)
        {
            return $"pack://application:,,,/{ASSEMBLY_NAME};component/{resourcePath}";
        }

        // Specific resource URIs
        public static Uri ThreeWaySwitchStyle => new Uri(GetPackUri("ThreeWaySwitch/ThreeWaySwitchStyle.xaml"), UriKind.Absolute);
        public static Uri DynamicDataGridStyle => new Uri(GetPackUri("CustomDataGrid/DynamicDataGridStyle.xaml"), UriKind.Absolute);
        public static Uri CellEditorStyle => new Uri(GetPackUri("CellEditor/CellEditorStyle.xaml"), UriKind.Absolute);
    }
}