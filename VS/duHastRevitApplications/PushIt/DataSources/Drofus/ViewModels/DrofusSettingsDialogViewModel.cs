// BSD License - Copyright 2025, Jan Christel

using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.PushIt.DataSources.Drofus.Models;
using duHastNet.PushIt.DataSources.Drofus.Services;
using System.Collections.ObjectModel;
using System.ComponentModel.DataAnnotations;

namespace duHastNet.PushIt.DataSources.Drofus.ViewModels;

/// <summary>
/// ViewModel for the drofus API-key entry dialog.
/// Follows the SupportedFileTypeDialogViewModel / CustomFieldDialogViewModel pattern:
///  - ObservableValidator for inline validation
///  - RelayCommand(CanExecute) on OK
///  - RequestClose event to signal the View
///
/// Responsibilities:
///  1. Let the user enter Region, DatabaseId, ProjectNumber, and ApiKey.
///  2. Validate that all fields are non-empty.
///  3. On OK: hit the live drofus API to confirm the key works.
///  4. If successful: expose a filled DrofusSettings for the caller to persist.
/// </summary>
public partial class DrofusSettingsDialogViewModel : ObservableValidator
{
    // -------------------------------------------------------------------------
    // Private fields
    // -------------------------------------------------------------------------

    private readonly ApiKeyAuthService _authService;

    // -------------------------------------------------------------------------
    // Observable properties (with inline validation)
    // -------------------------------------------------------------------------

    /// <summary>Selected drofus region (dropdown).</summary>
    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(OkCommand))]
    private DrofusRegion _selectedRegion = DrofusRegion.EU;

    /// <summary>drofus database identifier (e.g. "my-project-db").</summary>
    [ObservableProperty]
    [Required(ErrorMessage = "Database ID is required")]
    [NotifyDataErrorInfo]
    [NotifyCanExecuteChangedFor(nameof(OkCommand))]
    private string _databaseId = string.Empty;

    /// <summary>Project number within the database (e.g. "01").</summary>
    [ObservableProperty]
    [Required(ErrorMessage = "Project number is required")]
    [NotifyDataErrorInfo]
    [NotifyCanExecuteChangedFor(nameof(OkCommand))]
    private string _projectNumber = string.Empty;

    /// <summary>API-key generated in drofus.</summary>
    [ObservableProperty]
    [Required(ErrorMessage = "API-key is required")]
    [NotifyDataErrorInfo]
    [NotifyCanExecuteChangedFor(nameof(OkCommand))]
    private string _apiKey = string.Empty;

    /// <summary>Status message shown below the form (validation result / error).</summary>
    [ObservableProperty]
    private string _statusMessage = string.Empty;

    /// <summary>True while the live validation call is in progress.</summary>
    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(OkCommand))]
    private bool _isValidating = false;

    /// <summary>Colour key for the status message ("OK" = green, "Error" = red, "" = default).</summary>
    [ObservableProperty]
    private string _statusSeverity = string.Empty;

    // -------------------------------------------------------------------------
    // Read-only properties
    // -------------------------------------------------------------------------

    /// <summary>Available regions for the ComboBox.</summary>
    public ObservableCollection<DrofusRegion> AvailableRegions { get; } =
        new(Enum.GetValues<DrofusRegion>());

    /// <summary>
    /// Populated after a successful OK. The caller reads this to persist settings.
    /// Null if the user cancelled or validation failed.
    /// </summary>
    public DrofusSettings? SavedSettings { get; private set; }

    // -------------------------------------------------------------------------
    // Events
    // -------------------------------------------------------------------------

    /// <summary>Raised when the dialog should close. Sender carries the result.</summary>
    public event EventHandler? RequestClose;

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    public DrofusSettingsDialogViewModel(ApiKeyAuthService? authService = null)
    {
        _authService = authService ?? new ApiKeyAuthService();
    }

    /// <summary>Pre-populate the form from existing saved settings.</summary>
    public DrofusSettingsDialogViewModel(DrofusSettings existing, ApiKeyAuthService? authService = null)
        : this(authService)
    {
        SelectedRegion = existing.Region;
        DatabaseId     = existing.DatabaseId;
        ProjectNumber  = existing.ProjectNumber;
        ApiKey         = existing.ApiKey;
    }

    // -------------------------------------------------------------------------
    // Commands
    // -------------------------------------------------------------------------

    /// <summary>
    /// OK command: validates live against drofus, then closes with success.
    /// Disabled while fields are invalid or a validation call is in progress.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanExecuteOk))]
    private async Task OkAsync()
    {
        // Run DataAnnotations validation first
        ValidateAllProperties();
        if (HasErrors)
        {
            SetStatus("Please fix the errors above before continuing.", isError: true);
            return;
        }

        IsValidating = true;
        SetStatus("Connecting to drofus…", isError: false);

        try
        {
            var settings = BuildAuthSettings();
            var result   = await _authService.AcquireTokenAsync(settings);

            if (!result.Success)
            {
                SetStatus(result.ErrorMessage ?? "Unknown error.", isError: true);
                return;
            }

            // Success — package up the settings for the caller
            SavedSettings = new DrofusSettings
            {
                Region        = SelectedRegion,
                DatabaseId    = DatabaseId.Trim(),
                ProjectNumber = ProjectNumber.Trim(),
                ApiKey        = ApiKey.Trim()
            };

            SetStatus("Connection successful!", isError: false);

            // Small delay so the user sees the success message
            await Task.Delay(600);
            RequestClose?.Invoke(this, EventArgs.Empty);
        }
        finally
        {
            IsValidating = false;
        }
    }

    private bool CanExecuteOk() =>
        !IsValidating &&
        !string.IsNullOrWhiteSpace(DatabaseId) &&
        !string.IsNullOrWhiteSpace(ProjectNumber) &&
        !string.IsNullOrWhiteSpace(ApiKey);

    /// <summary>Cancel command — closes without saving.</summary>
    [RelayCommand]
    private void Cancel()
    {
        SavedSettings = null;
        RequestClose?.Invoke(this, EventArgs.Empty);
    }

    // -------------------------------------------------------------------------
    // Private helpers
    // -------------------------------------------------------------------------

    private DrofusAuthSettings BuildAuthSettings() => new()
    {
        AuthMode      = DrofusAuthMode.ApiKey,
        Region        = SelectedRegion,
        DatabaseId    = DatabaseId.Trim(),
        ProjectNumber = ProjectNumber.Trim(),
        ApiKey        = ApiKey.Trim()
    };

    private void SetStatus(string message, bool isError)
    {
        StatusMessage  = message;
        StatusSeverity = isError ? "Error" : "OK";
    }
}
