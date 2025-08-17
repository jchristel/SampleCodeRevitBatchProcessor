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

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Handles applying filter states to DataGrid controls.
    /// Contains specialized logic for each filter type (Text, Boolean, Numeric, DateTime, DropDown).
    /// </summary>
    internal static class FilterStateApply
    {
        #region Public Methods

        /// <summary>
        /// Applies a list of filter states to a DynamicDataGrid.
        /// Clears existing filters first, then applies each filter and refreshes the view.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply filters to.</param>
        /// <param name="filterStates">List of filter states to apply.</param>
        /// <returns>True if filters were successfully applied, false if there was an error.</returns>
        internal static bool ApplyAllFilterStates(DynamicDataGrid dataGrid, List<FilterState> filterStates)
        {
            if (dataGrid == null)
                return false;

            try
            {
                // Clear existing filters
                GridStateHelpers.ClearAllFilters(dataGrid);

                // Apply each filter if we have any
                if (filterStates?.Count > 0)
                {
                    foreach (var filterState in filterStates)
                    {
                        ApplyFilterState(dataGrid, filterState);
                    }
                }

                // Refresh the view to apply all filters
                GridStateHelpers.RefreshDataGridFilters(dataGrid);

                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error applying filter states: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Applies a single filter state to a DynamicDataGrid based on its filter type.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply the filter to.</param>
        /// <param name="filterState">The filter state to apply.</param>
        internal static void ApplyFilterState(DynamicDataGrid dataGrid, FilterState filterState)
        {
            if (dataGrid == null || filterState == null)
                return;

            try
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
                    default:
                        System.Diagnostics.Debug.WriteLine($"Unknown filter type: {filterState.FilterType}");
                        break;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error applying {filterState.FilterType} filter for {filterState.PropertyName}: {ex.Message}");
            }
        }

        #endregion

        #region Text Filter Application

        /// <summary>
        /// Applies a text filter state to the DynamicDataGrid's resources.
        /// Sets the filter text and logic (AND/OR) in the appropriate resource keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply the text filter to.</param>
        /// <param name="filterState">The text filter state to apply.</param>
        internal static void ApplyTextFilter(DynamicDataGrid dataGrid, FilterState filterState)
        {
            if (!filterState.FilterValues.TryGetValue("FilterText", out var filterText))
            {
                System.Diagnostics.Debug.WriteLine($"Text filter for {filterState.PropertyName} missing FilterText value");
                return;
            }

            var useAndLogic = filterState.FilterValues.TryGetValue("UseAndLogic", out var andLogic) &&
                             andLogic is bool boolValue && boolValue;

            var filterKey = GridStateHelpers.CreateFilterResourceKey("TextFilter", filterState.PropertyName);
            var logicKey = GridStateHelpers.CreateFilterResourceKey("TextFilterLogic", filterState.PropertyName);

            GridStateHelpers.SetResourceValue(dataGrid, filterKey, filterText.ToString());
            GridStateHelpers.SetResourceValue(dataGrid, logicKey, useAndLogic);
        }

        #endregion

        #region Boolean Filter Application

        /// <summary>
        /// Applies a boolean filter state to the DynamicDataGrid's resources.
        /// Sets the show true/false flags in the appropriate resource keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply the boolean filter to.</param>
        /// <param name="filterState">The boolean filter state to apply.</param>
        internal static void ApplyBooleanFilter(DynamicDataGrid dataGrid, FilterState filterState)
        {
            var showTrueKey = GridStateHelpers.CreateFilterResourceKey("BooleanFilter", filterState.PropertyName, "_ShowTrue");
            var showFalseKey = GridStateHelpers.CreateFilterResourceKey("BooleanFilter", filterState.PropertyName, "_ShowFalse");

            if (filterState.FilterValues.TryGetValue("ShowTrue", out var showTrue) && showTrue is bool showTrueValue)
            {
                GridStateHelpers.SetResourceValue(dataGrid, showTrueKey, showTrueValue);
            }

            if (filterState.FilterValues.TryGetValue("ShowFalse", out var showFalse) && showFalse is bool showFalseValue)
            {
                GridStateHelpers.SetResourceValue(dataGrid, showFalseKey, showFalseValue);
            }
        }

        #endregion

        #region Numeric Filter Application

        /// <summary>
        /// Applies a numeric filter state to the DynamicDataGrid's resources.
        /// Sets the operation and associated values (Value, FromValue, ToValue) in the appropriate resource keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply the numeric filter to.</param>
        /// <param name="filterState">The numeric filter state to apply.</param>
        internal static void ApplyNumericFilter(DynamicDataGrid dataGrid, FilterState filterState)
        {
            if (!filterState.FilterValues.TryGetValue("Operation", out var operation))
            {
                System.Diagnostics.Debug.WriteLine($"Numeric filter for {filterState.PropertyName} missing Operation value");
                return;
            }

            var operationKey = GridStateHelpers.CreateFilterResourceKey("NumericFilter", filterState.PropertyName, "_Operation");
            var valueKey = GridStateHelpers.CreateFilterResourceKey("NumericFilter", filterState.PropertyName, "_Value");
            var fromValueKey = GridStateHelpers.CreateFilterResourceKey("NumericFilter", filterState.PropertyName, "_FromValue");
            var toValueKey = GridStateHelpers.CreateFilterResourceKey("NumericFilter", filterState.PropertyName, "_ToValue");

            GridStateHelpers.SetResourceValue(dataGrid, operationKey, operation.ToString());

            if (filterState.FilterValues.TryGetValue("Value", out var value))
            {
                GridStateHelpers.SetResourceValue(dataGrid, valueKey, value);
            }

            if (filterState.FilterValues.TryGetValue("FromValue", out var fromValue))
            {
                GridStateHelpers.SetResourceValue(dataGrid, fromValueKey, fromValue);
            }

            if (filterState.FilterValues.TryGetValue("ToValue", out var toValue))
            {
                GridStateHelpers.SetResourceValue(dataGrid, toValueKey, toValue);
            }
        }

        #endregion

        #region DateTime Filter Application

        /// <summary>
        /// Applies a DateTime filter state to the DynamicDataGrid's resources.
        /// Sets the operation and associated dates (Date, FromDate, ToDate) in the appropriate resource keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply the DateTime filter to.</param>
        /// <param name="filterState">The DateTime filter state to apply.</param>
        internal static void ApplyDateTimeFilter(DynamicDataGrid dataGrid, FilterState filterState)
        {
            if (!filterState.FilterValues.TryGetValue("Operation", out var operation))
            {
                System.Diagnostics.Debug.WriteLine($"DateTime filter for {filterState.PropertyName} missing Operation value");
                return;
            }

            var operationKey = GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", filterState.PropertyName, "_Operation");
            var dateKey = GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", filterState.PropertyName, "_Date");
            var fromDateKey = GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", filterState.PropertyName, "_FromDate");
            var toDateKey = GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", filterState.PropertyName, "_ToDate");

            GridStateHelpers.SetResourceValue(dataGrid, operationKey, operation.ToString());

            if (filterState.FilterValues.TryGetValue("Date", out var date))
            {
                GridStateHelpers.SetResourceValue(dataGrid, dateKey, date);
            }

            if (filterState.FilterValues.TryGetValue("FromDate", out var fromDate))
            {
                GridStateHelpers.SetResourceValue(dataGrid, fromDateKey, fromDate);
            }

            if (filterState.FilterValues.TryGetValue("ToDate", out var toDate))
            {
                GridStateHelpers.SetResourceValue(dataGrid, toDateKey, toDate);
            }
        }

        #endregion

        #region DropDown Filter Application

        /// <summary>
        /// Applies a dropdown filter state to the DynamicDataGrid's resources.
        /// Sets the selected value and optional search text in the appropriate resource keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply the dropdown filter to.</param>
        /// <param name="filterState">The dropdown filter state to apply.</param>
        internal static void ApplyDropDownFilter(DynamicDataGrid dataGrid, FilterState filterState)
        {
            if (!filterState.FilterValues.TryGetValue("SelectedValue", out var selectedValue))
            {
                System.Diagnostics.Debug.WriteLine($"DropDown filter for {filterState.PropertyName} missing SelectedValue");
                return;
            }

            var selectedValueKey = GridStateHelpers.CreateFilterResourceKey("DropDownFilter", filterState.PropertyName, "_SelectedValue");
            var searchTextKey = GridStateHelpers.CreateFilterResourceKey("DropDownFilter", filterState.PropertyName, "_SearchText");

            GridStateHelpers.SetResourceValue(dataGrid, selectedValueKey, selectedValue);

            if (filterState.FilterValues.TryGetValue("SearchText", out var searchText) &&
                searchText is string searchTextValue && !string.IsNullOrWhiteSpace(searchTextValue))
            {
                GridStateHelpers.SetResourceValue(dataGrid, searchTextKey, searchTextValue);
            }
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Removes all filters for a specific property from the DynamicDataGrid.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to remove filters from.</param>
        /// <param name="propertyName">The property name to remove filters for.</param>
        internal static void ClearFiltersForProperty(DynamicDataGrid dataGrid, string propertyName)
        {
            if (dataGrid?.Resources == null || string.IsNullOrEmpty(propertyName))
                return;

            try
            {
                // Define all possible filter resource keys for this property
                var filterKeys = new[]
                {
                    // Text filters
                    GridStateHelpers.CreateFilterResourceKey("TextFilter", propertyName),
                    GridStateHelpers.CreateFilterResourceKey("TextFilterLogic", propertyName),
                    
                    // Boolean filters
                    GridStateHelpers.CreateFilterResourceKey("BooleanFilter", propertyName, "_ShowTrue"),
                    GridStateHelpers.CreateFilterResourceKey("BooleanFilter", propertyName, "_ShowFalse"),
                    
                    // Numeric filters
                    GridStateHelpers.CreateFilterResourceKey("NumericFilter", propertyName, "_Operation"),
                    GridStateHelpers.CreateFilterResourceKey("NumericFilter", propertyName, "_Value"),
                    GridStateHelpers.CreateFilterResourceKey("NumericFilter", propertyName, "_FromValue"),
                    GridStateHelpers.CreateFilterResourceKey("NumericFilter", propertyName, "_ToValue"),
                    
                    // DateTime filters
                    GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", propertyName, "_Operation"),
                    GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", propertyName, "_Date"),
                    GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", propertyName, "_FromDate"),
                    GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", propertyName, "_ToDate"),
                    
                    // DropDown filters
                    GridStateHelpers.CreateFilterResourceKey("DropDownFilter", propertyName, "_SelectedValue"),
                    GridStateHelpers.CreateFilterResourceKey("DropDownFilter", propertyName, "_SearchText")
                };

                foreach (var key in filterKeys)
                {
                    if (dataGrid.Resources.Contains(key))
                    {
                        dataGrid.Resources.Remove(key);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error clearing filters for property {propertyName}: {ex.Message}");
            }
        }

        /// <summary>
        /// Validates that a filter state is compatible with DynamicDataGrid.
        /// Checks that the property exists in the grid's available columns.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to validate against.</param>
        /// <param name="filterState">The filter state to validate.</param>
        /// <returns>True if the filter is valid for this grid, false otherwise.</returns>
        internal static bool ValidateFilterForDynamicGrid(DynamicDataGrid dataGrid, FilterState filterState)
        {
            if (dataGrid?.DataContext == null || filterState == null)
                return false;

            var viewModel = dataGrid.DataContext;
            var availableColumnsProperty = viewModel.GetType().GetProperty("AvailableColumns");

            if (availableColumnsProperty?.GetValue(viewModel) is IEnumerable<AvailableColumnDefinition> availableColumns)
            {
                return availableColumns.Any(ac => ac.PropertyName == filterState.PropertyName);
            }

            return false;
        }

        /// <summary>
        /// Applies multiple filter states to a DynamicDataGrid with validation.
        /// Only applies filters for properties that exist in the grid's available columns.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply filters to.</param>
        /// <param name="filterStates">List of filter states to apply.</param>
        /// <returns>Number of filters successfully applied.</returns>
        internal static int ApplyValidatedFiltersForDynamicGrid(DynamicDataGrid dataGrid, List<FilterState> filterStates)
        {
            if (dataGrid == null || filterStates?.Count == 0)
                return 0;

            int appliedCount = 0;

            try
            {
                // Clear existing filters first
                GridStateHelpers.ClearAllFilters(dataGrid);

                // Apply only validated filters
                foreach (var filterState in filterStates)
                {
                    if (ValidateFilterForDynamicGrid(dataGrid, filterState))
                    {
                        ApplyFilterState(dataGrid, filterState);
                        appliedCount++;
                    }
                    else
                    {
                        System.Diagnostics.Debug.WriteLine($"Skipping filter for unknown property: {filterState.PropertyName}");
                    }
                }

                // Refresh the view if any filters were applied
                if (appliedCount > 0)
                {
                    GridStateHelpers.RefreshDataGridFilters(dataGrid);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error applying filters to DynamicDataGrid: {ex.Message}");
            }

            return appliedCount;
        }

        #endregion
    }
}