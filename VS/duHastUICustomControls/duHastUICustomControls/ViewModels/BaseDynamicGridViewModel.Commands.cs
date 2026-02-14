using CommunityToolkit.Mvvm.Input;
using duHastNet.UI.CustomControls.CustomDataGrid;
using System;
using System.Collections.Generic;
using System.Linq;

namespace duHastNet.Utils.WPF.ViewModels
{
    /// <summary>
    /// Command implementations for BaseDynamicGridViewModel.
    /// Commands are generated via CommunityToolkit.Mvvm source generators using [RelayCommand] attributes.
    /// </summary>
    public abstract partial class BaseDynamicGridViewModel<TData>
        where TData : DynamicRowData, new()
    {
        #region Row Commands

        /// <summary>
        /// Command to add a new row to the grid.
        /// Generated command name: AddRowCommand
        /// </summary>
        [RelayCommand]
        private void AddRow()
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

        /// <summary>
        /// Command to remove a row from the grid.
        /// Generated command name: RemoveRowCommand
        /// </summary>
        /// <param name="parameter">The row to remove (TData), row index (int), or null to remove last row</param>
        [RelayCommand]
        private void RemoveRow(object parameter)
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

        #region Column Commands

        /// <summary>
        /// Command to add a column to the grid.
        /// Generated command name: AddSelectedColumnCommand
        /// </summary>
        /// <param name="propertyName">The property name of the column to add</param>
        [RelayCommand]
        private void AddSelectedColumn(string propertyName)
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

        /// <summary>
        /// Command to remove a column from the grid.
        /// Generated command name: RemoveColumnCommand
        /// </summary>
        /// <param name="propertyName">The property name of the column to remove, or "last" to remove the last column</param>
        [RelayCommand]
        private void RemoveColumn(string propertyName)
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

        /// <summary>
        /// Command to toggle the read-only state of a column.
        /// Generated command name: ToggleColumnLockCommand
        /// </summary>
        /// <param name="propertyName">The property name of the column to toggle</param>
        [RelayCommand]
        private void ToggleColumnLock(string propertyName)
        {
            var column = ColumnDefinitions.FirstOrDefault(c => c.PropertyName == propertyName);
            if (column != null)
            {
                column.IsReadOnly = !column.IsReadOnly;
                RefreshGrid();
            }
        }

        #endregion

        #region Data Commands

        /// <summary>
        /// Command to clear all data from the grid.
        /// Generated command name: ClearDataCommand
        /// </summary>
        [RelayCommand]
        private void ClearData()
        {
            Data.Clear();
            // Also clear stored column data since rows are gone
            _removedColumnData.Clear();
        }

        #endregion

        #region Helper Methods (not commands)

        /// <summary>
        /// Stores data from a column before it's removed, allowing restoration if the column is added back.
        /// </summary>
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

        /// <summary>
        /// Restores previously stored column data, or sets default values for a newly added column.
        /// Protected virtual so it can be overridden in inherited classes.
        /// </summary>
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

        /// <summary>
        /// Clears all stored column data that was saved when columns were removed.
        /// </summary>
        public virtual void ClearStoredColumnData()
        {
            _removedColumnData.Clear();
        }

        /// <summary>
        /// Removes the last column from the grid.
        /// </summary>
        public virtual void RemoveLastColumn()
        {
            if (ColumnDefinitions.Count > 0)
            {
                var lastColumn = ColumnDefinitions.Last();
                RemoveColumn(lastColumn.PropertyName);
            }
        }

        /// <summary>
        /// Triggers a refresh of the grid by resetting the ColumnDefinitions property.
        /// </summary>
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