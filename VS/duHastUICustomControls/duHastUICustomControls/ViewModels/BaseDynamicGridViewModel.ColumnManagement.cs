using duHastNet.UI.CustomControls.CustomDataGrid;
using System.Collections.Generic;
using System.Linq;

namespace duHastNet.Utils.WPF.ViewModels
{
    /// <summary>
    /// Helper methods for column management in BaseDynamicGridViewModel.
    /// Command implementations have been moved to BaseDynamicGridViewModel_Commands.cs.
    /// This file contains only the helper/utility methods used by those commands.
    /// </summary>
    public abstract partial class BaseDynamicGridViewModel<TData>
        where TData : DynamicRowData, new()
    {
        #region Column Management Helper Methods

        // NOTE: Command methods (AddSelectedColumn, RemoveColumn, ToggleColumnLock, ClearData)
        // have been moved to BaseDynamicGridViewModel_Commands.cs with [RelayCommand] attributes.
        // This file now contains only the helper methods used by those commands.

        /// <summary>
        /// Stores data from a column before it's removed, allowing restoration if the column is added back.
        /// Called by RemoveColumn command.
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
        /// Called by AddSelectedColumn command.
        /// </summary>
        /// <param name="propertyName">The property name of the column being restored/initialized</param>
        /// <param name="availableColumn">The column definition containing metadata</param>
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
        /// Useful when you want a fresh start without restoring old column values.
        /// </summary>
        public virtual void ClearStoredColumnData()
        {
            _removedColumnData.Clear();
        }

        /// <summary>
        /// Removes the last column from the grid.
        /// Called by RemoveColumn command when parameter is "last".
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
        /// This forces the DataGrid to rebuild its columns.
        /// Called by ToggleColumnLock command.
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