using System.Collections.Generic;
using System.Windows;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Views
{
    public partial class PrintSetNameDialog : Window
    {
        public PrintSetNameDialog(string defaultPrintSetName, IEnumerable<string> allCurrentSets)
        {
            InitializeComponent();

            var viewModel = new ViewModels.PrintSetNameDialogViewModel(defaultPrintSetName, allCurrentSets);
            DataContext = viewModel;

            // Subscribe to DialogResult changes to close the window
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(ViewModels.PrintSetNameDialogViewModel.DialogResult))
                {
                    this.DialogResult = viewModel.DialogResult;
                }
            };

            // Focus and select text when loaded
            Loaded += (s, e) =>
            {
                PrintSetTextBox.Focus();
                PrintSetTextBox.SelectAll();
            };
        }

        public string PrintSetName =>
            (DataContext as ViewModels.PrintSetNameDialogViewModel)?.PrintSetName?.Trim() ?? string.Empty;
    }
}