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
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

using System.Windows.Data;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static partial class DataGridColumnHeaderBehavior
    {
        #region Bulk Selection (Row Context Menus)

        /// <summary>
        /// Sets up context menus on DataGrid rows for bulk checkbox operations if bulk selection is enabled.
        /// Only applies to DataGrids with multiple selection mode.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to set up row context menus for.</param>
        private static void SetupRowContextMenus(DataGrid dataGrid)
        {
            if (!GetEnableBulkSelection(dataGrid)) return;

            // Don't show bulk selection menu if grid is set to single selection
            if (dataGrid.SelectionMode == DataGridSelectionMode.Single)
            {
                return;
            }

            // Create static context menu - we'll just update the text dynamically
            var staticContextMenu = CreateStaticRowContextMenu(dataGrid);

            // Apply to DataGrid rows
            var style = new Style(typeof(DataGridRow));
            style.Setters.Add(new Setter(FrameworkElement.ContextMenuProperty, staticContextMenu));

            if (dataGrid.RowStyle == null)
            {
                dataGrid.RowStyle = style;
            }
            else
            {
                var newStyle = new Style(typeof(DataGridRow), dataGrid.RowStyle);
                newStyle.Setters.Add(new Setter(FrameworkElement.ContextMenuProperty, staticContextMenu));
                dataGrid.RowStyle = newStyle;
            }
        }

        /// <summary>
        /// Creates a context menu for DataGrid rows with bulk checkbox operations.
        /// Includes options for checking/unchecking selected rows and all visible/all rows.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to create the row context menu for.</param>
        /// <returns>A ContextMenu configured for bulk selection operations.</returns>
        private static ContextMenu CreateStaticRowContextMenu(DataGrid dataGrid)
        {
            var contextMenu = new ContextMenu();

            var checkboxColumnName = GetBulkSelectionColumn(dataGrid);
            if (string.IsNullOrEmpty(checkboxColumnName))
            {
                checkboxColumnName = AutoDetectCheckboxColumn(dataGrid);
            }

            if (!string.IsNullOrEmpty(checkboxColumnName))
            {
                // Selected rows operations
                var checkSelectedItem = new MenuItem { Header = "☑️ Check Selected" };
                checkSelectedItem.Click += (s, e) => BulkSetSelectedCheckboxes(dataGrid, checkboxColumnName, true);

                var uncheckSelectedItem = new MenuItem { Header = "☐ Uncheck Selected" };
                uncheckSelectedItem.Click += (s, e) => BulkSetSelectedCheckboxes(dataGrid, checkboxColumnName, false);

                var separator1 = new Separator();

                // All rows operations
                var checkAllVisibleItem = new MenuItem { Header = "☑️ Check All Visible" };
                checkAllVisibleItem.Click += (s, e) => BulkSetCheckboxes(dataGrid, checkboxColumnName, true, false);

                var checkAllItem = new MenuItem { Header = "☑️ Check All Rows" };
                checkAllItem.Click += (s, e) => BulkSetCheckboxes(dataGrid, checkboxColumnName, true, true);

                var uncheckAllVisibleItem = new MenuItem { Header = "☐ Uncheck All Visible" };
                uncheckAllVisibleItem.Click += (s, e) => BulkSetCheckboxes(dataGrid, checkboxColumnName, false, false);

                var uncheckAllItem = new MenuItem { Header = "☐ Uncheck All Rows" };
                uncheckAllItem.Click += (s, e) => BulkSetCheckboxes(dataGrid, checkboxColumnName, false, true);

                // Load styles directly from resource dictionary
                contextMenu.Opened += (s, e) =>
                {
                    // Update headers with current selection count
                    var count = dataGrid.SelectedItems.Count;
                    checkSelectedItem.Header = $"☑️ Check Selected ({count} row{(count > 1 ? "s" : "")})";
                    uncheckSelectedItem.Header = $"☐ Uncheck Selected ({count} row{(count > 1 ? "s" : "")})";

                    // Load styles directly from resource dictionary
                    if (contextMenu.Style == null)
                    {
                        try
                        {
                            // Use helper to load resource dictionary
                            var resourceDict = LoadResourceDictionary();

                            var contextMenuStyle = resourceDict["BulkSelectionContextMenuStyle"] as Style;
                            var menuItemStyle = resourceDict["BulkOperationMenuItemStyle"] as Style;
                            var separatorStyle = resourceDict["BulkOperationSeparatorStyle"] as Style;

                            if (contextMenuStyle != null)
                            {
                                contextMenu.Style = contextMenuStyle;
                            }
                            else
                            {
                                System.Diagnostics.Debug.WriteLine("❌ BulkSelectionContextMenuStyle not found in resource dictionary");
                            }

                            if (menuItemStyle != null)
                            {
                                checkSelectedItem.Style = menuItemStyle;
                                uncheckSelectedItem.Style = menuItemStyle;
                                checkAllVisibleItem.Style = menuItemStyle;
                                checkAllItem.Style = menuItemStyle;
                                uncheckAllVisibleItem.Style = menuItemStyle;
                                uncheckAllItem.Style = menuItemStyle;
                            }

                            if (separatorStyle != null)
                            {
                                separator1.Style = separatorStyle;
                            }
                        }
                        catch (Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"❌ Error loading resource dictionary: {ex.Message}");
                        }
                    }
                };

                contextMenu.Items.Add(checkSelectedItem);
                contextMenu.Items.Add(uncheckSelectedItem);
                contextMenu.Items.Add(separator1);
                contextMenu.Items.Add(checkAllVisibleItem);
                contextMenu.Items.Add(checkAllItem);
                contextMenu.Items.Add(uncheckAllVisibleItem);
                contextMenu.Items.Add(uncheckAllItem);
            }

            return contextMenu;
        }

        /// <summary>
        /// Automatically detects a checkbox column by looking for boolean-type columns,
        /// preferring columns with selection-related names.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to search for checkbox columns.</param>
        /// <returns>The property name of the detected checkbox column, or null if none found.</returns>
        private static string AutoDetectCheckboxColumn(DataGrid dataGrid)
        {
            // Look for boolean columns that might be checkboxes
            var boolColumns = dataGrid.Columns
                .OfType<DataGridBoundColumn>()
                .Where(c => c.Binding is Binding binding &&
                           GetColumnDataType(dataGrid, GetColumnPropertyName(c)) == typeof(bool))
                .ToList();

            // Prefer columns with selection-related names
            var selectionColumn = boolColumns.FirstOrDefault(c =>
            {
                var propName = GetColumnPropertyName(c).ToLower();
                return propName.Contains("select") || propName.Contains("check") || propName.Contains("chosen");
            });

            return selectionColumn != null ? GetColumnPropertyName(selectionColumn) :
                   boolColumns.FirstOrDefault() != null ? GetColumnPropertyName(boolColumns.First()) : null;
        }

        /// <summary>
        /// Gets the data type of a column by querying the ViewModel's available columns metadata.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>The Type of the column's data, or typeof(object) if not found.</returns>
        private static Type GetColumnDataType(DataGrid dataGrid, string propertyName)
        {
            // Get data type from the ViewModel's available columns or column definitions
            var viewModel = dataGrid.DataContext;
            var availableColumnsProperty = viewModel?.GetType().GetProperty("AvailableColumns");

            if (availableColumnsProperty?.GetValue(viewModel) is IEnumerable availableColumns)
            {
                foreach (var column in availableColumns)
                {
                    var propNameProp = column.GetType().GetProperty("PropertyName");
                    var dataTypeProp = column.GetType().GetProperty("DataType");

                    if (propNameProp?.GetValue(column)?.ToString() == propertyName)
                    {
                        return dataTypeProp?.GetValue(column) as Type;
                    }
                }
            }

            return typeof(object);
        }

        /// <summary>
        /// Sets checkbox values for all currently selected rows in the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the selected rows.</param>
        /// <param name="checkboxColumnName">The property name of the checkbox column.</param>
        /// <param name="isChecked">True to check the checkboxes, false to uncheck them.</param>
        private static void BulkSetSelectedCheckboxes(DataGrid dataGrid, string checkboxColumnName, bool isChecked)
        {
            var selectedItems = dataGrid.SelectedItems.Cast<object>();

            if (!selectedItems.Any()) return;

            foreach (var item in selectedItems)
            {
                SetItemCheckboxValue(item, checkboxColumnName, isChecked);
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
        /// Sets checkbox values for rows in the DataGrid, with options to include filtered rows or only visible ones.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to update checkboxes in.</param>
        /// <param name="checkboxColumnName">The property name of the checkbox column.</param>
        /// <param name="isChecked">True to check the checkboxes, false to uncheck them.</param>
        /// <param name="includeFiltered">True to include filtered (hidden) rows, false to only affect visible rows.</param>
        private static void BulkSetCheckboxes(DataGrid dataGrid, string checkboxColumnName, bool isChecked, bool includeFiltered)
        {
            var itemsToUpdate = includeFiltered ?
                dataGrid.ItemsSource?.Cast<object>() :
                GetVisibleItems(dataGrid);

            if (itemsToUpdate == null) return;

            foreach (var item in itemsToUpdate)
            {
                SetItemCheckboxValue(item, checkboxColumnName, isChecked);
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
        /// Gets the collection of items that are currently visible (not filtered out) in the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to get visible items from.</param>
        /// <returns>An enumerable collection of visible items.</returns>
        private static IEnumerable<object> GetVisibleItems(DataGrid dataGrid)
        {
            var collectionView = System.Windows.Data.CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
            return collectionView?.Cast<object>() ?? dataGrid.ItemsSource?.Cast<object>() ?? Enumerable.Empty<object>();
        }

        /// <summary>
        /// Sets a checkbox value for a specific item, handling both DynamicRowData and regular objects.
        /// Attempts to trigger PropertyChanged events to ensure UI updates.
        /// </summary>
        /// <param name="item">The data item to update.</param>
        /// <param name="propertyName">The property name of the checkbox column.</param>
        /// <param name="value">The boolean value to set.</param>
        private static void SetItemCheckboxValue(object item, string propertyName, bool value)
        {
            if (item == null) return;

            // Handle DynamicRowData
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
                        if (item is INotifyPropertyChanged)
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
                if (property != null && property.PropertyType == typeof(bool) && property.CanWrite)
                {
                    property.SetValue(item, value);
                }
            }
        }

        /// <summary>
        /// Attempts to manually trigger a PropertyChanged event on an object using reflection.
        /// This is used as a fallback when the indexer property is not available.
        /// </summary>
        /// <param name="item">The object to trigger PropertyChanged on.</param>
        /// <param name="propertyName">The name of the property that changed.</param>
        private static void TriggerPropertyChanged(object item, string propertyName)
        {
            try
            {
                // Try to find and invoke OnPropertyChanged method
                var onPropertyChangedMethod = item.GetType().GetMethod("OnPropertyChanged",
                    System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public,
                    null,
                    new[] { typeof(string) },
                    null);

                if (onPropertyChangedMethod != null)
                {
                    onPropertyChangedMethod.Invoke(item, new object[] { propertyName });
                }
                else
                {
                    // Try parameterless OnPropertyChanged with CallerMemberName
                    var parameterlessMethod = item.GetType().GetMethod("OnPropertyChanged",
                        System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public,
                        null,
                        new Type[0],
                        null);

                    if (parameterlessMethod != null)
                    {
                        // This won't work perfectly since we can't pass the property name, but it's worth a try
                        parameterlessMethod.Invoke(item, new object[0]);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error triggering PropertyChanged: {ex.Message}");
            }
        }

        /// <summary>
        /// Attempts to call a sync method on the ViewModel to synchronize grid changes with underlying data
        /// </summary>
        /// <param name="dataGrid">The DataGrid whose ViewModel to sync</param>
        private static void SyncWithUnderlyingModel(DataGrid dataGrid)
        {
            try
            {
                var viewModel = dataGrid.DataContext;
                if (viewModel != null)
                {
                    // Try to find and call SyncGridDataToUnderlyingModel method
                    var syncMethod = viewModel.GetType().GetMethod("SyncGridDataToUnderlyingModel");
                    if (syncMethod != null)
                    {
                        syncMethod.Invoke(viewModel, null);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error syncing with underlying model: {ex.Message}");
            }
        }

        #endregion

    }
}
