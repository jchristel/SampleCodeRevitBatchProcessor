using duHastNet.UI.CustomControls.CustomDataGrid;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Collections.Specialized;
using System.ComponentModel;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public class DynamicDataGrid : DataGrid
    {
        public static readonly DependencyProperty ColumnDefinitionsProperty =
            DependencyProperty.Register(
                nameof(ColumnDefinitions),
                typeof(ObservableCollection<DynamicColumnDefinition>),
                typeof(DynamicDataGrid),
                new PropertyMetadata(null, OnColumnDefinitionsChanged));

        public ObservableCollection<DynamicColumnDefinition> ColumnDefinitions
        {
            get => (ObservableCollection<DynamicColumnDefinition>)GetValue(ColumnDefinitionsProperty);
            set => SetValue(ColumnDefinitionsProperty, value);
        }

        public DynamicDataGrid()
        {
            AutoGenerateColumns = false;
            CanUserAddRows = false;
        }

        private static void OnColumnDefinitionsChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is DynamicDataGrid grid)
            {
                grid.HandleColumnDefinitionsChanged(e.OldValue as ObservableCollection<DynamicColumnDefinition>,
                                                  e.NewValue as ObservableCollection<DynamicColumnDefinition>);
            }
        }

        private void HandleColumnDefinitionsChanged(ObservableCollection<DynamicColumnDefinition> oldValue,
                                                  ObservableCollection<DynamicColumnDefinition> newValue)
        {
            // Unsubscribe from old collection
            if (oldValue != null)
            {
                oldValue.CollectionChanged -= OnColumnDefinitionsCollectionChanged;
            }

            // Subscribe to new collection
            if (newValue != null)
            {
                newValue.CollectionChanged += OnColumnDefinitionsCollectionChanged;
            }

            GenerateColumns();
        }

        private void OnColumnDefinitionsCollectionChanged(object sender, NotifyCollectionChangedEventArgs e)
        {
            GenerateColumns();
        }

        private void GenerateColumns()
        {
            if (ColumnDefinitions == null) return;

            Columns.Clear();

            foreach (var columnDef in ColumnDefinitions)
            {
                DataGridColumn column = CreateColumn(columnDef);
                if (column != null)
                {
                    Columns.Add(column);
                }
            }
        }

        private DataGridColumn CreateColumn(DynamicColumnDefinition columnDef)
        {
            DataGridColumn column;

            // Create appropriate column type based on data type
            if (columnDef.DataType == typeof(bool) || columnDef.DataType == typeof(bool?))
            {
                column = new DataGridCheckBoxColumn();
            }
            else
            {
                column = new DataGridTextColumn();
            }

            // Set common properties
            column.Header = columnDef.DisplayName;
            column.Width = new DataGridLength(columnDef.Width);
            column.IsReadOnly = columnDef.IsReadOnly;

            // Create binding
            var binding = new Binding($"[{columnDef.PropertyName}]")
            {
                Mode = columnDef.IsReadOnly ? BindingMode.OneWay : BindingMode.TwoWay,
                UpdateSourceTrigger = UpdateSourceTrigger.PropertyChanged
            };

            // Set binding based on column type
            if (column is DataGridTextColumn textColumn)
            {
                textColumn.Binding = binding;
            }
            else if (column is DataGridCheckBoxColumn checkBoxColumn)
            {
                checkBoxColumn.Binding = binding;
            }

            return column;
        }
    }
}