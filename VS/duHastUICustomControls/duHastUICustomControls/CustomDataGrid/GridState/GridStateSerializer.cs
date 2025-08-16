//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// Written by Claude
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

using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Linq;
using System.Windows.Controls;
using System.Windows.Data;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Handles serialization and deserialization of DataGrid state to/from DataGridState objects
    /// </summary>
    public static class GridStateSerializer
    {
        #region Capture State from DataGrid

        /// <summary>
        /// Captures the current state of a DataGrid
        /// </summary>
        public static DataGridState CaptureState(DataGrid dataGrid, string gridId, string stateName = null)
        {
            if (dataGrid == null)
                throw new ArgumentNullException(nameof(dataGrid));

            var state = new DataGridState
            {
                GridId = gridId,
                StateName = stateName ?? "Current",
                CreatedDate = DateTime.Now,
                LastModified = DateTime.Now
            };

            // Capture column states
            state.Columns = CaptureColumnStates(dataGrid);

            // Capture sorting state
            state.Sorting = CaptureSortingState(dataGrid);

            // Capture filter states
            state.Filters = CaptureFilterStates(dataGrid);

            return state;
        }

        /// <summary>
        /// Captures the current state of a DynamicDataGrid
        /// </summary>
        public static DataGridState CaptureState(DynamicDataGrid dataGrid, string gridId, string stateName = null)
        {
            if (dataGrid == null)
                throw new ArgumentNullException(nameof(dataGrid));

            var state = CaptureState((DataGrid)dataGrid, gridId, stateName);

            // Add DynamicDataGrid-specific information
            if (dataGrid.DataContext != null)
            {
                var viewModel = dataGrid.DataContext;
                var availableColumnsProperty = viewModel.GetType().GetProperty("AvailableColumns");

                if (availableColumnsProperty?.GetValue(viewModel) is IEnumerable<AvailableColumnDefinition> availableColumns)
                {
                    // Store information about available columns for restoration
                    state.Metadata["AvailableColumns"] = availableColumns.Select(ac => new
                    {
                        PropertyName = ac.PropertyName,
                        DisplayName = ac.DisplayName,
                        DataType = ac.DataType.FullName,
                        Category = ac.Category,
                        Description = ac.Description,
                        UIType = ac.UIType.ToString(),
                        DropDownValues = ac.DropDownValues
                    }).ToList();
                }
            }

            return state;
        }

        private static List<ColumnState> CaptureColumnStates(DataGrid dataGrid)
        {
            var columnStates = new List<ColumnState>();

            foreach (var column in dataGrid.Columns.OrderBy(c => c.DisplayIndex))
            {
                var propertyName = GetColumnPropertyName(column);
                if (string.IsNullOrEmpty(propertyName))
                    continue;

                var columnState = new ColumnState
                {
                    PropertyName = propertyName,
                    DisplayName = column.Header?.ToString() ?? propertyName,
                    IsVisible = column.Visibility == System.Windows.Visibility.Visible,
                    DisplayIndex = column.DisplayIndex,
                    Width = column.ActualWidth,
                    IsReadOnly = column.IsReadOnly
                };

                // Try to determine data type
                if (column is DataGridBoundColumn boundColumn && boundColumn.Binding is Binding binding)
                {
                    var dataType = GetColumnDataType(dataGrid, propertyName);
                    columnState.DataTypeName = dataType?.FullName ?? typeof(string).FullName;
                }

                columnStates.Add(columnState);
            }

            return columnStates;
        }

        private static SortState CaptureSortingState(DataGrid dataGrid)
        {
            var collectionView = CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
            if (collectionView?.SortDescriptions?.Count > 0)
            {
                var sortDesc = collectionView.SortDescriptions.First();
                return new SortState
                {
                    PropertyName = sortDesc.PropertyName,
                    Direction = sortDesc.Direction,
                    SortIndex = 0
                };
            }

            return null;
        }

        private static List<FilterState> CaptureFilterStates(DataGrid dataGrid)
        {
            var filterStates = new List<FilterState>();

            if (dataGrid.Resources == null)
                return filterStates;

            var processedProperties = new HashSet<string>();

            // Capture different types of filters
            CaptureTextFilters(dataGrid, filterStates, processedProperties);
            CaptureBooleanFilters(dataGrid, filterStates, processedProperties);
            CaptureNumericFilters(dataGrid, filterStates, processedProperties);
            CaptureDateTimeFilters(dataGrid, filterStates, processedProperties);
            CaptureDropDownFilters(dataGrid, filterStates, processedProperties);

            return filterStates;
        }

        #endregion

        #region Filter Capture Methods

        private static void CaptureTextFilters(DataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var textFilterKeys = dataGrid.Resources.Keys.OfType<string>()
                .Where(k => k.StartsWith("TextFilter_"))
                .ToList();

            foreach (var key in textFilterKeys)
            {
                var propertyName = key.Substring("TextFilter_".Length);
                if (processedProperties.Contains(propertyName))
                    continue;

                var filterText = dataGrid.Resources[key] as string;
                if (string.IsNullOrWhiteSpace(filterText))
                    continue;

                var logicKey = $"TextFilterLogic_{propertyName}";
                var useAndLogic = dataGrid.Resources.Contains(logicKey) && (bool)dataGrid.Resources[logicKey];

                var filterState = new FilterState
                {
                    PropertyName = propertyName,
                    FilterType = FilterType.Text,
                    Description = $"Text: \"{filterText}\" ({(useAndLogic ? "AND" : "OR")})"
                };

                filterState.FilterValues["FilterText"] = filterText;
                filterState.FilterValues["UseAndLogic"] = useAndLogic;

                filterStates.Add(filterState);
                processedProperties.Add(propertyName);
            }
        }

        private static void CaptureBooleanFilters(DataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var booleanFilterKeys = dataGrid.Resources.Keys.OfType<string>()
                .Where(k => k.StartsWith("BooleanFilter_ShowTrue_"))
                .ToList();

            foreach (var key in booleanFilterKeys)
            {
                var propertyName = key.Substring("BooleanFilter_ShowTrue_".Length);
                if (processedProperties.Contains(propertyName))
                    continue;

                var showTrueKey = $"BooleanFilter_ShowTrue_{propertyName}";
                var showFalseKey = $"BooleanFilter_ShowFalse_{propertyName}";

                var showTrue = dataGrid.Resources.Contains(showTrueKey) ? (bool?)dataGrid.Resources[showTrueKey] : null;
                var showFalse = dataGrid.Resources.Contains(showFalseKey) ? (bool?)dataGrid.Resources[showFalseKey] : null;

                if (!showTrue.HasValue && !showFalse.HasValue)
                    continue;

                var filterState = new FilterState
                {
                    PropertyName = propertyName,
                    FilterType = FilterType.Boolean,
                    Description = GetBooleanFilterDescription(showTrue, showFalse)
                };

                if (showTrue.HasValue)
                    filterState.FilterValues["ShowTrue"] = showTrue.Value;
                if (showFalse.HasValue)
                    filterState.FilterValues["ShowFalse"] = showFalse.Value;

                filterStates.Add(filterState);
                processedProperties.Add(propertyName);
            }
        }

        private static void CaptureNumericFilters(DataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var numericFilterKeys = dataGrid.Resources.Keys.OfType<string>()
                .Where(k => k.StartsWith("NumericFilter_Operation_"))
                .ToList();

            foreach (var key in numericFilterKeys)
            {
                var propertyName = key.Substring("NumericFilter_Operation_".Length);
                if (processedProperties.Contains(propertyName))
                    continue;

                var operationKey = $"NumericFilter_Operation_{propertyName}";
                var valueKey = $"NumericFilter_Value_{propertyName}";
                var fromValueKey = $"NumericFilter_FromValue_{propertyName}";
                var toValueKey = $"NumericFilter_ToValue_{propertyName}";

                if (!dataGrid.Resources.Contains(operationKey))
                    continue;

                var operation = dataGrid.Resources[operationKey].ToString();
                var filterState = new FilterState
                {
                    PropertyName = propertyName,
                    FilterType = FilterType.Numeric
                };

                filterState.FilterValues["Operation"] = operation;

                if (dataGrid.Resources.Contains(valueKey))
                    filterState.FilterValues["Value"] = dataGrid.Resources[valueKey];
                if (dataGrid.Resources.Contains(fromValueKey))
                    filterState.FilterValues["FromValue"] = dataGrid.Resources[fromValueKey];
                if (dataGrid.Resources.Contains(toValueKey))
                    filterState.FilterValues["ToValue"] = dataGrid.Resources[toValueKey];

                filterState.Description = GetNumericFilterDescription(operation, filterState.FilterValues);

                filterStates.Add(filterState);
                processedProperties.Add(propertyName);
            }
        }

        private static void CaptureDateTimeFilters(DataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var dateTimeFilterKeys = dataGrid.Resources.Keys.OfType<string>()
                .Where(k => k.StartsWith("DateTimeFilter_Operation_"))
                .ToList();

            foreach (var key in dateTimeFilterKeys)
            {
                var propertyName = key.Substring("DateTimeFilter_Operation_".Length);
                if (processedProperties.Contains(propertyName))
                    continue;

                var operationKey = $"DateTimeFilter_Operation_{propertyName}";
                var dateKey = $"DateTimeFilter_Date_{propertyName}";
                var fromDateKey = $"DateTimeFilter_FromDate_{propertyName}";
                var toDateKey = $"DateTimeFilter_ToDate_{propertyName}";

                if (!dataGrid.Resources.Contains(operationKey))
                    continue;

                var operation = dataGrid.Resources[operationKey].ToString();
                var filterState = new FilterState
                {
                    PropertyName = propertyName,
                    FilterType = FilterType.DateTime
                };

                filterState.FilterValues["Operation"] = operation;

                if (dataGrid.Resources.Contains(dateKey))
                    filterState.FilterValues["Date"] = dataGrid.Resources[dateKey];
                if (dataGrid.Resources.Contains(fromDateKey))
                    filterState.FilterValues["FromDate"] = dataGrid.Resources[fromDateKey];
                if (dataGrid.Resources.Contains(toDateKey))
                    filterState.FilterValues["ToDate"] = dataGrid.Resources[toDateKey];

                filterState.Description = GetDateTimeFilterDescription(operation, filterState.FilterValues);

                filterStates.Add(filterState);
                processedProperties.Add(propertyName);
            }
        }

        private static void CaptureDropDownFilters(DataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var dropDownFilterKeys = dataGrid.Resources.Keys.OfType<string>()
                .Where(k => k.StartsWith("DropDownFilter_SelectedValue_"))
                .ToList();

            foreach (var key in dropDownFilterKeys)
            {
                var propertyName = key.Substring("DropDownFilter_SelectedValue_".Length);
                if (processedProperties.Contains(propertyName))
                    continue;

                var selectedValueKey = $"DropDownFilter_SelectedValue_{propertyName}";
                var searchTextKey = $"DropDownFilter_SearchText_{propertyName}";

                if (!dataGrid.Resources.Contains(selectedValueKey))
                    continue;

                var selectedValue = dataGrid.Resources[selectedValueKey];
                var searchText = dataGrid.Resources.Contains(searchTextKey) ?
                    dataGrid.Resources[searchTextKey] as string : null;

                var filterState = new FilterState
                {
                    PropertyName = propertyName,
                    FilterType = FilterType.DropDown
                };

                filterState.FilterValues["SelectedValue"] = selectedValue;
                if (!string.IsNullOrWhiteSpace(searchText))
                    filterState.FilterValues["SearchText"] = searchText;

                filterState.Description = GetDropDownFilterDescription(selectedValue, searchText);

                filterStates.Add(filterState);
                processedProperties.Add(propertyName);
            }
        }

        #endregion

        #region Apply State to DataGrid

        /// <summary>
        /// Applies a saved state to a DataGrid
        /// </summary>
        public static bool ApplyState(DataGrid dataGrid, DataGridState state, GridStateOptions options = null)
        {
            if (dataGrid == null || state == null)
                return false;

            options = options ?? new GridStateOptions();

            try
            {
                // Apply column states
                if (options.IncludeVisibility || options.IncludeColumnOrder || options.IncludeColumnWidths)
                {
                    ApplyColumnStates(dataGrid, state.Columns, options);
                }

                // Apply sorting state
                if (options.IncludeSorting && state.Sorting != null)
                {
                    ApplySortingState(dataGrid, state.Sorting);
                }

                // Apply filter states
                if (options.IncludeFilters && state.Filters?.Count > 0)
                {
                    ApplyFilterStates(dataGrid, state.Filters);
                }

                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error applying grid state: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Applies a saved state to a DynamicDataGrid
        /// </summary>
        public static bool ApplyState(DynamicDataGrid dataGrid, DataGridState state, GridStateOptions options = null)
        {
            if (dataGrid == null || state == null)
                return false;

            // First apply base DataGrid state
            var success = ApplyState((DataGrid)dataGrid, state, options);

            if (success && state.Metadata.ContainsKey("AvailableColumns"))
            {
                // Handle DynamicDataGrid-specific restoration
                ApplyDynamicDataGridSpecificState(dataGrid, state);
            }

            return success;
        }

        private static void ApplyColumnStates(DataGrid dataGrid, List<ColumnState> columnStates, GridStateOptions options)
        {
            if (columnStates == null || columnStates.Count == 0)
                return;

            // Create a mapping of current columns
            var currentColumns = dataGrid.Columns.ToDictionary(
                col => GetColumnPropertyName(col),
                col => col
            );

            // Apply states in display order
            var sortedStates = columnStates.OrderBy(cs => cs.DisplayIndex).ToList();

            for (int i = 0; i < sortedStates.Count; i++)
            {
                var columnState = sortedStates[i];
                if (!currentColumns.TryGetValue(columnState.PropertyName, out var column))
                    continue;

                // Apply visibility
                if (options.IncludeVisibility)
                {
                    column.Visibility = columnState.IsVisible ?
                        System.Windows.Visibility.Visible :
                        System.Windows.Visibility.Collapsed;
                }

                // Apply display order
                if (options.IncludeColumnOrder)
                {
                    column.DisplayIndex = i;
                }

                // Apply width
                if (options.IncludeColumnWidths && columnState.Width > 0)
                {
                    column.Width = new DataGridLength(columnState.Width);
                }
            }
        }

        private static void ApplySortingState(DataGrid dataGrid, SortState sortState)
        {
            var collectionView = CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
            if (collectionView == null)
                return;

            collectionView.SortDescriptions.Clear();
            collectionView.SortDescriptions.Add(new SortDescription(sortState.PropertyName, sortState.Direction));
        }

        private static void ApplyFilterStates(DataGrid dataGrid, List<FilterState> filterStates)
        {
            // Clear existing filters
            ClearAllFilters(dataGrid);

            // Apply each filter
            foreach (var filterState in filterStates)
            {
                ApplyFilterState(dataGrid, filterState);
            }

            // Refresh the view
            RefreshDataGridFilters(dataGrid);
        }

        private static void ApplyFilterState(DataGrid dataGrid, FilterState filterState)
        {
            switch (filterState.FilterType)
            {
                case FilterType.Text:
                    ApplyTextFilter(dataGrid, filterState);
                    break;
                case FilterType.Boolean:
                    ApplyBooleanFilter(dataGrid, filterState);
                    break;
                case FilterType.Numeric:
                    ApplyNumericFilter(dataGrid, filterState);
                    break;
                case FilterType.DateTime:
                    ApplyDateTimeFilter(dataGrid, filterState);
                    break;
                case FilterType.DropDown:
                    ApplyDropDownFilter(dataGrid, filterState);
                    break;
            }
        }

        private static void ApplyTextFilter(DataGrid dataGrid, FilterState filterState)
        {
            if (!filterState.FilterValues.TryGetValue("FilterText", out var filterText))
                return;

            var useAndLogic = filterState.FilterValues.TryGetValue("UseAndLogic", out var andLogic) &&
                             (bool)andLogic;

            var filterKey = $"TextFilter_{filterState.PropertyName}";
            var logicKey = $"TextFilterLogic_{filterState.PropertyName}";

            dataGrid.Resources[filterKey] = filterText.ToString();
            dataGrid.Resources[logicKey] = useAndLogic;
        }

        private static void ApplyBooleanFilter(DataGrid dataGrid, FilterState filterState)
        {
            var showTrueKey = $"BooleanFilter_ShowTrue_{filterState.PropertyName}";
            var showFalseKey = $"BooleanFilter_ShowFalse_{filterState.PropertyName}";

            if (filterState.FilterValues.TryGetValue("ShowTrue", out var showTrue))
            {
                dataGrid.Resources[showTrueKey] = (bool)showTrue;
            }

            if (filterState.FilterValues.TryGetValue("ShowFalse", out var showFalse))
            {
                dataGrid.Resources[showFalseKey] = (bool)showFalse;
            }
        }

        private static void ApplyNumericFilter(DataGrid dataGrid, FilterState filterState)
        {
            if (!filterState.FilterValues.TryGetValue("Operation", out var operation))
                return;

            var operationKey = $"NumericFilter_Operation_{filterState.PropertyName}";
            var valueKey = $"NumericFilter_Value_{filterState.PropertyName}";
            var fromValueKey = $"NumericFilter_FromValue_{filterState.PropertyName}";
            var toValueKey = $"NumericFilter_ToValue_{filterState.PropertyName}";

            dataGrid.Resources[operationKey] = operation.ToString();

            if (filterState.FilterValues.TryGetValue("Value", out var value))
                dataGrid.Resources[valueKey] = value;
            if (filterState.FilterValues.TryGetValue("FromValue", out var fromValue))
                dataGrid.Resources[fromValueKey] = fromValue;
            if (filterState.FilterValues.TryGetValue("ToValue", out var toValue))
                dataGrid.Resources[toValueKey] = toValue;
        }

        private static void ApplyDateTimeFilter(DataGrid dataGrid, FilterState filterState)
        {
            if (!filterState.FilterValues.TryGetValue("Operation", out var operation))
                return;

            var operationKey = $"DateTimeFilter_Operation_{filterState.PropertyName}";
            var dateKey = $"DateTimeFilter_Date_{filterState.PropertyName}";
            var fromDateKey = $"DateTimeFilter_FromDate_{filterState.PropertyName}";
            var toDateKey = $"DateTimeFilter_ToDate_{filterState.PropertyName}";

            dataGrid.Resources[operationKey] = operation.ToString();

            if (filterState.FilterValues.TryGetValue("Date", out var date))
                dataGrid.Resources[dateKey] = date;
            if (filterState.FilterValues.TryGetValue("FromDate", out var fromDate))
                dataGrid.Resources[fromDateKey] = fromDate;
            if (filterState.FilterValues.TryGetValue("ToDate", out var toDate))
                dataGrid.Resources[toDateKey] = toDate;
        }

        private static void ApplyDropDownFilter(DataGrid dataGrid, FilterState filterState)
        {
            if (!filterState.FilterValues.TryGetValue("SelectedValue", out var selectedValue))
                return;

            var selectedValueKey = $"DropDownFilter_SelectedValue_{filterState.PropertyName}";
            var searchTextKey = $"DropDownFilter_SearchText_{filterState.PropertyName}";

            dataGrid.Resources[selectedValueKey] = selectedValue;

            if (filterState.FilterValues.TryGetValue("SearchText", out var searchText))
                dataGrid.Resources[searchTextKey] = searchText.ToString();
        }

        private static void ApplyDynamicDataGridSpecificState(DynamicDataGrid dataGrid, DataGridState state)
        {
            // Handle restoration of columns that might not be currently visible
            // This is specific to DynamicDataGrid functionality
            if (dataGrid.DataContext != null && state.Metadata.ContainsKey("AvailableColumns"))
            {
                // Implementation would depend on how you want to handle adding/removing columns
                // This might involve calling AddSelectedColumn/RemoveColumn methods on the ViewModel
            }
        }

        #endregion

        #region Helper Methods

        private static string GetColumnPropertyName(DataGridColumn column)
        {
            if (column is DataGridBoundColumn boundColumn && boundColumn.Binding is Binding binding)
            {
                return binding.Path.Path.Trim('[', ']');
            }
            return column.Header?.ToString();
        }

        private static Type GetColumnDataType(DataGrid dataGrid, string propertyName)
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

        private static void ClearAllFilters(DataGrid dataGrid)
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

        private static void RefreshDataGridFilters(DataGrid dataGrid)
        {
            // This would call the existing ApplyAllColumnFilters method from DataGridColumnHeaderBehavior
            // We need to access it through reflection or make it public
            var behaviorType = typeof(DataGridColumnHeaderBehavior);
            var method = behaviorType.GetMethod("ApplyAllColumnFilters",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);

            method?.Invoke(null, new object[] { dataGrid });
        }

        #endregion

        #region Filter Description Methods

        private static string GetBooleanFilterDescription(bool? showTrue, bool? showFalse)
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

        private static string GetNumericFilterDescription(string operation, Dictionary<string, object> values)
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

        private static string GetDateTimeFilterDescription(string operation, Dictionary<string, object> values)
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

        private static string GetDropDownFilterDescription(object selectedValue, string searchText)
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
    }
}