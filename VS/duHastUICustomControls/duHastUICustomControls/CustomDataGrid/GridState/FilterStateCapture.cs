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

using System.Collections.Generic;
using System.Linq;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Handles capturing filter states from DataGrid controls.
    /// Contains specialized logic for each filter type (Text, Boolean, Numeric, DateTime, DropDown).
    /// </summary>
    internal static class FilterStateCapture
    {
        #region Public Methods

        /// <summary>
        /// Captures all active filter states from a DynamicDataGrid.
        /// Processes all filter types and returns a comprehensive list of active filters.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture filters from.</param>
        /// <returns>List of FilterState objects representing all active filters.</returns>
        internal static List<FilterState> CaptureAllFilterStates(DynamicDataGrid dataGrid)
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

        #region Text Filters

        /// <summary>
        /// Captures text filter states from the DynamicDataGrid's resources.
        /// Looks for TextFilter_ and TextFilterLogic_ resource keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture text filters from.</param>
        /// <param name="filterStates">List to add captured filter states to.</param>
        /// <param name="processedProperties">Set of property names already processed to avoid duplicates.</param>
        internal static void CaptureTextFilters(DynamicDataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var textFilterKeys = GridStateHelpers.GetFilterResourceKeys(dataGrid, "TextFilter_");

            foreach (var key in textFilterKeys)
            {
                var propertyName = GridStateHelpers.ExtractPropertyNameFromKey(key, "TextFilter_");
                if (string.IsNullOrEmpty(propertyName) || processedProperties.Contains(propertyName))
                    continue;

                var filterText = GridStateHelpers.GetResourceValue(dataGrid, key) as string;
                if (string.IsNullOrWhiteSpace(filterText))
                    continue;

                var logicKey = GridStateHelpers.CreateFilterResourceKey("TextFilterLogic", propertyName);
                var useAndLogic = GridStateHelpers.GetResourceValue(dataGrid, logicKey) is bool andLogic && andLogic;

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

        #endregion

        #region Boolean Filters

        /// <summary>
        /// Captures boolean filter states from the DynamicDataGrid's resources.
        /// Looks for BooleanFilter_ShowTrue_ and BooleanFilter_ShowFalse_ resource keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture boolean filters from.</param>
        /// <param name="filterStates">List to add captured filter states to.</param>
        /// <param name="processedProperties">Set of property names already processed to avoid duplicates.</param>
        internal static void CaptureBooleanFilters(DynamicDataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var booleanFilterKeys = GridStateHelpers.GetFilterResourceKeys(dataGrid, "BooleanFilter_ShowTrue_");

            foreach (var key in booleanFilterKeys)
            {
                var propertyName = GridStateHelpers.ExtractPropertyNameFromKey(key, "BooleanFilter_ShowTrue_");
                if (string.IsNullOrEmpty(propertyName) || processedProperties.Contains(propertyName))
                    continue;

                var showTrueKey = GridStateHelpers.CreateFilterResourceKey("BooleanFilter", propertyName, "_ShowTrue");
                var showFalseKey = GridStateHelpers.CreateFilterResourceKey("BooleanFilter", propertyName, "_ShowFalse");

                var showTrue = GridStateHelpers.GetResourceValue(dataGrid, showTrueKey) as bool?;
                var showFalse = GridStateHelpers.GetResourceValue(dataGrid, showFalseKey) as bool?;

                if (!showTrue.HasValue && !showFalse.HasValue)
                    continue;

                var filterState = new FilterState
                {
                    PropertyName = propertyName,
                    FilterType = FilterType.Boolean,
                    Description = GridStateHelpers.GetBooleanFilterDescription(showTrue, showFalse)
                };

                if (showTrue.HasValue)
                    filterState.FilterValues["ShowTrue"] = showTrue.Value;
                if (showFalse.HasValue)
                    filterState.FilterValues["ShowFalse"] = showFalse.Value;

                filterStates.Add(filterState);
                processedProperties.Add(propertyName);
            }
        }

        #endregion

        #region Numeric Filters

        /// <summary>
        /// Captures numeric filter states from the DynamicDataGrid's resources.
        /// Looks for NumericFilter_Operation_ resource keys and associated value keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture numeric filters from.</param>
        /// <param name="filterStates">List to add captured filter states to.</param>
        /// <param name="processedProperties">Set of property names already processed to avoid duplicates.</param>
        internal static void CaptureNumericFilters(DynamicDataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var numericFilterKeys = GridStateHelpers.GetFilterResourceKeys(dataGrid, "NumericFilter_Operation_");

            foreach (var key in numericFilterKeys)
            {
                var propertyName = GridStateHelpers.ExtractPropertyNameFromKey(key, "NumericFilter_Operation_");
                if (string.IsNullOrEmpty(propertyName) || processedProperties.Contains(propertyName))
                    continue;

                var operationKey = GridStateHelpers.CreateFilterResourceKey("NumericFilter", propertyName, "_Operation");
                var valueKey = GridStateHelpers.CreateFilterResourceKey("NumericFilter", propertyName, "_Value");
                var fromValueKey = GridStateHelpers.CreateFilterResourceKey("NumericFilter", propertyName, "_FromValue");
                var toValueKey = GridStateHelpers.CreateFilterResourceKey("NumericFilter", propertyName, "_ToValue");

                var operation = GridStateHelpers.GetResourceValue(dataGrid, operationKey)?.ToString();
                if (string.IsNullOrEmpty(operation))
                    continue;

                var filterState = new FilterState
                {
                    PropertyName = propertyName,
                    FilterType = FilterType.Numeric
                };

                filterState.FilterValues["Operation"] = operation;

                var value = GridStateHelpers.GetResourceValue(dataGrid, valueKey);
                if (value != null)
                    filterState.FilterValues["Value"] = value;

                var fromValue = GridStateHelpers.GetResourceValue(dataGrid, fromValueKey);
                if (fromValue != null)
                    filterState.FilterValues["FromValue"] = fromValue;

                var toValue = GridStateHelpers.GetResourceValue(dataGrid, toValueKey);
                if (toValue != null)
                    filterState.FilterValues["ToValue"] = toValue;

                filterState.Description = GridStateHelpers.GetNumericFilterDescription(operation, filterState.FilterValues);

                filterStates.Add(filterState);
                processedProperties.Add(propertyName);
            }
        }

        #endregion

        #region DateTime Filters

        /// <summary>
        /// Captures DateTime filter states from the DynamicDataGrid's resources.
        /// Looks for DateTimeFilter_Operation_ resource keys and associated date keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture DateTime filters from.</param>
        /// <param name="filterStates">List to add captured filter states to.</param>
        /// <param name="processedProperties">Set of property names already processed to avoid duplicates.</param>
        internal static void CaptureDateTimeFilters(DynamicDataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var dateTimeFilterKeys = GridStateHelpers.GetFilterResourceKeys(dataGrid, "DateTimeFilter_Operation_");

            foreach (var key in dateTimeFilterKeys)
            {
                var propertyName = GridStateHelpers.ExtractPropertyNameFromKey(key, "DateTimeFilter_Operation_");
                if (string.IsNullOrEmpty(propertyName) || processedProperties.Contains(propertyName))
                    continue;

                var operationKey = GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", propertyName, "_Operation");
                var dateKey = GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", propertyName, "_Date");
                var fromDateKey = GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", propertyName, "_FromDate");
                var toDateKey = GridStateHelpers.CreateFilterResourceKey("DateTimeFilter", propertyName, "_ToDate");

                var operation = GridStateHelpers.GetResourceValue(dataGrid, operationKey)?.ToString();
                if (string.IsNullOrEmpty(operation))
                    continue;

                var filterState = new FilterState
                {
                    PropertyName = propertyName,
                    FilterType = FilterType.DateTime
                };

                filterState.FilterValues["Operation"] = operation;

                var date = GridStateHelpers.GetResourceValue(dataGrid, dateKey);
                if (date != null)
                    filterState.FilterValues["Date"] = date;

                var fromDate = GridStateHelpers.GetResourceValue(dataGrid, fromDateKey);
                if (fromDate != null)
                    filterState.FilterValues["FromDate"] = fromDate;

                var toDate = GridStateHelpers.GetResourceValue(dataGrid, toDateKey);
                if (toDate != null)
                    filterState.FilterValues["ToDate"] = toDate;

                filterState.Description = GridStateHelpers.GetDateTimeFilterDescription(operation, filterState.FilterValues);

                filterStates.Add(filterState);
                processedProperties.Add(propertyName);
            }
        }

        #endregion

        #region DropDown Filters

        /// <summary>
        /// Captures dropdown filter states from the DynamicDataGrid's resources.
        /// Looks for DropDownFilter_SelectedValue_ and DropDownFilter_SearchText_ resource keys.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture dropdown filters from.</param>
        /// <param name="filterStates">List to add captured filter states to.</param>
        /// <param name="processedProperties">Set of property names already processed to avoid duplicates.</param>
        internal static void CaptureDropDownFilters(DynamicDataGrid dataGrid, List<FilterState> filterStates, HashSet<string> processedProperties)
        {
            var dropDownFilterKeys = GridStateHelpers.GetFilterResourceKeys(dataGrid, "DropDownFilter_SelectedValue_");

            foreach (var key in dropDownFilterKeys)
            {
                var propertyName = GridStateHelpers.ExtractPropertyNameFromKey(key, "DropDownFilter_SelectedValue_");
                if (string.IsNullOrEmpty(propertyName) || processedProperties.Contains(propertyName))
                    continue;

                var selectedValueKey = GridStateHelpers.CreateFilterResourceKey("DropDownFilter", propertyName, "_SelectedValue");
                var searchTextKey = GridStateHelpers.CreateFilterResourceKey("DropDownFilter", propertyName, "_SearchText");

                var selectedValue = GridStateHelpers.GetResourceValue(dataGrid, selectedValueKey);
                if (selectedValue == null)
                    continue;

                var searchText = GridStateHelpers.GetResourceValue(dataGrid, searchTextKey) as string;

                var filterState = new FilterState
                {
                    PropertyName = propertyName,
                    FilterType = FilterType.DropDown
                };

                filterState.FilterValues["SelectedValue"] = selectedValue;
                if (!string.IsNullOrWhiteSpace(searchText))
                    filterState.FilterValues["SearchText"] = searchText;

                filterState.Description = GridStateHelpers.GetDropDownFilterDescription(selectedValue, searchText);

                filterStates.Add(filterState);
                processedProperties.Add(propertyName);
            }
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Checks if a specific property has any active filters in the DynamicDataGrid.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to check.</param>
        /// <param name="propertyName">The property name to check for filters.</param>
        /// <returns>True if the property has any active filters, false otherwise.</returns>
        internal static bool HasActiveFiltersForProperty(DynamicDataGrid dataGrid, string propertyName)
        {
            if (dataGrid.Resources == null || string.IsNullOrEmpty(propertyName))
                return false;

            // Check for any filter type for this property
            var filterPrefixes = new[]
            {
                "TextFilter_",
                "BooleanFilter_ShowTrue_",
                "BooleanFilter_ShowFalse_",
                "NumericFilter_Operation_",
                "DateTimeFilter_Operation_",
                "DropDownFilter_SelectedValue_"
            };

            return filterPrefixes.Any(prefix =>
            {
                var key = GridStateHelpers.CreateFilterResourceKey(prefix.TrimEnd('_'), propertyName);
                return GridStateHelpers.GetResourceValue(dataGrid, key) != null;
            });
        }

        /// <summary>
        /// Gets a count of active filters by type in the DynamicDataGrid.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to analyze.</param>
        /// <returns>Dictionary with filter type names and their counts.</returns>
        internal static Dictionary<string, int> GetFilterCountsByType(DynamicDataGrid dataGrid)
        {
            var counts = new Dictionary<string, int>
            {
                ["Text"] = 0,
                ["Boolean"] = 0,
                ["Numeric"] = 0,
                ["DateTime"] = 0,
                ["DropDown"] = 0
            };

            if (dataGrid.Resources == null)
                return counts;

            counts["Text"] = GridStateHelpers.GetFilterResourceKeys(dataGrid, "TextFilter_").Count;
            counts["Boolean"] = GridStateHelpers.GetFilterResourceKeys(dataGrid, "BooleanFilter_ShowTrue_").Count;
            counts["Numeric"] = GridStateHelpers.GetFilterResourceKeys(dataGrid, "NumericFilter_Operation_").Count;
            counts["DateTime"] = GridStateHelpers.GetFilterResourceKeys(dataGrid, "DateTimeFilter_Operation_").Count;
            counts["DropDown"] = GridStateHelpers.GetFilterResourceKeys(dataGrid, "DropDownFilter_SelectedValue_").Count;

            return counts;
        }

        /// <summary>
        /// Gets all property names that have active filters in the DynamicDataGrid.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to analyze.</param>
        /// <returns>List of property names with active filters.</returns>
        internal static List<string> GetPropertiesWithActiveFilters(DynamicDataGrid dataGrid)
        {
            var properties = new HashSet<string>();

            if (dataGrid.Resources == null)
                return properties.ToList();

            // Extract property names from all filter types
            var filterPrefixes = new[]
            {
                ("TextFilter_", "TextFilter_"),
                ("BooleanFilter_ShowTrue_", "BooleanFilter_ShowTrue_"),
                ("NumericFilter_Operation_", "NumericFilter_Operation_"),
                ("DateTimeFilter_Operation_", "DateTimeFilter_Operation_"),
                ("DropDownFilter_SelectedValue_", "DropDownFilter_SelectedValue_")
            };

            foreach (var (searchPrefix, extractPrefix) in filterPrefixes)
            {
                var keys = GridStateHelpers.GetFilterResourceKeys(dataGrid, searchPrefix);
                foreach (var key in keys)
                {
                    var propertyName = GridStateHelpers.ExtractPropertyNameFromKey(key, extractPrefix);
                    if (!string.IsNullOrEmpty(propertyName))
                    {
                        properties.Add(propertyName);
                    }
                }
            }

            return properties.ToList();
        }

        #endregion
    }
}