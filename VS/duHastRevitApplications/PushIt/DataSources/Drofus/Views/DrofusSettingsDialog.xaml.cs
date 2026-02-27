// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.DataSources.Drofus.ViewModels;
using System.Windows;

namespace duHastNet.PushIt.DataSources.Drofus.Views;

/// <summary>
/// Interaction logic for DrofusSettingsDialog.xaml
/// Follows the CustomFieldDialog / SupportedFileTypeDialog pattern:
///  - ViewModel injected via constructor
///  - RequestClose event drives DialogResult
/// </summary>
public partial class DrofusSettingsDialog : Window
{
    public DrofusSettingsDialogViewModel ViewModel { get; }

    public DrofusSettingsDialog(DrofusSettingsDialogViewModel viewModel)
    {
        InitializeComponent();

        ViewModel   = viewModel ?? throw new ArgumentNullException(nameof(viewModel));
        DataContext = viewModel;

        viewModel.RequestClose += OnViewModelRequestClose;
    }

    private void OnViewModelRequestClose(object? sender, EventArgs e)
    {
        // SavedSettings is non-null only when OK was clicked and validation passed
        DialogResult = ViewModel.SavedSettings is not null;
        Close();
    }
}
