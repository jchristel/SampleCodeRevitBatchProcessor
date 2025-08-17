namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Options for grid state management (simplified for one state per grid)
    /// </summary>
    public class GridStateOptions
    {
        /// <summary>
        /// Whether to include filter states when saving
        /// </summary>
        public bool IncludeFilters { get; set; } = true;

        /// <summary>
        /// Whether to include sorting state when saving
        /// </summary>
        public bool IncludeSorting { get; set; } = true;

        /// <summary>
        /// Whether to include column visibility when saving
        /// </summary>
        public bool IncludeVisibility { get; set; } = true;

        /// <summary>
        /// Whether to include column order when saving
        /// </summary>
        public bool IncludeColumnOrder { get; set; } = true;

        /// <summary>
        /// Whether to include column widths when saving
        /// </summary>
        public bool IncludeColumnWidths { get; set; } = true;
    }
}