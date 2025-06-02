using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Media;

namespace duHastNet.UI.CustomControls
{
    public class CustomDataGrid<T> : CustomDataGridBase
    {
        public ObservableCollection<T> ItemsSourceCollection { get; set; } = new ObservableCollection<T>();
        public ObservableCollection<DataGridColumn> DynamicColumns { get; set; } = new ObservableCollection<DataGridColumn>();

        private ICollectionView _collectionView;

        public CustomDataGrid()
        {
            DefaultStyleKeyProperty.OverrideMetadata(typeof(CustomDataGrid<T>),new FrameworkPropertyMetadata(typeof(CustomDataGrid<T>)));

            AutoGenerateColumns = false;
            ItemsSource = ItemsSourceCollection;
            _collectionView = CollectionViewSource.GetDefaultView(ItemsSource);
            Sorting += OnSorting; // Register sorting event
        }

        public void AddTextColumn(string header, string bindingPath)
        {
            var column = new DataGridTextColumn
            {
                Header = header,
                Binding = new Binding(bindingPath)
            };
            DynamicColumns.Add(column);
            RefreshColumns();
        }

        public void AddCheckBoxColumn(string header, string bindingPath)
        {
            var column = new DataGridCheckBoxColumn
            {
                Header = header,
                Binding = new Binding(bindingPath)
            };
            DynamicColumns.Add(column);
            RefreshColumns();
        }

        private void RefreshColumns()
        {
            Columns.Clear();
            foreach (var col in DynamicColumns)
            {
                Columns.Add(col);
            }
        }

        private void OnSorting(object sender, DataGridSortingEventArgs e)
        {
            if (_collectionView == null) return;

            var existingSort = _collectionView.SortDescriptions.FirstOrDefault(sd => sd.PropertyName == e.Column.SortMemberPath);
            var direction = existingSort.Direction == ListSortDirection.Ascending ? ListSortDirection.Descending : ListSortDirection.Ascending;

            _collectionView.SortDescriptions.Clear();
            _collectionView.SortDescriptions.Add(new SortDescription(e.Column.SortMemberPath, direction));
            _collectionView.Refresh();
            e.Handled = true;
        }
    }
}