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
using System.ComponentModel;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static partial class DataGridColumnHeaderBehavior
    {

        #region Filtering

        /// <summary>
        /// Checks if a column has an active filter applied (text, boolean, numeric, or DateTime).
        /// </summary>
        /// <param name="dataGrid">The DataGrid to check for filters.</param>
        /// <param name="propertyName">The property name of the column to check.</param>
        /// <returns>True if the column has an active filter, false otherwise.</returns>
        private static bool HasActiveFilter(DataGrid dataGrid, string propertyName)
        {
            // Check for text filter
            var textFilterKey = $"TextFilter_{propertyName}";
            var hasTextFilter = dataGrid.Resources.Contains(textFilterKey) &&
                               !string.IsNullOrWhiteSpace((string)dataGrid.Resources[textFilterKey]);

            // Check for boolean filter
            var showTrueKey = $"BooleanFilter_ShowTrue_{propertyName}";
            var showFalseKey = $"BooleanFilter_ShowFalse_{propertyName}";
            var hasBooleanFilter = dataGrid.Resources.Contains(showTrueKey) || dataGrid.Resources.Contains(showFalseKey);

            // Check for numeric filter
            var numericOperationKey = $"NumericFilter_Operation_{propertyName}";
            var hasNumericFilter = dataGrid.Resources.Contains(numericOperationKey);

            // Check for DateTime filter
            var dateTimeOperationKey = $"DateTimeFilter_Operation_{propertyName}";
            var hasDateTimeFilter = dataGrid.Resources.Contains(dateTimeOperationKey);

            return hasTextFilter || hasBooleanFilter || hasNumericFilter || hasDateTimeFilter;
        }

        /// <summary>
        /// Populates the filter submenu with options appropriate for the column's data type.
        /// Always shows the current filter value at the top if one is applied.
        /// </summary>
        /// <param name="filterSubmenu">The filter submenu to populate.</param>
        /// <param name="dataGrid">The DataGrid containing the column.</param>
        /// <param name="propertyName">The property name of the column being filtered.</param>
        private static void PopulateFilterSubmenu(MenuItem filterSubmenu, DataGrid dataGrid, string propertyName)
        {
            // Clear existing items
            filterSubmenu.Items.Clear();

            // Get current filter for display (using the new display method)
            var currentFilterDisplay = GetCurrentFilterDisplayText(dataGrid, propertyName);

            // Show current filter first if there is one
            if (!string.IsNullOrEmpty(currentFilterDisplay))
            {
                var currentFilterItem = new MenuItem
                {
                    Header = $"Current: {currentFilterDisplay}",
                    IsEnabled = false,
                    FontWeight = FontWeights.Bold,
                    Foreground = new SolidColorBrush(Colors.DarkBlue)
                };
                filterSubmenu.Items.Add(currentFilterItem);
                filterSubmenu.Items.Add(new Separator());
            }

            // Clear filter option (always available)
            var clearFilterItem = new MenuItem { Header = "Clear Filter" };
            clearFilterItem.Click += (s, e) =>
            {
                ClearColumnFilter(dataGrid, propertyName);
                PopulateFilterSubmenu(filterSubmenu, dataGrid, propertyName);
            };

            clearFilterItem.IsEnabled = !string.IsNullOrEmpty(currentFilterDisplay);

            filterSubmenu.Items.Add(clearFilterItem);
            filterSubmenu.Items.Add(new Separator());

            // Check column data type and UI type for filter options
            var columnType = GetColumnDataType(dataGrid, propertyName);
            var isBooleanColumn = columnType == typeof(bool) || columnType == typeof(bool?);
            var isNumericColumn = IsNumericType(columnType);
            var isDateTimeColumn = IsDateTimeType(columnType);
            var isDropDownColumn = IsDropDownColumn(dataGrid, propertyName); // NEW

            if (isDropDownColumn) // NEW: DropDown filter option
            {
                var filterByDropDownItem = new MenuItem { Header = "Filter by List Value..." };
                filterByDropDownItem.Click += (s, e) => ShowFilterDropDownDialog(dataGrid, propertyName);
                filterSubmenu.Items.Add(filterByDropDownItem);
            }
            else if (isBooleanColumn)
            {
                var filterByBooleanItem = new MenuItem { Header = "Filter by Value..." };
                filterByBooleanItem.Click += (s, e) => ShowFilterBooleanDialog(dataGrid, propertyName);
                filterSubmenu.Items.Add(filterByBooleanItem);
            }
            else if (isNumericColumn)
            {
                var filterByNumericItem = new MenuItem { Header = "Filter by Number..." };
                filterByNumericItem.Click += (s, e) => ShowFilterNumericDialog(dataGrid, propertyName);
                filterSubmenu.Items.Add(filterByNumericItem);
            }
            else if (isDateTimeColumn)
            {
                var filterByDateTimeItem = new MenuItem { Header = "Filter by Date..." };
                filterByDateTimeItem.Click += (s, e) => ShowFilterDateTimeDialog(dataGrid, propertyName);
                filterSubmenu.Items.Add(filterByDateTimeItem);
            }
            else
            {
                var filterByTextItem = new MenuItem { Header = "Filter by Text..." };
                filterByTextItem.Click += (s, e) => ShowFilterTextDialog(dataGrid, propertyName);
                filterSubmenu.Items.Add(filterByTextItem);
            }
        }

        /// <summary>
        /// Determines if a Type represents a data type supported by the dynamic data grid.
        /// Based on the supported types: String, Int32, Double, Boolean, DateTime
        /// </summary>
        /// <param name="type">The Type to check.</param>
        /// <returns>True if the type is numeric (Int32 or Double), false otherwise.</returns>
        private static bool IsNumericType(Type type)
        {
            if (type == null) return false;

            // Handle nullable types
            if (type.IsGenericType && type.GetGenericTypeDefinition() == typeof(Nullable<>))
            {
                type = Nullable.GetUnderlyingType(type);
            }

            // Only Int32 and Double are numeric in your supported types
            return type == typeof(int) || type == typeof(double);
        }

        /// <summary>
        /// Determines if a Type represents a DateTime data type.
        /// </summary>
        /// <param name="type">The Type to check.</param>
        /// <returns>True if the type is DateTime, false otherwise.</returns>
        private static bool IsDateTimeType(Type type)
        {
            if (type == null) return false;

            // Handle nullable types
            if (type.IsGenericType && type.GetGenericTypeDefinition() == typeof(Nullable<>))
            {
                type = Nullable.GetUnderlyingType(type);
            }

            return type == typeof(DateTime);
        }

        /// <summary>
        /// Removes all filter information for a specific column and refreshes the display.
        /// Handles text, boolean, numeric, and DateTime filters.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to clear the filter from.</param>
        /// <param name="propertyName">The property name of the column to clear the filter for.</param>
        private static void ClearColumnFilter(DataGrid dataGrid, string propertyName)
        {
            // Clear text filters
            var textFilterKey = $"TextFilter_{propertyName}";
            var logicKey = $"TextFilterLogic_{propertyName}";
            dataGrid.Resources.Remove(textFilterKey);
            dataGrid.Resources.Remove(logicKey);

            // Clear dropdown filters
            var dropDownSelectedValueKey = $"DropDownFilter_SelectedValue_{propertyName}";
            var dropDownSearchTextKey = $"DropDownFilter_SearchText_{propertyName}";
            dataGrid.Resources.Remove(dropDownSelectedValueKey);
            dataGrid.Resources.Remove(dropDownSearchTextKey);

            // Clear boolean filters
            var showTrueKey = $"BooleanFilter_ShowTrue_{propertyName}";
            var showFalseKey = $"BooleanFilter_ShowFalse_{propertyName}";
            dataGrid.Resources.Remove(showTrueKey);
            dataGrid.Resources.Remove(showFalseKey);

            // Clear numeric filters
            var numericOperationKey = $"NumericFilter_Operation_{propertyName}";
            var numericValueKey = $"NumericFilter_Value_{propertyName}";
            var numericFromValueKey = $"NumericFilter_FromValue_{propertyName}";
            var numericToValueKey = $"NumericFilter_ToValue_{propertyName}";
            dataGrid.Resources.Remove(numericOperationKey);
            dataGrid.Resources.Remove(numericValueKey);
            dataGrid.Resources.Remove(numericFromValueKey);
            dataGrid.Resources.Remove(numericToValueKey);

            // Clear DateTime filters
            var dateTimeOperationKey = $"DateTimeFilter_Operation_{propertyName}";
            var dateTimeDateKey = $"DateTimeFilter_Date_{propertyName}";
            var dateTimeFromDateKey = $"DateTimeFilter_FromDate_{propertyName}";
            var dateTimeToDateKey = $"DateTimeFilter_ToDate_{propertyName}";
            dataGrid.Resources.Remove(dateTimeOperationKey);
            dataGrid.Resources.Remove(dateTimeDateKey);
            dataGrid.Resources.Remove(dateTimeFromDateKey);
            dataGrid.Resources.Remove(dateTimeToDateKey);

            // Update filter icon for this column
            var column = dataGrid.Columns.FirstOrDefault(c => GetColumnPropertyName(c) == propertyName);
            if (column != null)
            {
                UpdateFilterIcon(dataGrid, column, propertyName);
            }

            // Apply remaining filters
            var hasAnyFilters = dataGrid.Resources.Keys.OfType<string>()
                .Any(k => k.StartsWith("TextFilter_") || k.StartsWith("BooleanFilter_") ||
                          k.StartsWith("NumericFilter_") || k.StartsWith("DateTimeFilter_") ||
                          k.StartsWith("DropDownFilter_")); 

            if (!hasAnyFilters)
            {
                var collectionView = System.Windows.Data.CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
                if (collectionView != null)
                {
                    collectionView.Filter = null;
                    collectionView.Refresh();
                }
            }
            else
            {
                ApplyAllColumnFilters(dataGrid);
            }
        }

        /// <summary>
        /// Applies all active column filters to the DataGrid's collection view.
        /// Handles text, boolean, numeric, and DateTime filters.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to apply filters to.</param>
        private static void ApplyAllColumnFilters(DataGrid dataGrid)
        {
            if (dataGrid.ItemsSource == null) return;

            var collectionView = System.Windows.Data.CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
            if (collectionView == null) return;

            // Commit any pending edits before applying filters
            try
            {
                dataGrid.CommitEdit();

                if (dataGrid.CurrentItem != null)
                {
                    dataGrid.CommitEdit(DataGridEditingUnit.Row, true);
                }

                if (collectionView is IEditableCollectionView editableView)
                {
                    if (editableView.IsEditingItem)
                    {
                        editableView.CommitEdit();
                    }

                    if (editableView.IsAddingNew)
                    {
                        editableView.CommitNew();
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error committing edits: {ex.Message}");
            }

            collectionView.Filter = item =>
            {
                if (item == null) return false;

                // Check all active dropdown filters
                foreach (var resourceKey in dataGrid.Resources.Keys.OfType<string>()
                    .Where(k => k.StartsWith("DropDownFilter_SelectedValue_")))
                {
                    var propertyName = resourceKey["DropDownFilter_SelectedValue_".Length..];
                    if (!PassesDropDownFilter(item, dataGrid, propertyName))
                    {
                        return false;
                    }
                }

                // Check all active text filters
                foreach (var resourceKey in dataGrid.Resources.Keys.OfType<string>()
                    .Where(k => k.StartsWith("TextFilter_")))
                {
                    var propertyName = resourceKey["TextFilter_".Length..];
                    var filterText = (string)dataGrid.Resources[resourceKey];
                    var logicKey = $"TextFilterLogic_{propertyName}";
                    var useAndLogic = dataGrid.Resources.Contains(logicKey) && (bool)dataGrid.Resources[logicKey];

                    if (!string.IsNullOrWhiteSpace(filterText))
                    {
                        var itemValue = GetItemValue(item, propertyName)?.ToString() ?? "";
                        if (!PassesTextFilter(itemValue, filterText, useAndLogic))
                        {
                            return false;
                        }
                    }
                }

                // Check all active boolean filters
                foreach (var resourceKey in dataGrid.Resources.Keys.OfType<string>()
                    .Where(k => k.StartsWith("BooleanFilter_ShowTrue_")))
                {
                    var propertyName = resourceKey["BooleanFilter_ShowTrue_".Length..];
                    if (!PassesBooleanFilter(item, dataGrid, propertyName))
                    {
                        return false;
                    }
                }

                // Check all active numeric filters
                foreach (var resourceKey in dataGrid.Resources.Keys.OfType<string>()
                    .Where(k => k.StartsWith("NumericFilter_Operation_")))
                {
                    var propertyName = resourceKey["NumericFilter_Operation_".Length..];
                    if (!PassesNumericFilter(item, dataGrid, propertyName))
                    {
                        return false;
                    }
                }

                // Check all active DateTime filters
                foreach (var resourceKey in dataGrid.Resources.Keys.OfType<string>()
                    .Where(k => k.StartsWith("DateTimeFilter_Operation_")))
                {
                    var propertyName = resourceKey["DateTimeFilter_Operation_".Length..];
                    if (!PassesDateTimeFilter(item, dataGrid, propertyName))
                    {
                        return false;
                    }
                }

                return true;
            };

            // Use dispatcher to ensure the refresh happens after any pending UI updates
            dataGrid.Dispatcher.BeginInvoke(new Action(() =>
            {
                try
                {
                    collectionView.Refresh();
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error refreshing collection view: {ex.Message}");
                }
            }), System.Windows.Threading.DispatcherPriority.Background);
        }

        // Replace the existing GetCurrentFilterText with these two methods in your UtilityFiltering file:

        /// <summary>
        /// Gets the raw filter value for a column (used by filter dialogs).
        /// Returns just the filter value without any prefixes or formatting.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to get the filter from.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>The raw filter value, or null if no filter is applied.</returns>
        private static string GetCurrentFilterText(DataGrid dataGrid, string propertyName)
        {
            if (dataGrid?.Resources == null || string.IsNullOrEmpty(propertyName))
                return null;

            // Check for text filter only (this is what dialogs expect)
            var textFilterKey = $"TextFilter_{propertyName}";
            if (dataGrid.Resources.Contains(textFilterKey))
            {
                return dataGrid.Resources[textFilterKey] as string;
            }

            return null;
        }

        /// <summary>
        /// Gets a formatted display string for the current filter (used by context menu display).
        /// Returns a user-friendly description of the current filter with type prefixes.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to get the filter from.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A formatted description of the current filter, or null if no filter is applied.</returns>
        private static string GetCurrentFilterDisplayText(DataGrid dataGrid, string propertyName)
        {
            if (dataGrid?.Resources == null || string.IsNullOrEmpty(propertyName))
                return null;

            
            // Check for dropdown filter first (NEW)
            var dropDownFilter = GetCurrentDropDownFilterText(dataGrid, propertyName);
            if (!string.IsNullOrEmpty(dropDownFilter))
            {
                return dropDownFilter;
            }

            // Check for text filter
            var textFilterKey = $"TextFilter_{propertyName}";
            if (dataGrid.Resources.Contains(textFilterKey))
            {
                var filterText = dataGrid.Resources[textFilterKey] as string;
                if (!string.IsNullOrWhiteSpace(filterText))
                {
                    var logicKey = $"TextFilterLogic_{propertyName}";
                    var useAndLogic = dataGrid.Resources.Contains(logicKey) && (bool)dataGrid.Resources[logicKey];
                    var logicDisplay = useAndLogic ? " (AND)" : " (OR)";

                    var hasMultipleTerms = filterText.Split([' '], StringSplitOptions.RemoveEmptyEntries).Length > 1;
                    return hasMultipleTerms ? $"Text: \"{filterText}\"{logicDisplay}" : $"Text: \"{filterText}\"";
                }
            }

            // Check for boolean filter
            var showTrueKey = $"BooleanFilter_ShowTrue_{propertyName}";
            var showFalseKey = $"BooleanFilter_ShowFalse_{propertyName}";
            var showTrue = dataGrid.Resources.Contains(showTrueKey) ? (bool?)dataGrid.Resources[showTrueKey] : null;
            var showFalse = dataGrid.Resources.Contains(showFalseKey) ? (bool?)dataGrid.Resources[showFalseKey] : null;

            if (showTrue.HasValue || showFalse.HasValue)
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

            // Check for numeric filter
            var numericOperationKey = $"NumericFilter_Operation_{propertyName}";
            if (dataGrid.Resources.Contains(numericOperationKey))
            {
                var numericFilterText = GetCurrentNumericFilterText(dataGrid, propertyName);
                if (!string.IsNullOrEmpty(numericFilterText))
                {
                    return $"Number: {numericFilterText}";
                }
            }

            // Check for DateTime filter
            var dateTimeOperationKey = $"DateTimeFilter_Operation_{propertyName}";
            if (dataGrid.Resources.Contains(dateTimeOperationKey))
            {
                var dateTimeFilterText = GetCurrentDateTimeFilterText(dataGrid, propertyName);
                if (!string.IsNullOrEmpty(dateTimeFilterText))
                {
                    return $"Date: {dateTimeFilterText}";
                }
            }

            return null;
        }


        #endregion


    }
}
