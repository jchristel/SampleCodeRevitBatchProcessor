using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.UI.CustomControls.CustomDataGrid;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Windows.Controls;

namespace duHastNet.Utils.WPF.ViewModels
{
    /// <summary>
    /// Property definitions for BaseDynamicGridViewModel.
    /// Properties are generated via CommunityToolkit.Mvvm [ObservableProperty] attributes.
    /// </summary>
    public abstract partial class BaseDynamicGridViewModel<TData>
        where TData : DynamicRowData, new()
    {
        // Field to store removed column data for restoration when columns are re-added
        protected Dictionary<string, Dictionary<int, object>> _removedColumnData = new Dictionary<string, Dictionary<int, object>>();

        #region Observable Properties

        /// <summary>
        /// Collection of column definitions that determine which columns are displayed in the grid.
        /// Generated property: ColumnDefinitions
        /// </summary>
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(AvailableColumnsToAdd))]
        [NotifyPropertyChangedFor(nameof(AvailableColumnsByCategory))]
        [NotifyPropertyChangedFor(nameof(ColumnNames))]
        [NotifyPropertyChangedFor(nameof(EditableColumnNames))]
        private ObservableCollection<DynamicColumnDefinition> _columnDefinitions;

        /// <summary>
        /// Collection of data rows displayed in the grid.
        /// Generated property: Data
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<TData> _data;

        /// <summary>
        /// Collection of all available columns that can be added to the grid.
        /// Generated property: AvailableColumns
        /// </summary>
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(AvailableColumnsToAdd))]
        [NotifyPropertyChangedFor(nameof(AvailableColumnsByCategory))]
        private ObservableCollection<AvailableColumnDefinition> _availableColumns;

        #endregion

        #region Computed Properties

        /// <summary>
        /// Gets available columns that are not currently displayed in the grid.
        /// Used for populating "Add Column" dropdowns.
        /// </summary>
        public IEnumerable<AvailableColumnDefinition> AvailableColumnsToAdd =>
            AvailableColumns?.Where(ac => !ColumnDefinitions.Any(c => c.PropertyName == ac.PropertyName))
            ?? Enumerable.Empty<AvailableColumnDefinition>();

        /// <summary>
        /// Gets available columns grouped by category for organized column selection UI.
        /// </summary>
        public IEnumerable<IGrouping<string, AvailableColumnDefinition>> AvailableColumnsByCategory =>
            AvailableColumnsToAdd.GroupBy(c => c.Category);

        /// <summary>
        /// Gets the property names of all currently displayed columns.
        /// </summary>
        public IEnumerable<string> ColumnNames =>
            ColumnDefinitions?.Select(c => c.PropertyName) ?? Enumerable.Empty<string>();

        /// <summary>
        /// Gets the property names of columns that are not read-only.
        /// </summary>
        public IEnumerable<string> EditableColumnNames =>
            ColumnDefinitions?.Where(c => !c.IsReadOnly).Select(c => c.PropertyName)
            ?? Enumerable.Empty<string>();

        #endregion
    }
}