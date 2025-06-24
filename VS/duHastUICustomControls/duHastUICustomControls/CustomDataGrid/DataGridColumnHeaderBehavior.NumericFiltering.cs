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
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static partial class DataGridColumnHeaderBehavior
    {

        #region Numeric Filtering Support

        /// <summary>
        /// Displays a dialog for filtering numeric columns with various comparison operations.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column to filter.</param>
        /// <param name="propertyName">The property name of the numeric column to filter.</param>
        private static void ShowFilterNumericDialog(DataGrid dataGrid, string propertyName)
        {
            // Get current numeric filter state
            var (operation, value, fromValue, toValue) = GetCurrentNumericFilter(dataGrid, propertyName);

            var dialog = new FilterNumericDialog(propertyName, operation, value, fromValue, toValue)
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
                    ApplyNumericFilter(dataGrid, propertyName, dialog.Operation, dialog.Value, dialog.FromValue, dialog.ToValue);
                }
            }
        }

        /// <summary>
        /// Gets the current numeric filter state for a column.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to check.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A tuple containing the current filter operation and values.</returns>
        private static (NumericFilterOperation? operation, double? value, double? fromValue, double? toValue) GetCurrentNumericFilter(DataGrid dataGrid, string propertyName)
        {
            var operationKey = $"NumericFilter_Operation_{propertyName}";
            var valueKey = $"NumericFilter_Value_{propertyName}";
            var fromValueKey = $"NumericFilter_FromValue_{propertyName}";
            var toValueKey = $"NumericFilter_ToValue_{propertyName}";

            NumericFilterOperation? operation = null;
            if (dataGrid.Resources.Contains(operationKey))
            {
                if (Enum.TryParse<NumericFilterOperation>((string)dataGrid.Resources[operationKey], out var op))
                {
                    operation = op;
                }
            }

            double? value = dataGrid.Resources.Contains(valueKey) ? (double?)dataGrid.Resources[valueKey] : null;
            double? fromValue = dataGrid.Resources.Contains(fromValueKey) ? (double?)dataGrid.Resources[fromValueKey] : null;
            double? toValue = dataGrid.Resources.Contains(toValueKey) ? (double?)dataGrid.Resources[toValueKey] : null;

            return (operation, value, fromValue, toValue);
        }

        /// <summary>
        /// Applies a numeric filter to a column and refreshes the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to apply the filter to.</param>
        /// <param name="propertyName">The property name of the numeric column.</param>
        /// <param name="operation">The comparison operation to use.</param>
        /// <param name="value">The value for single-value operations.</param>
        /// <param name="fromValue">The from value for range operations.</param>
        /// <param name="toValue">The to value for range operations.</param>
        private static void ApplyNumericFilter(DataGrid dataGrid, string propertyName, NumericFilterOperation operation, double? value, double? fromValue, double? toValue)
        {
            SetColumnNumericFilter(dataGrid, propertyName, operation, value, fromValue, toValue);
            ApplyAllColumnFilters(dataGrid);

            // Update filter icon for this column
            var column = dataGrid.Columns.FirstOrDefault(c => GetColumnPropertyName(c) == propertyName);
            if (column != null)
            {
                UpdateFilterIcon(dataGrid, column, propertyName);
            }
        }

        /// <summary>
        /// Stores numeric filter information for a column in the DataGrid's resource collection.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to store the filter in.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <param name="operation">The comparison operation.</param>
        /// <param name="value">The value for single-value operations.</param>
        /// <param name="fromValue">The from value for range operations.</param>
        /// <param name="toValue">The to value for range operations.</param>
        private static void SetColumnNumericFilter(DataGrid dataGrid, string propertyName, NumericFilterOperation operation, double? value, double? fromValue, double? toValue)
        {
            var operationKey = $"NumericFilter_Operation_{propertyName}";
            var valueKey = $"NumericFilter_Value_{propertyName}";
            var fromValueKey = $"NumericFilter_FromValue_{propertyName}";
            var toValueKey = $"NumericFilter_ToValue_{propertyName}";

            // Remove existing numeric filters
            dataGrid.Resources.Remove(operationKey);
            dataGrid.Resources.Remove(valueKey);
            dataGrid.Resources.Remove(fromValueKey);
            dataGrid.Resources.Remove(toValueKey);

            // Add new filter
            dataGrid.Resources[operationKey] = operation.ToString();

            if (operation == NumericFilterOperation.Range)
            {
                if (fromValue.HasValue)
                    dataGrid.Resources[fromValueKey] = fromValue.Value;
                if (toValue.HasValue)
                    dataGrid.Resources[toValueKey] = toValue.Value;
            }
            else if (value.HasValue)
            {
                dataGrid.Resources[valueKey] = value.Value;
            }
        }

        /// <summary>
        /// Tests whether an item passes a numeric filter.
        /// </summary>
        /// <param name="item">The item to test.</param>
        /// <param name="dataGrid">The DataGrid containing filter settings.</param>
        /// <param name="propertyName">The property name of the numeric column.</param>
        /// <returns>True if the item passes the filter, false otherwise.</returns>
        private static bool PassesNumericFilter(object item, DataGrid dataGrid, string propertyName)
        {
            var (operation, value, fromValue, toValue) = GetCurrentNumericFilter(dataGrid, propertyName);

            // If no numeric filter is set, show all
            if (!operation.HasValue)
                return true;

            var itemValue = GetItemValue(item, propertyName);
            if (!IsNumericValue(itemValue, out double numericValue))
                return false; // Non-numeric values don't pass numeric filters

            switch (operation.Value)
            {
                case NumericFilterOperation.Equal:
                    return value.HasValue && Math.Abs(numericValue - value.Value) < double.Epsilon;
                case NumericFilterOperation.GreaterThan:
                    return value.HasValue && numericValue > value.Value;
                case NumericFilterOperation.GreaterThanOrEqual:
                    return value.HasValue && numericValue >= value.Value;
                case NumericFilterOperation.LessThan:
                    return value.HasValue && numericValue < value.Value;
                case NumericFilterOperation.LessThanOrEqual:
                    return value.HasValue && numericValue <= value.Value;
                case NumericFilterOperation.Range:
                    bool withinFrom = !fromValue.HasValue || numericValue >= fromValue.Value;
                    bool withinTo = !toValue.HasValue || numericValue <= toValue.Value;
                    return withinFrom && withinTo;
                default:
                    return true;
            }
        }

        /// <summary>
        /// Checks if a value is numeric and converts it to double.
        /// </summary>
        /// <param name="value">The value to check.</param>
        /// <param name="numericValue">The converted numeric value.</param>
        /// <returns>True if the value is numeric, false otherwise.</returns>
        private static bool IsNumericValue(object value, out double numericValue)
        {
            numericValue = 0;

            if (value == null)
                return false;

            // Handle different numeric types
            if (value is double d)
            {
                numericValue = d;
                return true;
            }
            if (value is float f)
            {
                numericValue = f;
                return true;
            }
            if (value is decimal dec)
            {
                numericValue = (double)dec;
                return true;
            }
            if (value is int i)
            {
                numericValue = i;
                return true;
            }
            if (value is long l)
            {
                numericValue = l;
                return true;
            }

            // Try to parse string representation
            return double.TryParse(value.ToString(), out numericValue);
        }

        /// <summary>
        /// Gets a description of the current numeric filter for display.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to get the filter from.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A human-readable description of the current filter, or null if no filter is applied.</returns>
        private static string GetCurrentNumericFilterText(DataGrid dataGrid, string propertyName)
        {
            var (operation, value, fromValue, toValue) = GetCurrentNumericFilter(dataGrid, propertyName);

            if (!operation.HasValue)
                return null;

            switch (operation.Value)
            {
                case NumericFilterOperation.Equal:
                    return value.HasValue ? $"= {value.Value}" : null;
                case NumericFilterOperation.GreaterThan:
                    return value.HasValue ? $"> {value.Value}" : null;
                case NumericFilterOperation.GreaterThanOrEqual:
                    return value.HasValue ? $">= {value.Value}" : null;
                case NumericFilterOperation.LessThan:
                    return value.HasValue ? $"< {value.Value}" : null;
                case NumericFilterOperation.LessThanOrEqual:
                    return value.HasValue ? $"<= {value.Value}" : null;
                case NumericFilterOperation.Range:
                    if (fromValue.HasValue && toValue.HasValue)
                        return $"{fromValue.Value} - {toValue.Value}";
                    else if (fromValue.HasValue)
                        return $">= {fromValue.Value}";
                    else if (toValue.HasValue)
                        return $"<= {toValue.Value}";
                    return null;
                default:
                    return null;
            }
        }

        #endregion
    }
}
