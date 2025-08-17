

using duHastNet.UI.CustomControls.CustomDataGrid;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace duHastNet.Utils.WPF.ViewModels
{
    public abstract partial class BaseDynamicGridViewModel<TData>
    where TData : DynamicRowData, new()
    {
        private ObservableCollection<DynamicColumnDefinition> _columnDefinitions;
        private ObservableCollection<TData> _data;
        private ObservableCollection<AvailableColumnDefinition> _availableColumns;

        // field to store removed column data
        protected Dictionary<string, Dictionary<int, object>> _removedColumnData = new Dictionary<string, Dictionary<int, object>>();

        #region Properties

        public ObservableCollection<DynamicColumnDefinition> ColumnDefinitions
        {
            get => _columnDefinitions;
            set
            {
                _columnDefinitions = value;
                OnPropertyChanged();
            }
        }

        public ObservableCollection<TData> Data
        {
            get => _data;
            set
            {
                _data = value;
                OnPropertyChanged();
            }
        }

        public ObservableCollection<AvailableColumnDefinition> AvailableColumns
        {
            get => _availableColumns;
            set
            {
                _availableColumns = value;
                OnPropertyChanged();
            }
        }

        #endregion

        #region Computed Properties

        public IEnumerable<AvailableColumnDefinition> AvailableColumnsToAdd =>
            AvailableColumns?.Where(ac => !ColumnDefinitions.Any(c => c.PropertyName == ac.PropertyName)) ?? Enumerable.Empty<AvailableColumnDefinition>();

        public IEnumerable<IGrouping<string, AvailableColumnDefinition>> AvailableColumnsByCategory =>
            AvailableColumnsToAdd.GroupBy(c => c.Category);

        public IEnumerable<string> ColumnNames => ColumnDefinitions?.Select(c => c.PropertyName) ?? Enumerable.Empty<string>();

        public IEnumerable<string> EditableColumnNames =>
            ColumnDefinitions?.Where(c => !c.IsReadOnly).Select(c => c.PropertyName) ?? Enumerable.Empty<string>();

        #endregion

    }
}