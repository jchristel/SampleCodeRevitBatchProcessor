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
using System.Windows.Controls;
using System.Windows.Data;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Shared utility methods for grid state serialization operations.
    /// Contains common helper functions used by capture and apply operations.
    /// </summary>
    internal static class GridStateHelpers
    {
        #region DataGrid Column Helpers

        /// <summary>
        /// Extracts the property name from a DataGrid column, handling both bound columns and header-only columns.
        /// </summary>
        /// <param name="column">The DataGridColumn to get the property name from.</param>
        /// <returns>The property name associated with the column.</returns>
        internal static string GetColumnPropertyName(DataGridColumn column)
        {
            if (column is DataGridBoundColumn boundColumn && boundColumn.Binding is Binding binding)
            {
                return binding.Path.Path.Trim('[', ']');
            }
            return column.Header?.ToString();
        }

        /// <summary>
        /// Gets the data type of a column by querying the DynamicDataGrid's ViewModel available columns metadata.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid containing the column.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>The Type of the column's data, or typeof(string) if not found.</returns>
        internal static Type GetColumnDataType(DynamicDataGrid dataGrid, string propertyName)
        {
            var viewModel = dataGrid.DataContext;
            var availableColumnsProperty = viewModel?.GetType().GetProperty("AvailableColumns");

            if (availableColumnsProperty?.GetValue(viewModel) is IEnumerable<AvailableColumnDefinition> availableColumns)
            {
                var columnDef = availableColumns.FirstOrDefault(c => c.PropertyName == propertyName);
                return columnDef?.DataType;
            }

            return typeof(string);
        }

        #endregion

        #region Filter Management Helpers

        /// <summary>
        /// Clears all filter resources from the DynamicDataGrid's resource collection.
        /// Removes text, boolean, numeric, datetime, and dropdown filters.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to clear filters from.</param>
        internal static void ClearAllFilters(DynamicDataGrid dataGrid)
        {
            if (dataGrid.Resources == null)
                return;

            var filterKeys = dataGrid.Resources.Keys.OfType<string>()
                .Where(k => k.StartsWith("TextFilter_") ||
                           k.StartsWith("TextFilterLogic_") ||
                           k.StartsWith("BooleanFilter_") ||
                           k.StartsWith("NumericFilter_") ||
                           k.StartsWith("DateTimeFilter_") ||
                           k.StartsWith("DropDownFilter_"))
                .ToList();

            foreach (var key in filterKeys)
            {
                dataGrid.Resources.Remove(key);
            }
        }

        /// <summary>
        /// Refreshes the DynamicDataGrid's filter view by calling the existing ApplyAllColumnFilters method
        /// from DataGridColumnHeaderBehavior using reflection.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to refresh filters for.</param>
        internal static void RefreshDataGridFilters(DynamicDataGrid dataGrid)
        {
            try
            {
                // Use reflection to call the existing ApplyAllColumnFilters method from DataGridColumnHeaderBehavior
                var behaviorType = typeof(DataGridColumnHeaderBehavior);
                var method = behaviorType.GetMethod("ApplyAllColumnFilters",
                    System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);

                method?.Invoke(null, new object[] { dataGrid });
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error refreshing DynamicDataGrid filters: {ex.Message}");
            }
        }

        #endregion

        #region Filter Description Helpers

        /// <summary>
        /// Gets a human-readable description for a boolean filter based on its show/hide settings.
        /// </summary>
        /// <param name="showTrue">Whether to show true values.</param>
        /// <param name="showFalse">Whether to show false values.</param>
        /// <returns>Human-readable description of the boolean filter.</returns>
        internal static string GetBooleanFilterDescription(bool? showTrue, bool? showFalse)
        {
            if (showTrue == true && showFalse == true)
                return "Boolean: Show All";
            else if (showTrue == true && showFalse != true)
                return "Boolean: Show True only";
            else if (showFalse == true && showTrue != true)
                return "Boolean: Show False only";
            else
                return "Boolean: Show None";
        }

        /// <summary>
        /// Gets a human-readable description for a numeric filter based on its operation and values.
        /// </summary>
        /// <param name="operation">The numeric filter operation (Equal, GreaterThan, etc.).</param>
        /// <param name="values">Dictionary containing the filter values (Value, FromValue, ToValue).</param>
        /// <returns>Human-readable description of the numeric filter.</returns>
        internal static string GetNumericFilterDescription(string operation, Dictionary<string, object> values)
        {
            switch (operation)
            {
                case "Equal":
                    return values.TryGetValue("Value", out var eqVal) ? $"Number: = {eqVal}" : "Number: Equal";
                case "GreaterThan":
                    return values.TryGetValue("Value", out var gtVal) ? $"Number: > {gtVal}" : "Number: Greater Than";
                case "GreaterThanOrEqual":
                    return values.TryGetValue("Value", out var gteVal) ? $"Number: >= {gteVal}" : "Number: Greater Than or Equal";
                case "LessThan":
                    return values.TryGetValue("Value", out var ltVal) ? $"Number: < {ltVal}" : "Number: Less Than";
                case "LessThanOrEqual":
                    return values.TryGetValue("Value", out var lteVal) ? $"Number: <= {lteVal}" : "Number: Less Than or Equal";
                case "Range":
                    var hasFrom = values.TryGetValue("FromValue", out var fromVal);
                    var hasTo = values.TryGetValue("ToValue", out var toVal);
                    if (hasFrom && hasTo)
                        return $"Number: {fromVal} - {toVal}";
                    else if (hasFrom)
                        return $"Number: >= {fromVal}";
                    else if (hasTo)
                        return $"Number: <= {toVal}";
                    return "Number: Range";
                default:
                    return $"Number: {operation}";
            }
        }

        /// <summary>
        /// Gets a human-readable description for a DateTime filter based on its operation and values.
        /// </summary>
        /// <param name="operation">The DateTime filter operation (On, Before, After, Between).</param>
        /// <param name="values">Dictionary containing the filter values (Date, FromDate, ToDate).</param>
        /// <returns>Human-readable description of the DateTime filter.</returns>
        internal static string GetDateTimeFilterDescription(string operation, Dictionary<string, object> values)
        {
            switch (operation)
            {
                case "On":
                    return values.TryGetValue("Date", out var onDate) ?
                        $"Date: On {((DateTime)onDate):yyyy-MM-dd}" : "Date: On";
                case "Before":
                    return values.TryGetValue("Date", out var beforeDate) ?
                        $"Date: Before {((DateTime)beforeDate):yyyy-MM-dd}" : "Date: Before";
                case "After":
                    return values.TryGetValue("Date", out var afterDate) ?
                        $"Date: After {((DateTime)afterDate):yyyy-MM-dd}" : "Date: After";
                case "Between":
                    var hasFrom = values.TryGetValue("FromDate", out var fromDate);
                    var hasTo = values.TryGetValue("ToDate", out var toDate);
                    if (hasFrom && hasTo)
                        return $"Date: {((DateTime)fromDate):yyyy-MM-dd} to {((DateTime)toDate):yyyy-MM-dd}";
                    else if (hasFrom)
                        return $"Date: From {((DateTime)fromDate):yyyy-MM-dd}";
                    else if (hasTo)
                        return $"Date: To {((DateTime)toDate):yyyy-MM-dd}";
                    return "Date: Between";
                default:
                    return $"Date: {operation}";
            }
        }

        /// <summary>
        /// Gets a human-readable description for a dropdown filter based on its selected value and search text.
        /// </summary>
        /// <param name="selectedValue">The selected value from the dropdown.</param>
        /// <param name="searchText">Optional search text applied within the selected value.</param>
        /// <returns>Human-readable description of the dropdown filter.</returns>
        internal static string GetDropDownFilterDescription(object selectedValue, string searchText)
        {
            var valueDisplay = selectedValue?.ToString() ?? "";

            if (!string.IsNullOrWhiteSpace(searchText))
            {
                return $"List: \"{valueDisplay}\" contains \"{searchText}\"";
            }
            else
            {
                return $"List: \"{valueDisplay}\"";
            }
        }

        #endregion

        #region Resource Key Helpers

        /// <summary>
        /// Gets all filter resource keys of a specific type from the DynamicDataGrid's resources.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to search.</param>
        /// <param name="filterPrefix">The prefix to search for (e.g., "TextFilter_", "BooleanFilter_").</param>
        /// <returns>List of matching resource keys.</returns>
        internal static List<string> GetFilterResourceKeys(DynamicDataGrid dataGrid, string filterPrefix)
        {
            if (dataGrid.Resources == null)
                return new List<string>();

            return dataGrid.Resources.Keys.OfType<string>()
                .Where(k => k.StartsWith(filterPrefix))
                .ToList();
        }

        /// <summary>
        /// Safely gets a resource value from the DynamicDataGrid's resources.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to get the resource from.</param>
        /// <param name="key">The resource key.</param>
        /// <returns>The resource value, or null if not found.</returns>
        internal static object GetResourceValue(DynamicDataGrid dataGrid, string key)
        {
            if (dataGrid.Resources == null || !dataGrid.Resources.Contains(key))
                return null;

            return dataGrid.Resources[key];
        }

        /// <summary>
        /// Safely sets a resource value in the DynamicDataGrid's resources.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to set the resource on.</param>
        /// <param name="key">The resource key.</param>
        /// <param name="value">The resource value.</param>
        internal static void SetResourceValue(DynamicDataGrid dataGrid, string key, object value)
        {
            if (dataGrid.Resources == null)
                return;

            dataGrid.Resources[key] = value;
        }

        #endregion

        #region Property Name Extraction Helpers

        /// <summary>
        /// Extracts property name from a filter resource key.
        /// </summary>
        /// <param name="resourceKey">The resource key (e.g., "TextFilter_PropertyName").</param>
        /// <param name="prefix">The prefix to remove (e.g., "TextFilter_").</param>
        /// <returns>The extracted property name.</returns>
        internal static string ExtractPropertyNameFromKey(string resourceKey, string prefix)
        {
            if (string.IsNullOrEmpty(resourceKey) || !resourceKey.StartsWith(prefix))
                return null;

            return resourceKey.Substring(prefix.Length);
        }

        /// <summary>
        /// Creates a filter resource key for a specific property and filter type.
        /// </summary>
        /// <param name="filterType">The filter type prefix (e.g., "TextFilter", "BooleanFilter").</param>
        /// <param name="propertyName">The property name.</param>
        /// <param name="suffix">Optional suffix (e.g., "_ShowTrue", "_Operation").</param>
        /// <returns>The formatted resource key.</returns>
        internal static string CreateFilterResourceKey(string filterType, string propertyName, string suffix = "")
        {
            return $"{filterType}_{propertyName}{suffix}";
        }

        #endregion

        #region DynamicDataGrid-Specific Helpers

        /// <summary>
        /// Gets the AvailableColumnDefinitions from the DynamicDataGrid's ViewModel.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to get available columns from.</param>
        /// <returns>List of available column definitions, or empty list if not found.</returns>
        internal static List<AvailableColumnDefinition> GetAvailableColumns(DynamicDataGrid dataGrid)
        {
            if (dataGrid?.DataContext == null)
                return new List<AvailableColumnDefinition>();

            var viewModel = dataGrid.DataContext;
            var availableColumnsProperty = viewModel.GetType().GetProperty("AvailableColumns");

            if (availableColumnsProperty?.GetValue(viewModel) is IEnumerable<AvailableColumnDefinition> availableColumns)
            {
                return availableColumns.ToList();
            }

            return new List<AvailableColumnDefinition>();
        }

        /// <summary>
        /// Gets a specific AvailableColumnDefinition by property name.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to search.</param>
        /// <param name="propertyName">The property name to find.</param>
        /// <returns>The AvailableColumnDefinition if found, null otherwise.</returns>
        internal static AvailableColumnDefinition GetColumnDefinition(DynamicDataGrid dataGrid, string propertyName)
        {
            if (string.IsNullOrEmpty(propertyName))
                return null;

            var availableColumns = GetAvailableColumns(dataGrid);
            return availableColumns.FirstOrDefault(ac => ac.PropertyName == propertyName);
        }

        /// <summary>
        /// Checks if a property name exists in the DynamicDataGrid's available columns.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to check.</param>
        /// <param name="propertyName">The property name to check.</param>
        /// <returns>True if the property exists in available columns, false otherwise.</returns>
        internal static bool IsValidProperty(DynamicDataGrid dataGrid, string propertyName)
        {
            return GetColumnDefinition(dataGrid, propertyName) != null;
        }

        /// <summary>
        /// Gets all property names from the DynamicDataGrid's available columns.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to get property names from.</param>
        /// <returns>List of all available property names.</returns>
        internal static List<string> GetAllPropertyNames(DynamicDataGrid dataGrid)
        {
            var availableColumns = GetAvailableColumns(dataGrid);
            return availableColumns.Select(ac => ac.PropertyName).ToList();
        }

        /// <summary>
        /// Gets all currently visible column property names from the DynamicDataGrid.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to get visible columns from.</param>
        /// <returns>List of visible column property names.</returns>
        internal static List<string> GetVisibleColumnPropertyNames(DynamicDataGrid dataGrid)
        {
            if (dataGrid?.ColumnDefinitions == null)
                return new List<string>();

            return dataGrid.ColumnDefinitions
                .Where(cd => !cd.IsReadOnly) // Assuming non-readonly columns are "visible" for filtering
                .Select(cd => cd.PropertyName)
                .ToList();
        }

        #endregion
    }
}