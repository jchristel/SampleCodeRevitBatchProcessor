
using duHastNet.Utils.WPF.Commands;
using global::duHastNet.UI.CustomControls.CustomDataGrid;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Windows.Input;

namespace duHastNet.Utils.WPF.ViewModels
{
    public abstract class BaseDynamicGridViewModel<TData> : INotifyPropertyChanged, duHastNet.Utils.WPF.Interfaces.ICloseable
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

        #region Commands

        public ICommand AddRowCommand { get; }
        public ICommand RemoveRowCommand { get; }
        public ICommand AddSelectedColumnCommand { get; }
        public ICommand RemoveColumnCommand { get; }
        public ICommand ToggleColumnLockCommand { get; }
        public ICommand ClearDataCommand { get; }

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

        protected BaseDynamicGridViewModel()
        {
            // Initialize collections
            ColumnDefinitions = new ObservableCollection<DynamicColumnDefinition>();
            Data = new ObservableCollection<TData>();

            // Initialize commands
            AddRowCommand = new RelayCommand(_ => AddRow());
            RemoveRowCommand = new RelayCommand(param => RemoveRow(param));
            AddSelectedColumnCommand = new RelayCommand(param => AddSelectedColumn(param?.ToString()));
            RemoveColumnCommand = new RelayCommand(param => RemoveColumn(param?.ToString()));
            ToggleColumnLockCommand = new RelayCommand(param => ToggleColumnLock(param?.ToString()));
            ClearDataCommand = new RelayCommand(_ => ClearData());

            // Initialize available columns (derived classes override this)
            InitializeAvailableColumns();

            // Initialize selection commands
            DeleteSelectedCommand = new RelayCommand(_ => DeleteSelectedRows(), _ => HasSelection);
            ProcessSelectedCommand = new RelayCommand(_ => ProcessSelectedRows(), _ => HasSelection);
            SelectAllCommand = new RelayCommand(_ => SelectAllRows());
            ClearSelectionCommand = new RelayCommand(_ => ClearSelection(), _ => HasSelection);

            // Initialize selected items collection
            SelectedItems = new ObservableCollection<TData>();
        }

        #region Abstract Methods - Must be implemented by derived classes

        /// <summary>
        /// Define what columns are available for this specific application
        /// </summary>
        protected abstract void InitializeAvailableColumns();

        /// <summary>
        /// Create a new row with default data for this application
        /// </summary>
        protected abstract TData CreateNewRow();

        /// <summary>
        /// Get default value for a specific column in this application context
        /// </summary>
        protected abstract object GetDefaultValueForColumn(AvailableColumnDefinition columnDef);

        #endregion

        #region Virtual Methods - Can be overridden by derived classes

        /// <summary>
        /// Determine if a column should be read-only by default. Needs to be overriden in application view model if colum,n locking is required!
        /// </summary>
        protected virtual bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            // Base implementation - no columns locked by default
            // Each application can override to define its own locking rules
            return false;
        }

        /// <summary>
        /// Get default width for a column based on its data type
        /// </summary>
        protected virtual double GetDefaultWidthForType(Type dataType)
        {
            if (dataType == typeof(bool))
                return 80;
            if (dataType == typeof(int))
                return 80;
            if (dataType == typeof(double))
                return 100;
            if (dataType == typeof(DateTime))
                return 120;

            // string and others
            return 150;
        }

        /// <summary>
        /// Get standard default value for data types
        /// </summary>
        protected virtual object GetDefaultValue(Type dataType)
        {
            if (dataType == typeof(string)) return string.Empty;
            if (dataType == typeof(int)) return 0;
            if (dataType == typeof(double)) return 0.0;
            if (dataType == typeof(bool)) return false;
            if (dataType == typeof(DateTime)) return DateTime.Now;

            return dataType.IsValueType ? Activator.CreateInstance(dataType) : null;
        }

        #endregion

        #region Column Management

        public virtual void AddSelectedColumn(string propertyName)
        {
            if (string.IsNullOrEmpty(propertyName)) return;

            var availableColumn = AvailableColumns.FirstOrDefault(c => c.PropertyName == propertyName);
            if (availableColumn == null) return;

            // Check if column already exists
            if (ColumnDefinitions.Any(c => c.PropertyName == propertyName)) return;

            var newColumn = new DynamicColumnDefinition(
                availableColumn.PropertyName,
                availableColumn.DisplayName,
                availableColumn.DataType)
            {
                Width = GetDefaultWidthForType(availableColumn.DataType),
                IsReadOnly = GetDefaultReadOnlyForColumn(availableColumn.PropertyName)
            };

            ColumnDefinitions.Add(newColumn);

            // Use RestoreOrSetDefaultColumnData to make sure original data is re-instanted
            RestoreOrSetDefaultColumnData(propertyName, availableColumn);

            OnPropertyChanged(nameof(AvailableColumnsToAdd));
        }

        public virtual void RemoveColumn(string propertyName)
        {
            if (string.IsNullOrEmpty(propertyName)) return;

            if (propertyName.Equals("last", StringComparison.OrdinalIgnoreCase))
            {
                RemoveLastColumn();
                return;
            }

            var columnToRemove = ColumnDefinitions.FirstOrDefault(c => c.PropertyName == propertyName);
            if (columnToRemove != null)
            {

                // Store the data before removing it
                StoreRemovedColumnData(propertyName);

                ColumnDefinitions.Remove(columnToRemove);

                // Remove data from all rows
                foreach (var row in Data)
                {
                    if (row.Values.ContainsKey(propertyName))
                    {
                        row.Values.Remove(propertyName);
                    }
                }

                OnPropertyChanged(nameof(AvailableColumnsToAdd));
            }
        }

        private void StoreRemovedColumnData(string propertyName)
        {
            var columnData = new Dictionary<int, object>();

            for (int i = 0; i < Data.Count; i++)
            {
                if (Data[i].Values.ContainsKey(propertyName))
                {
                    columnData[i] = Data[i].Values[propertyName];
                }
            }

            _removedColumnData[propertyName] = columnData;
        }

        // protected virtual so it can be overriden in inehrited class!!
        protected virtual void RestoreOrSetDefaultColumnData(string propertyName, AvailableColumnDefinition availableColumn)
        {
            if (_removedColumnData.ContainsKey(propertyName))
            {
                // Restore original data
                var storedData = _removedColumnData[propertyName];

                for (int i = 0; i < Data.Count; i++)
                {
                    if (storedData.ContainsKey(i))
                    {
                        Data[i][propertyName] = storedData[i];
                    }
                    else
                    {
                        // Row was added after column was removed, use default
                        Data[i][propertyName] = GetDefaultValueForColumn(availableColumn);
                    }
                }

                // Remove from stored data since we've restored it
                _removedColumnData.Remove(propertyName);
            }
            else
            {
                // No stored data, use defaults (new column or data was cleared)
                foreach (var row in Data)
                {
                    row[propertyName] = GetDefaultValueForColumn(availableColumn);
                }
            }
        }

        public virtual void ClearData()
        {
            Data.Clear();
            // Also clear stored column data since rows are gone
            _removedColumnData.Clear();
        }

        // Add this method to clear stored data when you want a fresh start
        public virtual void ClearStoredColumnData()
        {
            _removedColumnData.Clear();
        }

        public virtual void RemoveLastColumn()
        {
            if (ColumnDefinitions.Count > 0)
            {
                var lastColumn = ColumnDefinitions.Last();
                RemoveColumn(lastColumn.PropertyName);
            }
        }

        public virtual void ToggleColumnLock(string propertyName)
        {
            var column = ColumnDefinitions.FirstOrDefault(c => c.PropertyName == propertyName);
            if (column != null)
            {
                column.IsReadOnly = !column.IsReadOnly;
                RefreshGrid();
            }
        }

        protected virtual void RefreshGrid()
        {
            // Trigger collection change to refresh the grid
            var temp = ColumnDefinitions;
            ColumnDefinitions = null;
            ColumnDefinitions = temp;
        }

        #endregion

        #region Row Management

        public virtual void AddRow()
        {
            var newRow = CreateNewRow();

            // Set default values for all existing columns
            foreach (var columnDef in ColumnDefinitions)
            {
                if (!newRow.Values.ContainsKey(columnDef.PropertyName))
                {
                    var availableColumn = AvailableColumns.FirstOrDefault(ac => ac.PropertyName == columnDef.PropertyName);
                    newRow[columnDef.PropertyName] = availableColumn != null
                        ? GetDefaultValueForColumn(availableColumn)
                        : GetDefaultValue(columnDef.DataType);
                }
            }

            Data.Add(newRow);
        }

        public virtual void RemoveRow(object parameter)
        {
            if (parameter is TData row && Data.Contains(row))
            {
                Data.Remove(row);
            }
            else if (parameter is int index && index >= 0 && index < Data.Count)
            {
                Data.RemoveAt(index);
            }
            else if (Data.Count > 0)
            {
                Data.RemoveAt(Data.Count - 1); // Remove last row
            }
        }

        #endregion

        #region INotifyPropertyChanged

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        #endregion

        #region ICloseable

        public virtual void OnClosing()
        {
            // Override this method in derived classes to perform clean-up operations
        }

        #endregion

        #region Selection Properties

        private TData _selectedItem;
        private ObservableCollection<TData> _selectedItems;

        /// <summary>
        /// The currently selected item (for single selection mode)
        /// </summary>
        public TData SelectedItem
        {
            get => _selectedItem;
            set
            {
                _selectedItem = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(HasSelection));
                OnSelectionChanged();
            }
        }

        /// <summary>
        /// Collection of selected items (for extended/multiple selection mode)
        /// </summary>
        public ObservableCollection<TData> SelectedItems
        {
            get => _selectedItems ?? (_selectedItems = new ObservableCollection<TData>());
            set
            {
                if (_selectedItems != null)
                {
                    _selectedItems.CollectionChanged -= OnSelectedItemsCollectionChanged;
                }

                _selectedItems = value;

                if (_selectedItems != null)
                {
                    _selectedItems.CollectionChanged += OnSelectedItemsCollectionChanged;
                }

                OnPropertyChanged();
                OnPropertyChanged(nameof(HasSelection));
                OnPropertyChanged(nameof(SelectionCount));
                OnSelectionChanged();
            }
        }

        /// <summary>
        /// Whether any items are currently selected
        /// </summary>
        public bool HasSelection => SelectedItem != null || (SelectedItems?.Count > 0);

        /// <summary>
        /// Number of selected items
        /// </summary>
        public int SelectionCount => SelectedItems?.Count ?? (SelectedItem != null ? 1 : 0);

        #endregion

        #region Selection Commands

        public ICommand DeleteSelectedCommand { get; }
        public ICommand ProcessSelectedCommand { get; }
        public ICommand SelectAllCommand { get; }
        public ICommand ClearSelectionCommand { get; }

        #endregion

        #region Selection Event Handlers

        private void OnSelectedItemsCollectionChanged(object sender, System.Collections.Specialized.NotifyCollectionChangedEventArgs e)
        {
            OnPropertyChanged(nameof(HasSelection));
            OnPropertyChanged(nameof(SelectionCount));
            OnSelectionChanged();
        }

        /// <summary>
        /// Called whenever the selection changes. Override in derived classes for custom handling.
        /// </summary>
        protected virtual void OnSelectionChanged()
        {
            // Base implementation - derived classes can override for custom behavior
            System.Diagnostics.Debug.WriteLine($"Selection changed: {SelectionCount} items selected");

            // Refresh command states
            ((RelayCommand)DeleteSelectedCommand).RaiseCanExecuteChanged();
            ((RelayCommand)ProcessSelectedCommand).RaiseCanExecuteChanged();
            ((RelayCommand)ClearSelectionCommand).RaiseCanExecuteChanged();
        }

        #endregion

        #region Selection Methods

        /// <summary>
        /// Gets all currently selected rows
        /// </summary>
        public IEnumerable<TData> GetSelectedRows()
        {
            if (SelectedItems?.Count > 0)
            {
                return SelectedItems;
            }
            else if (SelectedItem != null)
            {
                return new[] { SelectedItem };
            }

            return Enumerable.Empty<TData>();
        }

        /// <summary>
        /// Gets values from a specific property of all selected rows
        /// </summary>
        public IEnumerable<object> GetSelectedPropertyValues(string propertyName)
        {
            return GetSelectedRows()
                .Where(row => row.Values.ContainsKey(propertyName))
                .Select(row => row.Values[propertyName]);
        }

        /// <summary>
        /// Sets the selection to specific items
        /// </summary>
        public void SetSelection(IEnumerable<TData> items)
        {
            SelectedItems.Clear();

            if (items != null)
            {
                foreach (var item in items)
                {
                    SelectedItems.Add(item);
                }
            }
        }

        /// <summary>
        /// Selects items by a property value
        /// </summary>
        public void SelectByPropertyValue(string propertyName, object value)
        {
            var matchingItems = Data
                .Where(row => row.Values.ContainsKey(propertyName) &&
                             Equals(row.Values[propertyName], value))
                .ToList();

            SetSelection(matchingItems);
        }

        /// <summary>
        /// Selects all rows
        /// </summary>
        public void SelectAllRows()
        {
            SetSelection(Data);
        }

        /// <summary>
        /// Clears the current selection
        /// </summary>
        public void ClearSelection()
        {
            SelectedItems.Clear();
            SelectedItem = null;
        }

        #endregion

        #region Selection Command Implementations

        /// <summary>
        /// Deletes all selected rows. Override in derived classes for custom validation.
        /// </summary>
        protected virtual void DeleteSelectedRows()
        {
            var selectedRows = GetSelectedRows().ToList(); // Create a copy to avoid collection modification issues

            foreach (var row in selectedRows)
            {
                Data.Remove(row);
            }

            ClearSelection();
        }

        /// <summary>
        /// Process selected rows. Override in derived classes for application-specific logic.
        /// </summary>
        protected virtual void ProcessSelectedRows()
        {
            var selectedRows = GetSelectedRows().ToList();

            // Base implementation - just log the selection
            System.Diagnostics.Debug.WriteLine($"Processing {selectedRows.Count} selected rows");

            // Override this method in derived classes to add specific processing logic
        }

        #endregion

        #region Helper Methods for Selection

        /// <summary>
        /// Checks if a specific row is selected
        /// </summary>
        public bool IsRowSelected(TData row)
        {
            return SelectedItems.Contains(row) || Equals(SelectedItem, row);
        }

        /// <summary>
        /// Toggles selection of a specific row
        /// </summary>
        public void ToggleRowSelection(TData row)
        {
            if (IsRowSelected(row))
            {
                SelectedItems.Remove(row);
                if (Equals(SelectedItem, row))
                {
                    SelectedItem = null;
                }
            }
            else
            {
                SelectedItems.Add(row);
            }
        }

        /// <summary>
        /// Gets the first selected row, or null if none selected
        /// </summary>
        public TData GetFirstSelectedRow()
        {
            return SelectedItem ?? SelectedItems?.FirstOrDefault();
        }

        /// <summary>
        /// Gets selected rows that have a specific property value
        /// </summary>
        public IEnumerable<TData> GetSelectedRowsWithPropertyValue(string propertyName, object value)
        {
            return GetSelectedRows()
                .Where(row => row.Values.ContainsKey(propertyName) &&
                             Equals(row.Values[propertyName], value));
        }

        #endregion

    }
}

