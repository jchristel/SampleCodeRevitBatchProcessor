using System.Collections.Generic;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Represents a filter applied to a column
    /// </summary>
    public class FilterState
    {
        /// <summary>
        /// Property name of the filtered column
        /// </summary>
        public string PropertyName { get; set; }

        /// <summary>
        /// Type of filter (Text, Boolean, Numeric, DateTime, DropDown)
        /// </summary>
        public FilterType FilterType { get; set; }

        /// <summary>
        /// Filter values stored as key-value pairs to handle different filter types
        /// </summary>
        public Dictionary<string, object> FilterValues { get; set; } = new Dictionary<string, object>();

        /// <summary>
        /// Human-readable description of the filter for display purposes
        /// </summary>
        public string Description { get; set; }
    }
}
