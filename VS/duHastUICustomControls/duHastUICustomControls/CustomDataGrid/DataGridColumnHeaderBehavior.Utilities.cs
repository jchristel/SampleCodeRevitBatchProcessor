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
using System.Windows.Data;
using System.Windows.Input;
using System.Windows.Media;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static partial class DataGridColumnHeaderBehavior
    {
        #region Utility Methods

        /// <summary>
        /// Retrieves a command from the ViewModel using reflection.
        /// </summary>
        /// <param name="viewModel">The ViewModel object to get the command from.</param>
        /// <param name="commandName">The name of the command property.</param>
        /// <returns>The ICommand instance, or null if not found.</returns>
        private static ICommand GetCommandFromViewModel(object viewModel, string commandName)
        {
            var property = viewModel?.GetType().GetProperty(commandName);
            return property?.GetValue(viewModel) as ICommand;
        }

        /// <summary>
        /// Extracts the property name from a DataGrid column, handling both bound columns and header-only columns.
        /// </summary>
        /// <param name="column">The DataGridColumn to get the property name from.</param>
        /// <returns>The property name associated with the column.</returns>
        private static string GetColumnPropertyName(DataGridColumn column)
        {
            if (column is DataGridBoundColumn boundColumn && boundColumn.Binding is Binding binding)
            {
                return binding.Path.Path.Trim('[', ']');
            }
            return column.Header?.ToString();
        }

        /// <summary>
        /// Helper method to find a visual child of a specific type.
        /// </summary>
        /// <typeparam name="T">The type of child to find.</typeparam>
        /// <param name="parent">The parent element to search in.</param>
        /// <returns>The first child of the specified type, or null if not found.</returns>
        private static T FindVisualChild<T>(DependencyObject parent) where T : DependencyObject
        {
            if (parent == null) return null;

            for (int i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
            {
                var child = VisualTreeHelper.GetChild(parent, i);
                if (child is T foundChild)
                    return foundChild;

                var descendant = FindVisualChild<T>(child);
                if (descendant != null)
                    return descendant;
            }
            return null;
        }

        /// <summary>
        /// Retrieves a property value from an object, handling both DynamicRowData and regular objects.
        /// </summary>
        /// <param name="item">The object to get the value from.</param>
        /// <param name="propertyName">The name of the property to retrieve.</param>
        /// <returns>The property value, or null if not found.</returns>
        private static object GetItemValue(object item, string propertyName)
        {
            if (item == null) return null;

            // Handle DynamicRowData
            if (item.GetType().GetProperty("Values") != null)
            {
                var valuesDict = item.GetType().GetProperty("Values").GetValue(item) as System.Collections.IDictionary;
                if (valuesDict != null && valuesDict.Contains(propertyName))
                {
                    return valuesDict[propertyName];
                }
            }
            else
            {
                // Handle regular objects
                var property = item.GetType().GetProperty(propertyName);
                if (property != null)
                {
                    return property.GetValue(item);
                }
            }

            return null;
        }

        /// <summary>
        /// Loads the resource dictionary containing styles for the DataGrid components.
        /// </summary>
        /// <returns>A ResourceDictionary loaded from the component's XAML resource file.</returns>
        private static ResourceDictionary LoadResourceDictionary()
        {
            var resourceDict = new ResourceDictionary();
            resourceDict.Source = new Uri("pack://application:,,,/duHastUICustomControls;component/CustomDataGrid/DynamicDataGridStyle.xaml", UriKind.Absolute);
            return resourceDict;
        }

        /// <summary>
        /// Clears all filters from all columns in the DataGrid and refreshes the display.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to clear all filters from.</param>
        private static void ClearAllColumnFilters(DataGrid dataGrid)
        {
            if (dataGrid == null) return;

            // Get all filter resource keys
            var filterKeys = new List<string>();

            foreach (var key in dataGrid.Resources.Keys.OfType<string>())
            {
                if (key.StartsWith("TextFilter_") ||
                    key.StartsWith("TextFilterLogic_") ||
                    key.StartsWith("BooleanFilter_") ||
                    key.StartsWith("NumericFilter_") ||
                    key.StartsWith("DateTimeFilter_") ||
                    key.StartsWith("DropDownFilter_"))
                {
                    filterKeys.Add(key);
                }
            }

            // Remove all filter resources
            foreach (var key in filterKeys)
            {
                dataGrid.Resources.Remove(key);
            }

            // Update all column header icons
            foreach (var column in dataGrid.Columns)
            {
                var propertyName = GetColumnPropertyName(column);
                UpdateFilterIcon(dataGrid, column, propertyName);
            }

            // Clear the collection view filter
            var collectionView = System.Windows.Data.CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
            if (collectionView != null)
            {
                collectionView.Filter = null;

                // Force refresh on dispatcher to ensure UI updates
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

            System.Diagnostics.Debug.WriteLine("All column filters cleared");
        }

        /// <summary>
        /// Checks if any filters are currently active on any column in the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to check for active filters.</param>
        /// <returns>True if any filters are active, false if no filters are applied.</returns>
        private static bool HasAnyActiveFilters(DataGrid dataGrid)
        {
            if (dataGrid?.Resources == null) return false;

            // Check for any filter-related resources
            return dataGrid.Resources.Keys.OfType<string>().Any(key =>
                key.StartsWith("TextFilter_") ||
                key.StartsWith("BooleanFilter_ShowTrue_") ||
                key.StartsWith("BooleanFilter_ShowFalse_") ||
                key.StartsWith("NumericFilter_Operation_") ||
                key.StartsWith("DateTimeFilter_Operation_") ||
                key.StartsWith("DropDownFilter_SelectedValue_"));
        }

        #endregion
    }
}
