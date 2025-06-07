using System;
using System.Collections;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.Linq;
using System.Reflection;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Input;
using System.Windows.Media;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static class DataGridColumnHeaderBehavior
    {
        public static readonly DependencyProperty EnableColumnManagementProperty =
            DependencyProperty.RegisterAttached(
                "EnableColumnManagement",
                typeof(bool),
                typeof(DataGridColumnHeaderBehavior),
                new PropertyMetadata(false, OnEnableColumnManagementChanged));

        public static bool GetEnableColumnManagement(DependencyObject obj)
        {
            return (bool)obj.GetValue(EnableColumnManagementProperty);
        }

        public static void SetEnableColumnManagement(DependencyObject obj, bool value)
        {
            obj.SetValue(EnableColumnManagementProperty, value);
        }

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
                }
                else
                {
                    dataGrid.Loaded -= DataGrid_Loaded;
                    dataGrid.ColumnDisplayIndexChanged -= DataGrid_ColumnDisplayIndexChanged;
                }
            }
        }

        private static void DataGrid_Loaded(object sender, RoutedEventArgs e)
        {
            if (sender is DataGrid dataGrid)
            {
                RefreshContextMenus(dataGrid);
            }
        }

        private static void DataGrid_ColumnDisplayIndexChanged(object sender, DataGridColumnEventArgs e)
        {
            if (sender is DataGrid dataGrid)
            {
                RefreshContextMenus(dataGrid);
            }
        }

        private static void RefreshContextMenus(DataGrid dataGrid)
        {
            // Use Dispatcher to ensure this runs after column changes are complete
            dataGrid.Dispatcher.BeginInvoke(new Action(() => AttachContextMenus(dataGrid)),
                System.Windows.Threading.DispatcherPriority.Background);
        }

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
            contextMenu.Items.Add(new Separator());

            // Remove Column menu item
            var removeItem = new MenuItem { Header = "Remove Column" };
            removeItem.Command = GetCommandFromViewModel(viewModel, "RemoveColumnCommand");
            removeItem.CommandParameter = propertyName;
            contextMenu.Items.Add(removeItem);

            // Separator
            contextMenu.Items.Add(new Separator());

            // Add available columns submenu
            var addSubmenu = new MenuItem { Header = "Add Column" };
            PopulateAddColumnSubmenu(addSubmenu, viewModel);
            contextMenu.Items.Add(addSubmenu);

            return contextMenu;
        }

        private static Style CreateHeaderStyleWithContextMenu(ContextMenu contextMenu)
        {
            var style = new Style(typeof(DataGridColumnHeader));

            // Try to get the filterable style
            Style filterableStyle = null;
            try
            {
                var resourceDict = new ResourceDictionary();
                resourceDict.Source = new Uri("/duHastUICustomControls;component/CustomDataGrid/DynamicDataGridStyle.xaml", UriKind.Relative);
                filterableStyle = resourceDict["FilterableColumnHeaderStyle"] as Style;

                if (filterableStyle != null)
                {
                    style.BasedOn = filterableStyle;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error: {ex.Message}");
            }

            style.Setters.Add(new Setter(FrameworkElement.ContextMenuProperty, contextMenu));
            return style;
        }

        private static void UpdateFilterIcon(DataGrid dataGrid, DataGridColumn column, string propertyName)
        {
            var hasFilter = HasActiveFilter(dataGrid, propertyName);

            dataGrid.Dispatcher.BeginInvoke(new Action(() =>
            {
                // Get the current style or create a new one
                var currentStyle = column.HeaderStyle;
                var newStyle = currentStyle != null
                    ? new Style(typeof(DataGridColumnHeader), currentStyle)
                    : new Style(typeof(DataGridColumnHeader));

                // Remove any existing background setters
                var backgroundSetters = newStyle.Setters
                    .OfType<Setter>()
                    .Where(s => s.Property == Control.BackgroundProperty)
                    .ToList();

                foreach (var setter in backgroundSetters)
                {
                    newStyle.Setters.Remove(setter);
                }

                // Add the appropriate background
                if (hasFilter)
                {
                    newStyle.Setters.Add(new Setter(Control.BackgroundProperty, Brushes.Red));
                }
                else if (column.IsReadOnly)
                {
                    newStyle.Setters.Add(new Setter(Control.BackgroundProperty, new SolidColorBrush(Color.FromRgb(245, 245, 245))));
                }
                else
                {
                    newStyle.Setters.Add(new Setter(Control.BackgroundProperty, Brushes.Transparent));
                }

                // Apply the style
                column.HeaderStyle = newStyle;

                // Force a visual refresh
                dataGrid.UpdateLayout();

            }), System.Windows.Threading.DispatcherPriority.Loaded);
        }

        private static bool HasActiveFilter(DataGrid dataGrid, string propertyName)
        {
            var filterKey = $"TextFilter_{propertyName}";
            return dataGrid.Resources.Contains(filterKey) &&
                   !string.IsNullOrWhiteSpace((string)dataGrid.Resources[filterKey]);
        }

        private static ICommand GetCommandFromViewModel(object viewModel, string commandName)
        {
            var property = viewModel?.GetType().GetProperty(commandName);
            return property?.GetValue(viewModel) as ICommand;
        }

        private static string GetColumnPropertyName(DataGridColumn column)
        {
            if (column is DataGridBoundColumn boundColumn && boundColumn.Binding is Binding binding)
            {
                return binding.Path.Path.Trim('[', ']');
            }
            return column.Header?.ToString();
        }

        private static void PopulateAddColumnSubmenu(MenuItem addSubmenu, object viewModel)
        {
            // Clear existing items first
            addSubmenu.Items.Clear();

            var availableColumnsProperty = viewModel?.GetType().GetProperty("AvailableColumnsToAdd");
            if (availableColumnsProperty?.GetValue(viewModel) is IEnumerable availableColumns)
            {
                foreach (var column in availableColumns)
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

            // Show message if no columns available
            if (addSubmenu.Items.Count == 0)
            {
                var noItemsMessage = new MenuItem { Header = "(No columns available)", IsEnabled = false };
                addSubmenu.Items.Add(noItemsMessage);
            }
        }

        private static void PopulateFilterSubmenu(MenuItem filterSubmenu, DataGrid dataGrid, string propertyName)
        {
            // Clear existing items
            filterSubmenu.Items.Clear();

            // Clear filter option
            var clearFilterItem = new MenuItem { Header = "Clear Filter" };
            clearFilterItem.Click += (s, e) => ClearColumnFilter(dataGrid, propertyName);
            filterSubmenu.Items.Add(clearFilterItem);

            filterSubmenu.Items.Add(new Separator());

            // Filter by text input
            var filterByTextItem = new MenuItem { Header = "Filter by Text..." };
            filterByTextItem.Click += (s, e) => ShowFilterTextDialog(dataGrid, propertyName);
            filterSubmenu.Items.Add(filterByTextItem);

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

        private static void ShowFilterTextDialog(DataGrid dataGrid, string propertyName)
        {
            var currentFilter = GetCurrentFilterText(dataGrid, propertyName);

            // Create a simple input dialog
            var dialog = new Window
            {
                Title = $"Filter {propertyName}",
                Width = 400,
                Height = 200,
                WindowStartupLocation = WindowStartupLocation.CenterOwner,
                Owner = Window.GetWindow(dataGrid),
                ResizeMode = ResizeMode.NoResize
            };

            var stackPanel = new StackPanel { Margin = new Thickness(10) };

            // Instructions
            var instructions = new TextBlock
            {
                Text = "Enter filter values separated by spaces.\nChoose how multiple values should be combined:",
                TextWrapping = TextWrapping.Wrap,
                Margin = new Thickness(0, 0, 0, 10)
            };
            stackPanel.Children.Add(instructions);

            // Radio buttons for OR/AND logic
            var orRadio = new RadioButton
            {
                Content = "OR (show rows that match ANY value)",
                IsChecked = true,
                Margin = new Thickness(0, 0, 0, 5)
            };
            stackPanel.Children.Add(orRadio);

            var andRadio = new RadioButton
            {
                Content = "AND (show rows that contain ALL values)",
                Margin = new Thickness(0, 0, 0, 10)
            };
            stackPanel.Children.Add(andRadio);

            // Text input
            var textBox = new TextBox
            {
                Text = currentFilter,
                Margin = new Thickness(0, 0, 0, 10),
                Height = 25
            };
            stackPanel.Children.Add(textBox);

            // Buttons
            var buttonPanel = new StackPanel
            {
                Orientation = Orientation.Horizontal,
                HorizontalAlignment = HorizontalAlignment.Right
            };

            var okButton = new Button
            {
                Content = "Apply Filter",
                Width = 80,
                Margin = new Thickness(0, 0, 10, 0),
                IsDefault = true
            };

            var cancelButton = new Button
            {
                Content = "Cancel",
                Width = 80,
                IsCancel = true
            };

            buttonPanel.Children.Add(okButton);
            buttonPanel.Children.Add(cancelButton);
            stackPanel.Children.Add(buttonPanel);

            dialog.Content = stackPanel;

            // Event handlers
            okButton.Click += (s, e) =>
            {
                var filterText = textBox.Text?.Trim();
                var useAndLogic = andRadio.IsChecked == true;
                ApplyTextFilter(dataGrid, propertyName, filterText, useAndLogic);
                dialog.DialogResult = true;
            };

            textBox.KeyDown += (s, e) =>
            {
                if (e.Key == Key.Enter)
                {
                    okButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
                }
            };

            // Focus the textbox
            textBox.Focus();
            textBox.SelectAll();

            dialog.ShowDialog();
        }

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

        private static string GetCurrentFilterText(DataGrid dataGrid, string propertyName)
        {
            var filterKey = $"TextFilter_{propertyName}";
            return dataGrid.Resources.Contains(filterKey) ? (string)dataGrid.Resources[filterKey] : null;
        }

        private static void ApplyAllColumnFilters(DataGrid dataGrid)
        {
            if (dataGrid.ItemsSource == null) return;

            // Get the collection view
            var collectionView = System.Windows.Data.CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
            if (collectionView == null) return;

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
                            return false; // Hide row if it fails any column filter
                        }
                    }
                }

                return true; // Show row if it passes all filters
            };

            // Force refresh
            collectionView.Refresh();
        }

        private static void ClearColumnFilter(DataGrid dataGrid, string propertyName)
        {
            var filterKey = $"TextFilter_{propertyName}";
            var logicKey = $"TextFilterLogic_{propertyName}";

            dataGrid.Resources.Remove(filterKey);
            dataGrid.Resources.Remove(logicKey);

            // Update filter icon for this column
            var column = dataGrid.Columns.FirstOrDefault(c => GetColumnPropertyName(c) == propertyName);
            if (column != null)
            {
                UpdateFilterIcon(dataGrid, column, propertyName);
            }

            // Apply remaining filters
            var hasAnyFilters = dataGrid.Resources.Keys.OfType<string>()
                .Any(k => k.StartsWith("TextFilter_"));

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
    }
}
