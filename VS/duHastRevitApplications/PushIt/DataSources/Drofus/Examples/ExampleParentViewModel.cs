// BSD License - Copyright 2025, Jan Christel
//
// ────────────────────────────────────────────────────────────────────────────
// HOW TO USE: DrofusSettingsDialog + DrofusSettingsService
// ────────────────────────────────────────────────────────────────────────────
//
// This file shows the pattern a parent ViewModel (e.g. DrofusDataSourceControlViewModel,
// once the full IDataSource implementation is built) would use to:
//
//   1. Open the dialog so the user can enter / update their API-key.
//   2. Persist the result via DrofusSettingsService.
//   3. Hold the loaded DrofusSettings ready for use by ApiKeyAuthService.
//
// It is NOT a production file — drop this logic into whichever ViewModel
// owns the "Configure drofus…" button.
// ────────────────────────────────────────────────────────────────────────────

using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.PushIt.DataSources.Drofus.Models;
using duHastNet.PushIt.DataSources.Drofus.Services;
using duHastNet.PushIt.DataSources.Drofus.ViewModels;
using duHastNet.PushIt.DataSources.Drofus.Views;

namespace duHastNet.PushIt.DataSources.Drofus.Examples;

/// <summary>
/// Example parent ViewModel — replace with the real DrofusDataSourceControlViewModel.
/// </summary>
public partial class ExampleParentViewModel : ObservableObject
{
    private readonly DrofusSettingsService _settingsService = new();

    // The active settings, loaded from disk on construction
    [ObservableProperty]
    private DrofusSettings _drofusSettings;

    // Display string shown in the UI ("Connected: my-db / 01"  or  "Not configured")
    [ObservableProperty]
    private string _connectionSummary = "Not configured";

    public ExampleParentViewModel()
    {
        // Load whatever was saved last session
        _drofusSettings = _settingsService.Load();
        UpdateConnectionSummary();
    }

    // ── "Configure drofus…" button ──────────────────────────────────────────

    [RelayCommand]
    private void ConfigureDrofus()
    {
        // Pre-populate from saved settings if available
        var dialogVm = DrofusSettings.IsConfigured
            ? new DrofusSettingsDialogViewModel(DrofusSettings)
            : new DrofusSettingsDialogViewModel();

        var dialog = new DrofusSettingsDialog(dialogVm)
        {
            Owner = System.Windows.Application.Current.MainWindow
        };

        bool? result = dialog.ShowDialog();

        if (result == true && dialogVm.SavedSettings is not null)
        {
            // Persist to disk
            _settingsService.Save(dialogVm.SavedSettings);

            // Update in-memory state
            DrofusSettings = dialogVm.SavedSettings;
            UpdateConnectionSummary();
        }
    }

    // ── "Disconnect" button — clears stored credentials ────────────────────

    [RelayCommand]
    private void DisconnectDrofus()
    {
        _settingsService.Clear();
        DrofusSettings = new DrofusSettings();
        UpdateConnectionSummary();
    }

    // ── Helper ──────────────────────────────────────────────────────────────

    private void UpdateConnectionSummary()
    {
        ConnectionSummary = DrofusSettings.IsConfigured
            ? $"Connected: {DrofusSettings.DatabaseId} / {DrofusSettings.ProjectNumber} ({DrofusSettings.Region})"
            : "Not configured";
    }
}
