using System.Windows;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public partial class FilterBooleanDialog : Window
    {
        public bool? ShowTrue { get; private set; }
        public bool? ShowFalse { get; private set; }
        public bool FilterCleared { get; private set; }

        public FilterBooleanDialog(string propertyName, bool? currentShowTrue = null, bool? currentShowFalse = null)
        {
            InitializeComponent();

            Title = $"Filter {propertyName}";

            // Set current filter state
            if (currentShowTrue.HasValue)
            {
                ShowTrueCheckBox.IsChecked = currentShowTrue.Value;
            }

            if (currentShowFalse.HasValue)
            {
                ShowFalseCheckBox.IsChecked = currentShowFalse.Value;
            }

            UpdateCurrentFilterDisplay();
        }

        private void ApplyButton_Click(object sender, RoutedEventArgs e)
        {
            ShowTrue = ShowTrueCheckBox.IsChecked;
            ShowFalse = ShowFalseCheckBox.IsChecked;
            FilterCleared = false;
            DialogResult = true;
        }

        private void ClearButton_Click(object sender, RoutedEventArgs e)
        {
            ShowTrue = null;
            ShowFalse = null;
            FilterCleared = true;
            DialogResult = true;
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
        }

        private void UpdateCurrentFilterDisplay()
        {
            var showTrue = ShowTrueCheckBox.IsChecked == true;
            var showFalse = ShowFalseCheckBox.IsChecked == true;

            if (showTrue && showFalse)
            {
                CurrentFilterText.Text = "Currently showing: All values";
            }
            else if (showTrue)
            {
                CurrentFilterText.Text = "Currently showing: True values only";
            }
            else if (showFalse)
            {
                CurrentFilterText.Text = "Currently showing: False values only";
            }
            else
            {
                CurrentFilterText.Text = "Currently showing: No values (all hidden)";
            }
        }
    }
}