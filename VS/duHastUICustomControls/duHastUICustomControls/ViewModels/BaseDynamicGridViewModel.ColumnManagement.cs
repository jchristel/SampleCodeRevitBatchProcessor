using duHastNet.UI.CustomControls.CustomDataGrid;
using System;
using System.Collections.Generic;
using System.Linq;


namespace duHastNet.Utils.WPF.ViewModels
{
    public abstract partial class BaseDynamicGridViewModel<TData>
    where TData : DynamicRowData, new()
    {
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
    }
}