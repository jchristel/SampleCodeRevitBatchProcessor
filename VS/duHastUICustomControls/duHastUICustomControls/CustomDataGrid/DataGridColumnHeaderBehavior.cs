using System;
using System.Collections;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.ComponentModel;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Input;
using System.Windows.Media;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    /// <summary>
    /// Provides attached behavior for DataGrid column header management, including context menus,
    /// filtering capabilities, and bulk selection operations.
    /// </summary>
    public static class DataGridColumnHeaderBehavior
    {
        #region Dependency Properties

        /// <summary>
        /// Dependency property for enabling column management features (context menus, filtering, etc.)
        /// </summary>
        public static readonly DependencyProperty EnableColumnManagementProperty =
            DependencyProperty.RegisterAttached(
                "EnableColumnManagement",
                typeof(bool),
                typeof(DataGridColumnHeaderBehavior),
                new PropertyMetadata(false, OnEnableColumnManagementChanged));

        /// <summary>
        /// Dependency property for enabling bulk selection operations on rows
        /// </summary>
        public static readonly DependencyProperty EnableBulkSelectionProperty =
        DependencyProperty.RegisterAttached(
                "EnableBulkSelection",
                typeof(bool),
                typeof(DataGridColumnHeaderBehavior),
                new PropertyMetadata(false));

        /// <summary>
        /// Dependency property for specifying which column contains the checkboxes for bulk selection
        /// </summary>
        public static readonly DependencyProperty BulkSelectionColumnProperty =
            DependencyProperty.RegisterAttached(
                "BulkSelectionColumn",
                typeof(string),
                typeof(DataGridColumnHeaderBehavior),
                new PropertyMetadata(null));

        #endregion

        #region Dependency Property Accessors

        /// <summary>
        /// Gets the value of the EnableColumnManagement attached property for the specified object.
        /// </summary>
        /// <param name="obj">The object from which to read the property value.</param>
        /// <returns>True if column management is enabled, false otherwise.</returns>
        public static bool GetEnableColumnManagement(DependencyObject obj)
        {
            return (bool)obj.GetValue(EnableColumnManagementProperty);
        }

        /// <summary>
        /// Sets the value of the EnableColumnManagement attached property for the specified object.
        /// </summary>
        /// <param name="obj">The object on which to set the property value.</param>
        /// <param name="value">True to enable column management features, false to disable.</param>
        public static void SetEnableColumnManagement(DependencyObject obj, bool value)
        {
            obj.SetValue(EnableColumnManagementProperty, value);
        }

        /// <summary>
        /// Gets the value of the EnableBulkSelection attached property for the specified object.
        /// </summary>
        /// <param name="obj">The object from which to read the property value.</param>
        /// <returns>True if bulk selection is enabled, false otherwise.</returns>
        public static bool GetEnableBulkSelection(DependencyObject obj)
        {
            return (bool)obj.GetValue(EnableBulkSelectionProperty);
        }

        /// <summary>
        /// Sets the value of the EnableBulkSelection attached property for the specified object.
        /// </summary>
        /// <param name="obj">The object on which to set the property value.</param>
        /// <param name="value">True to enable bulk selection operations, false to disable.</param>
        public static void SetEnableBulkSelection(DependencyObject obj, bool value)
        {
            obj.SetValue(EnableBulkSelectionProperty, value);
        }

        /// <summary>
        /// Gets the name of the column used for bulk selection checkboxes.
        /// </summary>
        /// <param name="obj">The object from which to read the property value.</param>
        /// <returns>The property name of the column containing checkboxes for bulk selection.</returns>
        public static string GetBulkSelectionColumn(DependencyObject obj)
        {
            return (string)obj.GetValue(BulkSelectionColumnProperty);
        }

        /// <summary>
        /// Sets the name of the column used for bulk selection checkboxes.
        /// </summary>
        /// <param name="obj">The object on which to set the property value.</param>
        /// <param name="value">The property name of the column containing checkboxes for bulk selection.</param>
        public static void SetBulkSelectionColumn(DependencyObject obj, string value)
        {
            obj.SetValue(BulkSelectionColumnProperty, value);
        }

        #endregion

        #region Event Handlers

        /// <summary>
        /// Handles changes to the EnableColumnManagement property and sets up or tears down the behavior.
        /// </summary>
        /// <param name="d">The DataGrid object that the property was changed on.</param>
        /// <param name="e">The event data containing the old and new values.</param>
        private static void OnEnableColumnManagementChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is DataGrid dataGrid)
            {
                if ((bool)e.NewValue)
                {
                    dataGrid.Loaded += DataGrid_Loaded;
                    dataGrid.ColumnDisplayIndexChanged += DataGrid_ColumnDisplayIndexChanged;

                    // Subscribe to column collection changes
                    ((INotifyCollectionChanged)dataGrid.Columns).CollectionChanged += (s, args) => RefreshContextMenus(dataGrid);

                    // Add row context menu if bulk selection is enabled
                    dataGrid.Loaded += (s, args) => SetupRowContextMenus(dataGrid);
                }
                else
                {
                    dataGrid.Loaded -= DataGrid_Loaded;
                    dataGrid.ColumnDisplayIndexChanged -= DataGrid_ColumnDisplayIndexChanged;
                }
            }
        }

        /// <summary>
        /// Handles the DataGrid Loaded event to initialize context menus and behaviors.
        /// </summary>
        /// <param name="sender">The DataGrid that was loaded.</param>
        /// <param name="e">The event arguments.</param>
        private static void DataGrid_Loaded(object sender, RoutedEventArgs e)
        {
            if (sender is DataGrid dataGrid)
            {
                RefreshContextMenus(dataGrid);
            }
        }

        /// <summary>
        /// Handles changes to column display order and refreshes context menus accordingly.
        /// </summary>
        /// <param name="sender">The DataGrid where the column display index changed.</param>
        /// <param name="e">The event arguments containing column information.</param>
        private static void DataGrid_ColumnDisplayIndexChanged(object sender, DataGridColumnEventArgs e)
        {
            if (sender is DataGrid dataGrid)
            {
                RefreshContextMenus(dataGrid);
            }
        }

        #endregion

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
        /// Prevents removal of the last remaining column to maintain grid functionality.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column.</param>
        /// <param name="column">The column to create a context menu for.</param>
        /// <returns>A configured ContextMenu with styling applied.</returns>
        private static ContextMenu CreateColumnContextMenu(DataGrid dataGrid, DataGridColumn column)
        {
            var contextMenu = new ContextMenu();
            var viewModel = dataGrid.DataContext;
            var propertyName = GetColumnPropertyName(column);

            // Filter submenu
            var filterSubmenu = new MenuItem { Header = "Filter" };
            PopulateFilterSubmenu(filterSubmenu, dataGrid, propertyName);
            contextMenu.Items.Add(filterSubmenu);

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

            // Add available columns submenu
            var addSubmenu = new MenuItem { Header = "Add Column" };
            PopulateAddColumnSubmenu(addSubmenu, viewModel);
            contextMenu.Items.Add(addSubmenu);

            // Apply styling when context menu opens
            contextMenu.Opened += (s, e) =>
            {
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
                            removeItem.Style = menuItemStyle;
                            addSubmenu.Style = menuItemStyle;

                            // Apply to submenu items as well
                            ApplyStyleToSubItems(filterSubmenu, menuItemStyle);
                            ApplyStyleToSubItems(addSubmenu, menuItemStyle);
                        }

                        if (separatorStyle != null)
                        {
                            separator1.Style = separatorStyle;
                            separator2.Style = separatorStyle;
                        }
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"❌ Error loading column context menu styles: {ex.Message}");
                    }
                }
            };

            return contextMenu;
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

        #endregion

        #region Header Styling

        /// <summary>
        /// Creates a header style that includes the filterable base style and attaches a context menu.
        /// </summary>
        /// <param name="contextMenu">The context menu to attach to the header.</param>
        /// <returns>A Style object configured for DataGridColumnHeader with context menu.</returns>
        private static Style CreateHeaderStyleWithContextMenu(ContextMenu contextMenu)
        {
            var style = new Style(typeof(DataGridColumnHeader));

            // Try to get the filterable style
            Style filterableStyle = null;
            try
            {
                // Use helper to load resource dictionary
                var resourceDict = LoadResourceDictionary();
                filterableStyle = resourceDict["FilterableColumnHeaderStyle"] as Style;

                if (filterableStyle != null)
                {
                    style.BasedOn = filterableStyle;
                }
                else
                {
                    System.Diagnostics.Debug.WriteLine("❌ FilterableColumnHeaderStyle not found in resource dictionary");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"❌ Error loading header style: {ex.Message}");
            }

            style.Setters.Add(new Setter(FrameworkElement.ContextMenuProperty, contextMenu));
            return style;
        }

        /// <summary>
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
        /// Boolean columns get checkbox options, numeric columns get numeric operations, 
        /// DateTime columns get date operations, other columns get text input options.
        /// </summary>
        /// <param name="filterSubmenu">The filter submenu to populate.</param>
        /// <param name="dataGrid">The DataGrid containing the column.</param>
        /// <param name="propertyName">The property name of the column being filtered.</param>
        private static void PopulateFilterSubmenu(MenuItem filterSubmenu, DataGrid dataGrid, string propertyName)
        {
            // Clear existing items
            filterSubmenu.Items.Clear();

            // Check column data type
            var columnType = GetColumnDataType(dataGrid, propertyName);
            var isBooleanColumn = columnType == typeof(bool) || columnType == typeof(bool?);
            var isNumericColumn = IsNumericType(columnType);
            var isDateTimeColumn = IsDateTimeType(columnType);

            // Clear filter option
            var clearFilterItem = new MenuItem { Header = "Clear Filter" };
            clearFilterItem.Click += (s, e) => ClearColumnFilter(dataGrid, propertyName);
            filterSubmenu.Items.Add(clearFilterItem);

            filterSubmenu.Items.Add(new Separator());

            if (isBooleanColumn)
            {
                // Boolean-specific filter options
                var filterByBooleanItem = new MenuItem { Header = "Filter by Value..." };
                filterByBooleanItem.Click += (s, e) => ShowFilterBooleanDialog(dataGrid, propertyName);
                filterSubmenu.Items.Add(filterByBooleanItem);
            }
            else if (isNumericColumn)
            {
                // Numeric-specific filter options
                var filterByNumericItem = new MenuItem { Header = "Filter by Number..." };
                filterByNumericItem.Click += (s, e) => ShowFilterNumericDialog(dataGrid, propertyName);
                filterSubmenu.Items.Add(filterByNumericItem);
            }
            else if (isDateTimeColumn)
            {
                // DateTime-specific filter options
                var filterByDateTimeItem = new MenuItem { Header = "Filter by Date..." };
                filterByDateTimeItem.Click += (s, e) => ShowFilterDateTimeDialog(dataGrid, propertyName);
                filterSubmenu.Items.Add(filterByDateTimeItem);
            }
            else
            {
                // Text-based filter for other column types
                var filterByTextItem = new MenuItem { Header = "Filter by Text..." };
                filterByTextItem.Click += (s, e) => ShowFilterTextDialog(dataGrid, propertyName);
                filterSubmenu.Items.Add(filterByTextItem);
            }

            // Show current filter if any
            var currentFilter = GetCurrentFilterText(dataGrid, propertyName);
            if (!string.IsNullOrEmpty(currentFilter))
            {
                filterSubmenu.Items.Add(new Separator());
                var currentFilterItem = new MenuItem
                {
                    Header = $"Current: {currentFilter}",
                    IsEnabled = false
                };
                filterSubmenu.Items.Add(currentFilterItem);
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
                          k.StartsWith("NumericFilter_") || k.StartsWith("DateTimeFilter_"));

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


        #region boolean filter 

        /// <summary>
        /// Displays a dialog for filtering boolean columns with checkbox options.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column to filter.</param>
        /// <param name="propertyName">The property name of the boolean column to filter.</param>
        private static void ShowFilterBooleanDialog(DataGrid dataGrid, string propertyName)
        {
            // Get current boolean filter state
            var (showTrue, showFalse) = GetCurrentBooleanFilter(dataGrid, propertyName);

            var dialog = new FilterBooleanDialog(propertyName, showTrue, showFalse)
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
                    ApplyBooleanFilter(dataGrid, propertyName, dialog.ShowTrue, dialog.ShowFalse);
                }
            }
        }

        /// <summary>
        /// Gets the current boolean filter state for a column.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to check.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A tuple indicating whether true and false values should be shown.</returns>
        private static (bool? showTrue, bool? showFalse) GetCurrentBooleanFilter(DataGrid dataGrid, string propertyName)
        {
            var showTrueKey = $"BooleanFilter_ShowTrue_{propertyName}";
            var showFalseKey = $"BooleanFilter_ShowFalse_{propertyName}";

            bool? showTrue = dataGrid.Resources.Contains(showTrueKey) ? (bool?)dataGrid.Resources[showTrueKey] : null;
            bool? showFalse = dataGrid.Resources.Contains(showFalseKey) ? (bool?)dataGrid.Resources[showFalseKey] : null;

            return (showTrue, showFalse);
        }

        /// <summary>
        /// Applies a boolean filter to a column and refreshes the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to apply the filter to.</param>
        /// <param name="propertyName">The property name of the boolean column.</param>
        /// <param name="showTrue">Whether to show true values.</param>
        /// <param name="showFalse">Whether to show false values.</param>
        private static void ApplyBooleanFilter(DataGrid dataGrid, string propertyName, bool? showTrue, bool? showFalse)
        {
            SetColumnBooleanFilter(dataGrid, propertyName, showTrue, showFalse);
            ApplyAllColumnFilters(dataGrid);

            // Update filter icon for this column
            var column = dataGrid.Columns.FirstOrDefault(c => GetColumnPropertyName(c) == propertyName);
            if (column != null)
            {
                UpdateFilterIcon(dataGrid, column, propertyName);
            }
        }

        /// <summary>
        /// Stores boolean filter information for a column in the DataGrid's resource collection.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to store the filter in.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <param name="showTrue">Whether to show true values.</param>
        /// <param name="showFalse">Whether to show false values.</param>
        private static void SetColumnBooleanFilter(DataGrid dataGrid, string propertyName, bool? showTrue, bool? showFalse)
        {
            var showTrueKey = $"BooleanFilter_ShowTrue_{propertyName}";
            var showFalseKey = $"BooleanFilter_ShowFalse_{propertyName}";

            // Remove existing filters
            dataGrid.Resources.Remove(showTrueKey);
            dataGrid.Resources.Remove(showFalseKey);

            // Add new filters if specified
            if (showTrue.HasValue)
            {
                dataGrid.Resources[showTrueKey] = showTrue.Value;
            }

            if (showFalse.HasValue)
            {
                dataGrid.Resources[showFalseKey] = showFalse.Value;
            }
        }


        /// <summary>
        /// Tests whether an item passes a boolean filter.
        /// </summary>
        /// <param name="item">The item to test.</param>
        /// <param name="dataGrid">The DataGrid containing filter settings.</param>
        /// <param name="propertyName">The property name of the boolean column.</param>
        /// <returns>True if the item passes the filter, false otherwise.</returns>
        private static bool PassesBooleanFilter(object item, DataGrid dataGrid, string propertyName)
        {
            var (showTrue, showFalse) = GetCurrentBooleanFilter(dataGrid, propertyName);

            // If no boolean filter is set, show all
            if (!showTrue.HasValue && !showFalse.HasValue)
                return true;

            var itemValue = GetItemValue(item, propertyName);
            if (itemValue is bool boolValue)
            {
                if (boolValue && showTrue == true) return true;
                if (!boolValue && showFalse == true) return true;
                return false;
            }

            // Handle nullable bools or non-bool values
            return true;
        }


        #endregion boolean filter

        #region text filter

        /// <summary>
        /// Displays a dialog for entering filter text and logic (AND/OR) for a specific column.
        /// </summary>
        /// <param name="dataGrid">The DataGrid containing the column to filter.</param>
        /// <param name="propertyName">The property name of the column to filter.</param>
        private static void ShowFilterTextDialog(DataGrid dataGrid, string propertyName)
        {
            var currentFilter = GetCurrentFilterText(dataGrid, propertyName);

            var dialog = new FilterTextDialog(propertyName, currentFilter)
            {
                Owner = Window.GetWindow(dataGrid)
            };

            if (dialog.ShowDialog() == true)
            {
                ApplyTextFilter(dataGrid, propertyName, dialog.FilterText, dialog.UseAndLogic);
            }
        }

        /// <summary>
        /// Applies a text filter to a column and refreshes the DataGrid to show filtered results.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to apply the filter to.</param>
        /// <param name="propertyName">The property name of the column to filter.</param>
        /// <param name="filterText">The text to filter by.</param>
        /// <param name="useAndLogic">True to use AND logic for multiple terms, false for OR logic.</param>
        private static void ApplyTextFilter(DataGrid dataGrid, string propertyName, string filterText, bool useAndLogic)
        {
            // Store filter information
            SetColumnTextFilter(dataGrid, propertyName, filterText, useAndLogic);

            // Apply the combined filter
            ApplyAllColumnFilters(dataGrid);

            // Update filter icon for this column
            var column = dataGrid.Columns.FirstOrDefault(c => GetColumnPropertyName(c) == propertyName);
            if (column != null)
            {
                UpdateFilterIcon(dataGrid, column, propertyName);
            }
        }

        /// <summary>
        /// Stores filter information for a column in the DataGrid's resource collection.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to store the filter information in.</param>
        /// <param name="propertyName">The property name of the column being filtered.</param>
        /// <param name="filterText">The filter text to store.</param>
        /// <param name="useAndLogic">The logic type (AND/OR) to store.</param>
        private static void SetColumnTextFilter(DataGrid dataGrid, string propertyName, string filterText, bool useAndLogic)
        {
            var filterKey = $"TextFilter_{propertyName}";
            var logicKey = $"TextFilterLogic_{propertyName}";

            if (string.IsNullOrWhiteSpace(filterText))
            {
                dataGrid.Resources.Remove(filterKey);
                dataGrid.Resources.Remove(logicKey);
            }
            else
            {
                dataGrid.Resources[filterKey] = filterText;
                dataGrid.Resources[logicKey] = useAndLogic;
            }
        }

        /// <summary>
        /// Retrieves the current filter text for a specific column, supporting all filter types.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to get the filter from.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>The current filter text, or null if no filter is applied.</returns>
        private static string GetCurrentFilterText(DataGrid dataGrid, string propertyName)
        {
            // Check for text filter first
            var textFilterKey = $"TextFilter_{propertyName}";
            if (dataGrid.Resources.Contains(textFilterKey))
            {
                return (string)dataGrid.Resources[textFilterKey];
            }

            // Check for numeric filter
            var numericFilter = GetCurrentNumericFilterText(dataGrid, propertyName);
            if (!string.IsNullOrEmpty(numericFilter))
            {
                return numericFilter;
            }

            // Check for DateTime filter
            var dateTimeFilter = GetCurrentDateTimeFilterText(dataGrid, propertyName);
            if (!string.IsNullOrEmpty(dateTimeFilter))
            {
                return dateTimeFilter;
            }

            // Check for boolean filter
            var (showTrue, showFalse) = GetCurrentBooleanFilter(dataGrid, propertyName);
            if (showTrue.HasValue || showFalse.HasValue)
            {
                if (showTrue == true && showFalse == true)
                    return "Show All";
                else if (showTrue == true)
                    return "Show True";
                else if (showFalse == true)
                    return "Show False";
                else
                    return "Show None";
            }

            return null;
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

                // Check all active text filters
                foreach (var resourceKey in dataGrid.Resources.Keys.OfType<string>()
                    .Where(k => k.StartsWith("TextFilter_")))
                {
                    var propertyName = resourceKey.Substring("TextFilter_".Length);
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
                    var propertyName = resourceKey.Substring("BooleanFilter_ShowTrue_".Length);
                    if (!PassesBooleanFilter(item, dataGrid, propertyName))
                    {
                        return false;
                    }
                }

                // Check all active numeric filters
                foreach (var resourceKey in dataGrid.Resources.Keys.OfType<string>()
                    .Where(k => k.StartsWith("NumericFilter_Operation_")))
                {
                    var propertyName = resourceKey.Substring("NumericFilter_Operation_".Length);
                    if (!PassesNumericFilter(item, dataGrid, propertyName))
                    {
                        return false;
                    }
                }

                // Check all active DateTime filters
                foreach (var resourceKey in dataGrid.Resources.Keys.OfType<string>()
                    .Where(k => k.StartsWith("DateTimeFilter_Operation_")))
                {
                    var propertyName = resourceKey.Substring("DateTimeFilter_Operation_".Length);
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

        /// <summary>
        /// Tests whether an item value passes a text filter using the specified logic (AND/OR).
        /// </summary>
        /// <param name="itemValue">The value from the item to test.</param>
        /// <param name="filterText">The filter text containing one or more search terms separated by spaces.</param>
        /// <param name="useAndLogic">True to require ALL terms to match (AND), false to require ANY term to match (OR).</param>
        /// <returns>True if the item passes the filter, false otherwise.</returns>
        private static bool PassesTextFilter(string itemValue, string filterText, bool useAndLogic)
        {
            if (string.IsNullOrWhiteSpace(filterText)) return true;

            // Split filter text by spaces to get individual filter terms
            var filterTerms = filterText.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);

            if (useAndLogic)
            {
                // AND logic: item must contain ALL terms
                return filterTerms.All(term =>
                    itemValue.IndexOf(term, StringComparison.OrdinalIgnoreCase) >= 0);
            }
            else
            {
                // OR logic: item must contain ANY term
                return filterTerms.Any(term =>
                    itemValue.IndexOf(term, StringComparison.OrdinalIgnoreCase) >= 0);
            }
        }
        #endregion text filter

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

        #endregion

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
        /// Creates a normal submenu without scrolling for 10 or fewer items.
        /// </summary>
        /// <param name="addSubmenu">The submenu to populate.</param>
        /// <param name="columnList">The list of available columns.</param>
        /// <param name="viewModel">The ViewModel containing commands.</param>
        private static void CreateNormalSubmenu(MenuItem addSubmenu, List<object> columnList, object viewModel)
        {
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
        }


        /// <summary>
        /// Creates a scrollable submenu container for more than 10 items.
        /// </summary>
        /// <param name="addSubmenu">The submenu to populate.</param>
        /// <param name="columnList">The list of available columns.</param>
        /// <param name="viewModel">The ViewModel containing commands.</param>
        private static void CreateScrollableSubmenu(MenuItem addSubmenu, List<object> columnList, object viewModel)
        {
            // Create a single MenuItem that contains a UserControl with scrolling
            var scrollableMenuItem = new MenuItem();

            // Create the scrollable content
            var scrollViewer = new ScrollViewer
            {
                MaxHeight = 300, // Approximately 10 items at ~30px each
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled
            };

            var stackPanel = new StackPanel();

            foreach (var column in columnList)
            {
                var propertyName = column.GetType().GetProperty("PropertyName")?.GetValue(column)?.ToString();
                var displayName = column.GetType().GetProperty("DisplayName")?.GetValue(column)?.ToString();

                if (!string.IsNullOrEmpty(propertyName))
                {
                    // Create a button that looks like a menu item
                    var button = new Button
                    {
                        Content = displayName,
                        HorizontalAlignment = HorizontalAlignment.Stretch,
                        HorizontalContentAlignment = HorizontalAlignment.Left,
                        Padding = new Thickness(10, 5, 10, 5),
                        Margin = new Thickness(0),
                        BorderThickness = new Thickness(0),
                        Background = Brushes.Transparent,
                        Command = GetCommandFromViewModel(viewModel, "AddSelectedColumnCommand"),
                        CommandParameter = propertyName
                    };

                    // Add hover effects
                    button.MouseEnter += (s, e) => button.Background = SystemColors.HighlightBrush;
                    button.MouseLeave += (s, e) => button.Background = Brushes.Transparent;

                    // Close the context menu when clicked
                    button.Click += (s, e) =>
                    {
                        // Find and close the context menu
                        var contextMenu = FindParentContextMenu(button);
                        if (contextMenu != null)
                        {
                            contextMenu.IsOpen = false;
                        }
                    };

                    stackPanel.Children.Add(button);
                }
            }

            scrollViewer.Content = stackPanel;
            scrollableMenuItem.Header = scrollViewer;

            // Disable the menu item selection behavior since we're using buttons inside
            scrollableMenuItem.IsEnabled = true;
            scrollableMenuItem.StaysOpenOnClick = true;

            addSubmenu.Items.Add(scrollableMenuItem);
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
        /// Finds the parent ContextMenu of a given element.
        /// </summary>
        /// <param name="element">The element to search from.</param>
        /// <returns>The parent ContextMenu, or null if not found.</returns>
        private static ContextMenu FindParentContextMenu(DependencyObject element)
        {
            var parent = VisualTreeHelper.GetParent(element);
            while (parent != null)
            {
                if (parent is ContextMenu contextMenu)
                    return contextMenu;
                parent = VisualTreeHelper.GetParent(parent);
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

        #endregion

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