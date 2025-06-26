using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Windows;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public partial class FilterDropDownDialog : Window, INotifyPropertyChanged
    {
        #region Properties

        private string _columnName;
        private List<object> _availableValues;
        private object _selectedValue;
        private string _searchText;

        public string ColumnName
        {
            get => _columnName;
            set
            {
                _columnName = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(ColumnDisplayText));
            }
        }

        public string ColumnDisplayText => $"'{ColumnName}'";

        public List<object> AvailableValues
        {
            get => _availableValues;
            set
            {
                _availableValues = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(StatusText));
            }
        }

        public object SelectedValue
        {
            get => _selectedValue;
            set
            {
                _selectedValue = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(HasSelectedValue));
                OnPropertyChanged(nameof(StatusText));
            }
        }

        public string SearchText
        {
            get => _searchText;
            set
            {
                _searchText = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(HasSearchText));
                OnPropertyChanged(nameof(StatusText));
            }
        }

        public bool HasSelectedValue => SelectedValue != null;
        public bool HasSearchText => !string.IsNullOrWhiteSpace(SearchText);

        public string StatusText
        {
            get
            {
                if (AvailableValues == null || AvailableValues.Count == 0)
                    return "No values available for this column";

                if (!HasSelectedValue)
                    return $"{AvailableValues.Count} values available - select one to filter";

                if (HasSearchText)
                    return $"Will show items where '{SelectedValue}' contains '{SearchText}'";

                return $"Will show items with value '{SelectedValue}'";
            }
        }

        #endregion

        #region Dialog Result Properties

        public bool FilterCleared { get; private set; }

        #endregion

        #region Constructors

        public FilterDropDownDialog(string columnName, List<object> availableValues, object currentSelectedValue = null, string currentSearchText = null)
        {
            InitializeComponent();
            DataContext = this;

            ColumnName = columnName;
            AvailableValues = availableValues ?? new List<object>();
            SelectedValue = currentSelectedValue;
            SearchText = currentSearchText;

            // Focus the list box
            Loaded += (s, e) => ValuesListBox.Focus();
        }

        #endregion

        #region Event Handlers

        private void ApplyFilter_Click(object sender, RoutedEventArgs e)
        {
            if (!HasSelectedValue)
            {
                MessageBox.Show("Please select a value from the list.", "No Value Selected",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            FilterCleared = false;
            DialogResult = true;
        }

        private void ClearFilter_Click(object sender, RoutedEventArgs e)
        {
            FilterCleared = true;
            DialogResult = true;
        }

        private void ClearSearchText_Click(object sender, RoutedEventArgs e)
        {
            SearchText = string.Empty;
            SearchTextBox.Focus();
        }

        #endregion

        #region INotifyPropertyChanged

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        #endregion
    }
}