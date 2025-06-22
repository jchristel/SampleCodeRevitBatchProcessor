
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
    }
}

