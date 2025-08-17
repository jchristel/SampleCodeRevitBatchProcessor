using System.ComponentModel;


namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{

    /// <summary>
    /// Represents the sorting state of the grid
    /// </summary>
    public class SortState
    {
        /// <summary>
        /// Property name of the column being sorted
        /// </summary>
        public string PropertyName { get; set; }

        /// <summary>
        /// Direction of the sort
        /// </summary>
        public ListSortDirection Direction { get; set; }

        /// <summary>
        /// Index for multi-column sorting (future enhancement)
        /// </summary>
        public int SortIndex { get; set; } = 0;
    }

}
