using System.Windows;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Views
{
    public partial class PrintSetNameDialog : Window
    {
        public string PrintsetName { get; private set; }
     
        public PrintSetNameDialog(string propertyName, string currentFilter = "")
        {
            InitializeComponent();

            Title = $"Filter {propertyName}";
            PrintSetTextBox.Text = currentFilter;

            // Focus and select the text
            Loaded += (s, e) =>
            {
                PrintSetTextBox.Focus();
                PrintSetTextBox.SelectAll();
            };

            // Handle Enter key in textbox
            PrintSetTextBox.KeyDown += (s, e) =>
            {
                if (e.Key == System.Windows.Input.Key.Enter)
                {
                    CreateSetName();
                }
            };
        }

        private void CreateButton_Click(object sender, RoutedEventArgs e)
        {
            CreateSetName();
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
        }

        private void CreateSetName()
        {
            PrintsetName = PrintSetTextBox.Text?.Trim() ?? "";
            DialogResult = true;
        }
    }
}