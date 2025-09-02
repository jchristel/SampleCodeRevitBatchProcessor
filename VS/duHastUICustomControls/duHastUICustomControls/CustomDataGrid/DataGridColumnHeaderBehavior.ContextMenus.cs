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
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Media;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static partial class DataGridColumnHeaderBehavior
    {
        #region Context Menu Management

        /// <summary>
        /// Schedules a refresh of all column context menus using the dispatcher to ensure proper timing.
        /// </summary>
        /// <param name="dataGrid">The DataGrid whose context menus need to be refreshed.</param>
        private static void RefreshContextMenus(DataGrid dataGrid)
        {
            // Use Dispatcher to ensure this runs after column changes are complete
            dataGrid.Dispatcher.BeginInvoke(new Action(() => AttachContextMenus(dataGrid)),
                System.Windows.Threading.DispatcherPriority.Background);
        }

        /// <summary>
        /// Attaches context menus to all column headers and updates their styling and filter indicators.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to attach context menus to.</param>
        private static void AttachContextMenus(DataGrid dataGrid)
        {
            foreach (var column in dataGrid.Columns)
            {
                // Always create a fresh context menu
                var contextMenu = CreateColumnContextMenu(dataGrid, column);
                var propertyName = GetColumnPropertyName(column);

                // Create or update header style
                if (column.HeaderStyle == null)
                {
                    column.HeaderStyle = CreateHeaderStyleWithContextMenu(contextMenu);
                }
                else
                {
                    // Update existing style
                    var newStyle = new Style(typeof(DataGridColumnHeader), column.HeaderStyle);

                    // Remove any existing context menu setter
                    var existingContextMenuSetter = newStyle.Setters
                        .OfType<Setter>()
                        .FirstOrDefault(s => s.Property == FrameworkElement.ContextMenuProperty);
                    if (existingContextMenuSetter != null)
                    {
                        newStyle.Setters.Remove(existingContextMenuSetter);
                    }

                    // Add the new context menu
                    newStyle.Setters.Add(new Setter(FrameworkElement.ContextMenuProperty, contextMenu));
                    column.HeaderStyle = newStyle;
                }

                // Update filter icon visibility
                UpdateFilterIcon(dataGrid, column, propertyName);
            }
        }

        /// <summary>
        /// Creates a context menu for a specific column header with filtering, add/remove column options.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column.</param>
        /// <param name="column">The column to create a context menu for.</param>
        private static ContextMenu CreateColumnContextMenu(DataGrid dataGrid, DataGridColumn column)
        {
            var contextMenu = new ContextMenu();
            var viewModel = dataGrid.DataContext;
            var propertyName = GetColumnPropertyName(column);

            // Filter submenu
            var filterSubmenu = new MenuItem { Header = "Filter" };
            PopulateFilterSubmenu(filterSubmenu, dataGrid, propertyName);

            // Refresh the submenu contents every time it opens
            filterSubmenu.SubmenuOpened += (s, e) =>
            {
                PopulateFilterSubmenu(filterSubmenu, dataGrid, propertyName);
            };

            contextMenu.Items.Add(filterSubmenu);

            //Clear All Filters menu item
            var clearAllFiltersItem = new MenuItem { Header = "Clear All Filters" };
            clearAllFiltersItem.Click += (s, e) => ClearAllColumnFilters(dataGrid);

            // Enable/disable based on whether any filters are active
            clearAllFiltersItem.IsEnabled = HasAnyActiveFilters(dataGrid);

            contextMenu.Items.Add(clearAllFiltersItem);

            // Separator
            var separator1 = new Separator();
            contextMenu.Items.Add(separator1);

            // Remove Column menu item - disable if it's the last column
            var removeItem = new MenuItem { Header = "Remove Column" };
            removeItem.Command = GetCommandFromViewModel(viewModel, "RemoveColumnCommand");
            removeItem.CommandParameter = propertyName;

            // Check if this is the last visible column
            if (dataGrid.Columns.Count <= 1)
            {
                removeItem.IsEnabled = false;
                removeItem.Header = "Remove Column (Cannot remove last column)";
            }

            contextMenu.Items.Add(removeItem);


            // Separator
            var separator2 = new Separator();
            contextMenu.Items.Add(separator2);

            // Resize Column submenu
            var resizeSubmenu = new MenuItem { Header = "Resize Column" };

            // Auto-fit to content
            var autoFitItem = new MenuItem { Header = "Auto-fit to Content" };
            autoFitItem.Click += (s, e) => AutoFitColumnToContent(dataGrid, column);
            resizeSubmenu.Items.Add(autoFitItem);

            // Auto-fit to header
            var autoFitHeaderItem = new MenuItem { Header = "Auto-fit to Header" };
            autoFitHeaderItem.Click += (s, e) => AutoFitColumnToHeader(dataGrid, column);
            resizeSubmenu.Items.Add(autoFitHeaderItem);

            contextMenu.Items.Add(resizeSubmenu);


            // Separator
            var separator3 = new Separator();
            contextMenu.Items.Add(separator3);

            // Add available columns submenu
            var addSubmenu = new MenuItem { Header = "Add Column" };
            PopulateAddColumnSubmenu(addSubmenu, viewModel);
            contextMenu.Items.Add(addSubmenu);

            // Apply styling when context menu opens
            contextMenu.Opened += (s, e) =>
            {
                // Update the Clear All Filters enabled state when menu opens
                clearAllFiltersItem.IsEnabled = HasAnyActiveFilters(dataGrid);

                if (contextMenu.Style == null)
                {
                    try
                    {
                        // Use helper to load resource dictionary
                        var resourceDict = LoadResourceDictionary();

                        var contextMenuStyle = resourceDict["ColumnHeaderContextMenuStyle"] as Style;
                        var menuItemStyle = resourceDict["ColumnHeaderMenuItemStyle"] as Style;
                        var separatorStyle = resourceDict["ColumnHeaderSeparatorStyle"] as Style;

                        if (contextMenuStyle != null)
                        {
                            contextMenu.Style = contextMenuStyle;
                        }

                        if (menuItemStyle != null)
                        {
                            filterSubmenu.Style = menuItemStyle;
                            clearAllFiltersItem.Style = menuItemStyle;
                            resizeSubmenu.Style = menuItemStyle;
                            removeItem.Style = menuItemStyle;
                            addSubmenu.Style = menuItemStyle;

                            // Apply to submenu items as well
                            ApplyStyleToSubItems(filterSubmenu, menuItemStyle);
                            ApplyStyleToSubItems(resizeSubmenu, menuItemStyle);
                            ApplyStyleToSubItems(addSubmenu, menuItemStyle);
                        }

                        if (separatorStyle != null)
                        {
                            separator1.Style = separatorStyle;
                            separator2.Style = separatorStyle;
                            separator3.Style = separatorStyle;
                        }
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Error loading column context menu styles: {ex.Message}");
                    }
                }
            };

            return contextMenu;
        }


        // <summary>
        /// Auto-fits a column width to its content.
        /// </summary>
        private static void AutoFitColumnToContent(DataGrid dataGrid, DataGridColumn column)
        {
            if (column == null) return;

            try
            {
                // Force the column to auto-size to content
                column.Width = DataGridLength.Auto;

                // Force layout update to calculate the auto width
                dataGrid.UpdateLayout();

                // Capture the auto-calculated width and set it as fixed
                var autoWidth = column.ActualWidth;
                if (autoWidth > 0)
                {
                    column.Width = new DataGridLength(autoWidth);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error auto-fitting column to content: {ex.Message}");
            }
        }

        /// <summary>
        /// Auto-fits a column width to its header text.
        /// </summary>
        private static void AutoFitColumnToHeader(DataGrid dataGrid, DataGridColumn column)
        {
            if (column == null) return;

            try
            {
                // Force the column to auto-size to header
                column.Width = DataGridLength.SizeToHeader;

                // Force layout update to calculate the auto width
                dataGrid.UpdateLayout();

                // Capture the auto-calculated width and set it as fixed
                var autoWidth = column.ActualWidth;
                if (autoWidth > 0)
                {
                    column.Width = new DataGridLength(autoWidth);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error auto-fitting column to header: {ex.Message}");
            }
        }

        
        /// <summary>
        /// Recursively applies a style to all menu items within a parent menu item, including nested submenus.
        /// </summary>
        /// <param name="parentItem">The parent menu item to apply styles to.</param>
        /// <param name="menuItemStyle">The style to apply to all menu items.</param>
        private static void ApplyStyleToSubItems(MenuItem parentItem, Style menuItemStyle)
        {
            foreach (var subItem in parentItem.Items.OfType<MenuItem>())
            {
                subItem.Style = menuItemStyle;
                ApplyStyleToSubItems(subItem, menuItemStyle); // Recursive for nested items
            }
        }

        /// <summary>
        /// Populates the "Add Column" submenu with available columns that can be added to the DataGrid.
        /// Limits to maximum 10 visible items with scrolling for larger lists.
        /// </summary>
        /// <param name="addSubmenu">The submenu to populate with available columns.</param>
        /// <param name="viewModel">The ViewModel containing the AvailableColumnsToAdd property.</param>
        private static void PopulateAddColumnSubmenu(MenuItem addSubmenu, object viewModel)
        {
            // Clear existing items first
            addSubmenu.Items.Clear();

            var availableColumnsProperty = viewModel?.GetType().GetProperty("AvailableColumnsToAdd");
            if (availableColumnsProperty?.GetValue(viewModel) is IEnumerable availableColumns)
            {
                var columnList = availableColumns.Cast<object>()
                    .OrderBy(column => column.GetType().GetProperty("DisplayName")?.GetValue(column)?.ToString() ?? "")
                    .ToList();

                // Add all columns as normal menu items
                foreach (var column in columnList)
                {
                    var propertyName = column.GetType().GetProperty("PropertyName")?.GetValue(column)?.ToString();
                    var displayName = column.GetType().GetProperty("DisplayName")?.GetValue(column)?.ToString();

                    if (!string.IsNullOrEmpty(propertyName))
                    {
                        var menuItem = new MenuItem { Header = displayName };
                        menuItem.Command = GetCommandFromViewModel(viewModel, "AddSelectedColumnCommand");
                        menuItem.CommandParameter = propertyName;
                        addSubmenu.Items.Add(menuItem);
                    }
                }

                // If more than 10 items, set MaxHeight to force scrolling
                if (columnList.Count > 10)
                {
                    // Set MaxHeight to show approximately 10 items (each item is roughly 25-30px)
                    addSubmenu.MaxHeight = 280;

                    // Apply scrolling template when the submenu opens
                    addSubmenu.SubmenuOpened += (s, e) =>
                    {
                        ApplyScrollTemplate(addSubmenu);
                    };
                }
            }

            // Show message if no columns available
            if (addSubmenu.Items.Count == 0)
            {
                var noItemsMessage = new MenuItem { Header = "(No columns available)", IsEnabled = false };
                addSubmenu.Items.Add(noItemsMessage);
            }
        }

        /// <summary>
        /// Applies a scroll template to a MenuItem when it has too many items.
        /// </summary>
        /// <param name="menuItem">The MenuItem to apply scrolling to.</param>
        private static void ApplyScrollTemplate(MenuItem menuItem)
        {
            // This will automatically enable scrolling when MaxHeight is exceeded
            // WPF's MenuItem control has built-in support for scrolling when MaxHeight is set

            // Find the popup and set scrolling properties
            menuItem.Loaded += (s, e) =>
            {
                var popup = FindVisualChild<System.Windows.Controls.Primitives.Popup>(menuItem);
                if (popup != null)
                {
                    popup.Loaded += (ps, pe) =>
                    {
                        var scrollViewer = FindVisualChild<ScrollViewer>(popup.Child);
                        if (scrollViewer != null)
                        {
                            scrollViewer.VerticalScrollBarVisibility = ScrollBarVisibility.Auto;
                            scrollViewer.HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled;
                        }
                    };
                }
            };
        }


        #endregion

        #region Header Styling

        /// <summary>
        /// Creates a header style that includes the filterable base style and attaches a context menu.
        /// </summary>
        private static Style CreateHeaderStyleWithContextMenu(ContextMenu contextMenu)
        {
            var style = new Style(typeof(DataGridColumnHeader));

            try
            {
                var resourceDict = LoadResourceDictionary();
                var filterableStyle = resourceDict["FilterableColumnHeaderStyle"] as Style;

                if (filterableStyle != null)
                {
                    style.BasedOn = filterableStyle;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"❌ Error loading header style: {ex.Message}");
            }

            style.Setters.Add(new Setter(FrameworkElement.ContextMenuProperty, contextMenu));
            return style;
        }

        // <summary>
        /// Updates the visual appearance of a column header based on its state (filtered, read-only, or normal).
        /// Applies appropriate styles from the resource dictionary while preserving the context menu.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column.</param>
        /// <param name="column">The column to update the header for.</param>
        /// <param name="propertyName">The property name associated with the column.</param>
        private static void UpdateFilterIcon(DataGrid dataGrid, DataGridColumn column, string propertyName)
        {
            var hasFilter = HasActiveFilter(dataGrid, propertyName);

            dataGrid.Dispatcher.BeginInvoke(new Action(() =>
            {
                try
                {
                    // Load styles from resource dictionary using helper method
                    var resourceDict = LoadResourceDictionary();

                    Style targetStyle = null;

                    // Determine which style to use
                    if (hasFilter)
                    {
                        targetStyle = resourceDict["FilteredColumnHeaderStyle"] as Style;
                    }
                    else if (column.IsReadOnly)
                    {
                        targetStyle = resourceDict["ReadOnlyColumnHeaderStyle"] as Style;
                    }
                    else
                    {
                        targetStyle = resourceDict["FilterableColumnHeaderStyle"] as Style;
                    }

                    if (targetStyle != null)
                    {
                        // Create a new style based on the target style
                        var newStyle = new Style(typeof(DataGridColumnHeader), targetStyle);

                        // Preserve any existing context menu from the current style
                        var existingContextMenu = GetContextMenuFromStyle(column.HeaderStyle);
                        if (existingContextMenu != null)
                        {
                            newStyle.Setters.Add(new Setter(FrameworkElement.ContextMenuProperty, existingContextMenu));
                        }

                        column.HeaderStyle = newStyle;
                    }
                    else
                    {
                        System.Diagnostics.Debug.WriteLine($"❌ Could not find header style for {propertyName}");
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"❌ Error applying header style: {ex.Message}");

                }

                // Force a visual refresh
                dataGrid.UpdateLayout();

            }), System.Windows.Threading.DispatcherPriority.Loaded);
        }

        /// <summary>
        /// Extracts the context menu from a column header style's setters.
        /// </summary>
        /// <param name="style">The style to extract the context menu from.</param>
        /// <returns>The ContextMenu if found, null otherwise.</returns>
        private static ContextMenu GetContextMenuFromStyle(Style style)
        {
            if (style == null) return null;

            var contextMenuSetter = style.Setters
                .OfType<Setter>()
                .FirstOrDefault(s => s.Property == FrameworkElement.ContextMenuProperty);

            return contextMenuSetter?.Value as ContextMenu;
        }

        #endregion
    }
}