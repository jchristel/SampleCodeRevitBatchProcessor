using System.Windows;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public partial class FilterTextDialog : Window
    {
        public string FilterText { get; private set; }
        public bool UseAndLogic { get; private set; }

        public FilterTextDialog(string propertyName, string currentFilter = "")
        {
            InitializeComponent();

            Title = $"Filter {propertyName}";
            FilterTextBox.Text = currentFilter;

            // Focus and select the text
            Loaded += (s, e) =>
            {
                FilterTextBox.Focus();
                FilterTextBox.SelectAll();
            };

            // Handle Enter key in textbox
            FilterTextBox.KeyDown += (s, e) =>
            {
                if (e.Key == System.Windows.Input.Key.Enter)
                {
                    ApplyFilter();
                }
            };
        }

        private void ApplyButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyFilter();
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
        }

        private void ApplyFilter()
        {
            FilterText = FilterTextBox.Text?.Trim() ?? "";
            UseAndLogic = AndRadio.IsChecked == true;
            DialogResult = true;
        }
    }
}