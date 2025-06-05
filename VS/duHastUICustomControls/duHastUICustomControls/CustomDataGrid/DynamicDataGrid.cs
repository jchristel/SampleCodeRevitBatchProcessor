using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Collections.Specialized;
using System.ComponentModel;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Media;

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

        public static readonly DependencyProperty ReadOnlyColumnStyleProperty =
            DependencyProperty.Register(
                nameof(ReadOnlyColumnStyle),
                typeof(Style),
                typeof(DynamicDataGrid),
                new PropertyMetadata(null));

        public static readonly DependencyProperty ReadOnlyHeaderStyleProperty =
            DependencyProperty.Register(
                nameof(ReadOnlyHeaderStyle),
                typeof(Style),
                typeof(DynamicDataGrid),
                new PropertyMetadata(null));

        public ObservableCollection<DynamicColumnDefinition> ColumnDefinitions
        {
            get => (ObservableCollection<DynamicColumnDefinition>)GetValue(ColumnDefinitionsProperty);
            set => SetValue(ColumnDefinitionsProperty, value);
        }

        public Style ReadOnlyColumnStyle
        {
            get => (Style)GetValue(ReadOnlyColumnStyleProperty);
            set => SetValue(ReadOnlyColumnStyleProperty, value);
        }

        public Style ReadOnlyHeaderStyle
        {
            get => (Style)GetValue(ReadOnlyHeaderStyleProperty);
            set => SetValue(ReadOnlyHeaderStyleProperty, value);
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
            // Unsubscribe from old collection and individual column changes
            if (oldValue != null)
            {
                oldValue.CollectionChanged -= OnColumnDefinitionsCollectionChanged;
                foreach (var column in oldValue)
                {
                    column.PropertyChanged -= OnColumnDefinitionPropertyChanged;
                }
            }

            // Subscribe to new collection and individual column changes
            if (newValue != null)
            {
                newValue.CollectionChanged += OnColumnDefinitionsCollectionChanged;
                foreach (var column in newValue)
                {
                    column.PropertyChanged += OnColumnDefinitionPropertyChanged;
                }
            }

            GenerateColumns();
        }

        private void OnColumnDefinitionPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(DynamicColumnDefinition.IsReadOnly))
            {
                GenerateColumns(); // Regenerate columns when readonly state changes
            }
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

            // Apply read-only styling
            if (columnDef.IsReadOnly)
            {
                // thinking about this one...
                //ApplyReadOnlyStyle(column);
            }

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

        private void ApplyReadOnlyStyle(DataGridColumn column)
        {
            // Apply header style
            if (ReadOnlyHeaderStyle != null)
            {
                column.HeaderStyle = ReadOnlyHeaderStyle;
            }

            // Apply cell style
            if (ReadOnlyColumnStyle != null)
            {
                column.CellStyle = ReadOnlyColumnStyle;
            }
            else
            {
                // Default read-only styling if no custom style provided
                column.CellStyle = CreateDefaultReadOnlyStyle();
            }
        }

        private Style CreateDefaultReadOnlyStyle()
        {
            var style = new Style(typeof(DataGridCell));

            // Set background to light gray
            style.Setters.Add(new Setter(BackgroundProperty, new SolidColorBrush(Color.FromRgb(240, 240, 240))));

            // Set foreground to darker color
            style.Setters.Add(new Setter(ForegroundProperty, new SolidColorBrush(Color.FromRgb(100, 100, 100))));

            // Add italic font style
            style.Setters.Add(new Setter(FontStyleProperty, FontStyles.Italic));

            // Optional: Add a subtle border
            style.Setters.Add(new Setter(BorderBrushProperty, new SolidColorBrush(Color.FromRgb(200, 200, 200))));
            style.Setters.Add(new Setter(BorderThicknessProperty, new Thickness(0, 0, 1, 0)));

            return style;
        }
    }
}