

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Represents the state of a single column
    /// </summary>
    public class ColumnState
    {
        /// <summary>
        /// Property name that identifies this column
        /// </summary>
        public string PropertyName { get; set; }

        /// <summary>
        /// Display name of the column
        /// </summary>
        public string DisplayName { get; set; }

        /// <summary>
        /// Whether this column is currently visible
        /// </summary>
        public bool IsVisible { get; set; } = true;

        /// <summary>
        /// Display order of the column (0-based)
        /// </summary>
        public int DisplayIndex { get; set; }

        /// <summary>
        /// Width of the column
        /// </summary>
        public double Width { get; set; }

        /// <summary>
        /// Whether this column is read-only
        /// </summary>
        public bool IsReadOnly { get; set; }

        /// <summary>
        /// Data type of the column for restoration purposes
        /// </summary>
        public string DataTypeName { get; set; }
    }
}
