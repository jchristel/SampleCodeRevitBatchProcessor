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

        #region DateTime Filtering Support

        /// <summary>
        /// Displays a dialog for filtering DateTime columns with various comparison operations.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column to filter.</param>
        /// <param name="propertyName">The property name of the DateTime column to filter.</param>
        private static void ShowFilterDateTimeDialog(DataGrid dataGrid, string propertyName)
        {
            // Get current DateTime filter state
            var (operation, date, fromDate, toDate) = GetCurrentDateTimeFilter(dataGrid, propertyName);

            var dialog = new FilterDateTimeDialog(propertyName, operation, date, fromDate, toDate)
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
                    ApplyDateTimeFilter(dataGrid, propertyName, dialog.Operation, dialog.Date, dialog.FromDate, dialog.ToDate);
                }
            }
        }

        /// <summary>
        /// Gets the current DateTime filter state for a column.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to check.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A tuple containing the current filter operation and values.</returns>
        private static (DateTimeFilterOperation? operation, DateTime? date, DateTime? fromDate, DateTime? toDate) GetCurrentDateTimeFilter(DataGrid dataGrid, string propertyName)
        {
            var operationKey = $"DateTimeFilter_Operation_{propertyName}";
            var dateKey = $"DateTimeFilter_Date_{propertyName}";
            var fromDateKey = $"DateTimeFilter_FromDate_{propertyName}";
            var toDateKey = $"DateTimeFilter_ToDate_{propertyName}";

            DateTimeFilterOperation? operation = null;
            if (dataGrid.Resources.Contains(operationKey))
            {
                if (Enum.TryParse<DateTimeFilterOperation>((string)dataGrid.Resources[operationKey], out var op))
                {
                    operation = op;
                }
            }

            DateTime? date = dataGrid.Resources.Contains(dateKey) ? (DateTime?)dataGrid.Resources[dateKey] : null;
            DateTime? fromDate = dataGrid.Resources.Contains(fromDateKey) ? (DateTime?)dataGrid.Resources[fromDateKey] : null;
            DateTime? toDate = dataGrid.Resources.Contains(toDateKey) ? (DateTime?)dataGrid.Resources[toDateKey] : null;

            return (operation, date, fromDate, toDate);
        }

        /// <summary>
        /// Applies a DateTime filter to a column and refreshes the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to apply the filter to.</param>
        /// <param name="propertyName">The property name of the DateTime column.</param>
        /// <param name="operation">The comparison operation to use.</param>
        /// <param name="date">The date for single-date operations.</param>
        /// <param name="fromDate">The from date for range operations.</param>
        /// <param name="toDate">The to date for range operations.</param>
        private static void ApplyDateTimeFilter(DataGrid dataGrid, string propertyName, DateTimeFilterOperation operation, DateTime? date, DateTime? fromDate, DateTime? toDate)
        {
            SetColumnDateTimeFilter(dataGrid, propertyName, operation, date, fromDate, toDate);
            ApplyAllColumnFilters(dataGrid);

            // Update filter icon for this column
            var column = dataGrid.Columns.FirstOrDefault(c => GetColumnPropertyName(c) == propertyName);
            if (column != null)
            {
                UpdateFilterIcon(dataGrid, column, propertyName);
            }
        }

        /// <summary>
        /// Stores DateTime filter information for a column in the DataGrid's resource collection.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to store the filter in.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <param name="operation">The comparison operation.</param>
        /// <param name="date">The date for single-date operations.</param>
        /// <param name="fromDate">The from date for range operations.</param>
        /// <param name="toDate">The to date for range operations.</param>
        private static void SetColumnDateTimeFilter(DataGrid dataGrid, string propertyName, DateTimeFilterOperation operation, DateTime? date, DateTime? fromDate, DateTime? toDate)
        {
            var operationKey = $"DateTimeFilter_Operation_{propertyName}";
            var dateKey = $"DateTimeFilter_Date_{propertyName}";
            var fromDateKey = $"DateTimeFilter_FromDate_{propertyName}";
            var toDateKey = $"DateTimeFilter_ToDate_{propertyName}";

            // Remove existing DateTime filters
            dataGrid.Resources.Remove(operationKey);
            dataGrid.Resources.Remove(dateKey);
            dataGrid.Resources.Remove(fromDateKey);
            dataGrid.Resources.Remove(toDateKey);

            // Add new filter
            dataGrid.Resources[operationKey] = operation.ToString();

            if (operation == DateTimeFilterOperation.Between)
            {
                if (fromDate.HasValue)
                    dataGrid.Resources[fromDateKey] = fromDate.Value;
                if (toDate.HasValue)
                    dataGrid.Resources[toDateKey] = toDate.Value;
            }
            else if (date.HasValue)
            {
                dataGrid.Resources[dateKey] = date.Value;
            }
        }

        /// <summary>
        /// Tests whether an item passes a DateTime filter.
        /// </summary>
        /// <param name="item">The item to test.</param>
        /// <param name="dataGrid">The DataGrid containing filter settings.</param>
        /// <param name="propertyName">The property name of the DateTime column.</param>
        /// <returns>True if the item passes the filter, false otherwise.</returns>
        private static bool PassesDateTimeFilter(object item, DataGrid dataGrid, string propertyName)
        {
            var (operation, date, fromDate, toDate) = GetCurrentDateTimeFilter(dataGrid, propertyName);

            // If no DateTime filter is set, show all
            if (!operation.HasValue)
                return true;

            var itemValue = GetItemValue(item, propertyName);
            if (!IsDateTimeValue(itemValue, out DateTime dateTimeValue))
                return false; // Non-DateTime values don't pass DateTime filters

            switch (operation.Value)
            {
                case DateTimeFilterOperation.On:
                    return date.HasValue && dateTimeValue.Date == date.Value.Date;
                case DateTimeFilterOperation.Before:
                    return date.HasValue && dateTimeValue.Date < date.Value.Date;
                case DateTimeFilterOperation.After:
                    return date.HasValue && dateTimeValue.Date > date.Value.Date;
                case DateTimeFilterOperation.Between:
                    bool withinFrom = !fromDate.HasValue || dateTimeValue.Date >= fromDate.Value.Date;
                    bool withinTo = !toDate.HasValue || dateTimeValue.Date <= toDate.Value.Date;
                    return withinFrom && withinTo;
                default:
                    return true;
            }
        }

        /// <summary>
        /// Checks if a value is a DateTime and converts it.
        /// </summary>
        /// <param name="value">The value to check.</param>
        /// <param name="dateTimeValue">The converted DateTime value.</param>
        /// <returns>True if the value is a DateTime, false otherwise.</returns>
        private static bool IsDateTimeValue(object value, out DateTime dateTimeValue)
        {
            dateTimeValue = default;

            if (value == null)
                return false;

            if (value is DateTime dt)
            {
                dateTimeValue = dt;
                return true;
            }

            // Try to parse string representation
            return DateTime.TryParse(value.ToString(), out dateTimeValue);
        }

        /// <summary>
        /// Gets a description of the current DateTime filter for display.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to get the filter from.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A human-readable description of the current filter, or null if no filter is applied.</returns>
        private static string GetCurrentDateTimeFilterText(DataGrid dataGrid, string propertyName)
        {
            var (operation, date, fromDate, toDate) = GetCurrentDateTimeFilter(dataGrid, propertyName);

            if (!operation.HasValue)
                return null;

            switch (operation.Value)
            {
                case DateTimeFilterOperation.On:
                    return date.HasValue ? $"On {date.Value:yyyy-MM-dd}" : null;
                case DateTimeFilterOperation.Before:
                    return date.HasValue ? $"Before {date.Value:yyyy-MM-dd}" : null;
                case DateTimeFilterOperation.After:
                    return date.HasValue ? $"After {date.Value:yyyy-MM-dd}" : null;
                case DateTimeFilterOperation.Between:
                    if (fromDate.HasValue && toDate.HasValue)
                        return $"{fromDate.Value:yyyy-MM-dd} to {toDate.Value:yyyy-MM-dd}";
                    else if (fromDate.HasValue)
                        return $"From {fromDate.Value:yyyy-MM-dd}";
                    else if (toDate.HasValue)
                        return $"To {toDate.Value:yyyy-MM-dd}";
                    return null;
                default:
                    return null;
            }
        }

        #endregion
    }
}
