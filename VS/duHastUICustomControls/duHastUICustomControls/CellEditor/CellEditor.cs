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

using duHastNet.UI.CustomControls.CustomDataGrid;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Media;

namespace duHastNet.UI.CustomControls
{
    [TemplatePart(Name = "PART_DataGrid", Type = typeof(DynamicDataGrid))]
    [TemplatePart(Name = "PART_AddRowButton", Type = typeof(Button))]
    [TemplatePart(Name = "PART_DuplicateRowButton", Type = typeof(Button))]
    [TemplatePart(Name = "PART_DeleteRowButton", Type = typeof(Button))]
    public class CellEditor : Control
    {
        #region Template Parts
        private DynamicDataGrid _dataGrid;

        //public DynamicDataGrid DataGrid
        //{
        //    get { return _dataGrid; }
        //}

        private Button _addRowButton;
        private Button _duplicateRowButton;
        private Button _deleteRowButton;
        #endregion

        #region Dependency Properties

        public static readonly DependencyProperty HeaderRowProperty =
            DependencyProperty.Register(
                nameof(HeaderRow),
                typeof(List<string>),
                typeof(CellEditor),
                new PropertyMetadata(null, OnHeaderRowChanged));

        public static readonly DependencyProperty DataRowsProperty =
            DependencyProperty.Register(
                nameof(DataRows),
                typeof(List<List<object>>),
                typeof(CellEditor),
                new PropertyMetadata(null, OnDataRowsChanged));

        public static readonly DependencyProperty AllowAddRowProperty =
            DependencyProperty.Register(
                nameof(AllowAddRow),
                typeof(bool),
                typeof(CellEditor),
                new PropertyMetadata(true));

        public static readonly DependencyProperty AllowDuplicateRowProperty =
            DependencyProperty.Register(
                nameof(AllowDuplicateRow),
                typeof(bool),
                typeof(CellEditor),
                new PropertyMetadata(true));

        public static readonly DependencyProperty AllowDeleteRowProperty =
            DependencyProperty.Register(
                nameof(AllowDeleteRow),
                typeof(bool),
                typeof(CellEditor),
                new PropertyMetadata(true));

        public static readonly DependencyProperty ReadOnlyColumnsProperty =
            DependencyProperty.Register(
                nameof(ReadOnlyColumns),
                typeof(List<string>),
                typeof(CellEditor),
                new PropertyMetadata(null, OnReadOnlyColumnsChanged));

        #endregion

        #region Properties

        public List<string> HeaderRow
        {
            get => (List<string>)GetValue(HeaderRowProperty);
            set => SetValue(HeaderRowProperty, value);
        }

        public List<List<object>> DataRows
        {
            get => (List<List<object>>)GetValue(DataRowsProperty);
            set => SetValue(DataRowsProperty, value);
        }

        public bool AllowAddRow
        {
            get => (bool)GetValue(AllowAddRowProperty);
            set => SetValue(AllowAddRowProperty, value);
        }

        public bool AllowDuplicateRow
        {
            get => (bool)GetValue(AllowDuplicateRowProperty);
            set => SetValue(AllowDuplicateRowProperty, value);
        }

        public bool AllowDeleteRow
        {
            get => (bool)GetValue(AllowDeleteRowProperty);
            set => SetValue(AllowDeleteRowProperty, value);
        }

        public List<string> ReadOnlyColumns
        {
            get => (List<string>)GetValue(ReadOnlyColumnsProperty);
            set => SetValue(ReadOnlyColumnsProperty, value);
        }

        #endregion

        #region Events

        public static readonly RoutedEvent DataChangedEvent =
            EventManager.RegisterRoutedEvent(
                nameof(DataChanged),
                RoutingStrategy.Bubble,
                typeof(RoutedEventHandler),
                typeof(CellEditor));

        public event RoutedEventHandler DataChanged
        {
            add { AddHandler(DataChangedEvent, value); }
            remove { RemoveHandler(DataChangedEvent, value); }
        }

        #endregion

        #region Internal Data Management

        private ViewModels.CellEditorViewModel _viewModel;

        #endregion

        static CellEditor()
        {
            DefaultStyleKeyProperty.OverrideMetadata(typeof(CellEditor),
                new FrameworkPropertyMetadata(typeof(CellEditor)));
        }

        public CellEditor()
        {
            _viewModel = new ViewModels.CellEditorViewModel();
            // Don't set DataContext here - let it inherit from parent
        }

        public override void OnApplyTemplate()
        {
            base.OnApplyTemplate();

            // Unhook old event handlers
            UnhookEventHandlers();

            // Get template parts
            _dataGrid = GetTemplateChild("PART_DataGrid") as DynamicDataGrid;
            _addRowButton = GetTemplateChild("PART_AddRowButton") as Button;
            _duplicateRowButton = GetTemplateChild("PART_DuplicateRowButton") as Button;
            _deleteRowButton = GetTemplateChild("PART_DeleteRowButton") as Button;

            // Set up DataGrid bindings programmatically
            if (_dataGrid != null)
            {
                // Set the DataGrid's DataContext to our ViewModel
                _dataGrid.DataContext = _viewModel;

                // Create bindings
                var columnDefBinding = new Binding("ColumnDefinitions") { Source = _viewModel };
                var itemsSourceBinding = new Binding("Data") { Source = _viewModel };

                _dataGrid.SetBinding(DynamicDataGrid.ColumnDefinitionsProperty, columnDefBinding);
                _dataGrid.SetBinding(DynamicDataGrid.ItemsSourceProperty, itemsSourceBinding);

                // Set up context menu
                SetupContextMenu();
            }

            // Hook up new event handlers
            HookEventHandlers();

            // Update the data grid with current data
            UpdateDataGrid();
        }

        private void SetupContextMenu()
        {
            if (_dataGrid?.ContextMenu == null) return;

            // Get menu items by name
            var addRowMenuItem = _dataGrid.ContextMenu.FindName("PART_AddRowMenuItem") as MenuItem;
            var duplicateRowMenuItem = _dataGrid.ContextMenu.FindName("PART_DuplicateRowMenuItem") as MenuItem;
            var deleteRowMenuItem = _dataGrid.ContextMenu.FindName("PART_DeleteRowMenuItem") as MenuItem;

            // Set up Add Row menu item
            if (addRowMenuItem != null)
            {
                addRowMenuItem.Command = _viewModel.AddRowCommand;
                var addRowVisibilityBinding = new Binding("AllowAddRow")
                {
                    Source = this,
                    Converter = new Converters.BooleanToVisibilityConverter()
                };
                addRowMenuItem.SetBinding(MenuItem.VisibilityProperty, addRowVisibilityBinding);
            }

            // Set up Duplicate Row menu item
            if (duplicateRowMenuItem != null)
            {
                duplicateRowMenuItem.Command = _viewModel.DuplicateRowCommand;
                var selectedItemBinding = new Binding("SelectedItem") { Source = _dataGrid };
                duplicateRowMenuItem.SetBinding(MenuItem.CommandParameterProperty, selectedItemBinding);
                var duplicateRowVisibilityBinding = new Binding("AllowDuplicateRow")
                {
                    Source = this,
                    Converter = new Converters.BooleanToVisibilityConverter()
                };
                duplicateRowMenuItem.SetBinding(MenuItem.VisibilityProperty, duplicateRowVisibilityBinding);
            }

            // Set up Delete Row menu item
            if (deleteRowMenuItem != null)
            {
                deleteRowMenuItem.Command = _viewModel.DeleteSelectedCommand;
                var deleteRowVisibilityBinding = new Binding("AllowDeleteRow")
                {
                    Source = this,
                    Converter = new Converters.BooleanToVisibilityConverter()
                };
                deleteRowMenuItem.SetBinding(MenuItem.VisibilityProperty, deleteRowVisibilityBinding);
            }
        }

        private void HookEventHandlers()
        {
            if (_addRowButton != null)
                _addRowButton.Click += OnAddRowClick;

            if (_duplicateRowButton != null)
                _duplicateRowButton.Click += OnDuplicateRowClick;

            if (_deleteRowButton != null)
                _deleteRowButton.Click += OnDeleteRowClick;

            if (_dataGrid != null)
            {
                _dataGrid.CellEditEnding += OnCellEditEnding;
                _dataGrid.Sorting += OnDataGridSorting;
                _dataGrid.ColumnDisplayIndexChanged += OnColumnDisplayIndexChanged;
                _dataGrid.ColumnReordered += OnColumnReordered;
            }
        }

        private void UnhookEventHandlers()
        {
            if (_addRowButton != null)
                _addRowButton.Click -= OnAddRowClick;

            if (_duplicateRowButton != null)
                _duplicateRowButton.Click -= OnDuplicateRowClick;

            if (_deleteRowButton != null)
                _deleteRowButton.Click -= OnDeleteRowClick;

            if (_dataGrid != null)
            {
                _dataGrid.CellEditEnding -= OnCellEditEnding;
                _dataGrid.Sorting -= OnDataGridSorting;
                _dataGrid.ColumnDisplayIndexChanged -= OnColumnDisplayIndexChanged;
                _dataGrid.ColumnReordered -= OnColumnReordered;
            }
        }

        #region Property Change Handlers

        private static void OnHeaderRowChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is CellEditor editor)
            {
                editor.UpdateDataGrid();
            }
        }

        private static void OnDataRowsChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is CellEditor editor)
            {
                editor.UpdateDataGrid();
            }
        }

        private static void OnReadOnlyColumnsChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is CellEditor editor)
            {
                editor.UpdateColumnReadOnlyStates();
            }
        }

        #endregion

        #region Event Handlers

        private void OnAddRowClick(object sender, RoutedEventArgs e)
        {
            _viewModel.AddRow();
            RaiseDataChangedEvent();
        }

        private void OnDuplicateRowClick(object sender, RoutedEventArgs e)
        {
            if (_dataGrid?.SelectedItem is CellEditorRowData selectedRow)
            {
                _viewModel.DuplicateRow(selectedRow);
                RaiseDataChangedEvent();
            }
        }

        private void OnDeleteRowClick(object sender, RoutedEventArgs e)
        {
            if (_dataGrid?.SelectedItem is CellEditorRowData selectedRow)
            {
                _viewModel.RemoveRow(selectedRow);
                RaiseDataChangedEvent();
            }
        }

        private void OnCellEditEnding(object sender, DataGridCellEditEndingEventArgs e)
        {
            // Delay the data changed event to ensure the edit is committed
            Dispatcher.BeginInvoke(new Action(() => RaiseDataChangedEvent()));
        }

        private void OnDataGridSorting(object sender, DataGridSortingEventArgs e)
        {
            // Capture current column widths to prevent unexpected growth
            var columnWidths = _dataGrid.Columns.ToDictionary(
                col => col,
                col => col.ActualWidth
            );

            // Capture current horizontal scroll position
            var scrollViewer = GetScrollViewer(_dataGrid);
            var horizontalOffset = scrollViewer?.HorizontalOffset ?? 0;

            // Let the default sorting happen, then restore positions and raise data changed event
            Dispatcher.BeginInvoke(new Action(() =>
            {
                // Restore column widths to prevent unexpected growth
                foreach (var kvp in columnWidths)
                {
                    if (kvp.Value > 0)
                    {
                        kvp.Key.Width = new DataGridLength(kvp.Value);
                    }
                }

                // Restore horizontal scroll position
                if (scrollViewer != null)
                {
                    scrollViewer.ScrollToHorizontalOffset(horizontalOffset);
                }

                RaiseDataChangedEvent();
            }));
        }

        private ScrollViewer GetScrollViewer(DataGrid dataGrid)
        {
            if (dataGrid == null) return null;

            try
            {
                // Navigate the visual tree to find the ScrollViewer
                var border = VisualTreeHelper.GetChild(dataGrid, 0) as Decorator;
                var scrollViewer = border?.Child as ScrollViewer;
                return scrollViewer;
            }
            catch
            {
                // If visual tree navigation fails, use the existing helper method
                return DataGridColumnHeaderBehavior.FindVisualChild<ScrollViewer>(dataGrid);
            }
        }

        private void OnColumnDisplayIndexChanged(object sender, DataGridColumnEventArgs e)
        {
            // Column order changed - raise data changed event
            Dispatcher.BeginInvoke(new Action(() => RaiseDataChangedEvent()));
        }

        private void OnColumnReordered(object sender, DataGridColumnEventArgs e)
        {
            // Column was reordered - raise data changed event
            Dispatcher.BeginInvoke(new Action(() => RaiseDataChangedEvent()));
        }

        #endregion

        #region Data Management

        private void UpdateDataGrid()
        {
            if (_viewModel == null || HeaderRow == null) return;

            _viewModel.LoadData(HeaderRow, DataRows ?? new List<List<object>>());
            UpdateColumnReadOnlyStates();

            // Refresh the DataGrid bindings if it's already set up
            if (_dataGrid != null && _dataGrid.DataContext == _viewModel)
            {
                // The bindings should automatically refresh due to INotifyPropertyChanged
                // But we can force a refresh if needed
                _dataGrid.GetBindingExpression(DynamicDataGrid.ColumnDefinitionsProperty)?.UpdateTarget();
                _dataGrid.GetBindingExpression(DynamicDataGrid.ItemsSourceProperty)?.UpdateTarget();
            }
        }

        private void UpdateColumnReadOnlyStates()
        {
            if (_viewModel?.ColumnDefinitions == null || ReadOnlyColumns == null) return;

            foreach (var column in _viewModel.ColumnDefinitions)
            {
                column.IsReadOnly = ReadOnlyColumns.Contains(column.PropertyName);
            }
        }

        private void RaiseDataChangedEvent()
        {
            RaiseEvent(new RoutedEventArgs(DataChangedEvent));
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Gets debug information about the current column order - for troubleshooting
        /// </summary>
        /// <returns>Debug information as a string</returns>
        public string GetColumnOrderDebugInfo()
        {
            if (_dataGrid == null)
                return "DataGrid is null";

            var debugInfo = new System.Text.StringBuilder();
            debugInfo.AppendLine("=== DEBUG COLUMN ORDER ===");
            debugInfo.AppendLine($"Total columns: {_dataGrid.Columns.Count}");

            var orderedColumns = _dataGrid.Columns.OrderBy(c => c.DisplayIndex).ToList();

            foreach (var column in orderedColumns)
            {
                var binding = (column as DataGridBoundColumn)?.Binding as Binding;
                debugInfo.AppendLine($"DisplayIndex: {column.DisplayIndex}, Header: {column.Header}, Binding: {binding?.Path?.Path}");
            }

            if (_viewModel?.ColumnDefinitions != null)
            {
                debugInfo.AppendLine("\n=== COLUMN DEFINITIONS ===");
                for (int i = 0; i < _viewModel.ColumnDefinitions.Count; i++)
                {
                    var colDef = _viewModel.ColumnDefinitions[i];
                    debugInfo.AppendLine($"[{i}] PropertyName: {colDef.PropertyName}, DisplayName: {colDef.DisplayName}");
                }
            }

            debugInfo.AppendLine("\n=== CURRENT vs ORDERED COMPARISON ===");
            debugInfo.AppendLine("Current order (storage): " + string.Join(", ", _dataGrid.Columns.Select(c => c.Header)));
            debugInfo.AppendLine("Display order (visual):  " + string.Join(", ", _dataGrid.Columns.OrderBy(c => c.DisplayIndex).Select(c => c.Header)));

            return debugInfo.ToString();
        }


        /// <summary>
        /// Gets the current data as it appears in the grid (respecting current column order, sorting, etc.)
        /// </summary>
        /// <returns>Tuple containing header row and data rows as they currently appear</returns>
        public (List<string> HeaderRow, List<List<object>> DataRows) GetCurrentData()
        {
            if (_viewModel?.ColumnDefinitions == null || _dataGrid == null)
                return (new List<string>(), new List<List<object>>());

            // Get current column order from the actual DataGrid by matching with ColumnDefinitions
            var currentColumns = new List<string>();
            var propertyNames = new List<string>();

            var orderedColumns = _dataGrid.Columns.OrderBy(c => c.DisplayIndex).ToList();

            foreach (var column in orderedColumns)
            {
                // Find the corresponding column definition by matching the header
                var columnDef = _viewModel.ColumnDefinitions
                    .FirstOrDefault(cd => cd.DisplayName == column.Header?.ToString());

                if (columnDef != null)
                {
                    currentColumns.Add(columnDef.DisplayName);
                    propertyNames.Add(columnDef.PropertyName);
                }
            }

            // Get the current view (which may be sorted)
            var currentView = _dataGrid.Items.Cast<CellEditorRowData>().ToList();

            // Build data rows in current display order
            var dataRows = new List<List<object>>();
            foreach (var row in currentView)
            {
                var dataRow = new List<object>();
                foreach (var propertyName in propertyNames)
                {
                    if (row.Values.ContainsKey(propertyName))
                    {
                        dataRow.Add(row.Values[propertyName]);
                    }
                    else
                    {
                        dataRow.Add(null);
                    }
                }
                dataRows.Add(dataRow);
            }

            return (currentColumns, dataRows);
        }

        /// <summary>
        /// Gets the original column order data (ignoring current display state)
        /// </summary>
        public (List<string> HeaderRow, List<List<object>> DataRows) GetOriginalData()
        {
            if (_viewModel?.ColumnDefinitions == null)
                return (new List<string>(), new List<List<object>>());

            var headers = _viewModel.ColumnDefinitions.Select(cd => cd.DisplayName).ToList();
            var dataRows = new List<List<object>>();

            foreach (var row in _viewModel.Data)
            {
                var dataRow = new List<object>();
                foreach (var columnDef in _viewModel.ColumnDefinitions)
                {
                    dataRow.Add(row.Values.ContainsKey(columnDef.PropertyName)
                        ? row.Values[columnDef.PropertyName]
                        : null);
                }
                dataRows.Add(dataRow);
            }

            return (headers, dataRows);
        }

        /// <summary>
        /// Refreshes the control with new data
        /// </summary>
        public void RefreshData(List<string> headerRow, List<List<object>> dataRows)
        {
            HeaderRow = headerRow;
            DataRows = dataRows;
        }

        /// <summary>
        /// Gets all available columns (including those not currently displayed)
        /// </summary>
        public List<string> GetAvailableColumns()
        {
            return _viewModel?.AvailableColumns?.Select(ac => ac.DisplayName).ToList() ?? new List<string>();
        }

        /// <summary>
        /// Gets currently displayed column names
        /// </summary>
        public List<string> GetCurrentColumns()
        {
            return _viewModel?.ColumnDefinitions?.Select(cd => cd.DisplayName).ToList() ?? new List<string>();
        }

        /// <summary>
        /// Gets columns that are available to add (not currently displayed)
        /// </summary>
        public List<string> GetColumnsAvailableToAdd()
        {
            if (_viewModel?.AvailableColumns == null || _viewModel?.ColumnDefinitions == null)
                return new List<string>();

            var currentColumns = _viewModel.ColumnDefinitions.Select(cd => cd.DisplayName).ToHashSet();
            return _viewModel.AvailableColumns
                .Where(ac => !currentColumns.Contains(ac.DisplayName))
                .Select(ac => ac.DisplayName)
                .ToList();
        }

        /// <summary>
        /// Adds a column that was previously removed
        /// </summary>
        public void AddColumn(string columnDisplayName)
        {
            _viewModel?.AddSelectedColumn(columnDisplayName);
        }

        /// <summary>
        /// Removes a column from display (data is preserved for later restoration)
        /// </summary>
        public void RemoveColumn(string columnDisplayName)
        {
            // Find the column definition to get the property name
            var columnDef = _viewModel?.ColumnDefinitions?
                .FirstOrDefault(cd => cd.DisplayName == columnDisplayName);

            if (columnDef != null)
            {
                _viewModel?.RemoveColumn(columnDef.PropertyName);
            }
        }

        /// <summary>
        /// Clears all data while preserving column structure
        /// </summary>
        public void ClearData()
        {
            _viewModel?.ClearData();
            RaiseDataChangedEvent();
        }

        #endregion
    }
}