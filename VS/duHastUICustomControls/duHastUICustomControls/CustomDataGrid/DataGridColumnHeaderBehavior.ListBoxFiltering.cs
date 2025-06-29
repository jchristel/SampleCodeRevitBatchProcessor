//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//

using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static partial class DataGridColumnHeaderBehavior
    {
        #region ListBox/DropDown Filtering

        /// <summary>
        /// Displays a dialog for filtering dropdown/listbox columns.
        /// Allows selecting a value from the dropdown list and applying text search against it.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column to filter.</param>
        /// <param name="propertyName">The property name of the dropdown column to filter.</param>
        private static void ShowFilterDropDownDialog(DataGrid dataGrid, string propertyName)
        {
            // Get current dropdown filter state
            var (selectedValue, searchText) = GetCurrentDropDownFilter(dataGrid, propertyName);

            // Get available values for this dropdown column
            var availableValues = GetDropDownValuesForColumn(dataGrid, propertyName);

            var dialog = new FilterDropDownDialog(propertyName, availableValues, selectedValue, searchText)
            {
                Owner = Window.GetWindow(dataGrid)
            };

            if (dialog.ShowDialog() == true)
            {
                if (dialog.FilterCleared)
                {
                    ClearColumnFilter(dataGrid, propertyName);
                }
                else
                {
                    ApplyDropDownFilter(dataGrid, propertyName, dialog.SelectedValue, dialog.SearchText);
                }
            }
        }

        /// <summary>
        /// Gets the current dropdown filter state for a column.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to check.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A tuple containing the selected value and search text.</returns>
        private static (object selectedValue, string searchText) GetCurrentDropDownFilter(DataGrid dataGrid, string propertyName)
        {
            var selectedValueKey = $"DropDownFilter_SelectedValue_{propertyName}";
            var searchTextKey = $"DropDownFilter_SearchText_{propertyName}";

            object selectedValue = dataGrid.Resources.Contains(selectedValueKey) ? dataGrid.Resources[selectedValueKey] : null;
            string searchText = dataGrid.Resources.Contains(searchTextKey) ? (string)dataGrid.Resources[searchTextKey] : null;

            return (selectedValue, searchText);
        }

        /// <summary>
        /// Applies a dropdown filter to a column and refreshes the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to apply the filter to.</param>
        /// <param name="propertyName">The property name of the dropdown column.</param>
        /// <param name="selectedValue">The selected value from the dropdown.</param>
        /// <param name="searchText">The text search to apply within the selected value.</param>
        private static void ApplyDropDownFilter(DataGrid dataGrid, string propertyName, object selectedValue, string searchText)
        {
            SetColumnDropDownFilter(dataGrid, propertyName, selectedValue, searchText);
            ApplyAllColumnFilters(dataGrid);

            // Update filter icon for this column
            var column = dataGrid.Columns.FirstOrDefault(c => GetColumnPropertyName(c) == propertyName);
            if (column != null)
            {
                UpdateFilterIcon(dataGrid, column, propertyName);
            }
        }

        /// <summary>
        /// Stores dropdown filter information for a column in the DataGrid's resource collection.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to store the filter in.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <param name="selectedValue">The selected value from the dropdown.</param>
        /// <param name="searchText">The text search to apply within the selected value.</param>
        private static void SetColumnDropDownFilter(DataGrid dataGrid, string propertyName, object selectedValue, string searchText)
        {
            var selectedValueKey = $"DropDownFilter_SelectedValue_{propertyName}";
            var searchTextKey = $"DropDownFilter_SearchText_{propertyName}";

            // Remove existing dropdown filters
            dataGrid.Resources.Remove(selectedValueKey);
            dataGrid.Resources.Remove(searchTextKey);

            // Add new filters if specified
            if (selectedValue != null)
            {
                dataGrid.Resources[selectedValueKey] = selectedValue;
            }

            if (!string.IsNullOrWhiteSpace(searchText))
            {
                dataGrid.Resources[searchTextKey] = searchText;
            }
        }

        /// <summary>
        /// Tests whether an item passes a dropdown filter.
        /// If no value is selected from dropdown, item fails regardless of search text.
        /// If value is selected, search text is applied against the selected value.
        /// </summary>
        /// <param name="item">The item to test.</param>
        /// <param name="dataGrid">The DataGrid containing filter settings.</param>
        /// <param name="propertyName">The property name of the dropdown column.</param>
        /// <returns>True if the item passes the filter, false otherwise.</returns>
        private static bool PassesDropDownFilter(object item, DataGrid dataGrid, string propertyName)
        {
            var (selectedValue, searchText) = GetCurrentDropDownFilter(dataGrid, propertyName);

            // If no dropdown filter is set, show all
            if (selectedValue == null)
                return true;

            var itemValue = GetItemValue(item, propertyName);

            // First check: does the item's value match the selected dropdown value?
            if (!Equals(itemValue, selectedValue))
                return false;

            // Second check: if there's search text, does the selected value contain it?
            if (!string.IsNullOrWhiteSpace(searchText))
            {
                var valueAsString = selectedValue?.ToString() ?? "";
                return valueAsString.IndexOf(searchText, StringComparison.OrdinalIgnoreCase) >= 0;
            }

            // No search text, just matching the selected value is enough
            return true;
        }

        /// <summary>
        /// Gets a description of the current dropdown filter for display.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to get the filter from.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A human-readable description of the current filter, or null if no filter is applied.</returns>
        private static string GetCurrentDropDownFilterText(DataGrid dataGrid, string propertyName)
        {
            var (selectedValue, searchText) = GetCurrentDropDownFilter(dataGrid, propertyName);

            if (selectedValue == null)
                return null;

            var valueDisplay = selectedValue.ToString();

            if (!string.IsNullOrWhiteSpace(searchText))
            {
                return $"List: \"{valueDisplay}\" contains \"{searchText}\"";
            }
            else
            {
                return $"List: \"{valueDisplay}\"";
            }
        }

        /// <summary>
        /// Gets the available dropdown values for a specific column from the ViewModel.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A list of available values for the dropdown, or empty list if not found.</returns>
        private static List<object> GetDropDownValuesForColumn(DataGrid dataGrid, string propertyName)
        {
            var viewModel = dataGrid.DataContext;
            var availableColumnsProperty = viewModel?.GetType().GetProperty("AvailableColumns");

            if (availableColumnsProperty?.GetValue(viewModel) is IEnumerable<AvailableColumnDefinition> availableColumns)
            {
                var columnDef = availableColumns.FirstOrDefault(c => c.PropertyName == propertyName);
                if (columnDef != null && columnDef.UIType == ColumnUIType.DropDown)
                {
                    return columnDef.DropDownValues ?? new List<object>();
                }
            }

            return new List<object>();
        }

        /// <summary>
        /// Checks if a column is configured as a dropdown/listbox column.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>True if the column is a dropdown column, false otherwise.</returns>
        private static bool IsDropDownColumn(DataGrid dataGrid, string propertyName)
        {
            var viewModel = dataGrid.DataContext;
            var availableColumnsProperty = viewModel?.GetType().GetProperty("AvailableColumns");

            if (availableColumnsProperty?.GetValue(viewModel) is IEnumerable<AvailableColumnDefinition> availableColumns)
            {
                var columnDef = availableColumns.FirstOrDefault(c => c.PropertyName == propertyName);
                return columnDef?.UIType == ColumnUIType.DropDown;
            }

            return false;
        }

        #endregion

        #region Bulk DropDown Operations

        /// <summary>
        /// Sets dropdown values for all currently selected rows in the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the selected rows.</param>
        /// <param name="propertyName">The property name of the dropdown column.</param>
        /// <param name="value">The value to set for all selected rows.</param>
        private static void BulkSetSelectedDropDownValues(DataGrid dataGrid, string propertyName, object value)
        {
            var selectedItems = dataGrid.SelectedItems.Cast<object>();

            if (!selectedItems.Any()) return;

            foreach (var item in selectedItems)
            {
                SetItemDropDownValue(item, propertyName, value);
            }

            SyncWithUnderlyingModel(dataGrid);

            // Force DataGrid to refresh its UI
            dataGrid.Dispatcher.BeginInvoke(new Action(() =>
            {
                dataGrid.Items.Refresh();

                // Also refresh the collection view if available
                var collectionView = System.Windows.Data.CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
                collectionView?.Refresh();

            }), System.Windows.Threading.DispatcherPriority.Background);
        }

        /// <summary>
        /// Sets dropdown values for all visible or all rows in the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to update dropdown values in.</param>
        /// <param name="propertyName">The property name of the dropdown column.</param>
        /// <param name="value">The value to set.</param>
        /// <param name="includeFiltered">True to include filtered (hidden) rows, false to only affect visible rows.</param>
        private static void BulkSetDropDownValues(DataGrid dataGrid, string propertyName, object value, bool includeFiltered)
        {
            var itemsToUpdate = includeFiltered ?
                dataGrid.ItemsSource?.Cast<object>() :
                GetVisibleItems(dataGrid);

            if (itemsToUpdate == null) return;

            foreach (var item in itemsToUpdate)
            {
                SetItemDropDownValue(item, propertyName, value);
            }

            SyncWithUnderlyingModel(dataGrid);

            // Force DataGrid to refresh its UI
            dataGrid.Dispatcher.BeginInvoke(new Action(() =>
            {
                dataGrid.Items.Refresh();

                // Also refresh the collection view if available
                var collectionView = System.Windows.Data.CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
                collectionView?.Refresh();

            }), System.Windows.Threading.DispatcherPriority.Background);
        }

        /// <summary>
        /// Sets a dropdown value for a specific item, handling both DynamicRowData and regular objects.
        /// </summary>
        /// <param name="item">The data item to update.</param>
        /// <param name="propertyName">The property name of the dropdown column.</param>
        /// <param name="value">The value to set.</param>
        private static void SetItemDropDownValue(object item, string propertyName, object value)
        {
            if (item == null) return;

            // Handle DynamicRowData (same logic as SetItemCheckboxValue)
            if (item.GetType().GetProperty("Values") != null)
            {
                var valuesDict = item.GetType().GetProperty("Values").GetValue(item) as System.Collections.IDictionary;
                if (valuesDict != null)
                {
                    // Use the indexer property instead of direct dictionary access
                    // This ensures PropertyChanged events are fired
                    var indexerProperty = item.GetType().GetProperty("Item", new[] { typeof(string) });
                    if (indexerProperty != null)
                    {
                        indexerProperty.SetValue(item, value, new object[] { propertyName });
                    }
                    else
                    {
                        // Fallback to direct dictionary access
                        valuesDict[propertyName] = value;

                        // Try to manually trigger PropertyChanged
                        if (item is System.ComponentModel.INotifyPropertyChanged)
                        {
                            TriggerPropertyChanged(item, propertyName);
                        }
                    }
                }
            }
            else
            {
                // Handle regular objects
                var property = item.GetType().GetProperty(propertyName);
                if (property != null && property.CanWrite)
                {
                    property.SetValue(item, value);
                }
            }
        }

        #endregion
    }
}